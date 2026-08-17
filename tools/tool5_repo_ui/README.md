# Tool 5 -- V-Model Repo Visualizer

A self-contained HTML page that lets you click through V-model artifacts and see how they're connected. Open `index.html` in a browser; no server, no setup. Switch between repos by clicking **Load repo** in the header.

## Two ways to use it

1. **Snapshot mode (default).** Run `python3 build.py` to embed the current state of a repo into `index.html`. Open the HTML directly. Good for sharing a frozen view (the HTML is fully self-contained).
2. **Live folder mode.** Click **Load repo** in the page header and pick a folder with the same structure as `prak-v-model`. The page reads the `.md` files in-browser and replaces the view. The **Reload** button re-reads the same folder without re-picking (Chrome / Edge only).

## Layout

- **Left sidebar** — collapsible sections (Personas, Use Cases, Product Requirements, System Requirements, Architecture Diagrams, Initiatives, Epics, Stories), grouped by feature bucket. Sections with no artifacts are omitted. Filter live with the search box in the header.
- **Center pane** — selected artifact: frontmatter table, body markdown, embedded Mermaid diagrams.
- **Right pane** — "Referenced by" list of artifacts that point to the current one.

Sidebar entries, frontmatter parent fields, inline `*.md` references in the body, and right-pane backlinks are all clickable. URL hash reflects the current artifact, so browser back / forward works.

## Folder structure the visualizer expects

The picked folder must contain any subset of:

```
<root>/
├── product/
│   ├── personas/<name>.md
│   ├── use-cases/<feature>/uc-<name>.md
│   └── requirements/<feature>/req-<name>.md
├── system/
│   ├── requirements/<feature>/sysreq-<name>.md
│   └── architecture/<feature>/arch-<name>.md
└── agile-planning/
    ├── initiatives/initiative-<name>.md
    ├── epics/epic-<name>.md
    └── stories/story-<name>.md
```

Filename prefixes are enforced by the glob: `uc-`, `req-`, `sysreq-`, `arch-`, `initiative-`, `epic-`, `story-`. Personas take any `*.md` name.

YAML frontmatter on each file:

| Artifact | Required fields |
|---|---|
| Persona | `id`, `title`, `class` |
| Use Case | `id`, `title`, `primary-actor`, `parent-persona` |
| Product Requirement | `id`, `title`, `parent-use-cases` (list), `priority` |
| System Requirement | `id`, `title`, `parent-product-requirement` |
| Architecture Diagram | `id`, `title`, `parent-product-requirement`, `diagram-type` |
| Initiative / Epic / Story | `id`, `title`, plus any of `parent-initiative`, `parent-epic`, `child-epics`, `child-stories` |

Cross-reference fields must hold the target's **`.md` filename**, not its `id`. A value that does not end in `.md`, or names a file not found in the scan, is ignored and produces no link.

Reference fields scanned: `parent-persona`, `primary-actor`, `parent-use-case`, `parent-use-cases`, `parent-product-requirement`, `parent-functional-requirement`, `parent-initiative`, `parent-system-requirement`, `parent-epic`, `child-epics`, `child-stories`. Backlinks are computed from those.

## Browser support

- **Chrome / Edge / Opera** — full support via the File System Access API. Picks a directory handle, can reload on demand.
- **Firefox / Safari** — uses `<input type="file" webkitdirectory>` as a fallback. To reload, re-click **Load repo**. (Safari requires user interaction each time.)

Loads `marked@12`, `mermaid@10`, and `js-yaml@4` from a CDN. First load needs a network connection; the browser will cache them on subsequent visits.

## Build

```
python3 build.py --repo /path/to/v-model-repo   # write ./index.html
python3 build.py --repo /path/to/repo --out /tmp/snapshot.html
python3 build.py --repo /path/to/repo --template ./my-template.html
```

Pass `--repo` explicitly. Its default resolves to `<script dir>/../prak-v-model`, which inside `se-tools` points at `tools/prak-v-model` and does not exist.

Requires Python 3.10+ and `pyyaml` (installed with the `se-tools` package, or `pip install pyyaml`).

## Files

- `build.py` — reads a v-model repo, parses frontmatter, computes references, injects data into the template
- `template.html` — HTML page with all rendering JS; `__DATA__` placeholder is replaced at build time
- `index.html` — generated artifact (overwritten on each build)
- `README.md` — this file

## Design notes

- **No structural changes to the target repo.** The visualizer lives outside the v-model repo and reads it read-only.
- **Single-file output.** Build-time snapshot embeds artifacts as JSON; the page is shareable as one file.
- **In-browser repo switching.** Picking a folder replaces the in-memory data with a freshly-parsed view. YAML is parsed client-side with js-yaml; backlinks are recomputed in JS using the same algorithm as `build.py`.
- **Adding an artifact kind** requires three edits: a collection block in `build.py`, an entry in the `KIND_LABELS` block in `template.html`, and the new parent field added to `REF_FIELDS` in `build.py`.
