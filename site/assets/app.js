/* Atdork-DB package catalog — vanilla JS, no dependencies */
(() => {
  "use strict";

  const view = document.getElementById("view");
  let DB = null;
  const state = { q: "", folder: "" };

  /* ── helpers ─────────────────────────────────────── */
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
  const fmtN = (n) => n.toLocaleString("en-US");
  const fmtSize = (b) => (b < 1024 ? `${b} B`
    : b < 1048576 ? `${(b / 1024).toFixed(1)} KB`
    : `${(b / 1048576).toFixed(1)} MB`);
  const fmtDate = (iso) => {
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? iso || "—" : d.toISOString().slice(0, 10);
  };

  async function copyText(text, btn) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); } catch { /* ignore */ }
      ta.remove();
    }
    if (btn) {
      const old = btn.innerHTML;
      btn.classList.add("copied");
      btn.textContent = "Copied ✓";
      setTimeout(() => { btn.classList.remove("copied"); btn.innerHTML = old; }, 1300);
    }
  }

  const folderTitle = (name) => (DB.folders.find((f) => f.name === name) || {}).title || name;
  let PLUGINS = null;

  const loadPlugins = () => (PLUGINS ? PLUGINS
    : fetch("data/plugins.json").then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
        .then((j) => { PLUGINS = j; return PLUGINS; }));

  const optType = (o) => (o.type === "store_true" ? "switch" : o.type);

  function filtered() {
    const toks = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    return DB.packages.filter((p) => {
      if (state.folder && p.folder !== state.folder) return false;
      if (!toks.length) return true;
      const hay = `${p.ref} ${p.desc} ${folderTitle(p.folder)}`.toLowerCase();
      return toks.every((t) => hay.includes(t));
    });
  }

  /* ── home view ───────────────────────────────────── */
  function renderHome() {
    const t = DB.totals;
    document.title = "Atdork-DB — Dork Package Catalog";
    view.innerHTML = `
      <section class="hero">
        <h1>${fmtN(t.dorks)} dorks · ${fmtN(t.plugins || 0)} plugins. One command away.</h1>
        <p class="sub">Browse curated OSINT dork packages and installable
          <a href="#/plugins">plugins</a>, then pull them straight into
          <a href="https://github.com/amnottdevv/atdork">AtDork</a>:
          <code>atdork install @cve/cve_1.txt</code> or
          <code>atdork install @plugins/dorkbuilder</code> — no copying, no
          <code>git clone</code>. Your own repo works too:
          <code>atdork install https://github.com/you/plugins#my-tool</code>.</p>
        <div class="search">
          <svg class="icon" width="17" height="17" viewBox="0 0 16 16" fill="currentColor"><path d="M11.5 7a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Zm-.82 4.74a6 6 0 1 1 1.06-1.06l3.04 3.04a.75.75 0 1 1-1.06 1.06l-3.04-3.06Z"/></svg>
          <input id="q" type="search" placeholder="Search packages & plugins…  e.g. s3, cve, subdomain, report"
                 autocomplete="off" spellcheck="false" value="${esc(state.q)}">
          <kbd>/</kbd>
        </div>
      </section>
      <section class="stats">
        <div class="stat"><b>${fmtN(t.packages)}</b><span>Packages</span></div>
        <div class="stat"><b>${fmtN(t.folders)}</b><span>Folders</span></div>
        <div class="stat"><b>${fmtN(t.dorks)}</b><span>Dorks</span></div>
        <a class="stat" href="#/plugins" title="Browse plugins"><b>${fmtN(t.plugins || 0)}</b><span>Plugins</span></a>
        <div class="stat"><b>${fmtDate(DB.generated)}</b><span>Last rebuild</span></div>
      </section>
      <div class="chips" id="chips"></div>
      <div class="result-bar"><span id="count"></span>
        <a href="https://github.com/amnottdevv/Atdork-DB">Edit data on GitHub →</a></div>
      <div id="plugin-hits"></div>
      <div class="table"><table>
        <thead><tr>
          <th>Package</th><th class="num">Dorks</th><th class="num size">Size</th>
          <th class="desc-h">Description</th><th></th>
        </tr></thead>
        <tbody id="rows"></tbody>
      </table></div>
      <div id="empty"></div>`;

    const chips = view.querySelector("#chips");
    const mkChip = (name, label) => {
      const el = document.createElement("span");
      el.className = "chip" + (state.folder === name ? " on" : "");
      el.textContent = label;
      el.addEventListener("click", () => {
        location.hash = name ? `#/f/${encodeURIComponent(name)}` : "#/";
      });
      return el;
    };
    chips.appendChild(mkChip("", `all · ${fmtN(DB.totals.packages)}`));
    DB.folders.slice().sort((a, b) => b.dorks - a.dorks).forEach((f) => {
      chips.appendChild(mkChip(f.name, `@${f.name} · ${fmtN(f.packages)}`));
    });

    view.querySelector("#q").addEventListener("input", (e) => {
      state.q = e.target.value;
      refreshRows();
    });
    refreshRows();
  }

  function pluginMatches() {
    const toks = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!toks.length || !PLUGINS) return [];
    return PLUGINS.plugins.filter((p) => toks.every((t) =>
      `${p.name} ${p.description} ${p.ref} plugin`.toLowerCase().includes(t)));
  }

  function renderPluginHits() {
    const host = view.querySelector("#plugin-hits");
    if (!host) return;
    if (!state.q) { host.innerHTML = ""; return; }
    loadPlugins().then(() => {
      if (!state.q) { host.innerHTML = ""; return; }  // query cleared while loading
      const hits = pluginMatches();
      host.innerHTML = hits.length ? `
        <div class="result-bar"><span>${hits.length} plugin${hits.length === 1 ? "" : "s"}
          matching “${esc(state.q)}”</span>
          <a href="#/plugins">all plugins →</a></div>
        <div class="table"><table>
          <thead><tr><th>Plugin</th><th class="num size">Version</th>
            <th class="desc-h">Description</th><th></th></tr></thead>
          <tbody>${hits.map((p) => `
            <tr>
              <td class="pkg"><a href="#/plugin/${encodeURIComponent(p.name)}">${esc(p.name)}</a>
                <span class="folder-tag">${esc(p.trigger)}</span></td>
              <td class="num size">${esc(p.version)}</td>
              <td class="desc">${esc(p.description)}</td>
              <td class="act"><button class="btn" data-copy="atdork install ${esc(p.ref)}"
                  title="Copy install command">⧉ install</button></td>
            </tr>`).join("")}
          </tbody></table></div>` : "";
    }).catch(() => { host.innerHTML = ""; });
  }

  function refreshRows() {
    renderPluginHits();
    const items = filtered();
    const rows = view.querySelector("#rows");
    const empty = view.querySelector("#empty");
    view.querySelector("#count").textContent =
      `${fmtN(items.length)} package${items.length === 1 ? "" : "s"}` +
      (state.folder ? ` in @${state.folder}` : "") +
      (state.q ? ` matching “${state.q}”` : "");
    rows.innerHTML = items.map((p) => `
      <tr>
        <td class="pkg"><a href="#/p/${encodeURIComponent(p.ref)}">${esc(p.ref)}</a>
          <span class="folder-tag">@${esc(p.folder)}</span></td>
        <td class="num"><strong>${fmtN(p.dorks)}</strong></td>
        <td class="num size">${fmtSize(p.bytes)}</td>
        <td class="desc">${esc(p.desc)}</td>
        <td class="act"><button class="btn" data-copy="atdork install ${esc(p.ref)}"
            title="Copy install command">⧉ install</button></td>
      </tr>`).join("");
    empty.innerHTML = items.length ? "" : `
      <div class="empty"><b>No packages match.</b>
        <p>Try another keyword, or clear the <code>@folder</code> filter.
        <button class="btn" id="clear" style="margin-left:8px">Clear filters</button></p></div>`;
    const clear = view.querySelector("#clear");
    if (clear) clear.addEventListener("click", () => { location.hash = "#/"; });
  }

  /* ── detail view ─────────────────────────────────── */
  function renderDetail(ref) {
    const p = DB.packages.find((x) => x.ref === ref);
    if (!p) {
      document.title = "Not found — Atdork-DB";
      view.innerHTML = `
        <div class="empty pad"><b>Package not found: <code>${esc(ref)}</code></b>
          <p>It may have been renamed. <a href="#/">← Back to the catalog</a> or run
          <code>atdork search</code> locally.</p></div>`;
      return;
    }
    const ext = p.name.includes(".") ? p.name.split(".").pop() : "txt";
    const loadable = ext === "txt";
    document.title = `${p.ref} — Atdork-DB`;
    const related = DB.packages.filter((x) => x.folder === p.folder && x.ref !== p.ref);

    view.innerHTML = `
      <nav class="crumb"><a href="#/">catalog</a> /
        <a href="#/f/${encodeURIComponent(p.folder)}">@${esc(p.folder)}</a> / ${esc(p.name)}</nav>
      <div class="detail-head">
        <h1>${esc(p.ref)}</h1>
        <button class="btn primary big" data-copy="atdork install ${esc(p.ref)}">⧉ atdork install</button>
      </div>
      <div class="badges">
        <span class="badge">${fmtN(p.dorks)} dorks</span>
        <span class="badge">${fmtSize(p.bytes)}</span>
        <span class="badge gray">.${esc(ext)}</span>
        <span class="badge gray">@${esc(p.folder)}</span>
      </div>
      <p class="detail-desc">${esc(p.desc)} ${esc((DB.folders.find((f) => f.name === p.folder) || {}).intro || "")}</p>

      <div class="cmd"><code><span class="prompt">$ </span>atdork install ${esc(p.ref)}</code>
        <button class="btn" data-copy="atdork install ${esc(p.ref)}">⧉ copy</button></div>
      <p class="hint">then run <code>atdork --batch-file ${esc(p.ref)} -r 20</code>${loadable
        ? ` · or load directly: <code>atdork --database-dork ${esc(p.ref)} --database-preview</code>`
        : ` · structured data — parse it after installing`}</p>

      <div class="card"><h3>Preview <span class="muted">first lines</span></h3>
        <div class="body"><pre class="preview" id="pv">Loading preview…</pre></div></div>

      <div class="card"><h3>Metadata</h3><div class="body meta-grid">
        <div><b>Dorks</b><span>${fmtN(p.dorks)}</span></div>
        <div><b>Size</b><span>${fmtSize(p.bytes)} (${fmtN(p.bytes)} B)</span></div>
        <div><b>sha256</b><span title="${esc(p.sha256)}">${esc(p.sha256.slice(0, 16))}…</span></div>
        <div><b>Download</b><span><a href="${esc(p.raw)}">raw file</a> · <a href="${esc(p.blob)}">source</a></span></div>
      </div></div>

      ${related.length ? `<div class="card"><h3>More in @${esc(p.folder)}</h3>
        <div class="body related">${related.map((r) => `
          <a href="#/p/${encodeURIComponent(r.ref)}">${esc(r.ref)}<span>${fmtN(r.dorks)} dorks</span></a>`).join("")}
        </div></div>` : ""}`;

    fetch(p.preview)
      .then((r) => (r.ok ? r.text() : Promise.reject(r.status)))
      .then((txt) => {
        const body = txt.trimEnd()
          ? txt.trimEnd().split("\n").map((l) => (l.startsWith("#")
              ? `<span class="c">${esc(l)}</span>` : esc(l))).join("\n")
          : "(empty package)";
        view.querySelector("#pv").innerHTML = body;
      })
      .catch(() => { view.querySelector("#pv").textContent = "(preview unavailable)"; });
  }

  /* ── plugins views ─────────────────────────────── */
  function renderPlugins() {
    loadPlugins().then((data) => {
      const list = data.plugins || [];
      document.title = "Plugins — Atdork-DB";
      view.innerHTML = `
        <nav class="crumb"><a href="#/">catalog</a> / plugins</nav>
        <div class="detail-head">
          <h1>Plugins</h1>
          <span class="muted">${list.length} tool${list.length === 1 ? "" : "s"} · run as
            <code>--&lt;plugin&gt;-&lt;option&gt;</code> flags</span>
        </div>
        <p class="detail-desc">Installable AtDork extensions: Python tools that add new
          flags to the CLI. Metadata is parsed without executing code — a plugin only
          runs when its flags are actually used.</p>
        <div class="table"><table>
          <thead><tr><th>Plugin</th><th class="num size">Version</th>
            <th class="desc-h">Description</th><th></th></tr></thead>
          <tbody>${list.map((p) => `
            <tr>
              <td class="pkg"><a href="#/plugin/${encodeURIComponent(p.name)}">${esc(p.name)}</a>
                <span class="folder-tag">${esc(p.trigger)}</span></td>
              <td class="num size">${esc(p.version)}</td>
              <td class="desc">${esc(p.description)}</td>
              <td class="act"><button class="btn" data-copy="atdork install ${esc(p.ref)}"
                  title="Copy install command">⧉ install</button></td>
            </tr>`).join("")}
          </tbody>
        </table></div>`;
    }).catch(() => {
      view.innerHTML = `<div class="empty pad"><b>Plugins failed to load.</b>
        <p>Try a hard refresh, or check <a href="https://github.com/amnottdevv/Atdork-DB">the repository</a>.</p></div>`;
    });
  }

  function renderPluginDetail(name) {
    loadPlugins().then((data) => {
      const p = (data.plugins || []).find((x) => x.name === name || x.ref === name);
      if (!p) {
        document.title = "Not found — Atdork-DB";
        view.innerHTML = `<div class="empty pad"><b>Plugin not found: <code>${esc(name)}</code></b>
          <p><a href="#/plugins">← Back to plugins</a></p></div>`;
        return;
      }
      document.title = `${p.name} — Atdork-DB plugins`;
      const example = p.trigger + (p.options.length
        ? " \\\n       " + p.options.slice(0, 3).map((o) => (
            o.type === "store_true" ? o.flag : `${o.flag} "value"`)).join(" \\\n       ")
        : "");
      view.innerHTML = `
        <nav class="crumb"><a href="#/">catalog</a> / <a href="#/plugins">plugins</a> / ${esc(p.name)}</nav>
        <div class="detail-head">
          <h1>${esc(p.name)} <span class="muted">v${esc(p.version)}</span></h1>
          <div class="detail-actions">
            <a class="btn" href="${esc(p.blob)}" target="_blank" rel="noopener">View source ↗</a>
            <button class="btn primary big" data-copy="atdork install ${esc(p.ref)}">⧉ atdork install</button>
          </div>
        </div>
        <div class="badges">
          <span class="badge">plugin</span>
          <span class="badge gray">${p.options.length} option(s)</span>
          <span class="badge gray">${fmtSize(p.bytes)}</span>
          <span class="badge gray">${esc(p.ref)}</span>
        </div>
        <p class="detail-desc">${esc(p.description)}</p>

        <div class="cmd"><code><span class="prompt">$ </span>atdork install ${esc(p.ref)}</code>
          <button class="btn" data-copy="atdork install ${esc(p.ref)}">⧉ copy</button></div>
        <div class="cmd"><code><span class="prompt">$ </span>atdork install https://github.com/amnottdevv/Atdork-DB#${esc(p.ref)}</code>
          <button class="btn" data-copy="atdork install https://github.com/amnottdevv/Atdork-DB#${esc(p.ref)}">⧉ copy</button></div>
        <div class="cmd"><code><span class="prompt">$ </span>${esc(example)}</code>
          <button class="btn" data-copy="${esc(example)}">⧉ copy</button></div>
        <p class="hint">every option is registered as <code>--${esc(p.name)}-&lt;option&gt;</code> —
          the plugin runs when the bare <code>${esc(p.trigger)}</code> flag or any
          <code>--${esc(p.name)}-…</code> argument is present.
          Publishing a tool of your own? <code>atdork plugins publish ${esc(p.ref)} --write</code>
          generates the <code>Index.idn</code> lines for your repository.</p>

        ${p.options.length ? `<div class="card"><h3>Options</h3>
          <div class="body flush"><table>
            <thead><tr><th>Flag</th><th>Type</th><th class="num size">Default</th>
              <th class="desc-h">Description</th></tr></thead>
            <tbody>${p.options.map((o) => `
              <tr><td class="pkg"><code>${esc(o.flag)}</code></td>
                <td class="desc">${esc(optType(o))}${o.choices.length ? ` · ${esc(o.choices.join(", "))}` : ""}</td>
                <td class="num size">${o.default == null ? "—" : esc(JSON.stringify(o.default))}</td>
                <td class="desc">${esc(o.help)}</td></tr>`).join("")}
            </tbody></table></div></div>` : ""}

        <div class="card"><h3>README <span class="muted">from the repository</span>
          <a class="h-link" href="${esc(p.readme_blob)}" target="_blank" rel="noopener">view raw ↗</a></h3>
          <div class="body md">${p.readme_html || "<p class='muted'>No README.</p>"}</div></div>

        <div class="card"><h3>Source</h3><div class="body meta-grid">
          <div><b>Module</b><span>${esc(p.module)}</span></div>
          <div><b>Size</b><span>${fmtSize(p.bytes)}</span></div>
          <div><b>Source</b><span><a href="${esc(p.blob)}">view</a> · <a href="${esc(p.raw)}">raw</a></span></div>
          <div><b>Install ref</b><span>${esc(p.ref)}</span></div>
        </div></div>`;
    }).catch(() => {
      view.innerHTML = `<div class="empty pad"><b>Plugins failed to load.</b>
        <p>Try a hard refresh, or check <a href="https://github.com/amnottdevv/Atdork-DB">the repository</a>.</p></div>`;
    });
  }

  /* ── router + boot ───────────────────────────────── */
  function route() {
    const h = location.hash.replace(/^#\/?/, "");
    window.scrollTo(0, 0);
    if (h === "plugins") return renderPlugins();
    if (h.startsWith("plugin/")) return renderPluginDetail(decodeURIComponent(h.slice(7)));
    if (h.startsWith("p/")) return renderDetail(decodeURIComponent(h.slice(2)));
    if (h.startsWith("f/")) {
      state.folder = decodeURIComponent(h.slice(2));
      return renderHome();
    }
    state.folder = "";
    return renderHome();
  }

  view.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-copy]");
    if (btn) copyText(btn.dataset.copy, btn);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
      const q = view.querySelector("#q");
      if (q) { e.preventDefault(); q.focus(); q.select(); }
    }
  });
  window.addEventListener("hashchange", route);

  fetch("data/packages.json")
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((json) => { DB = json; route(); })
    .catch(() => {
      view.innerHTML = `<div class="empty pad"><b>Catalog failed to load.</b>
        <p>Try a hard refresh, or check <a href="https://github.com/amnottdevv/Atdork-DB">the repository</a>.</p></div>`;
    });
})();
