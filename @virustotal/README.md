# `@virustotal` — VirusTotal Intelligence

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/virustotal) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

VirusTotal Enterprise / Intelligence search queries for malware hunting — file, network and behaviour filters that map onto the VT search bar. These are engine queries, not Google dorks: load them with `atdork --database-dork @virustotal/... --database-preview` to preview, then paste into VirusTotal Intelligence.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `vti-dorks-neo23x0.txt` | 34 | Curated VT Intelligence queries (Neo23x0/vti-dorks) |

**Folder total: 34 dorks across 1 packages.**

## Usage

```bash
atdork install @virustotal                     # install the whole folder
atdork install @virustotal/vti-dorks-neo23x0.txt   # install a single package
atdork --database-dork @virustotal/vti-dorks-neo23x0.txt --database-preview
```

Find more: `atdork search virustotal` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
