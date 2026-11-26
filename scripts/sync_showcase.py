#!/usr/bin/env python3
"""Pull showcase content from private repos into the portfolio site.

Only two things are ever read from a private repo:
  * each project's ``project.yml`` (metadata card)
  * the files under that project's ``.showcase/`` folder (public write-up + media)

Nothing else (source code, datasets, docs, technical READMEs) is fetched.

Sources
-------
GitHub mode (default): every repo owned by $SHOWCASE_OWNER that carries the
GitHub topic ``showcase``. Needs $SHOWCASE_TOKEN with read-only Contents and
Metadata access on those repos.

Local mode (``--local DIR``): every git-less folder in DIR is treated as a repo.
Used for tests and for previewing before pushing.

Output
------
* docs/projects/<repo>/<slug>/index.md (+ index.it.md, media/) for level >= page
* docs/projects/index.md and index.it.md: generated listing, grouped by context type
* docs/index.md / index.it.md featured block
* showcase.lock.json: what is live, where it came from
* significance (none | minor | substantial) printed and written to $GITHUB_OUTPUT

Significance rule (owner's rule, 2026-11-25): small updates to approved
content go out automatically; anything substantial waits for approval.
  substantial = a new project, a level going up, a demo added or changed,
                featured switched on
  minor       = text/media edits of an existing entry, a level going down,
                an entry removed
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PROJECTS_DIR = DOCS / "projects"
LOCK_FILE = ROOT / "showcase.lock.json"

LEVELS = ["hidden", "card", "page", "demo", "open"]
CONTEXT_TYPES = ["course", "thesis", "company", "personal"]
CONTEXT_LABELS = {
    "en": {"course": "University courses", "thesis": "Theses", "company": "Work", "personal": "Personal projects"},
    "it": {"course": "Corsi universitari", "thesis": "Tesi", "company": "Lavoro", "personal": "Progetti personali"},
}
REQUIRED = ["title", "slug", "summary", "context", "context_type", "level"]
MAX_FILE_BYTES = 20 * 1024 * 1024
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_SUFFIXES = {
    ".md", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ply", ".mp4", ".webm",
    ".json", ".csv", ".txt", ".glb", ".gltf", ".pdf",
}


# --------------------------------------------------------------------------- sources

class Source:
    """A repo we may read project.yml files and .showcase/ folders from."""

    name: str
    commit: str

    def project_files(self) -> list[str]:
        raise NotImplementedError

    def read(self, path: str) -> bytes:
        raise NotImplementedError

    def list_dir(self, prefix: str) -> list[tuple[str, int]]:
        """Files (path, size) under prefix. Symlinks are never returned."""
        raise NotImplementedError


class LocalSource(Source):
    def __init__(self, path: Path):
        self.root = path
        self.name = path.name
        self.commit = "local"

    def project_files(self) -> list[str]:
        out = []
        for p in self.root.rglob("project.yml"):
            rel = p.relative_to(self.root)
            if any(part.startswith(".") for part in rel.parts[:-1]):
                continue
            out.append(rel.as_posix())
        return sorted(out)

    def read(self, path: str) -> bytes:
        return (self.root / path).read_bytes()

    def list_dir(self, prefix: str) -> list[tuple[str, int]]:
        base = self.root / prefix
        if not base.is_dir():
            return []
        out = []
        for p in sorted(base.rglob("*")):
            if p.is_symlink() or not p.is_file():
                continue
            out.append((p.relative_to(self.root).as_posix(), p.stat().st_size))
        return out


class GitHubSource(Source):
    API = "https://api.github.com"

    def __init__(self, full_name: str, default_branch: str, token: str):
        self.full_name = full_name
        self.name = full_name.split("/", 1)[1]
        self.token = token
        branch = gh_get(f"/repos/{full_name}/branches/{urllib.parse.quote(default_branch)}", token)
        self.commit = branch["commit"]["sha"]
        tree = gh_get(f"/repos/{full_name}/git/trees/{self.commit}?recursive=1", token)
        if tree.get("truncated"):
            raise SystemExit(f"{full_name}: git tree too large to list in one call")
        # mode 120000 = symlink, 160000 = submodule: never followed
        self.blobs = {
            e["path"]: (e["sha"], e.get("size", 0))
            for e in tree["tree"]
            if e["type"] == "blob" and e["mode"] in ("100644", "100755")
        }

    def project_files(self) -> list[str]:
        return sorted(
            p for p in self.blobs
            if PurePosixPath(p).name == "project.yml"
            and not any(part.startswith(".") for part in PurePosixPath(p).parts[:-1])
        )

    def read(self, path: str) -> bytes:
        sha, _ = self.blobs[path]
        blob = gh_get(f"/repos/{self.full_name}/git/blobs/{sha}", self.token)
        return base64.b64decode(blob["content"])

    def list_dir(self, prefix: str) -> list[tuple[str, int]]:
        prefix = prefix.rstrip("/") + "/"
        return sorted((p, s) for p, (_, s) in self.blobs.items() if p.startswith(prefix))


def gh_get(path: str, token: str):
    req = urllib.request.Request(
        GitHubSource.API + path,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "portfolio-showcase-sync",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def github_sources(owner: str, token: str) -> list[Source]:
    repos, page = [], 1
    while True:
        batch = gh_get(f"/user/repos?affiliation=owner&per_page=100&page={page}", token)
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    picked = [
        r for r in repos
        if r["owner"]["login"].lower() == owner.lower()
        and "showcase" in r.get("topics", [])
        and not r.get("archived", False)
    ]
    return [GitHubSource(r["full_name"], r["default_branch"], token) for r in picked]


def local_sources(base: Path) -> list[Source]:
    return [LocalSource(p) for p in sorted(base.iterdir()) if p.is_dir() and not p.name.startswith(".")]


# --------------------------------------------------------------------------- model

@dataclass
class Entry:
    repo: str
    folder: str                   # project folder inside the repo ("" = repo root)
    meta: dict
    commit: str
    files: dict[str, bytes] = field(default_factory=dict)   # relative to .showcase/

    @property
    def key(self) -> str:
        return f"{self.repo}/{self.meta['slug']}"

    @property
    def level(self) -> str:
        return self.meta["level"]

    @property
    def rank(self) -> int:
        return LEVELS.index(self.level)

    def content_hash(self) -> str:
        h = hashlib.sha256()
        h.update(json.dumps(self.meta, sort_keys=True, default=str).encode())
        for name in sorted(self.files):
            h.update(name.encode())
            h.update(hashlib.sha256(self.files[name]).digest())
        return h.hexdigest()


def validate(meta: dict, where: str, private_repos: set[str]) -> list[str]:
    errs = []
    if not isinstance(meta, dict):
        return [f"{where}: project.yml is not a mapping"]
    for f in REQUIRED:
        if meta.get(f) in (None, ""):
            errs.append(f"{where}: missing required field '{f}'")
    if meta.get("level") not in LEVELS:
        errs.append(f"{where}: level must be one of {LEVELS}")
    if meta.get("level") != "hidden":
        if meta.get("context_type") not in CONTEXT_TYPES:
            errs.append(f"{where}: context_type must be one of {CONTEXT_TYPES}")
        if meta.get("slug") and not SLUG_RE.match(str(meta["slug"])):
            errs.append(f"{where}: slug must be kebab-case")
        langs = meta.get("languages", ["en"])
        if not isinstance(langs, list) or "en" not in langs or not set(langs) <= {"en", "it"}:
            errs.append(f"{where}: languages must be [en] or [en, it]")
        if meta.get("level") == "open" and not str(meta.get("source", "")).startswith("https://"):
            errs.append(f"{where}: level 'open' needs a public 'source' URL")
        if meta.get("level") == "demo" and not meta.get("demo"):
            errs.append(f"{where}: level 'demo' needs a 'demo' (URL or a file inside .showcase/)")
    return errs


def private_link_errors(text: str, where: str, owner: str, private_repos: set[str]) -> list[str]:
    errs = []
    for repo in private_repos:
        if re.search(rf"github\.com/{re.escape(owner)}/{re.escape(repo)}\b", text, re.I):
            errs.append(f"{where}: links to private repo {owner}/{repo}")
    return errs


def collect(sources: list[Source], owner: str) -> tuple[list[Entry], list[str]]:
    entries: list[Entry] = []
    errors: list[str] = []
    private_repos = {s.name for s in sources}
    seen: set[str] = set()
    for src in sources:
        for pfile in src.project_files():
            folder = str(PurePosixPath(pfile).parent)
            folder = "" if folder == "." else folder
            where = f"{src.name}/{pfile}"
            try:
                meta = yaml.safe_load(src.read(pfile)) or {}
            except yaml.YAMLError as e:
                errors.append(f"{where}: invalid YAML ({e})")
                continue
            errs = validate(meta, where, private_repos)
            if errs:
                errors += errs
                continue
            if meta["level"] == "hidden":
                continue
            entry = Entry(src.name, folder, meta, src.commit)
            if entry.key in seen:
                errors.append(f"{where}: duplicate slug '{meta['slug']}' in {src.name}")
                continue
            seen.add(entry.key)

            if entry.rank >= LEVELS.index("page"):
                prefix = f"{folder}/.showcase" if folder else ".showcase"
                for path, size in src.list_dir(prefix):
                    rel = path[len(prefix) + 1:]
                    if size > MAX_FILE_BYTES:
                        errors.append(f"{src.name}/{path}: {size / 1e6:.1f} MB is over the 20 MB limit")
                        continue
                    if PurePosixPath(rel).suffix.lower() not in ALLOWED_SUFFIXES:
                        errors.append(f"{src.name}/{path}: file type not allowed in .showcase/")
                        continue
                    entry.files[rel] = src.read(path)
                if "README.md" not in entry.files:
                    errors.append(f"{where}: level '{meta['level']}' needs .showcase/README.md")
                    continue
                if "it" in meta.get("languages", ["en"]) and "README.it.md" not in entry.files:
                    errors.append(f"{where}: languages lists 'it' but .showcase/README.it.md is missing")
                    continue
                for rel, data in entry.files.items():
                    if rel.endswith(".md"):
                        errors += private_link_errors(data.decode("utf-8", "replace"), f"{where} .showcase/{rel}", owner, private_repos)
            entries.append(entry)
    return entries, errors


# --------------------------------------------------------------------------- rendering

def tags(meta: dict) -> str:
    items = list(meta.get("tech", []) or []) + list(meta.get("topics", []) or [])
    return " ".join(f'<span class="tag">{t}</span>' for t in items)


def meta_line(meta: dict, lang: str) -> str:
    bits = [str(meta["context"])]
    if meta.get("date"):
        bits.append(str(meta["date"]))
    if meta.get("status") and meta["status"] != "done":
        bits.append(str(meta["status"]))
    return " · ".join(bits)


def page_header(e: Entry, lang: str) -> str:
    m = e.meta
    lines = [f'<p class="project-meta">{meta_line(m, lang)}</p>', "", tags(m), ""]
    demo = m.get("demo")
    if e.level in ("demo", "open") and demo and str(demo).startswith("https://"):
        label = "Open the demo" if lang == "en" else "Apri la demo"
        lines += [f"[{label}]({demo}){{ .md-button .md-button--primary }}", ""]
    if e.level == "open" and m.get("source"):
        label = "Source code" if lang == "en" else "Codice sorgente"
        lines += [f"[{label}]({m['source']}){{ .md-button }}", ""]
    elif e.level != "open":
        note = ("The source code is private; get in touch to request access."
                if lang == "en" else "Il codice sorgente è privato; contattami per richiedere l'accesso.")
        lines += [f"!!! note \"\"\n    {note}", ""]
    return "\n".join(lines)


def write_page(e: Entry, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for rel, data in e.files.items():
        if rel in ("README.md", "README.it.md"):
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    for lang, name, target in (("en", "README.md", "index.md"), ("it", "README.it.md", "index.it.md")):
        if name not in e.files:
            continue
        body = e.files[name].decode("utf-8")
        title = e.meta["title"]
        # The write-up's own H1 is replaced by the title from project.yml.
        body = re.sub(r"\A\s*# .*\n", "", body)
        text = f"# {title}\n\n{page_header(e, lang)}\n{body.lstrip()}"
        (out / target).write_text(text, encoding="utf-8")


def card(e: Entry, lang: str, link_prefix: str) -> str:
    m = e.meta
    title = m["title"]
    if e.rank >= LEVELS.index("page"):
        title = f'<a href="{link_prefix}{e.repo}/{m["slug"]}/">{title}</a>'
    return (
        f'<div class="project-card" markdown>\n'
        f'<h3>{title}</h3>\n'
        f'<p class="project-meta">{meta_line(m, lang)}</p>\n'
        f'<p>{m["summary"]}</p>\n'
        f'{tags(m)}\n'
        f'</div>\n'
    )


def sort_key(e: Entry):
    return (str(e.meta["context"]), e.meta.get("order", 999), str(e.meta.get("date", "")), e.meta["title"])


def listing(entries: list[Entry], lang: str) -> str:
    if not entries:
        return "*No projects published yet.*" if lang == "en" else "*Nessun progetto pubblicato.*"
    out = []
    for ctype in CONTEXT_TYPES:
        group = sorted((e for e in entries if e.meta["context_type"] == ctype), key=sort_key)
        if not group:
            continue
        out.append(f"## {CONTEXT_LABELS[lang][ctype]}\n")
        current = None
        for e in group:
            if e.meta["context"] != current:
                current = e.meta["context"]
                out.append(f"### {current}\n")
            out.append(card(e, lang, ""))
    return "\n".join(out)


def featured(entries: list[Entry], lang: str) -> str:
    feats = sorted((e for e in entries if e.meta.get("featured")), key=sort_key)
    if not feats:
        return ("*Featured projects will appear here once they are published.*" if lang == "en"
                else "*I progetti in evidenza appariranno qui una volta pubblicati.*")
    return "\n".join(card(e, lang, "projects/") for e in feats)


def replace_block(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(<!-- {marker}:start -->\n).*?(\n<!-- {marker}:end -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"{path}: markers for '{marker}' not found")
    path.write_text(pattern.sub(lambda m: m.group(1) + content + m.group(2), text), encoding="utf-8")


def render(entries: list[Entry]) -> None:
    # Wipe generated project folders, keep the hand-written index pages.
    for child in PROJECTS_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
    for e in entries:
        if e.rank >= LEVELS.index("page"):
            write_page(e, PROJECTS_DIR / e.repo / e.meta["slug"])
    for lang, suffix in (("en", ""), ("it", ".it")):
        replace_block(PROJECTS_DIR / f"index{suffix}.md", "generated", listing(entries, lang))
        replace_block(DOCS / f"index{suffix}.md", "featured", featured(entries, lang))


# --------------------------------------------------------------------------- lock + significance

def lock_of(entries: list[Entry]) -> dict:
    return {
        e.key: {
            "repo": e.repo,
            "folder": e.folder,
            "commit": e.commit,
            "level": e.level,
            "demo": e.meta.get("demo") or "",
            "featured": bool(e.meta.get("featured")),
            "hash": e.content_hash(),
        }
        for e in sorted(entries, key=lambda x: x.key)
    }


def compare(old: dict, new: dict) -> tuple[str, list[str]]:
    reasons_sub, reasons_min = [], []
    for key, n in new.items():
        o = old.get(key)
        if o is None:
            reasons_sub.append(f"new project {key} at level '{n['level']}'")
            continue
        if LEVELS.index(n["level"]) > LEVELS.index(o["level"]):
            reasons_sub.append(f"{key}: level {o['level']} -> {n['level']}")
        elif LEVELS.index(n["level"]) < LEVELS.index(o["level"]):
            reasons_min.append(f"{key}: level {o['level']} -> {n['level']}")
        if n["demo"] != o["demo"] and n["demo"]:
            reasons_sub.append(f"{key}: demo added or changed")
        if n["featured"] and not o["featured"]:
            reasons_sub.append(f"{key}: now featured")
        if n["hash"] != o["hash"] and not any(r.startswith(key) for r in reasons_sub):
            reasons_min.append(f"{key}: content updated")
    for key in old.keys() - new.keys():
        reasons_min.append(f"{key}: removed or hidden")
    if reasons_sub:
        return "substantial", reasons_sub + reasons_min
    if reasons_min:
        return "minor", reasons_min
    return "none", []


def set_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            if "\n" in value:
                f.write(f"{name}<<EOF_{name}\n{value}\nEOF_{name}\n")
            else:
                f.write(f"{name}={value}\n")


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--local", type=Path, help="folder of local repos to read instead of GitHub")
    ap.add_argument("--owner", default=os.environ.get("SHOWCASE_OWNER", "GrimHope"))
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()

    if args.local:
        sources = local_sources(args.local)
    else:
        token = os.environ.get("SHOWCASE_TOKEN")
        if not token:
            print("SHOWCASE_TOKEN is not set", file=sys.stderr)
            return 2
        sources = github_sources(args.owner, token)
    print(f"Reading {len(sources)} repo(s): {', '.join(s.name for s in sources) or '-'}")

    entries, errors = collect(sources, args.owner)
    if errors:
        print("Validation failed, nothing was changed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"{len(entries)} project(s) to show")

    old = json.loads(LOCK_FILE.read_text()) if LOCK_FILE.exists() else {}
    new = lock_of(entries)
    significance, reasons = compare(old, new)
    print(f"Significance: {significance}")
    for r in reasons:
        print(f"  - {r}")
    set_output("significance", significance)
    set_output("reasons", "\n".join(f"- {r}" for r in reasons) or "- no changes")

    if args.check:
        return 0
    render(entries)
    LOCK_FILE.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
