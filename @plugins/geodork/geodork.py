#!/usr/bin/env python3
"""
GeoDork — geographically-scoped dork builder.

    atdork install @plugins/geodork
    atdork --geodork-location "jakarta" --geodork-keyword "coffee"
    atdork --geodork-location "Bandung, Indonesia" --geodork-type all

Combines a location with a keyword (or a bare location) into dorks that
narrow search results to a place: Google Maps / Bing locality operators,
regional TLDs, "in <city>" phrasing and local directory sites. With
--geodork-search it runs them and prints matching URLs.
"""

from pathlib import Path
from urllib.parse import urlparse

PLUGIN = {
    "name": "geodork",
    "version": "1.0.0",
    "description": "Build (and optionally run) geographically-scoped dorks",
    "options": [
        {"name": "location",
         "help": "City / region / country (e.g. 'jakarta' or 'Bandung, Indonesia')"},
        {"name": "keyword",
         "help": "Keyword to combine with the location (optional)"},
        {"name": "type",
         "choices": ["maps", "local", "tld", "all"],
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
    "maps": [
        '"{keyword}" "in {location}" site:google.com/maps',
        '"{keyword}" "{location}" site:tripadvisor.*',
        '"{keyword}" "{location}" site:foursquare.com',
    ],
    "local": [
        '"{keyword}" "{location}" intitle:"index of"',
        '"{keyword}" "{location}" (inurl:contact OR inurl:about)',
        '"{keyword}" "{location}" (ext:pdf OR ext:docx)',
        '"{keyword}" "{location}" (whatsapp OR wa.me OR t.me)',
        '"{keyword}" "{location}" (price OR harga OR menu)',
    ],
    "tld": [
        '"{keyword}" site:.{location}',
    ],
}

# Country / region -> commonly used ccTLDs for the tld category.
CCTLD = {
    "indonesia": "id", "jakarta": "id", "bandung": "id", "surabaya": "id",
    "malaysia": "my", "singapore": "sg", "thailand": "th", "vietnam": "vn",
    "philippines": "ph", "united states": "us", "usa": "us", "amerika": "us",
    "united kingdom": "uk", "britain": "uk", "england": "uk",
    "germany": "de", "prancis": "fr", "france": "fr", "jepang": "jp",
    "japan": "jp", "australia": "au", "india": "in", "brasil": "br",
    "brazil": "br", "russia": "ru", "china": "cn", "korea": "kr",
}


def _patterns(kind, location, keyword):
    kw = keyword or location
    loc = location
    out = []
    cats = list(CATEGORIES) if kind == "all" else [kind]
    for cat in cats:
        for pattern in CATEGORIES.get(cat, []):
            d = pattern.format(keyword=kw, location=loc)
            # the tld category uses a ccTLD when we recognize the location
            if cat == "tld":
                cc = CCTLD.get(loc.lower())
                if cc:
                    d = d.replace(f"site:.{loc}", f"site:.{cc}")
                else:
                    continue  # unknown TLD — skip rather than emit junk
            out.append(d)
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def run(args, ctx) -> int:
    console = ctx.console
    say = console.print if console is not None else print

    location = (getattr(args, "geodork_location", None) or "").strip()
    keyword = (getattr(args, "geodork_keyword", None) or "").strip()
    kind = getattr(args, "geodork_type", "all")
    if not location:
        say("[red]Error:[/red] --geodork-location is required")
        return 1

    dorks = _patterns(kind, location, keyword)
    limit = int(getattr(args, "geodork_limit", 0) or 0)
    if limit > 0:
        dorks = dorks[:limit]

    say(f"[green]{len(dorks)} dork(s)[/green] for "
        f"[cyan]{keyword or ''}{' in ' if keyword else ''}{location}[/cyan] "
        f"[dim](category: {kind})[/dim]")

    urls = []
    if getattr(args, "geodork_search", False):
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
        say("[dim]add --geodork-search to actually run them[/dim]")

    save = getattr(args, "geodork_save", None)
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
