# `@sensitive` — Sensitive Data

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/sensitive) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Files and directories that should not be public: logs, hidden webmail, secret indexes and info-leaking endpoints.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `hidden-files-dorks.txt` | 749 | Hidden files & webmail exposure |
| `log-files-dorks.txt` | 17 | Exposed log files (PHP errors, ipsec...) |
| `sensitive-dirs-dorks.txt` | 444 | Secret/private directory indexes |
| `sensitive-files-dorks.txt` | 84 | General sensitive file searches (PDFs, indexes...) |
| `sensitive-info-dorks.txt` | 1,866 | Info-leaking PHP endpoints (`read.php`...) |

**Folder total: 3,160 dorks across 5 packages.**

## Usage

```bash
atdork install @sensitive                # install the whole folder
atdork install @sensitive/hidden-files-dorks.txt      # install a single package
atdork --database-dork @sensitive --database-preview   # preview as queries
```

Find more: `atdork search sensitive` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
