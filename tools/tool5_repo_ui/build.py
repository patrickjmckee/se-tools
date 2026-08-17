#!/usr/bin/env python3
"""Build a self-contained index.html that visualizes the prak-v-model repo.

Reads personas, use cases, product requirements, and architecture diagrams,
extracts YAML frontmatter and body, computes backlinks, and embeds everything
into a single static HTML file. Open the output in any browser; no server
needed.

The output HTML also supports loading a different repo at runtime via the
"Load repo" button in the page header (Chrome/Edge: File System Access API;
Firefox/Safari: webkitdirectory input). The embedded snapshot from this build
is the default view.

Run:
    python3 build.py [--repo PATH] [--out PATH] [--template PATH]

Defaults: --repo=../prak-v-model, --out=index.html, --template=template.html
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm if isinstance(fm, dict) else {}, text[m.end():]


def collect_artifacts(repo: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {
        "personas": [],
        "use-cases": [],
        "product-requirements": [],
        "system-requirements": [],
        "architecture-diagrams": [],
        "initiatives": [],
        "epics": [],
        "stories": [],
    }

    def add(kind: str, path: Path, bucket: str) -> None:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        out[kind].append({
            "id": path.stem,
            "filename": path.name,
            "title": fm.get("title", path.stem),
            "bucket": bucket,
            "kind": kind,
            "frontmatter": fm,
            "body": body,
            "path": str(path.relative_to(repo)).replace("\\", "/"),
        })

    personas_dir = repo / "product" / "personas"
    if personas_dir.exists():
        for p in sorted(personas_dir.glob("*.md")):
            add("personas", p, "")

    uc_root = repo / "product" / "use-cases"
    if uc_root.exists():
        for bucket_dir in sorted(uc_root.iterdir()):
            if bucket_dir.is_dir():
                for p in sorted(bucket_dir.glob("uc-*.md")):
                    add("use-cases", p, bucket_dir.name)

    req_root = repo / "product" / "requirements"
    if req_root.exists():
        for bucket_dir in sorted(req_root.iterdir()):
            if bucket_dir.is_dir():
                for p in sorted(bucket_dir.glob("req-*.md")):
                    add("product-requirements", p, bucket_dir.name)

    sysreq_root = repo / "system" / "requirements"
    if sysreq_root.exists():
        for bucket_dir in sorted(sysreq_root.iterdir()):
            if bucket_dir.is_dir():
                for p in sorted(bucket_dir.glob("sysreq-*.md")):
                    add("system-requirements", p, bucket_dir.name)

    arch_root = repo / "system" / "architecture"
    if arch_root.exists():
        for bucket_dir in sorted(arch_root.iterdir()):
            if bucket_dir.is_dir():
                for p in sorted(bucket_dir.glob("arch-*.md")):
                    add("architecture-diagrams", p, bucket_dir.name)

    init_root = repo / "agile-planning" / "initiatives"
    if init_root.exists():
        for p in sorted(init_root.glob("initiative-*.md")):
            text = p.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if fm.get("parent-functional-requirement"):
                bucket = "functional-requirement"
            elif fm.get("parent-product-requirement"):
                bucket = "product-requirement"
            else:
                bucket = ""
            add("initiatives", p, bucket)

    epics_root = repo / "agile-planning" / "epics"
    if epics_root.exists():
        for p in sorted(epics_root.glob("epic-*.md")):
            # Bucket = platform-team (single-team constraint)
            text = p.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            bucket = (fm.get("platform-team") or "").strip() or "unassigned"
            add("epics", p, bucket)

    stories_root = repo / "agile-planning" / "stories"
    if stories_root.exists():
        for p in sorted(stories_root.glob("story-*.md")):
            text = p.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            bucket = (fm.get("platform-team") or "").strip() or "unassigned"
            add("stories", p, bucket)

    return out


def compute_references(artifacts: dict[str, list[dict]]) -> None:
    by_filename: dict[str, dict] = {}
    for arr in artifacts.values():
        for a in arr:
            by_filename[a["filename"]] = a
            a["refs_out"] = []
            a["refs_in"] = []

    REF_FIELDS = (
        "parent-persona",
        "primary-actor",
        "parent-use-case",
        "parent-use-cases",
        "parent-product-requirement",
        "parent-functional-requirement",
        "parent-initiative",
        "parent-system-requirement",
        "parent-epic",
        "child-epics",
        "child-stories",
    )

    for a in by_filename.values():
        fm = a.get("frontmatter") or {}
        for field in REF_FIELDS:
            val = fm.get(field)
            if val is None:
                continue
            targets = val if isinstance(val, list) else [val]
            for t in targets:
                if not isinstance(t, str) or not t.endswith(".md"):
                    continue
                if t in by_filename:
                    target = by_filename[t]
                    a["refs_out"].append({
                        "field": field,
                        "filename": t,
                        "title": target["title"],
                        "kind": target["kind"],
                    })
                    target["refs_in"].append({
                        "field": field,
                        "filename": a["filename"],
                        "title": a["title"],
                        "kind": a["kind"],
                    })


def build(repo: Path, out: Path, template: Path) -> None:
    artifacts = collect_artifacts(repo)
    compute_references(artifacts)
    json_data = json.dumps(artifacts, indent=None, separators=(",", ":"))
    if not template.exists():
        print(f"ERROR: template not found at {template}", file=sys.stderr)
        sys.exit(1)
    tmpl_text = template.read_text(encoding="utf-8")
    if "__DATA__" not in tmpl_text:
        print("ERROR: template missing __DATA__ placeholder", file=sys.stderr)
        sys.exit(1)
    if not tmpl_text.rstrip().endswith("</html>"):
        print(
            "ERROR: template appears truncated (does not end with '</html>'); "
            "refusing to write output. Check for an Edit/Write truncation.",
            file=sys.stderr,
        )
        sys.exit(1)
    html_out = tmpl_text.replace("__DATA__", json_data)
    if not html_out.rstrip().endswith("</html>"):
        print("ERROR: generated HTML is not well-terminated; refusing to write.", file=sys.stderr)
        sys.exit(1)
    out.write_text(html_out, encoding="utf-8")
    counts = {k: len(v) for k, v in artifacts.items()}
    print(f"Built {out} ({out.stat().st_size:,} bytes)")
    print(f"  Personas:              {counts['personas']}")
    print(f"  Use Cases:             {counts['use-cases']}")
    print(f"  Product Requirements:  {counts['product-requirements']}")
    print(f"  System Requirements:   {counts['system-requirements']}")
    print(f"  Architecture Diagrams: {counts['architecture-diagrams']}")
    print(f"  Initiatives (agile):   {counts['initiatives']}")
    print(f"  Epics (agile):         {counts['epics']}")
    print(f"  Stories (agile):       {counts['stories']}")


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=here.parent / "prak-v-model",
                        help="Path to a v-model repo with personas / use-cases / requirements / architecture")
    parser.add_argument("--out", type=Path, default=here / "index.html",
                        help="Output HTML path")
    parser.add_argument("--template", type=Path, default=here / "template.html",
                        help="HTML template with a __DATA__ placeholder")
    args = parser.parse_args()
    if not args.repo.exists():
        print(f"ERROR: repo not found at {args.repo}", file=sys.stderr)
        return 1
    build(args.repo, args.out, args.template)
    return 0


if __name__ == "__main__":
    sys.exit(main())
