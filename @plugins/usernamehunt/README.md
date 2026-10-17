# usernamehunt — username / handle discovery across the web

Find where a handle is used: social platforms, code hosts, paste sites and
gaming profiles. Prints the dorks by default, or runs them and prints the
matching URLs.

## Install

```bash
atdork install @plugins/usernamehunt
```

## Usage

```bash
# all categories, offline
atdork --usernamehunt-name "johnwick"

# only code-hosting profiles
atdork --usernamehunt-name "johnwick" --usernamehunt-type code

# run them and print matching URLs
atdork --usernamehunt-name "johnwick" --usernamehunt-search

# save
atdork --usernamehunt-name "johnwick" --usernamehunt-save handles.txt
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--usernamehunt-name` | — | Username / handle to hunt (without `@`). Required. |
| `--usernamehunt-type` | `all` | Category: `social`, `code`, `paste`, `gaming`, `all`. |
| `--usernamehunt-search` | off | Run the dorks and print matching URLs (spends search credits). |
| `--usernamehunt-save` | — | Write URLs (with `--usernamehunt-search`) or the dorks (without) to a file, env-guarded. |
| `--usernamehunt-limit` | `0` | Emit at most N dorks (`0` = all). |

## Notes

- A leading `@` is stripped, so `--usernamehunt-name @johnwick` works too.
- Exact-handle dorks (`site:github.com/{name}`) are used where the platform
  has a predictable profile URL; quoted dorks elsewhere.
- Without `--usernamehunt-search` it is fully offline.
