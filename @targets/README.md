# `@targets` — Recon Target Lists

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/targets) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Domain lists, not dork queries. Each `.csv` is a `domain,category` list meant to be fed into dorking tooling (e.g. SiteDorks-style workflows) or your own scripts — iterate a list and prepend `site:` to build scoped queries. Structured data: installable, but not query-loadable by AtDork's `--batch-file`.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `bugbounty-no-platform-targets.csv` | 82 | Bug bounty domains hosted outside the big platforms |
| `netherlands-bugbounty-targets.csv` | 91 | Dutch bug bounty domains |
| `netherlands-edu-targets.csv` | 6,584 | Dutch educational institutions |
| `netherlands-gov-targets.csv` | 1,996 | Dutch government domains |
| `usa-county-targets.csv` | 1,398 | US county government domains |
| `usa-state-targets.csv` | 807 | US state government domains |
| `worldwide-targets.csv` | 638 | International starter list, grouped by site category |

**Folder total: 11,596 domains across 7 packages.**

## Usage

```bash
atdork install @targets                        # install the whole folder
atdork install @targets/worldwide-targets.csv  # single list
```

Build scoped queries from a list, for example:

```bash
while IFS=, read -r domain cat; do
  [[ $domain == \#* ]] && continue
  echo "site:$domain inurl:admin"
done < ~/.atdork/packages/targets/worldwide-targets.csv
```

Source: [Zarcolio/sitedorks](https://github.com/Zarcolio/sitedorks) (`csv/`) · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
