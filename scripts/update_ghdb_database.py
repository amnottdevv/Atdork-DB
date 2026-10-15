#!/usr/bin/env python
"""
Atdork-DB: scripts/update_ghdb_database.py

Fetches every dork from Exploit-DB's Google Hacking Database, splits them
per category, writes them into @ghdb/, then rebuilds Index.idn so the
Atdork-DB package index stays in sync.

Runs weekly via .github/workflows/update_ghdb.yml, and can be run manually:

    ATDORK_SRC=/path/to/atdork python scripts/update_ghdb_database.py

The scraping logic lives in the main AtDork repository
(core/ghdb_scraper.py). This script needs only requests + beautifulsoup4;
set ATDORK_SRC to an AtDork checkout (or have the package installed) so
`core.*` can be imported.
"""

import logging
import os
import re
import sys
from datetime import datetime, timezone

# Import core.ghdb_scraper / core.package_manager from an AtDork checkout
# (ATDORK_SRC) or from an installed package.
_bootstrap = os.environ.get("ATDORK_SRC")
if _bootstrap:
    sys.path.insert(0, _bootstrap)
try:
    from core.ghdb_scraper import fetch_all_dorks, summarize_categories
    from core.package_manager import build_index
except ImportError as exc:  # pragma: no cover - CI misconfiguration
    sys.exit(
        "Cannot import core.* from the AtDork package. Install AtDork or "
        f"point ATDORK_SRC at a checkout (tried: {_bootstrap or 'installed package only'}). "
        f"Original error: {exc}"
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHDB_DIR = "@ghdb"          # category folder inside Atdork-DB
INDEX_FILE = "Index.idn"    # rebuilt after the export


def _slugify(name: str) -> str:
    """Turn a category name into a safe filename:
    'Files Containing Passwords' -> 'files_containing_passwords'."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug or "unknown"


def _category_filename(cat_id: int, cat_title: str) -> str:
    return f"{cat_id:02d}_{_slugify(cat_title)}.txt"


def export_database():
    logger.info("Fetching GHDB data...")
    data = fetch_all_dorks()
    if data is None:
        logger.error("Failed to fetch GHDB data. Exiting with error.")
        sys.exit(1)

    all_dorks = data["dorks"]
    total_dorks = data["total_dorks"]
    logger.info("Fetched %d dorks (%d reported by GHDB)", len(all_dorks), total_dorks)

    dest = os.path.join(REPO_ROOT, GHDB_DIR)
    os.makedirs(dest, exist_ok=True)

    # Group dorks per category.
    by_category = {}
    for d in all_dorks:
        key = (d["cat_id"], d["cat_title"])
        by_category.setdefault(key, []).append(d)

    written_files = []
    for (cat_id, cat_title), dorks in sorted(by_category.items(), key=lambda kv: kv[0][0]):
        filename = _category_filename(cat_id, cat_title)
        filepath = os.path.join(dest, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for d in dorks:
                f.write(f"{d['text']}\n")
        written_files.append((filename, cat_title, len(dorks)))
        logger.info("Wrote %s (%d dorks)", filepath, len(dorks))

    # Summary README so it is easy to see when data last changed.
    summary = summarize_categories(all_dorks)  # noqa: F841 - keeps API sanity check
    readme_path = os.path.join(dest, "README.md")
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# GHDB Dork Database\n\n")
        f.write(f"Last updated: **{now_utc}**\n\n")
        f.write(f"Total dorks: **{total_dorks}**\n\n")
        f.write("Source: [Exploit-DB Google Hacking Database]"
                "(https://www.exploit-db.com/google-hacking-database)\n\n")
        f.write("| File | Category | Dorks |\n")
        f.write("|---|---|---|\n")
        for filename, cat_title, count in sorted(written_files, key=lambda x: x[0]):
            f.write(f"| `{filename}` | {cat_title} | {count} |\n")

    logger.info("README written to %s", readme_path)

    # Rebuild the package index so checksums/line counts stay accurate.
    stats = build_index(repo=REPO_ROOT)
    logger.info(
        "Index rebuilt: %d entries in %d folders (%d dorks) -> %s",
        stats["entries"], stats["folders"], stats["total_dorks"], INDEX_FILE,
    )
    logger.info("Done. %d dorks across %d category files.", total_dorks, len(written_files))


if __name__ == "__main__":
    export_database()
