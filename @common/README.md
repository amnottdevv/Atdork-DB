# `@common` — Common Web Vulns

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/common) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Curated everyday web-vulnerability dorks grouped by class: SQLi/IDOR, LFI/RFI, XSS, file upload/RCE/SSRF and debug endpoints.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `common1.txt` | 156 | SQL injection & IDOR parameter dorks |
| `common2.txt` | 237 | LFI / RFI & path disclosure |
| `common3.txt` | 262 | XSS & HTML injection |
| `common4.txt` | 264 | File upload, RCE & SSRF |
| `common5.txt` | 708 | phpinfo / debug endpoint discovery |

**Folder total: 1,627 dorks across 5 packages.**

## Usage

```bash
atdork install @common                # install the whole folder
atdork install @common/common1.txt      # install a single package
atdork --database-dork @common --database-preview   # preview as queries
```

Find more: `atdork search common` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
