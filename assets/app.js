/* The Capital Map — viewer (engine shared with The Supply Map).  Data comes from data.js (window.MUDMAP), built by tools/build.py */
(function () {
  "use strict";

  const DATA = window.MUDMAP;
  if (!DATA) {
    document.body.innerHTML = '<p style="padding:40px;font-family:sans-serif">data.js is missing. Run <code>python3 tools/build.py</code>.</p>';
    return;
  }
  const P = DATA.pages;
  const ROOT = DATA.root;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------- Storage (per-viewer conveniences only) ---------- */
  const store = {
    get(k, d) { try { const v = localStorage.getItem("mudmap:" + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("mudmap:" + k, JSON.stringify(v)); } catch { /* ignore */ } },
  };

  /* ---------- Welcome guide: decided before anything else reads settings ----------
     Shown once, on a first visit that lands on the home page (never on a deep link to a page, flow, job or qualification).
     A brand-new visitor (nothing saved in this browser yet) also starts in Core depth; anyone with saved settings keeps them. */
  const freshVisitor = (() => { try { return !Object.keys(localStorage).some((k) => k.startsWith("mudmap:")); } catch { return false; } })();
  const landedHome = /^(#\/?(map\/?)?)?$/.test(location.hash);
  const welcomeOnLoad = landedHome && !store.get("welcomed", false);
  if (welcomeOnLoad && freshVisitor) store.set("mode", "simple");

  /* ---------- Branch colours ---------- */
  const HUES = { foundation: 215, "personal-capital": 20, money: 42, "fixed-income": 192, equities: 152, "real-assets": 88, "digital-assets": 268, derivatives: 338, portfolio: 300, markets: 172, measure: 240, practice: 120, "failure-modes": 0 };
  const branchIds = P[ROOT].children;
  const fallbackHues = [215, 268, 20, 152, 42, 192, 338, 240, 88, 0, 300];
  function hue(id) {
    const b = P[id] ? P[id].branch : id;
    if (b in HUES) return HUES[b];
    const i = branchIds.indexOf(b);
    return fallbackHues[(i < 0 ? 0 : i) % fallbackHues.length];
  }
  const col = (id, a = 1) => `hsl(${hue(id)} var(--s) var(--l) / ${a})`;

  /* ---------- Theme ---------- */
  function applyTheme(t) { if (t) document.documentElement.setAttribute("data-theme", t); else document.documentElement.removeAttribute("data-theme"); }
  applyTheme(store.get("theme", null));
  $("#theme-btn").addEventListener("click", () => {
    const dark = getComputedStyle(document.documentElement).getPropertyValue("--bg").trim() === "#15171a";
    const next = dark ? "light" : "dark";
    applyTheme(next); store.set("theme", next);
  });

  /* ---------- View depth: Everything / Core (advanced layer hidden). Stored as "normal" / "simple". ---------- */
  const mode = { simple: store.get("mode", "normal") === "simple" };
  const vis = (id) => !(mode.simple && P[id] && P[id].adv);
  const kidsOf = (id) => P[id].children.filter(vis);
  const flowVis = (f) => !(mode.simple && f.adv);
  const linkVis = (pageId, src) => {
    if (src.startsWith("flow:")) { const f = DATA.flows[src.slice(5)]; return f && flowVis(f) && !(mode.simple && (P[pageId].backlinksAdv || []).includes(src)); }
    return vis(src) && !(mode.simple && (P[pageId].backlinksAdv || []).includes(src));
  };
  /* ---------- Focus: highlight one job's (or qualification's) study path ---------- */
  const ROLES = DATA.jobs || {};          // jobs on the job ladder (kept as ROLES: they drive role focus)
  const LEVELS = DATA.levels || {};
  const STREAMS = DATA.streams || [];
  const QUALS = DATA.quals || {};
  const FOCUS = Object.assign({}, ROLES, QUALS);   // focus can be a job role or a qualification
  const isQual = (id) => !!QUALS[id];
  const roleIds = Object.keys(ROLES).sort((a, b) => ROLES[a].level - ROLES[b].level || ROLES[a].order - ROLES[b].order);
  const targets = new Set(store.get("targets", []).filter((id) => ROLES[id]));   // "my target" jobs: this browser only
  function setTarget(id, on) { if (on) targets.add(id); else targets.delete(id); store.set("targets", [...targets]); }
  const STREAM_HUE = { procurement: 20, warehouse: 152, planning: 268, maintenance: 42 };
  const jobCol = (id, a = 1) => { const s = ROLES[id] && ROLES[id].stream; return s in STREAM_HUE ? `hsl(${STREAM_HUE[s]} var(--s) var(--l) / ${a})` : `var(--accent)`; };
  const qualIds = Object.keys(QUALS).sort((a, b) => QUALS[a].order - QUALS[b].order);
  const role = { id: null, pages: new Set(), ctx: new Set() };
  function setRoleState(id) {
    role.id = FOCUS[id] ? id : null;
    role.pages = new Set(role.id ? FOCUS[role.id].pages : []);
    role.ctx = new Set();
    role.pages.forEach((pid) => P[pid].path.slice(0, -1).forEach((a) => role.ctx.add(a)));
  }
  setRoleState(store.get("role", null));
  const onRole = (id) => role.pages.has(id);
  const dimmed = (id) => !!role.id && !role.pages.has(id) && !role.ctx.has(id);
  const known = new Set(store.get("known", []));
  function setKnown(id, on) { if (on) known.add(id); else known.delete(id); store.set("known", [...known]); }

  function renderRoleSeg() {
    // All + the jobs marked as targets + the focused job (if it isn't a target)
    const ids = roleIds.filter((r) => targets.has(r) || r === role.id);
    $("#role-seg").innerHTML = `<button data-role="">All</button>` + ids.map((r) => `<button data-role="${r}">${targets.has(r) ? "★ " : ""}${esc(ROLES[r].short)}</button>`).join("");
  }
  function applyMode() {
    renderRoleSeg();
    document.body.classList.toggle("simple", mode.simple);
    document.body.classList.toggle("role-on", !!role.id);
    $$("[data-mode]").forEach((b) => b.classList.toggle("active", (b.dataset.mode === "simple") === mode.simple));
    const roleOn = role.id && !isQual(role.id) ? role.id : null, qualOn = role.id && isQual(role.id) ? role.id : null;
    $$("#role-seg [data-role]").forEach((b) => b.classList.toggle("active", (b.dataset.role || null) === roleOn));
    $$("#qual-seg [data-role]").forEach((b) => b.classList.toggle("active", (b.dataset.role || null) === qualOn));
    $("#settings-btn").classList.toggle("on", mode.simple || !!role.id);
    const chip = $("#focus-chip");
    chip.hidden = !role.id;
    if (role.id) {
      $("#focus-chip-label").textContent = FOCUS[role.id].short;
      const main = $("#focus-chip .fc-main");
      if (isQual(role.id)) { main.removeAttribute("data-path"); main.dataset.qual = role.id; main.title = "Qualification focus — open its modules"; }
      else { main.removeAttribute("data-qual"); main.dataset.path = role.id; main.title = "Job focus — open this job"; }
    }
  }
  function setRole(id) {
    setRoleState(id); store.set("role", role.id);
    if (role.id) {
      // open the map down to every visible page on the path
      expanded = new Set([ROOT]);
      role.pages.forEach((pid) => { if (vis(pid)) P[pid].path.slice(0, -1).forEach((a) => expanded.add(a)); });
      store.set("expanded", [...expanded]);
    }
    applyMode();
    lastView = null;
    render();
    if (parseHash().view === "map") requestAnimationFrame(() => fit());
  }
  function setMode(simple) {
    mode.simple = simple; store.set("mode", simple ? "simple" : "normal");
    applyMode();
    lastView = null;            // force views to rebuild
    render();
  }
  const settingsBtn = $("#settings-btn"), settingsMenu = $("#settings-menu");
  settingsBtn.addEventListener("click", (e) => { e.stopPropagation(); settingsMenu.hidden = !settingsMenu.hidden; });
  settingsMenu.addEventListener("click", (e) => {
    e.stopPropagation();
    const b = e.target.closest("[data-mode]"); if (b) setMode(b.dataset.mode === "simple");
    const r = e.target.closest("[data-role]"); if (r) setRole(r.dataset.role || null);
    if (e.target.closest(".sm-about, .sm-privacy")) settingsMenu.hidden = true;   // the link navigates itself; just close the menu
  });
  const mappedQuals = qualIds.filter((q) => QUALS[q].pages.length);   // planned placeholders can't be a focus
  $("#qual-seg").innerHTML = `<button data-role="">None</button>` + mappedQuals.map((q) => `<button data-role="${q}">${esc(QUALS[q].short)}</button>`).join("");
  if (!mappedQuals.length) $$(".sm-qual").forEach((el) => { el.hidden = true; });
  $("#focus-chip-clear").addEventListener("click", (e) => { e.stopPropagation(); setRole(null); });
  document.addEventListener("click", () => { settingsMenu.hidden = true; });

  /* ---------- Routing:  #/map  #/map/p/<id>  #/flows/<flow>/p/<id>  #/jobs/<job>  #/quals/<qual>  #/index  (old #/paths links still work) ---------- */
  function parseHash() {
    const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
    if (parts[0] === "paths") parts[0] = "jobs";
    const view = ["map", "flows", "jobs", "quals", "cartography", "index", "about", "privacy"].includes(parts[0]) ? parts[0] : "map";
    let flow = null, page = null, path = null, qual = null;
    const pi = parts.indexOf("p");
    if (pi >= 0 && parts[pi + 1] && P[parts[pi + 1]]) page = parts[pi + 1];
    if (view === "flows" && parts[1] && parts[1] !== "p" && DATA.flows[parts[1]]) flow = parts[1];
    if (view === "jobs" && parts[1] && parts[1] !== "p" && ROLES[parts[1]]) path = parts[1];
    if (view === "quals" && parts[1] && parts[1] !== "p" && QUALS[parts[1]]) qual = parts[1];
    return { view, flow, page, path, qual };
  }
  function go(next, replace) {
    const cur = parseHash();
    const s = Object.assign({}, cur, next);
    let h = "#/" + s.view;
    if (s.view === "flows" && s.flow) h += "/" + s.flow;
    if (s.view === "jobs" && s.path) h += "/" + s.path;
    if (s.view === "quals" && s.qual) h += "/" + s.qual;
    if (s.page) h += "/p/" + s.page;
    if (h === location.hash) { render(); return; }
    if (replace) history.replaceState(null, "", h); else location.hash = h;
    if (replace) render();
  }
  const openPage = (id) => go({ page: id });
  window.addEventListener("hashchange", render);

  /* Every navigation element gets a real address, so Ctrl/Cmd+click, middle-click, Shift+click
     and right-click "open in new tab" work like any website. A plain click stays in this tab. */
  const NAV_SEL = "[data-page],[data-flow],[data-view],[data-mapto],[data-path],[data-qual]";
  function hrefFor(d) {
    if (d.path !== undefined) return d.path ? `#/jobs/${d.path}` : "#/jobs";
    if (d.qual !== undefined) return d.qual ? `#/quals/${d.qual}` : "#/quals";
    if (d.mapto) return `#/map/p/${d.mapto}`;
    if (d.view) return `#/${d.view}`;
    if (d.flow) return `#/flows/${d.flow}` + (d.page ? `/p/${d.page}` : "");
    if (d.page) return `#/map/p/${d.page}`;
    return null;
  }
  const linkify = (root) => root.querySelectorAll && root.querySelectorAll("a").forEach((a) => {
    if (!a.hasAttribute("href") && a.matches(NAV_SEL)) { const h = hrefFor(a.dataset); if (h) a.setAttribute("href", h); }
  });
  linkify(document);
  new MutationObserver((ms) => ms.forEach((m) => m.addedNodes.forEach((n) => { if (n.nodeType === 1) { linkify(n); if (n.matches && n.matches("a")) linkify(n.parentNode); } })))
    .observe(document.body, { childList: true, subtree: true });
  const wantsNewTab = (e) => e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1;
  function openNew(el) { const h = hrefFor(el.dataset); if (h) window.open(location.href.split("#")[0] + h, "_blank", "noopener"); }
  // middle-click on elements that aren't links (tabs, focus chip): open in a new tab too
  document.addEventListener("auxclick", (e) => {
    if (e.button !== 1) return;
    const a = e.target.closest(NAV_SEL);
    if (!a || a.closest("#map-svg") || a.closest("#settings-menu") || a.matches("a[href]")) return;
    e.preventDefault(); openNew(a);
  });

  /* Delegated clicks for anything with data-page / data-flow / data-view */
  document.addEventListener("click", (e) => {
    const a = e.target.closest(NAV_SEL);
    if (!a || a.closest("#map-svg") || a.closest("#settings-menu")) return;
    if (wantsNewTab(e)) {
      if (a.matches("a[href]")) return;          // the browser opens the link in a new tab / window
      e.preventDefault(); openNew(a); return;    // buttons: do the same by hand
    }
    e.preventDefault();
    if (a.dataset.path !== undefined) { go({ view: "jobs", path: a.dataset.path || null, page: null }); return; }
    if (a.dataset.qual !== undefined) {
      pendingModule = a.dataset.module || null;
      go({ view: "quals", qual: a.dataset.qual || null, page: null }); return;
    }
    if (a.dataset.mapto) { go({ view: "map", page: a.dataset.mapto }); revealOnMap(a.dataset.mapto); return; }
    if (a.dataset.view === "map" && a.classList.contains("tab") && parseHash().view === "map") { goHome(); return; }
    if (a.dataset.view) { go({ view: a.dataset.view, flow: null, path: null, qual: null }); return; }
    if (a.dataset.flow) { go({ view: "flows", flow: a.dataset.flow, page: a.dataset.page || null }); return; }
    if (a.dataset.page) openPage(a.dataset.page);
  });

  let lastView = null, lastPage = null, homePending = false;
  function render() {
    const s = parseHash();
    $$(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === s.view));
    const aboutBtn = $("#about-btn");
    aboutBtn.classList.toggle("active", s.view === "about");
    if (s.view === "about") aboutBtn.setAttribute("aria-current", "page"); else aboutBtn.removeAttribute("aria-current");
    $$(".view").forEach((v) => v.classList.toggle("active", v.id === s.view + "-view"));
    if (s.view === "flows") renderFlows(s.flow);
    if (s.view === "jobs") renderJobs(s.path);
    if (s.view === "quals") renderQuals(s.qual);
    if (s.view === "cartography") renderCart();
    if (s.view === "index" && lastView !== "index") renderIndex();
    if (s.view === "about" && lastView !== "about") renderAbout();
    if (s.view === "privacy" && lastView !== "privacy") renderPrivacy();
    renderPanel(s.page);
    if (s.view === "map") {
      if (lastView !== "map") { requestAnimationFrame(() => { drawMap(); if (!mapFitted) { fit(false); mapFitted = true; } }); }
      if (s.page && s.page !== lastPage && vis(s.page)) revealOnMap(s.page);
      else drawMap();
    }
    if (homePending && s.view === "map") { homePending = false; requestAnimationFrame(() => { drawMap(); fit(); }); }
    lastView = s.view; lastPage = s.page;
  }

  /* =====================================================================
     MAP
     ===================================================================== */
  const svg = $("#map-svg"), gRoot = $("#map-root"), mapView = $("#map-view");
  // First visit only: open the P2P branch so the map isn't empty. "Collapse all" closes everything.
  const FIRST_VISIT_OPEN = [ROOT, "money"].filter((id) => P[id]);
  let expanded = new Set(store.get("expanded", FIRST_VISIT_OPEN));
  expanded.add(ROOT);
  let view = { x: 0, y: 0, k: 1 };
  let layout = { nodes: {}, bbox: null };
  let mapFitted = false;
  let hits = new Set();

  const canvas = document.createElement("canvas").getContext("2d");
  const FONT = getComputedStyle(document.body).fontFamily;
  const MONO = getComputedStyle(document.documentElement).getPropertyValue("--mono").trim() || "monospace";
  function measure(text, size, weight, family) { canvas.font = `${weight} ${size}px ${family || FONT}`; return canvas.measureText(text).width; }

  const MAXW = 250, GAPX = 64, GAPY = 9, BRANCH_GAP = 26, GROUP_GAP = 30, GROUP_LABEL_H = 26;
  const groupOf = (id) => (P[id] && P[id].group) || "";
  function nodeKind(id) { return id === ROOT ? "root" : P[id].parent === ROOT ? "branch" : "leaf"; }
  function label(id) { return P[id].short || P[id].title; }

  function fitText(text, size, weight, maxw) {
    if (measure(text, size, weight) <= maxw) return text;
    let t = text;
    while (t.length > 3 && measure(t + "…", size, weight) > maxw) t = t.slice(0, -1);
    return t.trimEnd() + "…";
  }

  function computeLayout() {
    const nodes = {};
    const depthMax = [];
    // pass 1: sizes
    (function size(id, d) {
      const k = nodeKind(id);
      const fs = k === "root" ? 17 : k === "branch" ? 15 : 13.5;
      const fw = k === "root" ? 800 : k === "branch" ? 700 : 600;
      const text = fitText(label(id), fs, fw, MAXW - 30);
      const sub = k === "leaf" && P[id].tcodes.length ? P[id].tcodes.slice(0, 3).join(" · ") : "";
      const subw = sub ? measure(sub, 11, 400, MONO) + 4 : 0;
      const w = Math.ceil(Math.max(measure(text, fs, fw), subw) + (k === "leaf" ? 30 : 34));
      const h = k === "root" ? 52 : k === "branch" ? 42 : sub ? 46 : 34;
      nodes[id] = { id, d, w, h, text, sub, kind: k };
      depthMax[d] = Math.max(depthMax[d] || 0, w);
      if (expanded.has(id)) kidsOf(id).forEach((c) => size(c, d + 1));
    })(ROOT, 0);
    // columns
    const colX = [0];
    for (let d = 1; d < depthMax.length; d++) colX[d] = colX[d - 1] + depthMax[d - 1] + GAPX;
    // pass 2: vertical placement
    let cursor = 0;
    const groups = [];   // top-level groups: a small heading above each cluster of branches
    (function place(id) {
      const n = nodes[id];
      n.x = colX[n.d];
      const kids = expanded.has(id) ? kidsOf(id) : [];
      if (!kids.length) { n.y = cursor + n.h / 2; cursor += n.h + GAPY; return; }
      kids.forEach((c, i) => {
        if (id === ROOT) {
          const g = groupOf(c), newGroup = g && (i === 0 || g !== groupOf(kids[i - 1]));
          if (i > 0) cursor += BRANCH_GAP + (newGroup ? GROUP_GAP : 0);
          if (newGroup) { groups.push({ text: g, y: cursor + 12 }); cursor += GROUP_LABEL_H; }
        }
        place(c);
      });
      const first = nodes[kids[0]], last = nodes[kids[kids.length - 1]];
      n.y = (first.y + last.y) / 2;
      // keep tall parents from overlapping the next sibling
      cursor = Math.max(cursor, n.y + n.h / 2 + GAPY);
    })(ROOT);
    groups.forEach((g) => { g.x = colX[1] || 0; });
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    Object.values(nodes).forEach((n) => {
      minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x + n.w + 24);
      minY = Math.min(minY, n.y - n.h / 2); maxY = Math.max(maxY, n.y + n.h / 2);
    });
    groups.forEach((g) => { minY = Math.min(minY, g.y - 12); });
    return { nodes, groups: expanded.has(ROOT) ? groups : [], bbox: { minX, minY, maxX, maxY } };
  }

  function drawMap() {
    const s = parseHash();
    layout = computeLayout();
    const N = layout.nodes;
    let links = "", out = "";
    Object.values(N).forEach((n) => {
      if (n.id === ROOT || !N[P[n.id].parent]) return;
      const p = N[P[n.id].parent];
      const x1 = p.x + p.w + (kidsOf(p.id).length ? 20 : 0), y1 = p.y, x2 = n.x, y2 = n.y, mx = (x1 + x2) / 2;
      links += `<path class="link-path${dimmed(n.id) ? " dim" : ""}" d="M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}" style="stroke:${col(n.id)}"/>`;
    });
    Object.values(N).forEach((n) => {
      const pg = P[n.id], k = n.kind;
      const cls = ["node", k, pg.stub && k === "leaf" ? "stub" : "", pg.adv ? "adv" : "", s.page === n.id ? "selected" : "", hits.has(n.id) ? "hit" : "", dimmed(n.id) ? "dim" : "", role.id && onRole(n.id) ? "focus" : ""].join(" ");
      const top = n.y - n.h / 2, r = k === "leaf" ? 8 : n.h / 2;
      let box;
      if (k === "root") box = `<rect class="node-box" x="${n.x}" y="${top}" width="${n.w}" height="${n.h}" rx="${r}" style="fill:var(--text);stroke:var(--text)"/>`;
      else if (k === "branch") box = `<rect class="node-box" x="${n.x}" y="${top}" width="${n.w}" height="${n.h}" rx="${r}" style="fill:${col(n.id)};stroke:${col(n.id)}"/>`;
      else box = `<rect class="node-box" x="${n.x}" y="${top}" width="${n.w}" height="${n.h}" rx="${r}" style="fill:var(--surface);stroke:${col(n.id, pg.stub ? 0.55 : 0.75)}"/>` +
        `<rect x="${n.x + 4}" y="${top + 7}" width="3.5" height="${n.h - 14}" rx="1.75" style="fill:${col(n.id, pg.stub ? 0.35 : 1)}"/>`;
      const tx = k === "leaf" ? n.x + 16 : n.x + 17;
      let txt;
      if (n.sub) txt = `<text class="node-label" x="${tx}" y="${n.y - 8}">${esc(n.text)}</text><text class="node-sub" x="${tx}" y="${n.y + 10}">${esc(n.sub)}</text>`;
      else txt = `<text class="node-label" x="${tx}" y="${n.y + 0.5}">${esc(n.text)}</text>`;
      let tog = "";
      const kids = kidsOf(n.id).length;
      if (kids) {
        const open = expanded.has(n.id), cx = n.x + n.w + 12;
        tog = `<g class="toggle" data-toggle="${n.id}"><title>${open ? "Collapse" : "Expand"} (${kids})</title>` +
          `<circle cx="${cx}" cy="${n.y}" r="${open ? 7 : 10}" style="fill:${open ? "var(--surface)" : col(n.id)};stroke:${col(n.id)}"/>` +
          `<text x="${cx}" y="${n.y + 0.5}" style="fill:${open ? col(n.id) : "var(--surface)"}">${open ? "−" : kids}</text></g>`;
      }
      const done = role.id && onRole(n.id) && known.has(n.id) && k === "leaf" ? `<path class="known-mark" d="M${n.x + n.w - 15} ${n.y + n.h / 2 - 9} l3 3 l6 -6" />` : "";
      const mark = pg.adv && k !== "root" ? `<path class="adv-mark" d="M${n.x + n.w - 9} ${top - 4} l5 5 l-5 5 l-5 -5 z" style="fill:${col(n.id)}"/>` : "";
      out += `<g class="${cls}" data-node="${n.id}"><title>${esc(pg.title + (pg.summary ? " — " + pg.summary : "") + (pg.adv ? " · advanced" : ""))}</title>${box}${txt}${mark}${done}</g>${tog}`;
    });
    const heads = layout.groups.map((g) => `<text class="group-label" x="${g.x + 2}" y="${g.y}" data-group="${esc(g.text)}">${esc(g.text)}</text>`).join("");
    gRoot.innerHTML = `<g>${links}</g><g class="group-labels">${heads}</g><g>${out}</g>`;
    applyView();
  }

  function applyView() { gRoot.setAttribute("transform", `translate(${view.x},${view.y}) scale(${view.k})`); }
  function mapSize() { const r = mapView.getBoundingClientRect(); return { w: r.width, h: r.height }; }

  function fit(animate = true) {
    const b = layout.bbox; if (!b) return;
    const { w, h } = mapSize(), pad = 50;
    const bw = b.maxX - b.minX, bh = b.maxY - b.minY, MINK = 0.62;
    const k = Math.max(MINK, Math.min(1.15, (w - pad * 2) / bw, (h - pad * 2 - 40) / bh));
    // centre if it fits, otherwise pin to the left / top edge so the root is visible
    const x = bw * k <= w - pad * 2 ? (w - bw * k) / 2 - b.minX * k : pad - b.minX * k;
    const rootY = layout.nodes[ROOT].y;
    const y = bh * k <= h - pad * 2 - 40 ? (h - 40 - bh * k) / 2 - b.minY * k : h / 2 - rootY * k;
    const target = { k, x, y };
    tween(target, animate);
  }
  function zoomBy(f, cx, cy) {
    const { w, h } = mapSize();
    cx = cx ?? w / 2; cy = cy ?? h / 2;
    const k = Math.max(0.2, Math.min(2.5, view.k * f));
    view.x = cx - (cx - view.x) * (k / view.k);
    view.y = cy - (cy - view.y) * (k / view.k);
    view.k = k; applyView();
  }
  let anim = null;
  function tween(target, animate) {
    cancelAnimationFrame(anim);
    if (!animate) { view = target; applyView(); return; }
    const from = { ...view }, t0 = performance.now(), dur = 380;
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      view = { x: from.x + (target.x - from.x) * e, y: from.y + (target.y - from.y) * e, k: from.k + (target.k - from.k) * e };
      applyView();
      if (p < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
  }
  function centerOn(id, animate = true) {
    const n = layout.nodes[id]; if (!n) return;
    const { w, h } = mapSize(), k = Math.max(view.k, 0.85);
    tween({ k, x: w / 2 - (n.x + n.w / 2) * k, y: h / 2 - n.y * k }, animate);
  }
  function revealOnMap(id) {
    if (!P[id]) return;
    P[id].path.slice(0, -1).forEach((a) => expanded.add(a));
    store.set("expanded", [...expanded]);
    drawMap();
    if (parseHash().view === "map") requestAnimationFrame(() => centerOn(id));
  }
  function toggle(id) {
    const before = layout.nodes[id];
    const sx = before.x * view.k + view.x, sy = before.y * view.k + view.y;
    if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
    store.set("expanded", [...expanded]);
    drawMap();
    const after = layout.nodes[id];
    view.x = sx - after.x * view.k; view.y = sy - after.y * view.k; applyView();
  }

  // pan / zoom / click handling
  const pointers = new Map();
  let drag = null, pinch = null;
  svg.addEventListener("pointerdown", (e) => {
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    svg.setPointerCapture(e.pointerId);
    if (pointers.size === 1) drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, moved: false, target: e.target };
    if (e.button === 1) e.preventDefault();      // no auto-scroll on middle-click over the map
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), k: view.k };
      drag = null;
    }
  });
  svg.addEventListener("pointermove", (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const r = svg.getBoundingClientRect();
      const f = (Math.hypot(a.x - b.x, a.y - b.y) / pinch.d) * pinch.k / view.k;
      zoomBy(f, (a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top);
      return;
    }
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.moved && Math.hypot(dx, dy) > 4) { drag.moved = true; mapView.classList.add("dragging"); }
    if (drag.moved) { view.x = drag.vx + dx; view.y = drag.vy + dy; applyView(); }
  });
  function endPointer(e) {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (drag && !drag.moved && e.type === "pointerup") {
      const t = drag.target;
      const tg = t.closest && t.closest("[data-toggle]");
      const nd = t.closest && t.closest("[data-node]");
      if (tg) toggle(tg.dataset.toggle);
      else if (nd && (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1)) openNew({ dataset: { page: nd.dataset.node } });
      else if (nd) openPage(nd.dataset.node);
    }
    drag = null; mapView.classList.remove("dragging");
  }
  svg.addEventListener("pointerup", endPointer);
  svg.addEventListener("pointercancel", endPointer);
  svg.addEventListener("wheel", (e) => {
    e.preventDefault();
    const r = svg.getBoundingClientRect();
    if (e.ctrlKey || Math.abs(e.deltaY) > Math.abs(e.deltaX) && !e.shiftKey && e.deltaMode === 0 && Math.abs(e.deltaY) >= 50) {
      zoomBy(Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)), e.clientX - r.left, e.clientY - r.top);
    } else {
      view.x -= e.deltaX; view.y -= e.deltaY; applyView();
    }
  }, { passive: false });
  svg.addEventListener("dblclick", (e) => { if (!e.target.closest("[data-node],[data-toggle]")) zoomBy(1.4, e.offsetX, e.offsetY); });

  $(".map-controls").addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    const act = b.dataset.act;
    if (act === "expand") { Object.keys(P).forEach((id) => { if (vis(id) && kidsOf(id).length) expanded.add(id); }); store.set("expanded", [...expanded]); drawMap(); fit(); }
    if (act === "collapse") { expanded = new Set([ROOT]); store.set("expanded", [...expanded]); drawMap(); fit(); }
    if (act === "zoomin") zoomBy(1.25);
    if (act === "zoomout") zoomBy(0.8);
    if (act === "fit") fit();
  });
  window.addEventListener("resize", () => { if (parseHash().view === "map") applyView(); });

  /* =====================================================================
     PAGE PANEL
     ===================================================================== */
  const panelBody = $("#panel-body");
  function pill(id) {
    if (id.startsWith("flow:")) {
      const f = DATA.flows[id.slice(5)];
      return `<a data-flow="${f.id}"><span class="dot" style="background:var(--accent)"></span>Flow · ${esc(f.title)}</a>`;
    }
    const p = P[id];
    return `<a data-page="${id}" class="${p.stub ? "stub" : ""}" title="${esc(p.summary)}"><span class="dot" style="background:${col(id)}"></span>${esc(p.title)}</a>`;
  }
  /* Cartography of Wealth: tier and killer, from page frontmatter (tier, killer, traits) */
  const TIERS = { 1: "Tier 1 · Inside you", 2: "Tier 2 · Private / bearer", 3: "Tier 3 · Legible / state-visible" };
  function cartPanel(p) {
    if (!p.tier && !p.killer) return "";
    const tiers = String(p.tier || "").split(/[^1-3]+/).filter(Boolean);
    const label = tiers.map((n) => TIERS[n]).join(" ↔ ");
    return `<div class="cart-note">
      ${label ? `<div class="cart-tier">${esc(label)}</div>` : ""}
      ${p.killer ? `<div><b>Killer:</b> ${esc(p.killer)}</div>` : ""}
      ${p.traits.length ? `<div class="chips">${p.traits.map((t) => `<span class="chip tag">${esc(t)}</span>`).join("")}</div>` : ""}
      <div class="cart-foot">Placement on the <a data-page="cartography-of-wealth">Cartography of Wealth</a> is a judgment, not measured data.</div>
    </div>`;
  }
  function renderPanel(id) {
    document.body.classList.toggle("panel-open", !!id);
    if (!id) return;
    const p = P[id];
    $("#crumbs").innerHTML = p.path.slice(0, -1).map((a) => `<a data-page="${a}">${esc(P[a].short || P[a].title)}</a>`).join('<span class="sepr">›</span>') || "&nbsp;";
    const chips = [
      ...p.tcodes.map((t) => `<span class="chip" title="T-code">${esc(t)}</span>`),
      ...p.fiori.map((t) => `<span class="chip fiori" title="Fiori app">Fiori · ${esc(t)}</span>`),
      ...p.tags.map((t) => `<span class="chip tag">${esc(t)}</span>`),
    ].join("");
    const branch = p.id === ROOT ? "" : P[p.branch].short || P[p.branch].title;
    panelBody.innerHTML = `
      ${branch ? `<div class="p-branch" style="color:${col(id)}">${esc(branch)}</div>` : ""}
      <h1 class="p-title">${esc(p.title)}</h1>
      ${p.summary ? `<p class="p-summary">${esc(p.summary)}</p>` : ""}
      ${chips ? `<div class="chips">${chips}</div>` : ""}
      ${cartPanel(p)}
      ${p.adv && mode.simple ? `<div class="stub-note adv-note"><b>Advanced page.</b> It's hidden from the map in Core view. <button class="linkish" data-setmode="normal">Switch to Everything</button> to see it in place.</div>` : ""}
      ${rolePanel(id)}
      ${qualPanel(p)}
      ${p.adv && !mode.simple ? `<div class="adv-pill">Advanced layer</div>` : ""}
      ${p.stub ? `<div class="stub-note"><b>Stub.</b> This page is a placeholder on the map. It gets written when the topic is studied.</div>` : ""}
      <div class="content">${p.html}${p.deep || ""}</div>
      ${kidsOf(id).length ? `<div class="p-section"><h4>Inside this topic</h4><div class="p-list">${kidsOf(id).map(pill).join("")}</div></div>` : ""}
      ${(() => { const bl = p.backlinks.filter((b) => linkVis(id, b)); return `<div class="p-section"><h4>What links here</h4><div class="p-list">${bl.length ? bl.map(pill).join("") : '<span class="none">Nothing links here yet.</span>'}</div></div>`; })()}
      <div class="panel-actions">
        ${vis(id) ? `<a class="btn" data-mapto="${id}">Show on map</a>` : ""}
      </div>
      ${p.sources.length ? `<div class="footer-note">Based on: ${p.sources.map(esc).join(" · ")}</div>` : ""}
      <div class="footer-note">File: pages/${esc(id)}.md</div>`;
    panelBody.scrollTop = 0;
    $$(".node.selected").forEach((n) => n.classList.remove("selected"));
    const el = $(`[data-node="${CSS.escape(id)}"]`); if (el) el.classList.add("selected");
  }
  const modCode = (m) => m.split(/\s+[—–-]\s+/)[0];
  function qualPanel(p) {
    if (!p.quals || !p.quals.length) return "";
    return `<div class="p-quals"><span class="pq-label">Qualifications</span>${p.quals.map((x) =>
      `<a class="chip qual" data-qual="${x.q}" data-module="${esc(x.m)}" title="${esc(QUALS[x.q].title + " · " + x.m)}">${esc(QUALS[x.q].short)} · ${esc(modCode(x.m))}</a>`).join("")}</div>`;
  }
  function rolePanel(id) {
    if (!role.id) return "";
    const r = FOCUS[role.id], q = isQual(role.id), word = q ? "qualification" : "path";
    const i = r.pages.indexOf(id);
    if (i < 0) return `<div class="role-bar off"><span>Not on the <b>${esc(r.short)}</b> ${word}</span></div>`;
    const prev = r.pages[i - 1], next = r.pages[i + 1];
    return `<div class="role-bar"><a class="rb-path" ${q ? `data-qual="${r.id}"` : `data-path="${r.id}"`} title="Open ${esc(r.title)}">${esc(r.short)} ${word} · ${i + 1} of ${r.pages.length}</a>
      <label class="rb-known"><input type="checkbox" data-known="${id}" ${known.has(id) ? "checked" : ""}> I know this</label>
      <span class="rb-nav">${prev ? `<a data-page="${prev}" title="${esc(P[prev].title)}">‹ Prev</a>` : ""}${next ? `<a data-page="${next}" title="${esc(P[next].title)}">Next ›</a>` : ""}</span></div>`;
  }
  $("#panel-close").addEventListener("click", () => go({ page: null }));
  panelBody.addEventListener("click", (e) => { const b = e.target.closest("[data-setmode]"); if (b) setMode(b.dataset.setmode === "simple"); });
  document.addEventListener("change", (e) => {
    const c = e.target.closest("[data-known]"); if (!c) return;
    setKnown(c.dataset.known, c.checked);
    $$(`[data-known="${CSS.escape(c.dataset.known)}"]`).forEach((x) => { x.checked = c.checked; });
    if (parseHash().view === "map") drawMap();
    updatePathProgress();
    if (parseHash().view === "jobs" && !c.closest("#panel")) { const sc = $("#jobs-view .scroll"), y = sc.scrollTop; rerenderJobs(); sc.scrollTop = y; }
    updateModuleCounts();
  });

  /* Resizable panel: drag the left edge. Min = default width, max = 2/3 of the window. */
  (function panelResize() {
    const handle = $("#panel-resize"), root = document.documentElement;
    const MIN = 540;
    const max = () => Math.max(MIN, Math.round(window.innerWidth * 2 / 3));
    const clamp = (w) => Math.min(max(), Math.max(MIN, Math.round(w)));
    const apply = (w) => { if (w) root.style.setProperty("--panel-custom", clamp(w) + "px"); else root.style.removeProperty("--panel-custom"); };
    apply(store.get("panelWidth", null));
    let dragging = false;
    handle.addEventListener("pointerdown", (e) => {
      dragging = true; handle.setPointerCapture(e.pointerId);
      document.body.classList.add("resizing"); e.preventDefault();
    });
    handle.addEventListener("pointermove", (e) => { if (dragging) apply(window.innerWidth - e.clientX); });
    const end = () => {
      if (!dragging) return;
      dragging = false; document.body.classList.remove("resizing");
      const w = parseInt(root.style.getPropertyValue("--panel-custom"), 10);
      store.set("panelWidth", w > MIN ? w : null);
      if (parseHash().view === "map") applyView();
    };
    handle.addEventListener("pointerup", end);
    handle.addEventListener("pointercancel", end);
    handle.addEventListener("dblclick", () => { apply(null); store.set("panelWidth", null); });
    window.addEventListener("resize", () => apply(store.get("panelWidth", null)));
  })();

  /* =====================================================================
     FLOWS
     ===================================================================== */
  function cellHtml(v) {
    const t = (v || "").trim();
    if (!t || /^(—|-|none|no)$/i.test(t)) return `<span class="none">${t ? esc(t) : "—"}</span>`;
    return esc(t).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }
  function renderFlows(fid) {
    const body = $("#flows-body");
    if (!fid) {
      const flows = Object.values(DATA.flows).filter(flowVis).sort((a, b) => a.order - b.order);
      const areas = [];
      flows.forEach((f) => { const a = f.area || "Other"; let g = areas.find((x) => x.name === a); if (!g) areas.push(g = { name: a, items: [] }); g.items.push(f); });
      body.innerHTML = `<h1 class="view-title">Flows</h1><p class="view-sub">Processes in the order they happen. Each step opens its page.</p>` +
        areas.map((g) => `<h2 class="section flow-area">${esc(g.name)}</h2><div class="flow-cards">${g.items.map((f) =>
          `<a class="flow-card${f.adv ? " adv" : ""}" data-flow="${f.id}"><h3>${esc(f.title)}</h3><p>${esc(f.summary)}</p><div class="meta">${f.steps.length} steps</div></a>`).join("")}</div>`).join("");
      return;
    }
    const f = DATA.flows[fid], n = f.steps.length;
    let grid = `<div class="lane-label head"></div>` + f.steps.map((s, i) => `<div class="step-head${i === n - 1 ? " last" : ""}">
        ${s.page && vis(s.page)
          ? `<a class="step-card linked" data-flow="${fid}" data-page="${s.page}" style="border-top:3px solid ${col(s.page)}">`
          : `<button class="step-card${s.page ? " linked" : ""}" disabled>`}
          <div class="n">STEP ${i + 1}</div><div class="t">${esc(s.label)}</div>${s.page && vis(s.page) ? "</a>" : "</button>"}</div>`).join("");
    f.lanes.forEach((lbl, li) => {
      const mono = /t-?code/i.test(lbl);
      grid += `<div class="lane-label">${esc(lbl)}</div>` + f.steps.map((s) => `<div class="cell ${mono ? "mono" : ""}">${cellHtml(s.cells[li])}</div>`).join("");
    });
    body.innerHTML = `<button class="back" data-view="flows">← All flows</button>
      <h1 class="view-title">${esc(f.title)}</h1>
      <div class="flow-intro content">${f.intro}</div>
      <div class="lanes-hint" hidden>Scroll sideways for more steps →</div>
      <div class="lanes-wrap"><div class="lanes"><div class="lane-grid" style="grid-template-columns: 130px repeat(${n}, auto)">${grid}</div></div></div>
      <div class="flow-intro content">${f.outro}</div>`;
    const lanesEl = $(".lanes", body), wrap = $(".lanes-wrap", body), hint = $(".lanes-hint", body);
    const update = () => {
      const more = lanesEl.scrollWidth > lanesEl.clientWidth + 4;
      const atEnd = lanesEl.scrollLeft + lanesEl.clientWidth >= lanesEl.scrollWidth - 4;
      hint.hidden = !more;
      wrap.classList.toggle("fade", more && !atEnd);
    };
    lanesEl.addEventListener("scroll", update, { passive: true });
    requestAnimationFrame(update);
  }

  /* =====================================================================
     JOBS (job ladder and study paths)
     ===================================================================== */
  function pathStats(r) {
    const items = FOCUS[r].pages.filter(vis);
    return { total: items.length, done: items.filter((x) => known.has(x)).length };
  }
  function bar(st) { const pct = st.total ? Math.round(st.done / st.total * 100) : 0; return `<div class="progress"><i style="width:${pct}%"></i></div><div class="progress-txt">${st.done} of ${st.total} known · ${pct}%</div>`; }
  function updatePathProgress() {
    $$("[data-progress]").forEach((el) => { el.innerHTML = bar(pathStats(el.dataset.progress)); });
  }
  /* ---------- Jobs: the job ladder as a chart, and one page per job ---------- */
  let lastJobShown = undefined;
  const jobLevel = (id) => `L${ROLES[id].level} · ${LEVELS[ROLES[id].level] || ""}`;
  const pct = (st) => (st.total ? Math.round(st.done / st.total * 100) : 0);
  function jobCard(id) {
    const j = ROLES[id], st = pathStats(id), from = j.alsoFrom && ROLES[j.alsoFrom];
    return `<a class="job-card${role.id === id ? " current" : ""}${targets.has(id) ? " target" : ""}" data-path="${id}" style="--jc:${jobCol(id)}">
      <span class="jc-level">${esc(jobLevel(id))}${targets.has(id) ? '<b class="jc-star" title="My target">★</b>' : ""}</span>
      <span class="jc-title">${esc(j.title)}</span>
      <span class="jc-sum">${esc(j.summary)}</span>
      ${from ? `<span class="jc-from">Also a common move from ${esc(from.short)}</span>` : ""}
      <span class="jc-foot"><span class="jc-prog"><i style="width:${pct(st)}%"></i></span>${st.done}/${st.total}</span>
    </a>`;
  }
  function jobStream() {
    const pref = store.get("jobStream", null);
    if (STREAMS.some((s) => s.id === pref)) return pref;
    const t0 = [...targets][0] || (ROLES[role.id] ? role.id : null);
    return t0 && ROLES[t0].stream !== "all" ? ROLES[t0].stream : STREAMS[0].id;
  }
  function renderJobChart(body) {
    const levels = Object.keys(LEVELS).map(Number).sort((a, b) => b - a);
    const at = (lvl, stream) => roleIds.filter((id) => ROLES[id].level === lvl && ROLES[id].stream === stream);
    let rows = "";
    levels.forEach((lvl) => {
      const label = `<div class="jl"><b>L${lvl}</b><small>${esc(LEVELS[lvl])}</small></div>`;
      const all = at(lvl, "all");
      if (all.length) { rows += label + `<div class="jcell jspan" data-stream="all">${all.map(jobCard).join("")}</div>`; }
      else {
        rows += label + STREAMS.map((s) => {
          const ids = at(lvl, s.id);
          if (ids.length) return `<div class="jcell" data-stream="${s.id}">${ids.map(jobCard).join("")}</div>`;
          const passes = roleIds.some((id) => ROLES[id].stream === s.id && ROLES[id].level < lvl && ROLES[ROLES[id].next] && ROLES[ROLES[id].next].level > lvl);
          return `<div class="jcell jempty${passes ? " pass" : ""}" data-stream="${s.id}" style="--jc:hsl(${STREAM_HUE[s.id]} var(--s) var(--l))">${passes ? "<span>No desk job at this level</span>" : ""}</div>`;
        }).join("");
      }
      if (lvl === 6) rows += `<div class="jl jl-head"></div>` + STREAMS.map((s) => `<div class="jhead" data-stream="${s.id}" style="--jc:hsl(${STREAM_HUE[s.id]} var(--s) var(--l))">${esc(s.title)}</div>`).join("");
    });
    const stream = jobStream();
    const tlist = [...targets].filter((id) => ROLES[id]);
    body.innerHTML = `<h1 class="view-title">Jobs</h1>
      <p class="view-sub">Every job on one chart, by level and stream — entry level at the bottom. Pick a job to see what it does, what's new at that level, and its learning path in priority order. Ticks and targets are saved in this browser only.</p>
      ${tlist.length ? `<div class="job-targets"><span class="pq-label">My targets</span>${tlist.map((id) => `<a class="chip qual" data-path="${id}">★ ${esc(ROLES[id].title)}</a>`).join("")}</div>` : ""}
      <div class="seg job-streams" role="tablist" aria-label="Stream">${STREAMS.map((s) => `<button data-stream-pick="${s.id}" class="${s.id === stream ? "active" : ""}">${esc(s.title.split(" ")[0])}</button>`).join("")}</div>
      <div class="job-grid" data-stream="${stream}">${rows}</div>`;
  }
  function renderJobs(rid) {
    const body = $("#jobs-body"), scroller = body.parentElement;
    if (!rid) {
      renderJobChart(body);
      if (lastJobShown !== null) scroller.scrollTop = 0;
      lastJobShown = null;
      return;
    }
    const r = ROLES[rid], newOnly = store.get("newOnly", false);
    const name = (id) => `<a class="job-mini" data-path="${id}" style="--jc:${jobCol(id)}"><small>${esc(jobLevel(id))}</small>${esc(ROLES[id].title)}</a>`;
    const streamName = r.stream === "all" ? "All streams" : (STREAMS.find((s) => s.id === r.stream) || {}).title || "";
    const order = r.stages.flatMap((s) => s.items).filter((it) => vis(it.page) && !(newOnly && it.from));
    const next = order.find((it) => !known.has(it.page));
    let n = 0;
    const stages = r.stages.map((s) => {
      const shown = s.items.filter((it) => !(newOnly && it.from));
      const ids = shown.map((it) => it.page).filter(vis), done = ids.filter((x) => known.has(x)).length;
      const items = shown.map((it) => {
        const pg = P[it.page], hidden = !vis(it.page);
        n += 1;
        return `<li class="path-item${hidden ? " hidden-adv" : ""}${known.has(it.page) ? " is-known" : ""}">
          <input type="checkbox" data-known="${it.page}" ${known.has(it.page) ? "checked" : ""} aria-label="I know ${esc(pg.title)}">
          <span class="pi-n">${n}</span>
          <a data-page="${it.page}" class="pi-title"><span class="dot" style="background:${col(it.page)}"></span>${esc(pg.title)}${pg.adv ? ' <span class="adv-tag">◆ Everything view</span>' : ""}</a>
          <span class="pi-note${it.note ? "" : " muted"}">${it.from ? `<span class="from-tag" title="Also on the ${esc(ROLES[it.from].title)} path">from L${ROLES[it.from].level} ${esc(ROLES[it.from].short)}</span> ` : ""}${it.note || esc(pg.summary)}</span>
        </li>`;
      }).join("");
      const [badge, ...rest] = s.title.split(/\s+[—–-]\s+/);
      return shown.length ? `<h2 class="section tier-head tier-${s.tier}"><span class="tier-badge">${esc(badge)}</span>${esc(rest.join(" — "))}<span class="mod-count">${done} of ${ids.length} known</span></h2><ol class="path-list">${items}</ol>` : "";
    }).join("");
    const ladder = [
      r.next ? `<div class="jl-row"><span class="jl-k">Next step up</span>${name(r.next)}</div>` : `<div class="jl-row"><span class="jl-k">Next step up</span><span class="muted">Top of the ladder</span></div>`,
      r.below.length ? `<div class="jl-row"><span class="jl-k">Comes after</span>${r.below.map(name).join("")}</div>` : `<div class="jl-row"><span class="jl-k">Comes after</span><span class="muted">Entry level — no experience needed in this stream</span></div>`,
      r.alsoFrom ? `<div class="jl-row"><span class="jl-k">Also a common move from</span>${name(r.alsoFrom)}</div>` : "",
    ].join("");
    body.innerHTML = `<a class="back" data-path="">← All jobs</a>
      <div class="p-branch" style="color:${jobCol(rid)}">${esc(jobLevel(rid))} · ${esc(streamName)}</div>
      <h1 class="view-title">${esc(r.title)}</h1>
      <p class="p-summary">${esc(r.summary)}</p>
      ${r.aliases.length ? `<p class="job-aliases"><b>Also advertised as:</b> ${r.aliases.map(esc).join(" · ")}</p>` : ""}
      <div class="job-ladder">${ladder}</div>
      <div class="path-actions">
        <button class="btn${targets.has(rid) ? " on" : ""}" data-target="${rid}" aria-pressed="${targets.has(rid)}">${targets.has(rid) ? "★ My target" : "☆ Mark as my target"}</button>
        ${role.id === rid ? `<span class="btn ghost">Map focused on this job</span>` : `<button class="btn" data-setrole="${rid}">Focus the map on this job</button>`}
      </div>
      <div class="content path-intro">${r.intro}</div>
      ${r.quals.length ? `<div class="p-quals"><span class="pq-label">Qualifications</span>${r.quals.filter((q) => QUALS[q]).map((q) => `<a class="chip qual" data-qual="${q}" title="${esc(QUALS[q].title)}">${esc(QUALS[q].short)}</a>`).join("")}</div>` : ""}
      <h2 class="section">Learning path</h2>
      <p class="view-sub">In priority order: finish Critical before High, High before Medium. Pages marked <span class="from-tag">from L…</span> are also on a lower job's path, so moving up a level means learning only the rest.</p>
      <div class="path-actions">
        ${next ? `<a class="btn primary" data-page="${next.page}">${order.some((it) => known.has(it.page)) ? "Continue" : "Start here"}: ${esc(P[next.page].title)} →</a>` : `<span class="btn ghost">✓ Everything on this path is ticked</span>`}
        <label class="newonly"><input type="checkbox" data-newonly ${newOnly ? "checked" : ""}> Only what's new at this level</label>
        <div class="path-progress" data-progress="${rid}">${bar(pathStats(rid))}</div>
      </div>
      ${stages || '<p class="muted">Nothing new at this level — everything here is covered by the jobs below it. Untick "only what\'s new" to see the full path.</p>'}`;
    if (lastJobShown !== rid) scroller.scrollTop = 0;
    lastJobShown = rid;
  }
  const rerenderJobs = () => { if (parseHash().view === "jobs") renderJobs(parseHash().path); };
  $("#jobs-body").addEventListener("click", (e) => {
    const s = e.target.closest("[data-stream-pick]");
    if (s) { store.set("jobStream", s.dataset.streamPick); rerenderJobs(); return; }
    const b = e.target.closest("[data-target]");
    if (b) { setTarget(b.dataset.target, !targets.has(b.dataset.target)); applyMode(); rerenderJobs(); }
  });
  $("#jobs-body").addEventListener("change", (e) => {
    if (e.target.matches("[data-newonly]")) { store.set("newOnly", e.target.checked); rerenderJobs(); }
  });
  ["#jobs-body", "#quals-body"].forEach((sel) => $(sel).addEventListener("click", (e) => {
    const b = e.target.closest("[data-setrole]"); if (!b) return;
    setRole(b.dataset.setrole); go({ view: "map", path: null, qual: null, page: null });
  }));

  /* =====================================================================
     QUALS (qualifications: modules mapped to pages)
     ===================================================================== */
  let pendingModule = null, lastQualShown = null;
  const mappedCount = (q) => QUALS[q].stages.filter((s) => s.items.length).length;
  function qualMeta(q) {
    const r = QUALS[q];
    if (r.status === "planned") return `<div class="meta">${r.stages.length} modules · not mapped yet</div>`;
    return `<div class="meta">${r.stages.length} modules · ${mappedCount(q)} mapped · ${r.pages.length} pages</div><div class="meta" data-progress="${q}">${bar(pathStats(q))}</div>`;
  }
  const modId = (q, i) => `mod-${q}-${i}`;
  function renderQuals(qid) {
    const body = $("#quals-body");
    if (!qid) {
      body.innerHTML = `<h1 class="view-title">Qualifications</h1>
        <p class="view-sub">Each qualification's modules, mapped to the pages that cover them — so a topic from the course can be seen in place in the system. Placeholders list every module now and are mapped as the branches are written. Ticks are saved in this browser only.</p>
        <div class="flow-cards">${qualIds.map((q) => `<a class="flow-card path-card${role.id === q ? " current" : ""}" data-qual="${q}">
          <h3>${esc(QUALS[q].title)}${QUALS[q].status === "planned" ? ' <span class="planned-tag">Planned</span>' : ""}</h3><p>${esc(QUALS[q].summary)}</p>${qualMeta(q)}</a>`).join("")}</div>`;
      lastQualShown = null;
      return;
    }
    const r = QUALS[qid];
    const jump = r.stages.map((s, i) => `<button class="mod-jump" data-jump="${modId(qid, i)}" title="${esc(s.title)}">${esc(modCode(s.title))}</button>`).join("");
    const mods = r.stages.map((s, si) => {
      const ids = s.items.map((it) => it.page).filter(vis);
      const done = ids.filter((x) => known.has(x)).length;
      const items = s.items.map((it, n) => {
        const pg = P[it.page], hidden = !vis(it.page);
        return `<li class="path-item${hidden ? " hidden-adv" : ""}${known.has(it.page) ? " is-known" : ""}">
          <input type="checkbox" data-known="${it.page}" ${known.has(it.page) ? "checked" : ""} aria-label="I know ${esc(pg.title)}">
          <span class="pi-n">${n + 1}</span>
          <a data-page="${it.page}" class="pi-title"><span class="dot" style="background:${col(it.page)}"></span>${esc(pg.title)}${pg.adv ? ' <span class="adv-tag">◆ Everything view</span>' : ""}</a>
          ${it.note ? `<span class="pi-note">${it.note}</span>` : `<span class="pi-note muted">${esc(pg.summary)}</span>`}
        </li>`;
      }).join("");
      const note = s.note ? `<p class="mod-note">${s.note}</p>` : "";
      const outOfScope = /outside this site.s scope/i.test(s.note);
      if (!s.items.length) return `<h2 class="section mod-head mod-empty" id="${modId(qid, si)}">${esc(s.title)}<span class="mod-count">${outOfScope ? "Out of scope" : "Not mapped yet"}</span></h2>${note || '<p class="mod-note">No pages are mapped to this module yet.</p>'}`;
      return `<h2 class="section mod-head" id="${modId(qid, si)}">${esc(s.title)}<span class="mod-count" data-modcount="${qid}:${si}">${done} of ${ids.length} known</span></h2>${note}<ol class="path-list">${items}</ol>`;
    }).join("");
    body.innerHTML = `<a class="back" data-qual="">← All qualifications</a>
      <h1 class="view-title">${esc(r.title)}${r.status === "planned" ? ' <span class="planned-tag">Planned</span>' : ""}</h1>
      <div class="content path-intro">${r.intro}</div>
      ${r.pages.length ? `<div class="path-actions">
        ${role.id === qid ? `<span class="btn ghost">Map focused on this qualification</span>` : `<button class="btn" data-setrole="${qid}">Focus the map on this qualification</button>`}
        <div class="path-progress" data-progress="${qid}">${bar(pathStats(qid))}</div>
      </div>` : `<p class="mod-note">A placeholder: the modules are listed so the whole syllabus is visible, and pages are mapped as the matching branches are written.</p>`}
      <div class="mod-jumps" aria-label="Jump to module">${jump}</div>
      ${mods}`;
    if (pendingModule) {
      const i = r.stages.findIndex((s) => s.title === pendingModule);
      pendingModule = null;
      if (i >= 0) requestAnimationFrame(() => { const el = document.getElementById(modId(qid, i)); if (el) el.scrollIntoView({ block: "start" }); });
    } else if (qid !== lastQualShown) body.parentElement.scrollTop = 0;
    lastQualShown = qid;
  }
  $("#quals-body").addEventListener("click", (e) => {
    const b = e.target.closest("[data-jump]"); if (!b) return;
    const el = document.getElementById(b.dataset.jump); if (el) el.scrollIntoView({ block: "start", behavior: "smooth" });
  });
  function updateModuleCounts() {
    $$("[data-modcount]").forEach((el) => {
      const [q, si] = el.dataset.modcount.split(":");
      const ids = QUALS[q].stages[+si].items.map((it) => it.page).filter(vis);
      el.textContent = `${ids.filter((x) => known.has(x)).length} of ${ids.length} known`;
    });
  }

  /* =====================================================================
     CARTOGRAPHY OF WEALTH: stores plotted by how embodied and how visible they are
     Data: page frontmatter place (x inside->outside, y hidden->recorded, 0-100), span, tier, killer, killer_kind
     ===================================================================== */
  const CART_TIER_HUE = { 1: 28, 2: 152, 3: 215 };
  let cartTier = "", cartKind = "";
  const tiersOf = (p) => String(p.tier).split(/[^1-3]+/).filter(Boolean);
  const cartOn = (p) => (!cartTier || tiersOf(p).includes(cartTier)) && (!cartKind || p.killerKind === cartKind);
  function renderCart() {
    const stores = Object.values(P).filter((p) => p.place && vis(p.id)).sort((a, b) => a.place[0] + a.place[1] - b.place[0] - b.place[1]);
    const kinds = [...new Set(stores.map((p) => p.killerKind))].sort();
    const W = 1000, H = 660, L = 70, R = 980, T = 30, B = 600;
    const X = (v) => L + (v / 100) * (R - L), Y = (v) => T + (v / 100) * (B - T);
    const hueOf = (p) => CART_TIER_HUE[tiersOf(p).slice(-1)[0]];
    const quad = (x, y, w, h, hue, label, anchor) => `<rect x="${X(x)}" y="${Y(y)}" width="${X(x + w) - X(x)}" height="${Y(y + h) - Y(y)}" class="cq" style="fill:${hue === null ? "var(--surface-2)" : `hsl(${hue} 45% 50% / .09)`}"/>` +
      `<text class="cq-label" x="${anchor === "end" ? X(x + w) - 12 : X(x) + 12}" y="${Y(y) + 22}" text-anchor="${anchor}">${label}</text>`;
    let svg = quad(0, 0, 50, 50, 28, "Safe from seizure and theft — but dies with you", "start") +
      quad(50, 0, 50, 50, 152, "Beyond the state's reach — exposed to theft and error", "end") +
      quad(0, 50, 50, 50, null, "Nearly empty: little is both inside you and on the record", "start") +
      quad(50, 50, 50, 50, 215, "Protected by the state — therefore exposed to it", "end");
    svg += `<line class="c-diag" x1="${X(4)}" y1="${Y(4)}" x2="${X(97)}" y2="${Y(97)}"/>`;
    svg += `<text class="c-axis" x="${L}" y="${H - 22}">← Inside you</text><text class="c-axis" x="${R}" y="${H - 22}" text-anchor="end">Outside you →</text>`;
    svg += `<text class="c-axis" transform="translate(30 ${T}) rotate(-90)" text-anchor="end">Hidden ↑</text><text class="c-axis" transform="translate(30 ${B}) rotate(-90)">↓ Recorded by authority</text>`;
    stores.forEach((p) => {
      const cx = X(p.place[0]), cy = Y(p.place[1]), c = `hsl(${hueOf(p)} 55% 42%)`, right = p.place[0] < 75;
      const span = p.span ? `<line class="c-span" x1="${cx}" y1="${Y(p.span[0])}" x2="${cx}" y2="${Y(p.span[1])}" style="stroke:${c}"/>` : "";
      svg += `<a class="cart-pt${cartOn(p) ? "" : " off"}" data-page="${p.id}" aria-label="${esc(p.title)}">${span}<title>${esc(p.title + " — killer: " + p.killer)}</title>` +
        `<circle cx="${cx}" cy="${cy}" r="11" style="fill:${c}"/>` +
        `<text class="c-pt-label" x="${right ? cx + 18 : cx - 18}" y="${cy}" text-anchor="${right ? "start" : "end"}">${esc(p.short || p.title)}</text></a>`;
    });
    const chip = (attr, val, cur, label) => `<button class="chip-btn${cur === val ? " on" : ""}" data-${attr}="${esc(val)}">${esc(label)}</button>`;
    const rows = stores.map((p) => `<tr class="${cartOn(p) ? "" : "off"}"><td><span class="dot" style="background:hsl(${hueOf(p)} 55% 42%)"></span><a data-page="${p.id}">${esc(p.title)}</a></td>` +
      `<td>${esc(tiersOf(p).join("–"))}</td><td>${esc(p.killer)}</td><td>${esc(p.killerKind)}</td></tr>`).join("");
    $("#cartography-body").innerHTML = `<h1 class="view-title">Cartography of Wealth</h1>
      <p class="view-sub">Stores of wealth placed by how embodied in you they are and how visible to the state, each with the one thing most likely to kill it. Positions are judgments, not measured data. The model is explained on <a data-page="cartography-of-wealth">The Cartography of Wealth</a>.</p>
      <div class="cart-filters" role="group" aria-label="Filter by tier">${chip("ctier", "", cartTier, "All tiers")}${[1, 2, 3].map((n) => chip("ctier", String(n), cartTier, ["", "Tier 1 · Inside you", "Tier 2 · Private / bearer", "Tier 3 · Legible"][n])).join("")}</div>
      <div class="cart-filters" role="group" aria-label="Filter by kind of killer">${chip("ckind", "", cartKind, "All killers")}${kinds.map((k) => chip("ckind", k, cartKind, k)).join("")}</div>
      <div class="cart-chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Chart of stores of wealth">${svg}</svg></div>
      <div class="tablewrap"><table class="cart-table"><thead><tr><th>Store</th><th>Tier</th><th>Killer</th><th>Kind of killer</th></tr></thead><tbody>${rows}</tbody></table></div>
      <p class="mod-note">Click any store to open its page. The enemy is correlation, not risk: spread across the chart so no single killer clears the board.</p>`;
  }
  $("#cartography-body").addEventListener("click", (e) => {
    const t = e.target.closest("[data-ctier]"), k = e.target.closest("[data-ckind]");
    if (t) { cartTier = t.dataset.ctier; renderCart(); }
    if (k) { cartKind = k.dataset.ckind; renderCart(); }
  });

  /* =====================================================================
     ABOUT (from about.md, with live counts)
     ===================================================================== */
  function renderAbout() {
    const A = DATA.about, body = $("#about-body");
    if (!A) { body.innerHTML = `<h1 class="view-title">About</h1><p class="view-sub">No about.md in this build.</p>`; return; }
    const all = Object.values(P), core = all.filter((p) => !p.adv).length;
    const stats = [
      [all.length, "pages", `${core} core · ${all.length - core} advanced`],
      [Object.keys(DATA.flows).length, "flows", "processes end to end"],
      // Jobs are hidden while there are none; show the Cartography stores instead
      Object.keys(ROLES).length ? [Object.keys(ROLES).length, "jobs", `${Object.keys(LEVELS).length} levels · ${STREAMS.length} streams`]
        : [all.filter((p) => p.place).length, "stores of wealth", "plotted on the Cartography chart"],
      [Object.keys(QUALS).length, "qualifications", qualIds.map((q) => QUALS[q].short).join(" · ")],
    ];
    body.innerHTML = `<h1 class="view-title">${esc(A.title)}</h1>
      <div class="about-stats">${stats.map(([n, k, s]) => `<div class="about-stat"><b>${n}</b><span>${esc(k)}</span><small>${esc(s)}</small></div>`).join("")}</div>
      <div class="content about-body">${A.html}</div>
      <p class="wc-reopen"><button class="btn" id="wc-reopen" type="button">Show the welcome guide</button></p>
      <p class="footer-note">Built ${esc(DATA.built)} · edit <code>about.md</code> to change this page.</p>`;
    body.parentElement.scrollTop = 0;
  }

  /* ---------- PRIVACY (from privacy.md) ---------- */
  function renderPrivacy() {
    const A = DATA.privacy, body = $("#privacy-body");
    body.innerHTML = A
      ? `<h1 class="view-title">${esc(A.title)}</h1><div class="content about-body">${A.html}</div>
         <p class="footer-note"><a data-view="about" class="about-link">About this site</a></p>`
      : `<h1 class="view-title">Privacy</h1><p class="view-sub">No privacy.md in this build.</p>`;
    body.parentElement.scrollTop = 0;
  }

  /* =====================================================================
     INDEX
     ===================================================================== */
  function renderIndex() {
    const all = Object.values(P).filter((p) => vis(p.id)), written = all.filter((p) => !p.stub).length;
    const advCount = all.filter((p) => p.adv).length;
    let groups = "";
    branchIds.filter(vis).forEach((b, i, arr) => {
      if (groupOf(b) && (i === 0 || groupOf(b) !== groupOf(arr[i - 1]))) groups += `<h2 class="index-grouphead">${esc(groupOf(b))}</h2>`;
      const items = [];
      (function walk(id, d) { items.push([id, d]); kidsOf(id).forEach((c) => walk(c, d + 1)); })(b, 0);
      groups += `<div class="index-group"><h3><i style="background:${col(b)}"></i><a data-page="${b}">${esc(P[b].short || P[b].title)}</a></h3>` +
        items.slice(1).map(([id, d]) => `<a data-page="${id}" class="${P[id].stub ? "stub" : ""}${P[id].adv ? " adv" : ""}${dimmed(id) ? " dim" : ""}${role.id && onRole(id) ? " focus" : ""}" style="padding-left:${(d - 1) * 14}px">${esc(P[id].title)}${P[id].tcodes.length ? `<span class="tc">${esc(P[id].tcodes.slice(0, 2).join(", "))}</span>` : ""}</a>`).join("") + `</div>`;
    });
    const tmap = {};
    all.forEach((p) => p.tcodes.forEach((t) => (tmap[t] = tmap[t] || []).push(p.id)));
    const trows = Object.keys(tmap).sort().map((t) => `<tr><td>${esc(t)}</td><td>${tmap[t].map((id) => `<a data-page="${id}">${esc(P[id].title)}</a>`).join(", ")}</td></tr>`).join("");
    $("#index-body").innerHTML = `<h1 class="view-title">Index</h1>
      <p class="view-sub"><a data-view="about" class="about-link">About this site</a> · <a data-view="privacy" class="about-link">Privacy</a> · ${mode.simple ? "Core view · " : ""}${role.id ? `Focus: ${esc(FOCUS[role.id].short)} (${FOCUS[role.id].pages.length} pages highlighted) · ` : ""}${all.length} pages${advCount ? ` (${advCount} advanced)` : ""} · ${all.length - written ? `${written} written · ${all.length - written} stubs` : "all written"} · built ${esc(DATA.built)}</p>
      <div class="index-grid">${groups}</div>
      ${trows ? `<h2 class="section">T-code index</h2>
      <table class="tcode-table"><thead><tr><th>T-code</th><th>Pages</th></tr></thead><tbody>${trows}</tbody></table>` : ""}`;
  }

  /* =====================================================================
     SEARCH
     ===================================================================== */
  const input = $("#search"), results = $("#results");
  let sel = 0, found = [];
  function search(q) {
    q = q.trim().toLowerCase(); if (!q) return [];
    const terms = q.split(/\s+/);
    // short terms (≤3 letters, e.g. "RMA", "ASN") match only at the start of a word,
    // so they don't hit the middle of longer words ("performance")
    const rx = (t) => new RegExp("(^|[^a-z0-9])" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const matcher = (t) => { if (t.length > 3) return (s) => s.includes(t); const r = rx(t); return (s) => r.test(s); };
    const qHas = matcher(q), termHas = terms.map(matcher);
    // page text is stored with hyphens turned into spaces, so also try the query that way ("de-peg" finds "de peg").
    // Module codes such as CFA1-FI still match on the original query.
    const loose = q.replace(/[-–—]+/g, " ").trim(), looseHas = loose !== q ? loose.split(/\s+/).map(matcher) : null;
    const textHit = (s) => termHas.every((has) => has(s)) || (looseHas && looseHas.every((has) => has(s)));
    // whole-phrase bonus for multi-word queries; a hyphenated query ("risk-free rate") is compared in its spaced form too
    const phrase = (s) => (terms.length > 1 && s.includes(q)) || (looseHas && looseHas.length > 1 && s.includes(loose));
    const count = (s, sub) => { let n = 0, i = 0; while (sub && (i = s.indexOf(sub, i)) !== -1) { n++; i += sub.length; } return n; };
    const out = [];
    Object.values(P).filter((p) => vis(p.id)).forEach((p) => {
      const title = p.title.toLowerCase(), tc = p.tcodes.map((t) => t.toLowerCase());
      let score = 0;
      if (tc.some((t) => t.split(/[\s/]+/).includes(q))) score += 120;
      if (title === q) score += 100;
      else if (title.startsWith(q)) score += 60;
      else if (qHas(title)) score += 40;
      const mods = (p.quals || []).map((x) => x.m.toLowerCase());
      if (mods.some((m) => modCode(m) === q)) score += 30;
      const hay = (title + " " + tc.join(" ") + " " + p.fiori.join(" ").toLowerCase() + " " + p.tags.join(" ").toLowerCase() + " " + mods.join(" ") + " " + p.summary.toLowerCase() + " " + p.text.toLowerCase() + (mode.simple ? "" : " " + (p.textDeep || "").toLowerCase()));
      if (textHit(hay)) {
        // Where the words appear matters more than whether they appear: a page that names the topic in its
        // summary or tags, or keeps coming back to it, beats a page that mentions it once in passing.
        const summ = p.summary.toLowerCase(), tags = p.tags.join(" ").toLowerCase();
        const body = p.text.toLowerCase() + (mode.simple ? "" : " " + (p.textDeep || "").toLowerCase());
        const inSumm = textHit(summ), inTags = textHit(tags);
        const needle = looseHas && looseHas.length > 1 ? loose : q;
        const freq = terms.length > 1 || looseHas ? count(body, needle) : count(body, q);
        score += 10 + (inSumm ? 14 : 0) + (inTags ? 8 : 0) + (phrase(hay) ? 15 : 0) + Math.min(15, 3 * freq);
      }
      // ties (e.g. a t-code used by a topic and its sub-pages) go to the more general page, but only as a tie-break
      if (score) out.push({ type: "page", id: p.id, score: score + (p.stub ? 0 : 3) + (8 - Math.min(8, p.path.length)) / 2 });
    });
    Object.values(DATA.flows).filter(flowVis).forEach((f) => {
      if (qHas((f.title + " " + f.summary).toLowerCase())) out.push({ type: "flow", id: f.id, score: 50 });
    });
    qualIds.forEach((qid) => QUALS[qid].stages.forEach((s) => {
      const m = s.title.toLowerCase();
      if (modCode(m) === q) out.push({ type: "module", id: qid, m: s.title, score: 200 });
      else if (termHas.every((has) => has((QUALS[qid].short + " " + m).toLowerCase()))) out.push({ type: "module", id: qid, m: s.title, score: 45 });
    }));
    return out.sort((a, b) => b.score - a.score).slice(0, 12);
  }
  function drawResults() {
    if (!input.value.trim()) { results.classList.remove("open"); return; }
    results.classList.add("open");
    if (!found.length) { results.innerHTML = `<div class="empty">No matches.</div>`; return; }
    results.innerHTML = found.map((r, i) => {
      const open = `<a class="result ${i === sel ? "sel" : ""}" data-i="${i}" href="${resultHref(r)}">`;
      if (r.type === "flow") { const f = DATA.flows[r.id]; return `${open}<div class="r-title"><span class="r-dot" style="background:var(--accent)"></span>Flow · ${esc(f.title)}</div><div class="r-sub">${esc(f.summary)}</div></a>`; }
      if (r.type === "module") { const st = QUALS[r.id].stages.find((s) => s.title === r.m); return `${open}<div class="r-title"><span class="r-dot qual-dot"></span>${esc(QUALS[r.id].short)} · ${esc(r.m)}</div><div class="r-sub">Qualification module · ${st ? st.items.length : 0} pages</div></a>`; }
      const p = P[r.id];
      const sub = [p.tcodes.join(", "), p.summary].filter(Boolean).join(" — ");
      return `${open}<div class="r-title"><span class="r-dot" style="background:${col(p.id)}"></span>${esc(p.title)}${p.adv ? ' <span class="adv-tag">advanced</span>' : ""}${p.stub ? ' <span style="color:var(--text-3);font-weight:400;font-size:12px">stub</span>' : ""}</div><div class="r-sub">${esc(sub || P[p.branch].title)}</div></a>`;
    }).join("");
  }
  function resultHref(r) {
    if (r.type === "flow") return `#/flows/${r.id}`;
    if (r.type === "module") return `#/quals/${r.id}`;
    return `#/map/p/${r.id}`;
  }
  function choose(i) {
    const r = found[i]; if (!r) return;
    input.value = ""; results.classList.remove("open"); input.blur();
    hits = new Set();
    if (r.type === "flow") go({ view: "flows", flow: r.id, page: null });
    else if (r.type === "module") { pendingModule = r.m; go({ view: "quals", qual: r.id, page: null }); }
    else openPage(r.id);
  }
  input.addEventListener("input", () => {
    found = search(input.value); sel = 0; drawResults();
    hits = new Set(found.filter((r) => r.type === "page").map((r) => r.id));
    if (parseHash().view === "map") $$("#map-svg .node").forEach((n) => n.classList.toggle("hit", hits.has(n.dataset.node)));
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { sel = Math.min(found.length - 1, sel + 1); drawResults(); e.preventDefault(); }
    if (e.key === "ArrowUp") { sel = Math.max(0, sel - 1); drawResults(); e.preventDefault(); }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && found[sel]) { e.preventDefault(); window.open(location.href.split("#")[0] + resultHref(found[sel]), "_blank", "noopener"); }
    else if (e.key === "Enter") choose(sel);
    if (e.key === "Escape") { input.value = ""; found = []; hits = new Set(); drawResults(); input.blur(); drawMap(); }
  });
  // plain click: choose in this tab (on mousedown, before the input loses focus); modified or middle click: let the browser open the link
  results.addEventListener("mousedown", (e) => { const b = e.target.closest("[data-i]"); if (!b) return; e.preventDefault(); if (!wantsNewTab(e)) choose(+b.dataset.i); });
  results.addEventListener("click", (e) => { if (!wantsNewTab(e)) e.preventDefault(); });
  input.addEventListener("blur", () => setTimeout(() => results.classList.remove("open"), 120));
  input.addEventListener("focus", () => { if (input.value.trim()) drawResults(); });

  /* ---------- Welcome guide ---------- */
  const welcome = $("#welcome"), wcCard = $("#welcome .wc-card");
  const wcBehind = () => $$("body > :not(#welcome):not(script)");
  let wcReturnFocus = null;
  const welcomeOpen = () => !welcome.hidden;
  function showWelcome() {
    if (welcomeOpen()) return;
    settingsMenu.hidden = true;
    wcReturnFocus = document.activeElement;
    welcome.hidden = false;
    wcBehind().forEach((el) => el.setAttribute("inert", ""));   // the page behind can't be clicked, tabbed to or read out
    wcCard.scrollTop = 0;
    wcCard.focus();
  }
  function hideWelcome(remember = true) {
    if (!welcomeOpen()) return;
    welcome.hidden = true;
    wcBehind().forEach((el) => el.removeAttribute("inert"));
    if (remember) store.set("welcomed", true);
    const back = wcReturnFocus; wcReturnFocus = null;
    if (back && back !== document.body && document.contains(back)) back.focus();
  }
  $("#wc-close").addEventListener("click", () => hideWelcome());
  $("#wc-backdrop").addEventListener("click", () => hideWelcome());
  welcome.addEventListener("click", (e) => {
    const a = e.target.closest("[data-wc]"); if (!a) return;
    if (wantsNewTab(e)) return;                 // Ctrl/Cmd/Shift+click: the browser opens the link; the guide stays
    e.preventDefault();
    hideWelcome();
    const where = a.dataset.wc;
    if (where === "map") { if (parseHash().view !== "map" || parseHash().page) go({ view: "map", flow: null, path: null, qual: null, page: null }); }
    else if (where === "flow") go({ view: "flows", flow: (a.getAttribute("href") || "").split("/")[2] || null, page: null });  // flow id comes from the link, not hard-coded
    else go({ view: where, flow: null, path: null, qual: null, page: null });
  });
  document.addEventListener("click", (e) => { if (e.target.closest("#wc-reopen")) showWelcome(); });
  // Keys while the guide is open: Esc closes it, Tab stays inside it, and the page's own shortcuts (/, H, Esc) wait.
  window.addEventListener("keydown", (e) => {
    if (!welcomeOpen()) return;
    if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); hideWelcome(); return; }
    if (e.key === "Tab") {
      const f = $$("button, a[href]", wcCard).filter((el) => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === first || document.activeElement === wcCard)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      return;
    }
    e.stopPropagation();
  }, true);

  document.addEventListener("keydown", (e) => {
    const typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
    if (e.key === "/" && !typing) { e.preventDefault(); input.focus(); }
    if ((e.key === "h" || e.key === "H") && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); goHome(); }
    if (e.key === "Escape" && !typing && parseHash().page) go({ page: null });
  });

  /* ---------- Home: back to the starting view ----------
     Map tab, nothing open, search cleared, map fully collapsed and fitted.
     Settings (depth, role / qualification focus, theme, ticks) are kept.
     Recorded as a normal history step, so browser Back returns to where you were. */
  function goHome() {
    input.value = ""; found = []; hits = new Set(); results.classList.remove("open"); input.blur();
    settingsMenu.hidden = true;
    pendingModule = null;
    expanded = new Set([ROOT]); store.set("expanded", [...expanded]);
    $$(".view .scroll").forEach((s) => { s.scrollTop = 0; });
    panelBody.scrollTop = 0;
    homePending = true;
    if (location.hash === "#/map") render(); else location.hash = "#/map";
  }
  $("#home-btn").addEventListener("click", (e) => { e.preventDefault(); goHome(); });

  /* ---------- Other tabs: when one tab saves ticks, targets or settings, the others follow ---------- */
  window.addEventListener("storage", (e) => {
    if (!e.key || !e.key.startsWith("mudmap:")) return;
    const k = e.key.slice(7);
    if (k === "known") { known.clear(); store.get("known", []).forEach((x) => known.add(x)); }
    else if (k === "targets") { targets.clear(); store.get("targets", []).filter((id) => ROLES[id]).forEach((x) => targets.add(x)); }
    else if (k === "role") setRoleState(store.get("role", null));
    else if (k === "mode") mode.simple = store.get("mode", "normal") === "simple";
    else if (k === "theme") { applyTheme(store.get("theme", null)); return; }
    else if (k === "welcomed") { if (store.get("welcomed", false)) hideWelcome(false); return; }
    else return;
    applyMode(); lastView = null; render();
  });

  /* The stub legend only means something while there are stubs */
  const anyStubs = Object.values(P).some((p) => p.stub);
  $$(".legend-stub").forEach((el) => { el.hidden = !anyStubs; });

  /* ---------- Start ---------- */
  if (!location.hash) history.replaceState(null, "", "#/map");
  applyMode();
  render();
  if (welcomeOnLoad) showWelcome();
})();
