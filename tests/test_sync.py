"""Run the sync against local fixture repos in a throwaway copy of the site."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
FIXTURES = HERE / "fixtures" / "repos"


@pytest.fixture
def site(tmp_path):
    dst = tmp_path / "site"
    shutil.copytree(SITE, dst, ignore=shutil.ignore_patterns("tests", "site", ".git", "__pycache__"))
    (dst / "showcase.lock.json").write_text("{}")
    repos = tmp_path / "repos"
    shutil.copytree(FIXTURES, repos)
    return dst, repos


def run(site_dir, repos, *extra):
    return subprocess.run(
        [sys.executable, str(site_dir / "scripts" / "sync_showcase.py"), "--local", str(repos), *extra],
        capture_output=True, text=True,
    )


def project_yml(repos):
    return repos / "msc-example-course" / "example-lab" / "project.yml"


def edit(path, **changes):
    data = yaml.safe_load(path.read_text())
    data.update(changes)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def test_first_sync_is_substantial_and_copies_only_showcase(site):
    site_dir, repos = site
    r = run(site_dir, repos)
    assert r.returncode == 0, r.stderr
    assert "Significance: substantial" in r.stdout
    page = site_dir / "docs/projects/msc-example-course/example-lab"
    assert (page / "index.md").exists() and (page / "index.it.md").exists()
    assert (page / "media/result.png").exists()
    copied = "\n".join(p.read_text(errors="ignore") for p in site_dir.rglob("*") if p.is_file() and p.suffix in {".md", ".py", ".json"} and "scripts" not in p.parts)
    assert "must never be copied" not in copied
    assert "Hidden lab" not in (site_dir / "docs/projects/index.md").read_text()
    assert "Example lab" in (site_dir / "docs/projects/index.md").read_text()
    lock = json.loads((site_dir / "showcase.lock.json").read_text())
    assert list(lock) == ["msc-example-course/example-lab"]


def test_text_edit_is_minor(site):
    site_dir, repos = site
    run(site_dir, repos)
    readme = repos / "msc-example-course/example-lab/.showcase/README.md"
    readme.write_text(readme.read_text() + "\nOne more sentence.\n")
    r = run(site_dir, repos)
    assert "Significance: minor" in r.stdout


def test_no_change_is_none(site):
    site_dir, repos = site
    run(site_dir, repos)
    assert "Significance: none" in run(site_dir, repos).stdout


@pytest.mark.parametrize("changes", [
    {"level": "demo", "demo": "https://example.org/demo"},
    {"featured": True},
])
def test_level_up_demo_or_featured_is_substantial(site, changes):
    site_dir, repos = site
    run(site_dir, repos)
    edit(project_yml(repos), **changes)
    assert "Significance: substantial" in run(site_dir, repos).stdout


def test_hiding_is_minor_and_removes_page(site):
    site_dir, repos = site
    run(site_dir, repos)
    edit(project_yml(repos), level="hidden")
    r = run(site_dir, repos)
    assert "Significance: minor" in r.stdout
    assert not (site_dir / "docs/projects/msc-example-course").exists()


def test_validation_blocks_everything(site):
    site_dir, repos = site
    edit(project_yml(repos), context_type="school")
    r = run(site_dir, repos)
    assert r.returncode == 1
    assert "context_type" in r.stderr
    assert json.loads((site_dir / "showcase.lock.json").read_text()) == {}


def test_link_to_private_repo_is_rejected(site):
    site_dir, repos = site
    readme = repos / "msc-example-course/example-lab/.showcase/README.md"
    readme.write_text(readme.read_text() + "\nSee https://github.com/GrimHope/msc-example-course\n")
    r = run(site_dir, repos)
    assert r.returncode == 1 and "private repo" in r.stderr


def test_missing_italian_copy_is_rejected(site):
    site_dir, repos = site
    (repos / "msc-example-course/example-lab/.showcase/README.it.md").unlink()
    r = run(site_dir, repos)
    assert r.returncode == 1 and "README.it.md" in r.stderr


def test_site_builds_with_synced_project(site):
    site_dir, repos = site
    run(site_dir, repos)
    b = subprocess.run(["mkdocs", "build", "--strict", "-q"], cwd=site_dir, capture_output=True, text=True)
    assert b.returncode == 0, b.stderr
    assert (site_dir / "site/projects/msc-example-course/example-lab/index.html").exists()
    assert (site_dir / "site/it/projects/msc-example-course/example-lab/index.html").exists()
