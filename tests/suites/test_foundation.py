"""Foundation branch: hub children written, worked figures correct, depth rules, search, keyboard. Usage: python3 test_foundation.py <repo> <outdir>"""
import sys, pathlib, math
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

PAGES = ["foundation", "claims-and-liabilities", "cartography-of-wealth", "four-ways-to-earn", "time-value-of-money", "compounding", "risk-and-return", "inflation"]   # 2026-10-26: Four Ways to Earn a Return added
f2 = lambda x: f"{x:,.2f}"
# every worked figure is recomputed here, so a typo on a page fails the test
FIGURES = {
    "time-value-of-money": [f2(1000 * 1.05 ** 10), f2(1000 / 1.05 ** 10), f2(1100 / 1.05)],
    "compounding": [f2(1000 * 1.05 ** 10), f2(1000 + 1000 * 0.05 * 10), f2(10000 * 1.07 ** 30), f2(10000 * 1.06 ** 30),
                    f"{((1 + 0.12 / 12) ** 12 - 1) * 100:.2f}%", f"{math.log(2) / math.log(1.06):.1f}"],
    "inflation": [f"{(1.05 / 1.03 - 1) * 100:.2f}%", f"{round(100 / 1.03 ** 20)}%"],
}
check(round(1 - 1.06 ** 30 / 1.07 ** 30, 2) == 0.25, "fee example really removes about a quarter")
# losses table: gain needed to recover = 1/(1-loss) - 1
RECOVER = {f"−{int(l * 100)}%": f"+{round((1 / (1 - l) - 1) * 100)}%" for l in (0.2, 0.5, 0.8)}

def tap_toggle(pg, mob, tid):
    """Tap a map toggle once it has stopped moving and is the thing under the finger (the map animates after collapse and panel close)."""
    loc = pg.locator(f'#map-svg [data-toggle="{tid}"] circle')
    prev = None
    for _ in range(30):
        bx = loc.bounding_box()
        if bx and prev and abs(bx["x"] - prev["x"]) < 0.5 and abs(bx["y"] - prev["y"]) < 0.5:
            x, y = bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2
            if pg.evaluate(f"(() => {{ const e = document.elementFromPoint({x}, {y}); return !!(e && e.closest('[data-toggle=\"{tid}\"]')); }})()"):
                break
        prev = bx; pg.wait_for_timeout(100)
    if mob: pg.touchscreen.tap(x, y)
    else: pg.mouse.click(x, y)
    pg.wait_for_timeout(600)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        simple = mode == "simple"
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(500)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

            # every Foundation page is written and clean
            P = pg.evaluate("(() => { const P = window.MUDMAP.pages, o = {}; for (const k in P) o[k] = { stub: !!P[k].stub, parent: P[k].parent }; return o; })()")
            check(sorted(k for k, v in P.items() if v["parent"] == "foundation") == sorted(PAGES[1:]), "Foundation has exactly its seven child pages")
            bad = []
            for pid in PAGES:
                if P[pid]["stub"]: bad.append(f"{pid}: stub")
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(150)
                body = pg.locator("#panel-body")
                heads = " | ".join(body.locator("h2:visible").all_inner_texts()).lower()
                if "what it is" not in heads: bad.append(f"{pid}: no 'What it is'")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}: broken link")
                if body.locator(".qa:visible").count() < 1: bad.append(f"{pid}: no visible quiz")
                if not noscroll(): bad.append(f"{pid}: h-scroll")
                text = body.text_content()   # includes quiz answers inside closed <details>
                for fig in FIGURES.get(pid, []):
                    if fig not in text: bad.append(f"{pid}: figure {fig} missing or wrong")
            check(not bad, f"Foundation pages complete, figures match the maths {bad}")

            # losses table
            pg.goto(URL + "#/map/p/risk-and-return"); pg.wait_for_timeout(200)
            rows = pg.evaluate("""() => { const t = [...document.querySelectorAll('#panel-body table')].find(t => /Gain needed/.test(t.innerText));
                return t ? [...t.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.innerText.trim())) : []; }""")
            check(dict(rows) == RECOVER, f"recovery table matches 1/(1−loss)−1 ({rows})")
            check(pg.locator("#panel-body .deeper:visible").count() == (0 if simple else 1), "volatility drag only in Everything")
            if simple and w in (1366, 390): pg.screenshot(path=str(OUT / f"foundation-risk-{w}.png"))

            # map: open the Foundation branch, its seven children are drawn
            pg.goto(URL + "#/map"); pg.wait_for_timeout(250)
            pg.locator('.map-controls [data-act="collapse"]').click(); pg.wait_for_timeout(250)
            tap_toggle(pg, mob, "foundation")
            drawn = pg.evaluate("[...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node)")
            check(all(k in drawn for k in PAGES[1:]), "opening Foundation on the map draws all seven pages")
            if simple and w == 1366: pg.screenshot(path=str(OUT / "foundation-map-1366.png"))

            # keyboard: Tab from the close button reaches an in-text link with a focus ring
            if not mob:
                pg.goto(URL + "#/map/p/foundation"); pg.wait_for_timeout(300)
                pg.locator("#panel-close").focus(); hit = None
                for _ in range(40):
                    pg.keyboard.press("Tab")
                    hit = pg.evaluate("""() => { const a = document.activeElement;
                        if (!a || !a.matches('#panel-body a.wl')) return null;
                        const s = getComputedStyle(a); return { id: a.dataset.page, ring: s.outlineStyle !== 'none' || s.boxShadow !== 'none' }; }""")
                    if hit: break
                check(bool(hit) and hit["ring"], f"Tab reaches a Foundation link with a focus ring ({hit})")
                if hit:
                    pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
                    check(pg.evaluate("location.hash") == f"#/map/p/{hit['id']}", "Enter opens the focused link")

            # search
            for q, want, deep in [("rule of 72", "compounding", False), ("real return", "inflation", False),
                                  ("discount rate", "time-value-of-money", False), ("risk premium", "risk-and-return", False),
                                  ("volatility drag", "risk-and-return", True)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                found = f"#/map/p/{want}" in hrefs
                if deep and simple:
                    check(not found or "volatility drag" in pg.evaluate(f"window.MUDMAP.pages['{want}'].text").lower(), f"search '{q}': Going deeper text not searched in Core ({hrefs[:3]})")
                else:
                    check(found, f"search '{q}' finds {want} in the top 5 ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
