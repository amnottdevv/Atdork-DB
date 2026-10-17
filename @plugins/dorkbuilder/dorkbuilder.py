#!/usr/bin/env python3
"""
DorkBuilder — build ready-to-run dork lists from text + a category.

    atdork install @plugins/dorkbuilder
    atdork --dorkbuilder-text "John wick" \
           --dorkbuilder-type social-media \
           --dorkbuilder-save dorks.txt

Categories cover social-media, exposed-files, logins, credentials and
cloud; "all" emits the union. Output can be printed, saved (through the
environment write guard), and sliced with --dorkbuilder-limit.
"""

from pathlib import Path

PLUGIN = {
    "name": "dorkbuilder",
    "version": "1.0.0",
    "description": "Build ready-to-run dork lists from text + a category",
    "options": [
        {"name": "text",
         "help": "Text to hunt for (name, brand, keyword, username)"},
        {"name": "type",
         "choices": ["social-media", "sosial-media", "exposed-files",
                     "logins", "credentials", "cloud", "all"],
         "default": "social-media",
         "help": "Dork category ('sosial-media' is an alias of 'social-media')"},
        {"name": "save",
         "help": "Write the dorks to this file (env-guarded; relative paths "
                 "resolve inside the active environment)"},
        {"name": "limit",
         "type": "int",
         "default": 0,
         "help": "Emit at most N dorks (0 = all)"},
        {"name": "list-types",
         "action": "store_true",
         "help": "List the available categories and exit"},
    ],
}

TYPES = {
    "social-media": [
        'site:linkedin.com/in "{text}"',
        'site:twitter.com "{text}" OR site:x.com "{text}"',
        'site:instagram.com "{text}"',
        'site:facebook.com "{text}"',
        'site:tiktok.com "{text}"',
        'site:pinterest.com "{text}"',
        'site:github.com "{text}"',
        'site:linktr.ee "{text}"',
        'site:reddit.com/user "{text}"',
        '"{text}" (site:medium.com OR site:substack.com)',
    ],
    "exposed-files": [
        '"{text}" ext:pdf',
        '"{text}" (ext:doc OR ext:docx OR ext:xls OR ext:xlsx)',
        '"{text}" (ext:csv OR ext:sql OR ext:bak OR ext:old)',
        'intitle:"index of" "{text}"',
        '"{text}" inurl:backup',
        '"{text}" (filename:.env OR filename:credentials.json)',
        '"{text}" intitle:"index of" .git',
        '"{text}" (ext:txt OR ext:log) (password OR secret OR token)',
    ],
    "logins": [
        '"{text}" (inurl:login OR inurl:signin)',
        '"{text}" (intitle:"sign in" OR intitle:login)',
        '"{text}" inurl:admin',
        '"{text}" inurl:wp-login.php',
        '"{text}" inurl:portal',
        '"{text}" (intext:password OR intext:"forgot password")',
        '"{text}" inurl:"/auth/"',
    ],
    "credentials": [
        '"{text}" filename:id_rsa',
        '"{text}" filename:.htpasswd',
        '"{text}" "password" ext:txt',
        '"{text}" (ext:sql AND "INSERT INTO users")',
        '"{text}" filename:credentials.json',
        '"{text}" "AWS_SECRET_ACCESS_KEY"',
        '"{text}" "api_key" (filename:.env OR ext:yaml OR ext:json)',
        '"{text}" (inurl:phpinfo OR intitle:phpinfo)',
    ],
    "cloud": [
        'site:storage.googleapis.com "{text}"',
        'site:s3.amazonaws.com "{text}"',
        'site:blob.core.windows.net "{text}"',
        'site:drive.google.com "{text}"',
        'site:dropbox.com/s "{text}"',
        'site:onedrive.live.com "{text}"',
        'site:sites.google.com "{text}"',
        'site:docs.google.com "{text}"',
    ],
}

ALIASES = {
    "sosial-media": "social-media",
}


def _patterns(kind: str):
    if kind == "all":
        seen, out = set(), []
        for patterns in TYPES.values():
            for pattern in patterns:
                if pattern not in seen:
                    seen.add(pattern)
                    out.append(pattern)
        return out
    return list(TYPES.get(kind, []))


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    kind = getattr(args, "dorkbuilder_type", "social-media")
    if getattr(args, "dorkbuilder_list_types", False):
        say("[bold]Available categories:[/bold]")
        for name, patterns in TYPES.items():
            say(f"  [cyan]{name}[/cyan] — {len(patterns)} dorks")
        say("  [cyan]all[/cyan] — union of every category "
            f"({len(_patterns('all'))} dorks)")
        say("[dim]alias: sosial-media = social-media[/dim]")
        return 0

    text = (getattr(args, "dorkbuilder_text", None) or "").strip()
    if not text:
        say("[red]Error:[/red] --dorkbuilder-text is required "
            "(or use --dorkbuilder-list-types)")
        return 1

    kind = ALIASES.get(kind, kind)
    patterns = _patterns(kind)
    if not patterns:
        say(f"[red]Unknown category:[/red] {kind!r} — "
            "run --dorkbuilder-list-types")
        return 1

    dorks = [pattern.format(text=text) for pattern in patterns]
    limit = int(getattr(args, "dorkbuilder_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    say(f"[green]{len(dorks)} dork(s)[/green] for [cyan]{text}[/cyan] "
        f"[dim](category: {kind})[/dim]")
    for dork in dorks:
        say(f"  [dim]•[/dim] {dork}")

    save = getattr(args, "dorkbuilder_save", None)
    if save:
        try:
            path = Path(ctx.guard_write(save))
        except Exception as e:
            say(f"[red]Cannot save:[/red] {e}")
            return 1
        if path.suffix.lower() == ".csv":
            body = "\n".join(f'"{d.replace(chr(34), chr(34) * 2)}"' for d in dorks) + "\n"
        else:
            body = "\n".join(dorks) + "\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        say(f"[green]✔ saved[/green] {len(dorks)} dorks → {path}")
    return 0
