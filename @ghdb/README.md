# `@ghdb` — Google Hacking Database

> **Atdork-DB package folder** · [Browse in the web catalog](https://amnottdevv.github.io/Atdork-DB/#/f/ghdb) · Part of [Atdork-DB](https://github.com/amnottdevv/Atdork-DB)

The numbered GHDB categories (footholds → advisories), auto-refreshed **weekly** from [Exploit-DB's GHDB](https://www.exploit-db.com/google-hacking-database).

## Packages

| Package | Dorks | Description |
| --- | ---: | --- |
| `01_footholds.txt` | 121 | Foothold discovery — shells, proxies, gated admin pages |
| `02_files_containing_usernames.txt` | 47 | Files leaking usernames (webalizer, Steam configs...) |
| `03_sensitive_directories.txt` | 450 | Secret/private directory indexes |
| `04_web_server_detection.txt` | 205 | Web server & version fingerprints (IIS, Novell...) |
| `05_vulnerable_files.txt` | 86 | Upload managers & vulnerable scripts exposed |
| `06_vulnerable_servers.txt` | 129 | Samba, FTP and admin consoles exposed |
| `07_error_messages.txt` | 124 | Database & server error messages (ORA-, IIS...) |
| `08_files_containing_juicy_info.txt` | 1,743 | Ganglia reports, JSP snoop & info leaks |
| `09_files_containing_passwords.txt` | 401 | Password lists & passlist.txt exposure |
| `10_sensitive_online_shopping_info.txt` | 15 | Tracking pages, hosting panels & shop data |
| `11_network_or_vulnerability_data.txt` | 108 | Finger/portscan CGI & vulnerability data |
| `12_pages_containing_login_portals.txt` | 1,549 | Router & VPN login portals (MikroTik, MetaFrame) |
| `13_various_online_devices.txt` | 743 | IP cameras, HP printers & remote UIs |
| `14_advisories_and_vulnerabilities.txt` | 2,219 | CMS advisories & WordPress logins |

**Folder total: 7,940 dorks across 14 packages.**

## Usage

```bash
atdork install @ghdb                # install the whole folder
atdork install @ghdb/01_footholds.txt      # install a single package
atdork --database-dork @ghdb --database-preview   # preview as queries
```

Find more: `atdork search ghdb` · [All folders](https://github.com/amnottdevv/Atdork-DB#package-folders)
