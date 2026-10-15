# `@iot` — IoT & CCTV

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/iot) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

Exposed cameras, NVRs and embedded device UIs — CGI endpoints, network camera titles and remote panels.

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `cctv.txt` | 434 | CCTV/webcam CGI exposure (`CgiStart`, `view.shtml`) |
| `cctv2.json` | 153 | CCTV device dork set (structured JSON) |
| `cctv3.txt` | 64 | Network camera title-based dorks |
| `various-iot-devices-dorks.txt` | 719 | IoT UIs — HP printers, remote UI panels |

**Folder total: 1,370 dorks across 4 packages.**

## Usage

```bash
atdork install @iot                # install the whole folder
atdork install @iot/cctv.txt      # install a single package
atdork --database-dork @iot --database-preview   # preview as queries
```

Find more: `atdork search iot` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
