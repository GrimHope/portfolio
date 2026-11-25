# portfolio

Source of the public portfolio site at **https://grimhope.github.io/portfolio/**: documentation and demos of projects whose code mostly lives in private repos.

## How it works

Every private repo with something to show carries the GitHub topic `showcase`. Each project folder in it has a `project.yml` (metadata) and a `.showcase/` folder (public write-up and media). Every night, [`sync.yml`](.github/workflows/sync.yml) runs [`scripts/sync_showcase.py`](scripts/sync_showcase.py), which reads **only** those two things, rebuilds the project pages and deploys the site.

| `level` in project.yml | Shown on the site |
| --- | --- |
| `hidden` | nothing |
| `card` | a card in the project list |
| `page` | card + page from `.showcase/README.md` |
| `demo` | page + demo link or embedded demo (`demo` field) |
| `open` | page + link to the public source (`source` field) |

Italian copies: projects with `languages: [en, it]` also need `.showcase/README.it.md`; the site shows an English/Italian switch.

### What goes live on its own, and what waits for approval

| Change found by the nightly sync | What happens |
| --- | --- |
| Text or media edits of an entry already on the site | Committed to `main` and deployed |
| Level lowered, or project hidden | Committed to `main` and deployed |
| New project, level raised, demo added or changed, newly featured | Pull request labelled `needs-approval`; goes live when merged |

The sync refuses to change anything if a `project.yml` is invalid, a file is over 20 MB or of an unexpected type, an Italian copy is missing, or a write-up links into a private repo.

## One-time setup

1. **Settings → Pages → Source: GitHub Actions.**
2. **Settings → Actions → General → Workflow permissions:** read and write, and allow GitHub Actions to create pull requests.
3. Create a fine-grained personal access token (GitHub → Settings → Developer settings → Fine-grained tokens): resource owner GrimHope, access to the private repos to showcase (or all repos), permissions **Contents: read-only** and **Metadata: read-only**. Save it in this repo as the Actions secret `SHOWCASE_TOKEN`.
4. Add the topic `showcase` to each private repo that should appear.

## Working locally

```bash
pip install -r requirements.txt
mkdocs serve                                   # preview at http://127.0.0.1:8000/portfolio/
python scripts/sync_showcase.py --local ../    # preview sync from local clones (check `git status` before committing)
pytest -q                                      # tests use the fixture repos in tests/fixtures/
```

## Point cloud viewer

`docs/assets/viewer/ply-viewer.html` shows a `.ply` file in the browser. Embed it in a `.showcase/README.md`:

```html
<iframe class="viewer-frame" src="../../../assets/viewer/ply-viewer.html?src=../../projects/<repo>/<slug>/media/cloud.ply"></iframe>
```
