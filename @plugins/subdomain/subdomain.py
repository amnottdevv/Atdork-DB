#!/usr/bin/env python3
"""
Subdomain — subdomain discovery via search-engine dorks.

    atdork install @plugins/subdomain
    atdork --subdomain-target example.com
    atdork --subdomain-target example.com --subdomain-verbose --subdomain-save subs.txt

Emits dorks that surface indexed subdomains (api/staging/admin/dev panels,
cloud assets, dev/staging hosts, forgotten panels). With --subdomain-search
it actually runs them through the AtDork engine and prints unique subdomains
found in the result URLs.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

PLUGIN = {
    "name": "subdomain",
    "version": "1.0.0",
    "description": "Discover indexed subdomains of a target via search dorks",
    "options": [
        {"name": "target",
         "help": "Root domain to enumerate (e.g. example.com)"},
        {"name": "save",
         "help": "Write the subdomains to this file (env-guarded)"},
        {"name": "search",
         "action": "store_true",
         "help": "Actually run the dorks and print discovered subdomains "
                 "(spends search credits)"},
        {"name": "verbose",
         "action": "store_true",
         "help": "Print the raw dorks too (implied by --subdomain-search)"},
        {"name": "limit",
         "type": "int",
         "default": 0,
         "help": "Emit at most N dorks (0 = all)"},
    ],
}

DORKS = [
    'site:*.{target}',
    'site:*.*.{target}',
    'site:{target} inurl:api',
    'site:{target} inurl:dev',
    'site:{target} inurl:staging',
    'site:{target} inurl:test',
    'site:{target} inurl:admin',
    'site:{target} inurl:portal',
    'site:{target} inurl:dashboard',
    'site:{target} inurl:cpanel',
    'site:{target} inurl:webmail',
    'site:{target} inurl:vpn',
    'site:{target} inurl:git',
    'site:{target} inurl:jenkins',
    'site:{target} inurl:grafana',
    'site:{target} inurl:kibana',
    'site:{target} inurl:cloudfront.net',
    'site:{target} inurl:amazonaws.com',
    'site:{target} inurl:azurewebsites.net',
    'site:{target} inurl:herokuapp.com',
    'site:{target} inurl:readme.md',
    'site:{target} ext:txt "index of"',
    'site:{target} intitle:"index of" .git',
]

# Subdomains commonly left off the main host that dorks rarely catch.
# The extraction pattern is built inline in _extract_subdomains() from the
# target so the root domain is escaped exactly once.


def _extract_subdomains(urls, root):
    """Unique subdomains of *root* found in a list of result URLs."""
    pattern = re.compile(
        r"(?:^|\.|\s)((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+" +
        re.escape(root) + r")(?::\d+)?(?:/|$|\s)", re.IGNORECASE)
    found = set()
    for url in urls:
        host = urlparse(url if "//" in url else "//" + url).netloc.lower()
        for m in pattern.finditer(host + " " + url):
            found.add(m.group(1).lower())
    found.discard(root.lower())
    return sorted(found)


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    target = (getattr(args, "subdomain_target", None) or "").strip().lower()
    target = target.removeprefix("https://").removeprefix("http://").strip("/")
    if not target or "." not in target:
        say("[red]Error:[/red] --subdomain-target is required "
            "(e.g. example.com)")
        return 1

    dorks = [d.format(target=target) for d in DORKS]
    limit = int(getattr(args, "subdomain_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    do_search = bool(getattr(args, "subdomain_search", False))
    verbose = bool(getattr(args, "subdomain_verbose", False)) or do_search
    if verbose:
        say(f"[dim]{len(dorks)} dork(s) for[/dim] [cyan]{target}[/cyan]")
        for dork in dorks:
            say(f"  [dim]•[/dim] {dork}")

    subs = []
    if do_search:
        say(f"[dim]running {len(dorks)} dorks…[/dim]")
        urls = []
        for dork in dorks:
            try:
                results = ctx.search(dork)
            except Exception as e:
                say(f"[yellow]  dork failed:[/yellow] {dork} — {e}")
                continue
            for r in results or []:
                href = r.get("href") if isinstance(r, dict) else str(r)
                if href:
                    urls.append(href)
        subs = _extract_subdomains(urls, target)
        say(f"[green]{len(subs)} subdomain(s)[/green] for [cyan]{target}[/cyan]")
        for s in subs:
            say(f"  [dim]•[/dim] {s}")
        if not subs:
            say("[yellow]no subdomains surfaced — the dorks above are still "
                "useful to paste into a browser.[/yellow]")
    else:
        say(f"[green]{len(dorks)} dork(s)[/green] for [cyan]{target}[/cyan] "
            "[dim](add --subdomain-search to actually run them)[/dim]")

    save = getattr(args, "subdomain_save", None)
    if save:
        try:
            path = Path(ctx.guard_write(save))
        except Exception as e:
            say(f"[red]Cannot save:[/red] {e}")
            return 1
        body = subs if subs else dorks
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        say(f"[green]✔ saved[/green] {len(body)} line(s) → {path}")
    return 0
