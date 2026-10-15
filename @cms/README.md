# `@cms` — CMS

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/cms) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Content-management-system dorks: WordPress plugin presence, Joomla component exploits, Laravel debug endpoints and Magento panels.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `joomla.txt` | 382 | Joomla component vulnerability dorks (`com_*` exploits) |
| `laravel.txt` | 422 | Laravel/PHPUnit RFI & debug exposure |
| `magento.txt` | 76 | Magento admin & exposed panel dorks |
| `wp.txt` | 26,324 | WordPress plugin presence dorks (plugin index list) |
| `wp2.txt` | 474 | WordPress vulnerable plugin & upload-path dorks |

**Folder total: 27,678 dorks across 5 packages.**

## Usage

```bash
atdork install @cms                # install the whole folder
atdork install @cms/joomla.txt      # install a single package
atdork --database-dork @cms --database-preview   # preview as queries
```

Find more: `atdork search cms` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
