# `@cve` — CVE Hunting

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/cve) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Queries that surface pages referencing CVEs — advisories, changelogs and proof-of-concept write-ups. Comments (`#`) are skipped by the loader.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `cve_1.txt` | 14 | CVE reference hunting — batch 1 |

**Folder total: 14 dorks across 1 package.**

## Usage

```bash
atdork install @cve                # install the whole folder
atdork install @cve/cve_1.txt      # install a single package
atdork --database-dork @cve --database-preview   # preview as queries
```

Find more: `atdork search cve` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
