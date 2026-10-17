# dorkbuilder — build ready-to-run dork lists from text + a category

Turn a name, brand or keyword into a set of ready-to-run Google dorks:
social profiles, exposed files, login portals, credential leaks and cloud
buckets — no manual pattern writing.

## Install

```bash
atdork install @plugins/dorkbuilder
```

## Usage

```bash
# social-media dorks for a person/brand, saved to dorks.txt
atdork --dorkbuilder-text "John wick" \
       --dorkbuilder-type social-media \
       --dorkbuilder-save dorks.txt

# see every category
atdork --dorkbuilder-list-types

# first 5 credential-leak dorks
atdork --dorkbuilder-text acme --dorkbuilder-type credentials --dorkbuilder-limit 5
```

Run the generated dorks straight from a file:

```bash
atdork --batch-file dorks.txt -r 20
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--dorkbuilder-text` | — | Text to hunt for (name, brand, keyword, username). Required. |
| `--dorkbuilder-type` | `social-media` | Category: `social-media`, `exposed-files`, `logins`, `credentials`, `cloud`, `all` (`sosial-media` is an alias). |
| `--dorkbuilder-save` | — | Write the dorks to a file (env-guarded; relative paths resolve inside the active environment). CSV quoting is applied for `.csv`. |
| `--dorkbuilder-limit` | `0` | Emit at most N dorks (`0` = all). |
| `--dorkbuilder-list-types` | off | List the available categories and exit. |

## Notes

- Fully offline — no search credits are spent; it only builds patterns.
- Output is one dork per line, ready for `--batch-file` or
  `--database-dork` after installing a package.
