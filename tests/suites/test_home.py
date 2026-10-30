"""Home button tests. Usage: python3 test_home.py <repo> <outdir>"""
import sys, pathlib
from playwright.sync_api import sync_playwright
import os as _os
_W = _os.environ.get("CAPMAP_WIDTHS", "1366,390,360").split(",")
def sizes(lst):
    """Screen sizes to test. Set CAPMAP_WIDTHS=1366 for a quick desktop-only run."""
    return [s for s in lst if str(s[0]) in _W]
URL = pathlib.Path(sys.argv[1]).resolve().joinpath("index.html").as_uri()
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
fails, errs = [], []
def check(c, m):
    print(("  ok   " if c else "  FAIL ") + m)
    if not c: fails.append(m)

HOME_STATE = """() => {
  const D = window.MUDMAP, P = D.pages, simple = document.body.classList.contains('simple');
  const vis = id => !(simple && P[id].adv);
  const branches = P[D.root].children.filter(vis).length;
  const nodes = document.querySelectorAll('#map-svg [data-node]').length;
  const open = [...document.querySelectorAll('#map-svg [data-toggle]')].filter(t => t.querySelector('text').textContent === '−').map(t => t.dataset.toggle);
  const r = document.getElementById('map-root').getBoundingClientRect();
  return { hash: location.hash, mapActive: document.getElementById('map-view').classList.contains('active'),
    panel: document.body.classList.contains('panel-open'), search: document.getElementById('search').value,
    results: document.getElementById('results').classList.contains('open'),
    menu: !document.getElementById('settings-menu').hidden,
    collapsed: open.length === 1 && open[0] === D.root && nodes === 1 + branches,
    onScreen: r.right > 0 && r.left < innerWidth && r.bottom > 0 && r.top < innerHeight,
    simple, theme: document.documentElement.getAttribute('data-theme'),
    role: JSON.parse(localStorage.getItem('mudmap:role') || 'null'), known: JSON.parse(localStorage.getItem('mudmap:known') || '[]').length };
}"""

def is_home(s, label):
    ok = s["hash"] == "#/map" and s["mapActive"] and not s["panel"] and s["search"] == "" and not s["results"] and not s["menu"] and s["collapsed"] and s["onScreen"]
    check(ok, f"{label} → home" + ("" if ok else f" {s}"))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {'Core' if mode == 'simple' else 'Everything'} @ {w}px")
            c = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = c.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')")
            pg.reload(); pg.wait_for_timeout(500)
            st = lambda: pg.evaluate(HOME_STATE)
            logo_visible = pg.locator("#home-btn").is_visible()
            check(logo_visible == (w > 480), f"logo visible only above 480px ({logo_visible})")

            def press_home(how):
                if how == "logo": pg.locator("#home-btn").click()
                elif how == "tab": pg.locator('.tab[data-view="map"]').click()
                elif how == "key": pg.locator("body").press("h")
                pg.wait_for_timeout(600)

            hows = (["logo"] if w > 480 else []) + ["tab", "key"]
            # A. deep in the map: expanded, page open
            for how in hows:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(250)
                pg.locator('.map-controls [data-act="expand"]').click(); pg.wait_for_timeout(300)
                pg.goto(URL + "#/map/p/hierarchy-of-money"); pg.wait_for_timeout(400)
                if how == "tab" and mob: pass  # panel is full screen on phones; tabs stay in the top bar
                press_home(how); is_home(st(), f"[{how}] from an open page, map expanded")
            # B. from another view, scrolled down
            for how in hows:
                if how == "tab": continue   # the Map tab from another view just switches view (by design)
                pg.goto(URL + "#/flows"); pg.wait_for_timeout(400)
                pg.evaluate("document.querySelector('#flows-view .scroll').scrollTop = 1500"); pg.wait_for_timeout(100)
                press_home(how); s = st(); is_home(s, f"[{how}] from Flows, scrolled")
                pg.goto(URL + "#/flows"); pg.wait_for_timeout(300)
                top = pg.evaluate("document.querySelector('#flows-view .scroll').scrollTop")
                check(top == 0, f"[{how}] Flows list scrolled back to top ({top})")
            # Map tab from another view still just switches to the map
            pg.goto(URL + "#/flows/where-money-comes-from"); pg.wait_for_timeout(300)
            pg.locator('.map-controls [data-act="expand"]').evaluate("b => b.click()"); pg.wait_for_timeout(200)
            pg.locator('.tab[data-view="flows"]').click(); pg.wait_for_timeout(200)
            pg.goto(URL + "#/flows/where-money-comes-from"); pg.wait_for_timeout(300)
            pg.locator('.tab[data-view="map"]').click(); pg.wait_for_timeout(400)
            s = st(); check(s["hash"] == "#/map" and not s["collapsed"], "Map tab from another view switches view without collapsing")
            # C. with a search typed and results open
            pg.goto(URL + "#/map"); pg.wait_for_timeout(250)
            if w < 481: pg.locator("#search").click()
            pg.fill("#search", "migo"); pg.wait_for_timeout(250)
            pg.locator("#search").press("Escape") if False else None
            if w > 480: pg.locator("#home-btn").click()
            else: pg.locator("#search").blur(); pg.locator('.tab[data-view="map"]').click()
            pg.wait_for_timeout(500); is_home(st(), "with a search typed")
            # D. 'h' typed in the search box is just a letter, not Home
            if w < 481: pg.locator("#search").click()
            pg.locator("#search").fill(""); pg.locator("#search").type("hydraulic"); pg.wait_for_timeout(200)
            check(pg.locator("#search").input_value() == "hydraulic", "typing h in search doesn't trigger Home")
            pg.locator("#search").fill(""); pg.locator("#search").blur(); pg.wait_for_timeout(200)
            # E. settings kept: focus, theme, ticks
            pg.goto(URL + "#/map/p/bank-deposits"); pg.wait_for_timeout(300)
            pg.evaluate("document.getElementById('settings-menu').hidden = true"); pg.click("#settings-btn"); pg.wait_for_timeout(150)
            pg.mouse.click(5, h - 5); pg.wait_for_timeout(150)
            pg.goto(URL + "#/map/p/bank-deposits"); pg.wait_for_timeout(300)
            pg.click("#theme-btn"); pg.wait_for_timeout(150)
            before = st()
            pg.evaluate("document.getElementById('settings-menu').hidden = true"); pg.click("#settings-btn"); pg.wait_for_timeout(150)
            press_home("key"); after = st(); is_home(after, "[key] with settings menu open")
            check(after["role"] is None and after["theme"] == before["theme"] and after["known"] == 0 and after["simple"] == (mode == "simple"),
                  f"focus, theme, ticks and depth kept ({after['role']}, {after['theme']}, {after['known']}, {after['simple']})")
            pg.locator('.map-controls [data-act="expand"]').evaluate("b => b.click()"); pg.wait_for_timeout(400)
            pg.locator("body").press("h"); pg.wait_for_timeout(500)
            # F. Browser Back returns to where you were
            pg.goto(URL + "#/map/p/liquidity"); pg.wait_for_timeout(400)
            press_home("key"); pg.go_back(); pg.wait_for_timeout(500)
            s = st(); check(s["hash"] == "#/map/p/liquidity" and s["panel"], f"Back after Home returns to the page ({s['hash']})")
            if mode == "simple" and w in (1366, 390):
                press_home("key"); pg.screenshot(path=str(OUT / f"home-{w}.png"))
                pg.locator("#home-btn").hover() if w > 480 else None
            c.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILURES:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
