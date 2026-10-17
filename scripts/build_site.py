#!/usr/bin/env python3
"""Build the static package-catalog site (site/) from Index.idn + folder READMEs.

Outputs:
  site/data/packages.json   — machine-readable catalog for the web UI
  site/data/plugins.json    — plugin catalog (metadata + rendered README HTML)
  site/previews/<slug>.txt  — first 20 lines of every package (detail preview)

Run from anywhere: python3 scripts/build_site.py
The deploy-site GitHub Actions workflow runs this before publishing Pages.
"""
import ast
import html as html_mod
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


# --------------------------------------------------------------------------- #
# Tiny dependency-free Markdown renderer (subset used by plugin READMEs)
# --------------------------------------------------------------------------- #

def _inline_md(text):
    """Render inline Markdown: code spans, bold, italic, links."""
    s = html_mod.escape(text, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def render_markdown(md):
    """Render the small Markdown dialect used in @plugins/*/README.md."""
    out, i, lines = [], 0, md.splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            lang, i = ln[3:].strip(), i + 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # closing fence
            cls = f' class="language-{html_mod.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html_mod.escape(chr(10).join(block))}"
                       "</code></pre>")
            continue
        if ln.startswith(("# ", "## ", "### ")):
            level = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{level}>{_inline_md(ln[level + 1:].strip())}</h{level}>")
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            headers = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{_inline_md(c)}</th>" for c in headers)
            body = "".join(
                "<tr>" + "".join(f"<td>{_inline_md(c)}</td>" for c in r) + "</tr>"
                for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>")
            continue
        if re.match(r"^\s*[-*] ", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(f"<li>{_inline_md(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if ln.strip() == "---":
            out.append("<hr>")
            i += 1
            continue
        if ln.strip():
            para = [ln.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and \
                    not lines[i].startswith(("```", "#", "|", "- ", "* ", "---")):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{_inline_md(' '.join(para))}</p>")
            continue
        i += 1
    return "\n".join(out)


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


# --------------------------------------------------------------------------- #
# Plugins (@plugins/<tool>/<tool>.py + README.md)
# --------------------------------------------------------------------------- #

def parse_plugins():
    """Plugin catalog entries: AST metadata (never executed) + rendered README."""
    root = ROOT / "@plugins"
    plugins = []
    if not root.is_dir():
        return plugins
    for tool_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        module = tool_dir / f"{tool_dir.name}.py"
        if not module.is_file():
            continue
        try:
            tree = ast.parse(module.read_text(encoding="utf-8"),
                             filename=str(module))
        except SyntaxError:
            continue
        meta = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", "") == "PLUGIN" for t in node.targets):
                try:
                    meta = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    meta = None
                break
        if not isinstance(meta, dict):
            continue
        name = str(meta.get("name", tool_dir.name))
        readme = tool_dir / "README.md"
        readme_html = render_markdown(
            readme.read_text(encoding="utf-8")) if readme.is_file() else ""
        rel = f"@plugins/{tool_dir.name}/{module.name}"
        options = []
        for opt in (meta.get("options") or []):
            if isinstance(opt, dict) and isinstance(opt.get("name"), str):
                options.append({
                    "flag": f"--{name}-{opt['name']}",
                    "type": str(opt.get(
                        "type", "store_true" if opt.get("action") == "store_true"
                        else "str")),
                    "default": opt.get("default"),
                    "choices": [str(c) for c in opt["choices"]]
                               if isinstance(opt.get("choices"), list) else [],
                    "help": str(opt.get("help", "")),
                })
        plugins.append({
            "name": name,
            "version": str(meta.get("version", "")),
            "description": str(meta.get("description", "")),
            "ref": f"@plugins/{tool_dir.name}",
            "module": rel,
            "bytes": module.stat().st_size,
            "options": options,
            "trigger": f"--{name}",
            "readme_html": readme_html,
            "blob": BLOB_BASE + rel,
            "raw": RAW_BASE + rel,
            "readme_blob": BLOB_BASE + f"@plugins/{tool_dir.name}/README.md",
        })
    return plugins


def main() -> int:
    if not (ROOT / "Index.idn").is_file():
        print("Index.idn not found — run 'atdork index --build' first.", file=sys.stderr)
        return 1
    entries, header = parse_index()
    # Plugins are a separate catalog (not dork packages) — split them out.
    entries = [e for e in entries if e["folder"] != "plugins"]
    plugins = parse_plugins()
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
            "plugins": len(plugins),
        },
        "folders": sorted(folders.values(), key=lambda f: f["name"]),
        "packages": sorted(entries, key=lambda e: e["ref"]),
    }
    data = SITE / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "packages.json").write_text(json.dumps(catalog, indent=1) + "\n", encoding="utf-8")
    plugin_doc = {
        "generated": catalog["generated"],
        "count": len(plugins),
        "plugins": plugins,
    }
    (data / "plugins.json").write_text(
        json.dumps(plugin_doc, indent=1) + "\n", encoding="utf-8")
    print(
        f"Site data built: {catalog['totals']['packages']} packages, "
        f"{catalog['totals']['folders']} folders, {catalog['totals']['dorks']:,} dorks, "
        f"{len(plugins)} plugins, {n_previews} previews -> {data}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
