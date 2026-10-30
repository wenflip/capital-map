"""Figures: SVG diagrams embedded in pages. Files, naming, safety (no scripts or outside links), every file used, alt text
matching each SVG's description, captions, figures' figures matching their pages, build validation, text fitting inside each
drawing, rendering in the panel (loaded, scaled, tap-to-enlarge, dark mode), the ladder figure gone. Usage: python3 test_figures.py <repo> <outdir>"""
import sys, pathlib, json, re, shutil, subprocess, tempfile, sqlite3, html
from playwright.sync_api import sync_playwright
import os as _os
_W = _os.environ.get("CAPMAP_WIDTHS", "1366,390,360").split(",")
def sizes(lst):
    """Screen sizes to test. Set CAPMAP_WIDTHS=1366 for a quick desktop-only run."""
    return [s for s in lst if str(s[0]) in _W]
REPO = pathlib.Path(sys.argv[1]).resolve()
URL = REPO.joinpath("index.html").as_uri()
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
fails, errs = [], []
def check(c, m):
    print(("  ok   " if c else "  FAIL ") + m)
    if not c: fails.append(m)

FIGS = REPO / "assets/figures"
# file: pages it's embedded on. Update when a figure is added or moved (say so in the PR).
PLACED = {"shares-ownership-chain.svg": ["custody", "shares"], "compounding-fee-drag.svg": ["compounding"],
          "hierarchy-of-money-layers.svg": ["hierarchy-of-money"], "inflation-your-basket.svg": ["inflation"]}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
files = sorted(f.name for f in FIGS.glob("*"))
check(files == sorted(PLACED), f"four figures, nothing else ({files})")
check(not (FIGS / "failure-modes-ladder.svg").exists(), "the failure-ladder figure is gone (the Failures tab draws it live)")
check(all(any(f.startswith(pid + "-") for pid in P) for f in files), "every file is named <page-id>-<name>.svg")
for f in files:
    t = (FIGS / f).read_text()
    check(not re.search(r"<script|\son[a-z]+=|href=|<foreignObject|@import|url\((?!#)", t, re.I), f"{f}: no scripts, handlers or outside links")
    check("<title>" in t and "<desc>" in t and re.search(r'viewBox="0 0 560 \d+"', t), f"{f}: has a title, a description and a 560-wide viewBox")
placed = {}
for pid, p in P.items():
    for m in re.finditer(r'<img src="assets/figures/([^"]+)" alt="([^"]*)"', p["html"] + p.get("deep", "")):
        placed.setdefault(m.group(1), []).append((pid, html.unescape(m.group(2))))
check({f: sorted(x for x, _ in v) for f, v in placed.items()} == PLACED, f"each figure is on the expected pages ({ {f: [x for x, _ in v] for f, v in placed.items()} })")
check(set(placed) == set(files), "every figure file is used")
for f, uses in placed.items():
    desc = re.search(r"<desc>(.*?)</desc>", (FIGS / f).read_text(), re.S).group(1).strip()
    check(all(alt == desc for _, alt in uses), f"{f}: alt text is the SVG's own description, word for word")
for pid in sorted({x for v in PLACED.values() for x in v}):
    caps = re.findall(r"<figcaption>(.*?)<span", P[pid]["html"])
    check(caps and all(len(c) >= 30 for c in caps), f"{pid}: the figure has a real caption")
    check('class="fig-link" href="assets/figures/' in P[pid]["html"] and 'target="_blank"' in P[pid]["html"], f"{pid}: the figure opens full size")
check("Article 8" in " ".join(P["custody"]["sources"]) and "nominee" in " ".join(P["custody"]["sources"]).lower(), "Custody credits the chain's US legal terms")
check("security entitlement" in P["custody"]["html"].replace("&quot;", '"'), "the chain's caption names the US legal term")
check("[[custody" in REPO.joinpath("pages/brokers.md").read_text() and "draws the whole chain" in P["brokers"]["text"], "Brokers links to the chain instead of a third copy")

# the figures' numbers match their pages
fee = (FIGS / "compounding-fee-drag.svg").read_text()
check(round(10000 * 1.07 ** 30) == 76123 and round(10000 * 1.06 ** 30) == 57435 and "$76,123" in fee and "$57,435" in fee and "$18,688" in fee, "fee drag: 76,123, 57,435 and the 18,688 gap recomputed")
check("76,122.55" in P["compounding"]["text"] and "57,434.91" in P["compounding"]["text"], "fee drag matches Compounding's worked example")
for x, yr in [(70, 0), (130, 5), (250, 15), (430, 30)]:
    y_nf = 480 - 10000 * 1.07 ** yr / 80000 * 300; y_f = 480 - 10000 * 1.06 ** yr / 80000 * 300
    check(f"{x},{y_nf:.1f}" in fee and f"{x},{y_f:.1f}" in fee, f"fee drag: year {yr} plotted where the maths puts it")
bk = (FIGS / "inflation-your-basket.svg").read_text()
rates = [6, 4, 2, 5, 1.5]
for label, y, shown in [("Headline", 306, "3.7%"), ("Renter", 380, "4.3%"), ("Homeowner", 454, "3.1%")]:
    widths = [float(w) for w in re.findall(rf'<rect x="[0-9.]+" y="{y}" width="([0-9.]+)"', bk)]
    rate = sum(w / sum(widths) * r for w, r in zip(widths, rates))
    check(len(widths) == 5 and f"{rate:.1f}%" == shown, f"your basket: the {label} rate from its bar widths is {rate:.2f}%, shown as {shown}")
