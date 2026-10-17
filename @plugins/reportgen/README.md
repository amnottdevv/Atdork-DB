# reportgen — summarize result files into an HTML/JSON report

Turn the result files in your environment's results folder into a single
self-contained HTML report (or JSON) with every result row, its source file
and a per-file entry count.

## Install

```bash
atdork install @plugins/reportgen
```

## Usage

```bash
# run some searches first so results exist
atdork -q 'site:example.com ext:pdf' -r 20 -o json

# build an HTML report in the environment root
atdork --reportgen-save report.html

# or machine-readable JSON
atdork --reportgen-format json --reportgen-save report.json
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--reportgen-from` | active results dir | Folder with result files (`.json` / `.txt` / `.csv`). |
| `--reportgen-save` | `report.html` | Output report path (env-guarded). |
| `--reportgen-format` | `html` | `html` or `json`. |
| `--reportgen-title` | `AtDork Report` | Report title. |
| `--reportgen-max-rows` | `500` | Maximum result rows in the report (`0` = all). |

## Notes

- Fully offline — reads local result files only, spends no credits.
- The HTML report is self-contained (inline CSS), so it can be shared as a
  single file.
- The output file itself is excluded from the scan, so re-running never
  double-counts the report.
