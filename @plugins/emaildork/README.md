# emaildork — email discovery dorks for a name / brand + domain

Build (and optionally run) dorks that surface indexed email addresses:
contact pages, PDFs and documents, breach-style dumps, GitHub/config leaks
and people-search directories.

## Install

```bash
atdork install @plugins/emaildork
```

## Usage

```bash
# dorks for a person/brand
atdork --emaildork-name "john wick"

# restrict to one domain
atdork --emaildork-name "john wick" --emaildork-domain acme.com

# run them and extract unique addresses from the result snippets
atdork --emaildork-name acme --emaildork-domain acme.com --emaildork-search

# save
atdork --emaildork-name acme --emaildork-save emails.txt
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--emaildork-name` | — | Name, brand or keyword to hunt emails for. |
| `--emaildork-domain` | — | Restrict to a domain (e.g. `acme.com`). |
| `--emaildork-search` | off | Run the dorks and print extracted emails (spends search credits). |
| `--emaildork-save` | — | Write emails (with `--emaildork-search`) or the dorks (without) to a file, env-guarded. |
| `--emaildork-limit` | `0` | Emit at most N dorks (`0` = all). |

## Notes

- At least one of `--emaildork-name` / `--emaildork-domain` is required.
- With `--emaildork-domain`, extracted addresses are filtered to that
  domain (`*@domain`).
- Extraction is a light regex over result snippets — treat hits as leads to
  verify, not confirmed addresses.
- Without `--emaildork-search` it is fully offline.
