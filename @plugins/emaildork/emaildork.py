#!/usr/bin/env python3
"""
EmailDork — email discovery dorks for a name / brand + domain.

    atdork install @plugins/emaildork
    atdork --emaildork-name "john wick" --emaildork-domain acme.com
    atdork --emaildork-name acme --emaildork-save emails.txt

Generates dorks that surface leaked or indexed email addresses tied to a
target (contact pages, documents, breach lists, GitHub/config leaks,
LinkedIn/ZoomInfo people search). With --emaildork-search it runs them and
extracts unique email addresses from the result snippets.
"""

import re
from pathlib import Path

PLUGIN = {
    "name": "emaildork",
    "version": "1.0.0",
    "description": "Build (and optionally run) email-discovery dorks",
    "options": [
        {"name": "name",
         "help": "Name, brand or keyword to hunt emails for"},
        {"name": "domain",
         "help": "Restrict to a domain (e.g. acme.com) — optional"},
        {"name": "save",
         "help": "Write output to this file (env-guarded)"},
        {"name": "search",
         "action": "store_true",
         "help": "Run the dorks and print extracted emails (spends credits)"},
        {"name": "limit",
         "type": "int",
         "default": 0,
         "help": "Emit at most N dorks (0 = all)"},
    ],
}

DORKS_NAME = [
    '"{name}" ext:pdf',
    '"{name}" ext:docx OR ext:xls OR ext:csv',
    '"{name}" filetype:txt "email"',
    '"{name}" "email" "phone"',
    'intitle:"contact" "{name}"',
    '"{name}" inurl:contact',
    'site:linkedin.com/in "{name}"',
    'site:rocketreach.co "{name}"',
    'site:zoominfo.com "{name}"',
    '"{name}" "@gmail.com" OR "@yahoo.com" OR "@outlook.com"',
]

DORKS_DOMAIN = [
    '"@{domain}" ext:pdf',
    '"@{domain}" ext:docx OR ext:xls OR ext:csv',
    '"@{domain}" filetype:txt',
    '"@{domain}" "password" OR "login"',
    'intitle:"index of" "{domain}"',
    '"@{domain}" (inurl:admin OR inurl:login)',
    '"@{domain}" (filename:.env OR filename:credentials.json)',
    '"@{domain}" (inurl:wp-login OR inurl:contact)',
    'site:github.com "@{domain}"',
    '"@{domain}" (inurl:backup OR inurl:dump)',
    '"{domain}" "SELECT * FROM users" ext:sql',
]

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _extract_emails(texts):
    """Unique, normalized email addresses found across result snippets."""
    found = set()
    for text in texts:
        for m in EMAIL_RE.finditer(text or ""):
            found.add(m.group(0).lower())
    return sorted(found)


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    name = (getattr(args, "emaildork_name", None) or "").strip()
    domain = (getattr(args, "emaildork_domain", None) or "").strip().lower()
    domain = domain.removeprefix("@").removeprefix("https://") \
        .removeprefix("http://").strip("/")
    if not name and not domain:
        say("[red]Error:[/red] --emaildork-name and/or --emaildork-domain "
            "required")
        return 1

    dorks = []
    if name:
        dorks += [d.format(name=name) for d in DORKS_NAME]
    if domain:
        dorks += [d.format(domain=domain) for d in DORKS_DOMAIN]

    limit = int(getattr(args, "emaildork_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    say(f"[green]{len(dorks)} dork(s)[/green] for "
        f"[cyan]{name or ''}{'@' if name and domain else ''}{domain}[/cyan]")

    emails = []
    if getattr(args, "emaildork_search", False):
        say(f"[dim]running {len(dorks)} dorks…[/dim]")
        snippets = []
        for dork in dorks:
            try:
                results = ctx.search(dork)
            except Exception as e:
                say(f"[yellow]  dork failed:[/yellow] {dork} — {e}")
                continue
            for r in results or []:
                if isinstance(r, dict):
                    snippets.append(str(r.get("body", "")) + " "
                                    + str(r.get("title", "")))
                else:
                    snippets.append(str(r))
        emails = _extract_emails(snippets)
        if domain:
            emails = [e for e in emails if e.endswith("@" + domain)]
        say(f"[green]{len(emails)} email(s)[/green] found")
        for e in emails:
            say(f"  [dim]•[/dim] {e}")
        if not emails:
            say("[yellow]no emails surfaced in snippets — the dorks above "
                "are still useful to paste into a browser.[/yellow]")
    else:
        for dork in dorks:
            say(f"  [dim]•[/dim] {dork}")
        say("[dim]add --emaildork-search to actually run them[/dim]")

    save = getattr(args, "emaildork_save", None)
    if save:
        try:
            path = Path(ctx.guard_write(save))
        except Exception as e:
            say(f"[red]Cannot save:[/red] {e}")
            return 1
        body = emails if emails else dorks
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        say(f"[green]✔ saved[/green] {len(body)} line(s) → {path}")
    return 0
