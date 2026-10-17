#!/usr/bin/env python3
"""
UsernameHunt — username / handle discovery across social platforms.

    atdork install @plugins/usernamehunt
    atdork --usernamehunt-name "johnwick"
    atdork --usernamehunt-name "johnwick" --usernamehunt-type all \
           --usernamehunt-save handles.txt

Builds dorks that surface a handle on social platforms, code hosts, pastes,
forums and gaming sites. With --usernamehunt-search it runs them and prints
the matching URLs.
"""

from pathlib import Path

PLUGIN = {
    "name": "usernamehunt",
    "version": "1.0.0",
    "description": "Find where a username/handle is used across the web",
    "options": [
        {"name": "name",
         "help": "Username / handle to hunt (without @)"},
        {"name": "type",
         "choices": ["social", "code", "paste", "gaming", "all"],
         "default": "all",
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
    "social": [
        'site:twitter.com "{name}"',
        'site:x.com "{name}"',
        'site:instagram.com "{name}"',
        'site:facebook.com "{name}"',
        'site:tiktok.com "{name}"',
        'site:snapchat.com/add/{name}',
        'site:linkedin.com/in/{name}',
        'site:reddit.com/user/{name}',
        'site:pinterest.com/{name}',
        'site:tumblr.com/{name}',
    ],
    "code": [
        'site:github.com/{name}',
        'site:gitlab.com/{name}',
        'site:bitbucket.org/{name}',
        'site:sourceforge.net/u/{name}',
        'site:pypi.org/user/{name}',
        'site:npmjs.com/~{name}',
    ],
    "paste": [
        'site:pastebin.com/u/{name}',
        'site:hastebin.com/u/{name}',
        'site:ghostbin.com "{name}"',
        'site:rentry.co "{name}"',
        '"{name}" (inurl:pastebin OR inurl:rentry)',
    ],
    "gaming": [
        'site:steamcommunity.com/id/{name}',
        'site:twitch.tv/{name}',
        'site:youtube.com/@{name}',
        'site:discord.com "{name}"',
        'site:roblox.com/user.aspx?id={name}',
        'site:chess.com/member/{name}',
    ],
}


def _patterns(kind, name):
    cats = list(CATEGORIES) if kind == "all" else [kind]
    out = []
    for cat in cats:
        for pattern in CATEGORIES.get(cat, []):
            out.append(pattern.format(name=name))
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    name = (getattr(args, "usernamehunt_name", None) or "").strip().lstrip("@")
    kind = getattr(args, "usernamehunt_type", "all")
    if not name:
        say("[red]Error:[/red] --usernamehunt-name is required")
        return 1

    dorks = _patterns(kind, name)
    limit = int(getattr(args, "usernamehunt_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    say(f"[green]{len(dorks)} dork(s)[/green] for [cyan]{name}[/cyan] "
        f"[dim](category: {kind})[/dim]")

    urls = []
    if getattr(args, "usernamehunt_search", False):
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
        urls = uniq
    else:
        for dork in dorks:
            say(f"  [dim]•[/dim] {dork}")
        say("[dim]add --usernamehunt-search to actually run them[/dim]")

    save = getattr(args, "usernamehunt_save", None)
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
