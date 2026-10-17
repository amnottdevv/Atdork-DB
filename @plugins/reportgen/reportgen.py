#!/usr/bin/env python3
"""
ReportGen — summarize AtDork result files into an HTML or JSON report.

    atdork install @plugins/reportgen
    atdork --reportgen-save report.html
    atdork --reportgen-format json --reportgen-save report.json

Scans the environment's results folder (or --reportgen-from), collects
entries from .json result files and counts .txt/.csv ones, then writes a
self-contained report through the environment write guard.
"""

import html
import json
from pathlib import Path

PLUGIN = {
    "name": "reportgen",
    "version": "1.0.0",
    "description": "Summarize result files into an HTML/JSON report",
    "options": [
        {"name": "from",
         "help": "Folder with result files (default: the active "
                 "environment's results dir)"},
        {"name": "save",
         "default": "report.html",
         "help": "Output report path (env-guarded)"},
        {"name": "format",
         "choices": ["html", "json"],
         "default": "html",
         "help": "Report format"},
        {"name": "title",
         "default": "AtDork Report",
         "help": "Report title"},
        {"name": "max-rows",
         "type": "int",
         "default": 500,
         "help": "Maximum result rows in the report (0 = all)"},
    ],
}

RESULT_EXTS = {".json", ".txt", ".csv"}


def _collect(folder: Path, skip: Path):
    """Return (files_summary, rows) for every result file in *folder*."""
    files, rows = [], []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in RESULT_EXTS:
            continue
        try:
            if path.resolve() == skip.resolve():
                continue
        except OSError:
            pass
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                files.append({"file": path.name, "entries": 0, "error": str(e)})
                continue
            entries = data if isinstance(data, list) else []
            count = 0
            for item in entries:
                if not isinstance(item, dict):
                    continue
                rows.append({
                    "file": path.name,
                    "title": str(item.get("title", "")),
                    "href": str(item.get("href", item.get("url", ""))),
                    "body": str(item.get("body", item.get("snippet", "")))[:200],
                })
                count += 1
            files.append({"file": path.name, "entries": count})
        else:
            try:
                lines = [ln for ln in path.read_text(
                    encoding="utf-8", errors="replace").splitlines() if ln.strip()]
            except OSError as e:
                files.append({"file": path.name, "entries": 0, "error": str(e)})
                continue
            files.append({"file": path.name, "entries": len(lines)})
    return files, rows


def _render_html(title: str, files, rows) -> str:
    head = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title>"
        "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#14181f}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #d7dde5;"
        "padding:.4rem .6rem;text-align:left;font-size:.9rem}th{background:#f2f5f9}"
        "a{color:#0b57d0}tr:nth-child(even){background:#fafbfd}"
        ".meta{color:#5f6b7a}</style></head><body>"
    )
    parts = [head, f"<h1>{html.escape(title)}</h1>",
             f"<p class='meta'>{len(files)} file(s), {len(rows)} result row(s)</p>"]
    parts.append("<table><tr><th>#</th><th>Title</th><th>URL</th>"
                 "<th>Source</th></tr>")
    for i, row in enumerate(rows, 1):
        title_e = html.escape(row["title"] or "(no title)")
        href = row["href"]
        link = (f"<a href='{html.escape(href, quote=True)}'>"
                f"{html.escape(href)}</a>" if href else "")
        parts.append(
            f"<tr><td>{i}</td><td>{title_e}</td><td>{link}</td>"
            f"<td class='meta'>{html.escape(row['file'])}</td></tr>"
        )
    parts.append("</table>")
    parts.append("<h2>Files</h2><table><tr><th>File</th><th>Entries</th></tr>")
    for f in files:
        note = f" — {html.escape(f['error'])}" if f.get("error") else ""
        parts.append(f"<tr><td>{html.escape(f['file'])}</td>"
                     f"<td>{f['entries']}{note}</td></tr>")
    parts.append("</table></body></html>")
    return "".join(parts)


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    folder = getattr(args, "reportgen_from", None)
    folder = Path(folder).expanduser() if folder else Path(ctx.results_dir)
    if not folder.is_dir():
        say(f"[red]No results folder:[/red] {folder}")
        return 1

    fmt = getattr(args, "reportgen_format", "html")
    save = getattr(args, "reportgen_save", "report.html")
    try:
        out_path = Path(ctx.guard_write(save))
    except Exception as e:
        say(f"[red]Cannot save:[/red] {e}")
        return 1

    files, rows = _collect(folder, skip=out_path)
    max_rows = int(getattr(args, "reportgen_max_rows", 500) or 0)
    if max_rows > 0:
        rows = rows[:max_rows]

    if not files:
        say(f"[yellow]No result files found in {folder}[/yellow] "
            "(run a search first).")
        return 1

    title = str(getattr(args, "reportgen_title", "AtDork Report"))
    if fmt == "json":
        payload = {"title": title, "files": files, "rows": rows,
                   "total_rows": len(rows)}
        body = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    else:
        body = _render_html(title, files, rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    say(f"[green]✔ report written[/green] {len(rows)} row(s) from "
        f"{len(files)} file(s) → {out_path}")
    return 0
