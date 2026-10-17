# vulndork — vulnerability-hunting dork sets by target / product / CVE

Generate dorks that surface exposed files, version strings, admin panels
and known-exploit paths for a target, a product+version, or a specific CVE.

## Install

```bash
atdork install @plugins/vulndork
```

## Usage

```bash
# exposed-file dorks for a target
atdork --vulndork-target example.com

# version-disclosure dorks
atdork --vulndork-target example.com --vulndork-type version

# product + version, all categories
atdork --vulndork-product "apache 2.4.49" --vulndork-type all

# add PoC paths for a known CVE
atdork --vulndork-target example.com --vulndork-cve CVE-2021-41773

# run them and print the matching URLs
atdork --vulndork-target example.com --vulndork-search --vulndork-save hits.txt
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--vulndork-target` | — | Root domain to hunt (e.g. `example.com`). |
| `--vulndork-product` | — | Product + version string (e.g. `apache 2.4.49`). |
| `--vulndork-cve` | — | Add proof-of-concept paths for a CVE (e.g. `CVE-2021-41773`). |
| `--vulndork-type` | `exposed` | Category: `exposed`, `version`, `panels`, `all`. |
| `--vulndork-search` | off | Run the dorks and print matching URLs (spends search credits). |
| `--vulndork-save` | — | Write URLs (with `--vulndork-search`) or the dorks (without) to a file, env-guarded. |
| `--vulndork-limit` | `0` | Emit at most N dorks (`0` = all). |

## CVE PoC paths

Recognized CVEs (best-effort path prefixes for reconnaissance):

`CVE-2021-41773`, `CVE-2021-42013`, `CVE-2014-6271` (Shellshock),
`CVE-2017-5638`, `CVE-2019-11510`, `CVE-2020-1472`, `CVE-2021-44228`
(Log4Shell), `CVE-2023-1389`. Unknown CVEs fall back to generic
`"<cve>" "proof of concept"` dorks.

## Notes

- **Reconnaissance only.** A hit means the path is *indexed* by the search
  engine — not that the target is vulnerable. Verify against systems you
  are authorized to test.
- Without `--vulndork-search` it is fully offline.
