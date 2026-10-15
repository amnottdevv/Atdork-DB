# `@github` — GitHub Secrets

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/github) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Dorks for hunting secrets and exposed configuration on GitHub — credentials, tokens and `.git` artifacts.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `git-dorks.txt` | 513 | Secret hunting (passwords, ICA keys, connection strings) |
| `git-files-dorks.txt` | 11 | Exposed `.git-credentials` / `.gitconfig` files |
| `github.txt` | 19 | General GitHub secrets & config dorks |
| `githubdorks.txt` | 180 | Filename-based dorks (`.npmrc _auth`, `.dockercfg`...) |

**Folder total: 723 dorks across 4 packages.**

## Usage

```bash
atdork install @github                # install the whole folder
atdork install @github/git-dorks.txt      # install a single package
atdork --database-dork @github --database-preview   # preview as queries
```

Find more: `atdork search github` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
