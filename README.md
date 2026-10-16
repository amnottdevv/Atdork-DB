# Atdork-DB

Dork package repository for [AtDork](https://github.com/amnottdevv/AtDork).
Every `@folder` is a themed collection of dork files, `Index.idn` is the
manifest that AtDork's package manager reads.

```
Atdork-DB/
├── Index.idn               # generated manifest — do not edit by hand
├── @exploit-db/            # Exploit-DB GHDB categories
├── @ghdb/                  # auto-refreshed GHDB export (weekly CI)
├── @cve/                   # CVE hunting queries
├── @shodan/ @censys/       # search-engine specific dorks
├── @virustotal/ @targets/  # VT Intelligence queries, recon domain lists
├── @cms/ @cloud/ @crypto/  # technology themed collections
├── @admin/ @sensitive/     # recon targets
└── ...
```

## Web catalog

**[amnottdevv.github.io/Atdork-DB](https://amnottdevv.github.io/Atdork-DB/)** — a
PyPI-style catalog of every package: instant search, `@folder` filters,
per-package previews and one-click `atdork install` commands. The site is fully
static, generated from this repository (`Index.idn` + the folder `README.md`
files) by `scripts/build_site.py`, and deployed to GitHub Pages on every push.

## Using it from AtDork

```bash
# browse the index
atdork search cve
atdork index

# install packages (shorthand resolves the folder by unique prefix)
atdork install c@cve_1.txt
atdork install @exploit-db          # whole folder
atdork installed

# use them
atdork --batch-file c@cve_1.txt -r 20
atdork --database-dork @ghdb/01_footholds --database-preview

# refresh data + index
atdork update
```

Installed copies live in `~/.atdork/packages/`; package refs always prefer
the installed copy, then fall back to this repository.

## Reference grammar

| Ref | Meaning |
|---|---|
| `@cve/cve_1.txt` | canonical reference (folder + file) |
| `c@cve_1.txt` | shorthand — unique folder prefix `c` → `@cve` |
| `cve_1.txt` | bare file name (must be unique in the index) |
| `@cve` | whole folder (install/uninstall) |

## Index.idn format

One line per data file (`.txt`, `.csv`, `.json`), pipe-separated:

```
@ghdb/01_footholds.txt|<sha256>|<bytes>|<dork-lines>|<description>
```

Rebuild it after adding or changing files:

```bash
atdork index --build
```

## Adding data

1. Drop the file into a themed `@folder/` (kebab-case folder names, no
   spaces in filenames).
2. Run `atdork index --build` (or let CI do it).
3. Add a row for the file to the folder's `README.md` Packages table —
   those descriptions power the web catalog's search and detail pages.
4. Commit. Files load as queries only when they are line-per-dork `.txt`
   files; structured `.csv`/`.json` packages are installable but not
   query-loadable.

## Automation

- `.github/workflows/update_ghdb.yml` re-exports Exploit-DB's GHDB into
  `@ghdb/` every Monday and rebuilds `Index.idn`.
- `.github/workflows/deploy-site.yml` regenerates the web catalog
  (`site/data/packages.json` + per-package previews) and deploys it to
  GitHub Pages whenever `Index.idn`, a folder `README.md` or `site/`
  changes (plus a weekly safety rebuild).
