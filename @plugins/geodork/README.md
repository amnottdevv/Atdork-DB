# geodork — geographically-scoped dork builder

Combine a location with a keyword (or a bare location) into dorks that
narrow search results to a place: map/locality operators, regional TLDs,
`in <city>` phrasing and local directory sites.

## Install

```bash
atdork install @plugins/geodork
```

## Usage

```bash
# dorks for coffee shops in Jakarta
atdork --geodork-location "jakarta" --geodork-keyword "coffee"

# bare location
atdork --geodork-location "Bandung, Indonesia"

# only maps results
atdork --geodork-location jakarta --geodork-keyword kopi --geodork-type maps

# run them and print matching URLs
atdork --geodork-location jakarta --geodork-keyword kopi --geodork-search
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--geodork-location` | — | City / region / country (e.g. `jakarta` or `Bandung, Indonesia`). Required. |
| `--geodork-keyword` | location | Keyword to combine with the location. |
| `--geodork-type` | `all` | Category: `maps`, `local`, `tld`, `all`. |
| `--geodork-search` | off | Run the dorks and print matching URLs (spends search credits). |
| `--geodork-save` | — | Write URLs (with `--geodork-search`) or the dorks (without) to a file, env-guarded. |
| `--geodork-limit` | `0` | Emit at most N dorks (`0` = all). |

## Notes

- The `tld` category maps recognized countries/regions to their ccTLD
  (`indonesia` → `.id`, `malaysia` → `.my`, …); unrecognized locations are
  skipped rather than emitting a junk `site:.` operator.
- Without `--geodork-search` it is fully offline.