lay = (FIGS / "hierarchy-of-money-layers.svg").read_text()
order = re.findall(r'font-size="16" font-weight="600" fill="#1d1b18">([^<]+)</text>', lay)[:6]
check(order == ["Shares, property, crypto", "Bonds and T-bills", "Offshore and private dollars", "Bank deposits", "Central bank money", "Gold"], f"layers: the same six layers as the page's table, top to base ({order})")
check(all(x in REPO.joinpath("pages/hierarchy-of-money.md").read_text() for x in ["Risk assets", "Securities", "Offshore and private dollars", "Bank money", "Central bank money", "| Base | [[gold]]"]), "the page's table has the same layers")

# --- build validation (throwaway copy)
def build_with(edits):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        for path, old, new in edits:
            f = r / path; t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout
code, out = build_with([])
check(code == 0 and "figures 5" in out, "clean build: five figure placements exported")
C = "pages/compounding.md"
for label, edits, want in [
    ("a missing file", [(C, "compounding-fee-drag.svg", "compounding-no-such.svg")], "does not exist"),
    ("a missing caption", [(C, ' "The same 10,000 for 30 years, at 7% a year and at 6% (7% less a 1% fee). Fictional figures.")', ")")], "needs a caption"),
    ("thin alt text", [(C, "![A line chart of $10,000", "![Chart](x)\n\n![Chart")], "needs descriptive alt text"),
    ("a file outside assets/figures", [(C, "assets/figures/compounding-fee-drag.svg", "assets/share.png")], "must be an .svg in assets/figures/"),
]:
    c2, o2 = build_with(edits)
    check(c2 != 0 and want in o2, f"build fails on {label}")
db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
check(sorted(db.execute("SELECT page_id, file FROM figures").fetchall()) == sorted((p, "assets/figures/" + f) for f, ps in PLACED.items() for p in ps), "figures table matches the placements")
db.close()

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    # each drawing on its own: every text stays inside the card, and inside the box it labels where it has one
    pg = b.new_page(viewport={"width": 700, "height": 900})
    for f in files:
        pg.goto((FIGS / f).as_uri()); pg.wait_for_timeout(200)
        r = pg.evaluate("""() => { const card = document.querySelector('svg > rect').getBoundingClientRect(); const out = [];
          for (const t of document.querySelectorAll('text')) { const b = t.getBoundingClientRect();   // on-screen box, so rotated labels count correctly
            if (b.left < card.left + 2 || b.top < card.top + 2 || b.right > card.right - 2 || b.bottom > card.bottom - 2) out.push(t.textContent.trim().slice(0, 30)); }
          return out; }""")
        check(not r, f"{f}: every label fits inside the card ({r[:3]})")
        r2 = pg.evaluate("""() => { const out = []; const rects = [...document.querySelectorAll('rect')].slice(1).map(r => r.getBBox());
          for (const t of document.querySelectorAll('text')) { const b = t.getBBox(); const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
            const host = rects.find(r => cx > r.x && cx < r.x + r.width && cy > r.y && cy < r.y + r.height && r.width > 40);
            if (host && (b.x < host.x - 1 || b.x + b.width > host.x + host.width + 1)) out.push(t.textContent.trim().slice(0, 30)); }
          return out; }""")
        check(not r2, f"{f}: labels inside boxes don't spill out of them ({r2[:3]})")
    pg.close()
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            for theme in (["light", "dark"] if mode == "normal" else ["light"]):
                print(f"== {mode} @ {w} {theme}")
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1, color_scheme=theme)
                pg = ctx.new_page()
                pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
                pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
                for f, pids in PLACED.items():
                    for pid in pids:
                        pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(450)
                        img = pg.locator(f'#panel-body figure.fig img[src="assets/figures/{f}"]')
                        img.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
                        st = img.evaluate("e => ({ok: e.complete && e.naturalWidth > 0, w: e.getBoundingClientRect().width, box: e.closest('.panel-body').clientWidth, f: getComputedStyle(e).filter})")
                        check(st["ok"] and st["w"] <= min(560, st["box"]) + 1, f"{pid}: {f} loads and fits the panel ({st['w']:.0f}px)")
                        check(("brightness" in st["f"]) == (theme == "dark"), f"{pid}: dimmed only in dark mode ({st['f']})")
                        hint = pg.locator("#panel-body .fig-hint").first.is_visible()
                        check(hint == (w <= 860), f"{pid}: the 'Tap to enlarge' hint shows only on narrow screens")
                        check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{pid}: no sideways page scroll")
                        if pid in ("custody", "inflation") and mode == "normal" and w in (1366, 390): pg.screenshot(path=str(OUT / f"fig-{pid}-{w}-{theme}.png"))
                # tapping opens the full-size file
                pg.goto(URL + "#/map/p/compounding"); pg.wait_for_timeout(450)
                link = pg.locator("#panel-body .fig-link").first
                link.scroll_into_view_if_needed()
                with ctx.expect_page() as info:
                    link.click()
                full = info.value; full.wait_for_timeout(300)
                check(full.url.endswith("assets/figures/compounding-fee-drag.svg"), "tapping a figure opens it full size")
                full.close()
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
