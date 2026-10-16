# `@shodan` — Shodan

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/shodan) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Shodan filter cheat-sheets and curated query collections for internet-device reconnaissance. Structured `.csv` files are installable data, not directly loadable queries.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `shodan1.txt` | 189 | Basic Shodan filter cheat-sheet (city, port, product...) |
| `shodan2.txt` | 233 | Curated query collection (by @lothos612) |
| `shodan_ace-ics-iot-dorks.csv` | 130 | ICS/OT vendor-product query table (CSV) |
| `shodanqueries.txt` | 168 | Grouped queries by use case (admin, SSH...) |
| `shodan-appliances-bushidouk.txt` | 45 | Shodan ssl:/port: queries for common appliances |
| `shodan-dorks-dootss.txt` | 114 | Auto-updating Shodan dorks grouped by category |
| `shodan-dorks-nullfuzz.txt` | 2,833 | Large Shodan query/fingerprint collection |

**Folder total: 3,712 dorks across 7 packages.**

## Usage

```bash
atdork install @shodan                # install the whole folder
atdork install @shodan/shodan1.txt      # install a single package
atdork --database-dork @shodan --database-preview   # preview as queries
```

Find more: `atdork search shodan` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
