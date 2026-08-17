# ./TODO.md

## se-tools **In-Progress: 70% Complete**

Basis: four tools are implemented and three have console-script entry points. No tests exist despite the test harness being configured, and `docs/` is empty.

### Session summary 2026-08-17

Added Tool 5 (V-Model Repo Visualizer) as `tools/tool5_repo_ui/` on branch `add-tool5-repo-ui`, PR #1. Source was `~/Downloads/tool5_repo-ui`; directory renamed to underscores to match the existing three tools. `pyproject.toml` gained `pyyaml`, which `build.py` imports and which was not declared. Root `README.md` gained a Tool 5 section and file-structure entry. The tool's own README was corrected against its code in three places.

- [x] Add Tool 5 to `tools/`
- [x] Declare `pyyaml` dependency
- [x] Document Tool 5 in root README
- [x] Correct stale claims in the Tool 5 README

### Bugs

- [ ] **Tool 5's `--repo` default points nowhere.** It resolves to `<script dir>/../prak-v-model`, which inside this repo is `tools/prak-v-model` and does not exist. Both READMEs now instruct passing `--repo` explicitly. Fix the default, or make the argument required so it fails with a usage error instead of a path error.
- [ ] **Tool 5 rendering unverified against real data.** `build.py` was exercised against a synthetic four-artifact fixture only; `prak-v-model` is not present on this machine. Build a real snapshot and confirm the sidebar, backlinks, and Mermaid rendering.

### Missing

- [ ] **`tests/` is empty.** `pyproject.toml` sets `testpaths = ["tests"]` with `addopts = "--tb=short -q"`, so `pytest` runs and collects nothing -- a green run that proves nothing. Start with `tool1_req_analyzer/analyzer.py` (rule-based issue detection and confidence scoring is pure logic, no API calls needed) and `tool5_repo_ui/build.py` (`parse_frontmatter`, `compute_references`).
- [ ] **`docs/` is empty.** All documentation currently lives in `README.md`, which is now long enough that per-tool pages would be easier to maintain.
- [ ] **No Tool 2, and no record of what it was.** Numbering runs 1, 3, 4, 5 with no reference to a Tool 2 anywhere in the repo. Either it exists outside this repo, or the gap is an artifact of planning. Decide whether to fill it or renumber.
- [ ] **Tool 5 has no console-script entry point.** Tools 1, 3, and 4 install as `req-analyzer`, `traceability`, and `mermaid-gen`. Tool 5 has no `cli:main`, so it is invoked as `python3 tools/tool5_repo_ui/build.py`. Add a `main()` and an entry point for consistency.

### Recommended next steps

1. Merge PR #1.
2. Write the first tests so the configured pytest run means something.
3. Fix Tool 5's `--repo` default and verify a real `prak-v-model` build.
4. Settle the Tool 2 question before adding a Tool 6.
