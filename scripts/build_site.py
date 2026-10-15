#!/usr/bin/env python3
"""Build the static package-catalog site (site/) from Index.idn + folder READMEs.

Outputs:
  site/data/packages.json   — machine-readable catalog for the web UI
  site/previews/<slug>.txt  — first 20 lines of every package (detail preview)

Run from anywhere: python3 scripts/build_site.py
The deploy-site GitHub Actions workflow runs this before publishing Pages.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PREVIEW_LINES = 20
RAW_BASE = "https://raw.githubusercontent.com/amnottdevv/Atdork-DB/main/"
BLOB_BASE = "https://github.com/amnottdevv/Atdork-DB/blob/main/"

TABLE_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([\d,]+)\s*\|\s*(.+?)\s*\|\s*$")


def parse_index():
    """[(folder, name, sha, bytes, dorks)] from Index.idn."""
    entries, header = [], {}
    for line in (ROOT / "Index.idn").read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            m = re.match(r"#\s*([\w-]+):\s*(.+)", line)
            if m:
                header[m.group(1)] = m.group(2).strip()
            continue
        if not line.startswith("@"):
            continue
        ref, sha, size, dorks, desc = line.split("|", 4)
        folder, name = ref[1:].split("/", 1)
        entries.append({
            "ref": ref, "folder": folder, "name": name,
            "sha256": sha, "bytes": int(size), "dorks": int(dorks),
            "desc": desc,
        })
    return entries, header


def parse_folder_readmes(entries):
    """Enrich entries with per-file descriptions and folder meta from READMEs."""
    folders = {}
    by_folder = {}
    for e in entries:
        by_folder.setdefault(e["folder"], []).append(e)
    for folder, items in by_folder.items():
        readme = ROOT / f"@{folder}" / "README.md"
        title, intro = None, None
        file_desc = {}
        if readme.is_file():
            lines = readme.read_text(encoding="utf-8").splitlines()
            in_table = False
            seen_packages = False
            intro_buf = []
            for ln in lines:
                if ln.startswith("# "):
                    m = re.match(r"# `@[^`]+` — (.+)", ln)
                    if m and title is None:
                        title = m.group(1).strip()
                    continue
                if ln.strip().startswith(">"):
                    continue
                if ln.strip() == "## Packages":
                    in_table = True
                    seen_packages = True
                    continue
                if in_table:
                    m = TABLE_ROW.match(ln)
                    if m:
                        file_desc[m.group(1)] = m.group(3)
                    elif ln.strip() and not ln.startswith("|"):
                        in_table = False
                    continue
                if seen_packages:
                    continue  # usage section etc. — not intro
                if ln.strip() and title and intro is None and not ln.startswith(("#", "|", "```")):
                    intro_buf.append(ln.strip())
            intro = " ".join(intro_buf) or None
        for e in items:
            d = file_desc.get(e["name"])
            if d and d.lower() not in ("", "none"):
                e["desc"] = d
        folders[folder] = {
            "name": folder,
            "title": title or folder.replace("-", " ").title(),
            "intro": intro or f"Package folder `@{folder}`.",
            "packages": len(items),
            "dorks": sum(i["dorks"] for i in items),
        }
    return folders


def write_previews(entries):
    out = SITE / "previews"
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.txt"):
        stale.unlink()
    n = 0
    for e in entries:
        src = ROOT / f"@{e['folder']}" / e["name"]
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{e['folder']}__{e['name']}")
        e["preview"] = f"previews/{slug}"
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        lines = [ln for ln in text.splitlines() if ln.strip()][:PREVIEW_LINES]
        (out / slug).write_text("\n".join(lines) + "\n", encoding="utf-8")
        n += 1
    return n


def main() -> int:
    if not (ROOT / "Index.idn").is_file():
        print("Index.idn not found — run 'atdork index --build' first.", file=sys.stderr)
        return 1
    entries, header = parse_index()
    folders = parse_folder_readmes(entries)
    n_previews = write_previews(entries)
    for e in entries:
        ref_enc = e["ref"].replace(" ", "%20")
        e["raw"] = RAW_BASE + ref_enc
        e["blob"] = BLOB_BASE + ref_enc
    catalog = {
        "generated": header.get("generated", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "totals": {
            "packages": len(entries),
            "folders": len(folders),
            "dorks": sum(e["dorks"] for e in entries),
            "bytes": sum(e["bytes"] for e in entries),
        },
        "folders": sorted(folders.values(), key=lambda f: f["name"]),
        "packages": sorted(entries, key=lambda e: e["ref"]),
    }
    data = SITE / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "packages.json").write_text(json.dumps(catalog, indent=1) + "\n", encoding="utf-8")
    print(
        f"Site data built: {catalog['totals']['packages']} packages, "
        f"{catalog['totals']['folders']} folders, {catalog['totals']['dorks']:,} dorks, "
        f"{n_previews} previews -> {data / 'packages.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
