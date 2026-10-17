#!/usr/bin/env python3
"""
VulnDork — vulnerability-hunting dork sets by target or product/version.

    atdork install @plugins/vulndork
    atdork --vulndork-target example.com
    atdork --vulndork-product "apache 2.4.49" --vulndork-cve CVE-2021-41773
    atdork --vulndork-type exposed --vulndork-save vulns.txt

Generates dorks that surface exposed panels, error pages, version strings,
known-exploit paths and admin consoles. --vulndork-cve adds the classic
proof-of-concept paths for a specific CVE. With --vulndork-search it runs
the dorks and prints the matching URLs.
"""

from pathlib import Path

PLUGIN = {
    "name": "vulndork",
    "version": "1.0.0",
    "description": "Build (and optionally run) vulnerability-hunting dorks",
    "options": [
        {"name": "target",
         "help": "Root domain to hunt (e.g. example.com)"},
        {"name": "product",
         "help": "Product + version string (e.g. 'apache 2.4.49')"},
        {"name": "cve",
         "help": "Add proof-of-concept paths for a CVE (e.g. CVE-2021-41773)"},
        {"name": "type",
         "choices": ["exposed", "version", "panels", "all"],
         "default": "exposed",
         "help": "Dork category"},
        {"name": "save",
         "help": "Write the dorks to this file (env-guarded)"},
        {"name": "search",
         "action": "store_true",
         "help": "Run the dorks and print matching URLs (spends credits)"},
        {"name": "limit",
         "type": "int",
         "default": 0,
         "help": "Emit at most N dorks (0 = all)"},
    ],
}

CATEGORIES = {
    "exposed": [
        'site:{target} ext:log',
        'site:{target} ext:bak OR ext:old OR ext:save',
        'site:{target} ext:sql OR ext:sqlite',
        'site:{target} (ext:env OR ext:ini OR ext:conf)',
        'site:{target} intitle:"index of" .git',
        'site:{target} intitle:"index of" "config"',
        'site:{target} inurl:phpinfo',
        'site:{target} inurl:"/backup/"',
        'site:{target} inurl:dump.sql',
        'site:{target} inurl:wp-config.php',
    ],
    "version": [
        'site:{target} "Apache/2.4" "Server at"',
        'site:{target} "nginx/" "Welcome to nginx"',
        'site:{target} "PHP/" "Warning"',
        'site:{target} "X-Powered-By"',
        'site:{target} "Microsoft-IIS" error',
        'site:{target} "WordPress" "ver="',
        'site:{target} "Joomla" "version"',
        'site:{target} "Drupal" "X-Generator"',
        'site:{target} inurl:server-status',
        'site:{target} inurl:server-info',
    ],
    "panels": [
        'site:{target} intitle:"Dashboard" inurl:admin',
        'site:{target} inurl:administrator',
        'site:{target} inurl:wp-admin',
        'site:{target} inurl:cpanel',
        'site:{target} inurl:phpmyadmin',
        'site:{target} inurl:manager/html',
        'site:{target} inurl:jmx-console',
        'site:{target} inurl:web-console',
        'site:{target} inurl:elmah',
        'site:{target} inurl:actuator/env',
    ],
}

# Best-effort PoC path prefixes per CVE family (search-engine reconnaissance
# only — no exploitation; a hit just means the path is INDEXED, not vulnerable).
CVE_PATHS = {
    "cve-2021-41773": ["/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd"],
    "cve-2021-42013": ["/cgi-bin/.%%32%65/.%%32%65/.%%32%65/.%%32%65/etc/passwd"],
    "cve-2014-6271": ["/cgi-bin/test-cgi", "/cgi-bin/printenv"],
    "cve-2017-5638": ["/struts2-showcase/"],
    "cve-2018-13379": ["/remote/login?lang=en"],
    "cve-2019-11510": ["/ui/lspolicy", "/perl/lspolicy"],
    "cve-2020-1472": ["/"],
    "cve-2021-44228": ["/actuator/loggers"],
    "cve-2023-1389": ["/cgi-bin/login"],
}


def _patterns(kind, target, product, cve):
    out = []
    if target:
        cats = list(CATEGORIES) if kind == "all" else [kind]
        for cat in cats:
            for pattern in CATEGORIES.get(cat, []):
                out.append(pattern.format(target=target))
    if product:
        q = f'"{product}"'
        out += [
            f'{q} ext:log OR ext:txt',
            f'{q} (error OR "stack trace")',
            f'{q} (inurl:login OR inurl:admin)',
            f'{q} (changelog OR "release notes")',
            f'{q} (password OR secret) ext:conf',
            f'{q} intitle:"index of"',
            f'{q} (inurl:download OR inurl:setup)',
        ]
    if cve:
        key = cve.strip().lower()
        paths = CVE_PATHS.get(key)
        if paths:
            if target:
                for p in paths:
                    out.append(f'site:{target} inurl:"{p}"')
            out += [f'"{cve}" "{p}"' for p in paths]
        else:
            out.append(f'"{cve}" "proof of concept"')
            out.append(f'"{cve}" exploit poc')
    # dedupe, keep order
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    target = (getattr(args, "vulndork_target", None) or "").strip().lower()
    target = target.removeprefix("https://").removeprefix("http://").strip("/")
    product = (getattr(args, "vulndork_product", None) or "").strip()
    cve = (getattr(args, "vulndork_cve", None) or "").strip()
    kind = getattr(args, "vulndork_type", "exposed")

    if not target and not product and not cve:
        say("[red]Error:[/red] --vulndork-target, --vulndork-product or "
            "--vulndork-cve required")
        return 1

    dorks = _patterns(kind, target, product, cve)
    limit = int(getattr(args, "vulndork_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    label = target or product or cve
    say(f"[green]{len(dorks)} dork(s)[/green] for [cyan]{label}[/cyan] "
        f"[dim](category: {kind})[/dim]")

    urls = []
    if getattr(args, "vulndork_search", False):
        say(f"[dim]running {len(dorks)} dorks…[/dim]")
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
        uniq = sorted(set(urls))
        say(f"[green]{len(uniq)} unique URL(s)[/green] surfaced")
        for u in uniq:
            say(f"  [dim]•[/dim] {u}")
        if not uniq:
            say("[yellow]no URLs surfaced — the dorks above are still "
                "useful to paste into a browser.[/yellow]")
        urls = uniq
    else:
        for dork in dorks:
            say(f"  [dim]•[/dim] {dork}")
        say("[dim]add --vulndork-search to actually run them[/dim]")

    save = getattr(args, "vulndork_save", None)
    if save:
        try:
            path = Path(ctx.guard_write(save))
        except Exception as e:
            say(f"[red]Cannot save:[/red] {e}")
            return 1
        body = urls if urls else dorks
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        say(f"[green]✔ saved[/green] {len(body)} line(s) → {path}")
    return 0
