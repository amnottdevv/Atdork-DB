# `@bing` — Bing Search Dorks

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/bing) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Bing-specific dork sets built around operators Google does not support (`contains:`, `linkfromdomain:`, `location:`, `feed:`, ...).

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `bing1.txt` | 195 | OR groups & the `contains:` operator |
| `bing2.txt` | 310 | Advanced operators: location, ip, domain, linkfromdomain, language, feed, prefer |

**Folder total: 505 dorks across 2 packages.**

## Usage

```bash
atdork install @bing                # install the whole folder
atdork install @bing/bing1.txt      # install a single package
atdork --database-dork @bing --database-preview   # preview as queries
```

Find more: `atdork search bing` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
