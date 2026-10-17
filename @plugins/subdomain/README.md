# subdomain — discover indexed subdomains of a target

Surface a target's subdomains (api, staging, admin, dev panels, cloud
assets) through search-engine dorks. Prints the dorks by default, or actually
runs them and prints the unique subdomains found in the result URLs.

## Install

```bash
atdork install @plugins/subdomain
```

## Usage

```bash
# print the dorks (offline, no credits)
atdork --subdomain-target example.com

# run them through the engine and print discovered subdomains
atdork --subdomain-target example.com --subdomain-search

# save discovered subdomains
atdork --subdomain-target example.com --subdomain-search --subdomain-save subs.txt
```

Feed the results into other tooling:

```bash
atdork --batch-file subs.txt -r 20
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--subdomain-target` | — | Root domain to enumerate (e.g. `example.com`). Required. |
| `--subdomain-search` | off | Actually run the dorks and print discovered subdomains (spends search credits). |
| `--subdomain-verbose` | off | Print the raw dorks too (implied by `--subdomain-search`). |
| `--subdomain-save` | — | Write subdomains (with `--subdomain-search`) or the dorks (without) to a file, env-guarded. |
| `--subdomain-limit` | `0` | Emit at most N dorks (`0` = all). |

## Notes

- The dork set targets panels (`inurl:admin`, `inurl:grafana`), cloud hosts
  (`inurl:amazonaws.com`, `inurl:herokuapp.com`) and open indexes
  (`intitle:"index of" .git`).
- Without `--subdomain-search` it is fully offline.
- Only subdomains of the target root are extracted; the bare root is
  excluded from the output.
