"""Map control and toggle-button tests. Usage: python3 test_controls.py <repo> <outdir>"""
import sys, pathlib, json
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

STATE = """() => {
  const D = window.MUDMAP, P = D.pages, simple = document.body.classList.contains('simple');
  const vis = id => !(simple && P[id].adv);
  const kids = id => P[id].children.filter(vis);
  const visible = Object.keys(P).filter(vis);
  const parents = visible.filter(id => kids(id).length);
  const branches = kids(D.root);
  const nodes = [...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node);
  const openToggles = [...document.querySelectorAll('#map-svg [data-toggle]')].filter(t => t.querySelector('text').textContent === '−').map(t => t.dataset.toggle);
  return { nodes: nodes.length, uniq: new Set(nodes).size, visible: visible.length, parents: parents.length, branches: branches.length, openToggles, root: D.root };
}"""

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
            click = lambda act: (pg.locator(f'.map-controls [data-act="{act}"]').click(), pg.wait_for_timeout(450))

            # 1. Collapse all: only the root is open; every branch closed
            click("collapse"); s = pg.evaluate(STATE)
            check(s["openToggles"] == [s["root"]], f"collapse: only root open (open: {s['openToggles']})")
            check(s["nodes"] == 1 + s["branches"], f"collapse: root + {s['branches']} branches drawn ({s['nodes']})")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"collapsed-{w}.png"))
            # 2. Expand all: every visible page drawn, every parent open
            click("expand"); s = pg.evaluate(STATE)
            check(s["nodes"] == s["visible"] and s["uniq"] == s["visible"], f"expand: all {s['visible']} visible pages drawn ({s['nodes']})")
            check(len(s["openToggles"]) == s["parents"], f"expand: all {s['parents']} parents open ({len(s['openToggles'])})")
            # 3. Collapse again after expand
            click("collapse"); s = pg.evaluate(STATE)
            check(s["openToggles"] == [s["root"]] and s["nodes"] == 1 + s["branches"], "collapse after expand: fully collapsed")
            # 4. Collapse is remembered after reload
            pg.reload(); pg.wait_for_timeout(500); s = pg.evaluate(STATE)
            check(s["openToggles"] == [s["root"]], "collapsed state survives reload")
            # 5. Single toggle: real clicks open Source, then close it
            def tap_toggle(i):
                bx = pg.locator(f'#map-svg [data-toggle="{i}"] circle').bounding_box()
                if mob: pg.touchscreen.tap(bx["x"] + bx["width"]/2, bx["y"] + bx["height"]/2)
                else: pg.mouse.click(bx["x"] + bx["width"]/2, bx["y"] + bx["height"]/2)
                pg.wait_for_timeout(600)
            tap_toggle("money"); s = pg.evaluate(STATE)
            check("money" in s["openToggles"], "single toggle opens a branch")
            tap_toggle("money"); s = pg.evaluate(STATE)
            check("money" not in s["openToggles"], "single toggle closes it again")
            # 6. Collapse with a nested branch open and a page panel open
            click("expand"); pg.goto(URL + "#/map/p/liquidity"); pg.wait_for_timeout(400)
            if w > 860:   # on phones the page panel covers the map, so its buttons can't be pressed
                click("collapse"); s = pg.evaluate(STATE)
                check(s["openToggles"] == [s["root"]], "collapse with a page open: fully collapsed")
                check(pg.locator("body.panel-open").count() == 1, "page panel stays open after collapse")
            else:
                pg.click("#panel-close"); pg.wait_for_timeout(300); click("collapse")
                pg.goto(URL + "#/map/p/liquidity"); pg.wait_for_timeout(400)
            # 7. Show on map re-opens the path to that page
            pg.locator('#panel-body [data-mapto="liquidity"]').click(); pg.wait_for_timeout(500); s = pg.evaluate(STATE)
            check({"money"} <= set(s["openToggles"]), "Show on map opens the page's path")
            # 8. Collapse with role focus on, then expand all again
            pg.goto(URL + "#/map"); pg.wait_for_timeout(300)
            click("collapse"); s = pg.evaluate(STATE)
            check(s["openToggles"] == [s["root"]], "collapse with role focus: fully collapsed")
            click("expand"); s = pg.evaluate(STATE)
            check(s["nodes"] == s["visible"], "expand with role focus: everything drawn")
            # 9. Depth switch after collapse keeps it collapsed
            click("collapse")
            pg.evaluate("document.getElementById('settings-menu').hidden = true"); pg.click("#settings-btn"); pg.wait_for_timeout(150)
            other = "normal" if mode == "simple" else "simple"
            pg.locator(f'[data-mode="{other}"]').click(); pg.wait_for_timeout(500)
            pg.mouse.click(5, h - 5); pg.wait_for_timeout(150); s = pg.evaluate(STATE)
            check(s["openToggles"] == [s["root"]] and s["nodes"] == 1 + s["branches"], "collapsed state holds after a depth switch")
            pg.locator(f'[data-mode="{mode}"]').first.evaluate("b => b.click()"); pg.wait_for_timeout(400)
            # 10. Zoom and Fit buttons change the view and keep it on screen
            tf = lambda: pg.evaluate("document.getElementById('map-root').getAttribute('transform')")
            t0 = tf(); click("zoomin"); t1 = tf(); click("zoomout"); click("zoomout"); t2 = tf(); click("fit"); t3 = tf()
            check(t0 != t1 and t1 != t2, "zoom in / out change the view")
            bb = pg.evaluate("(() => { const r = document.getElementById('map-root').getBoundingClientRect(); return [r.left, r.right, r.top, r.bottom]; })()")
            check(bb[1] > 0 and bb[0] < w and bb[3] > 0 and bb[2] < h, "after Fit the map is on screen")
            # 11. Theme toggle flips and persists
            before = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()")
            pg.click("#theme-btn"); pg.wait_for_timeout(150)
            after = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()")
            pg.reload(); pg.wait_for_timeout(400)
            kept = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()")
            pg.click("#theme-btn"); pg.wait_for_timeout(150)
            back = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()")
            check(before != after and after == kept and back == before, f"theme toggles both ways and persists ({before} → {after} → {back})")
            # 12. Settings segments show exactly one active button each
            pg.evaluate("document.getElementById('settings-menu').hidden = true"); pg.click("#settings-btn"); pg.wait_for_timeout(150)
            act = pg.evaluate("[...document.querySelectorAll('#settings-menu .seg')].filter(s => !s.closest('[hidden]') && !s.hidden).map(s => s.querySelectorAll('button.active').length)")
            check(all(n == 1 for n in act), f"each settings group has one active button {act}")
            pg.mouse.click(5, h - 5); pg.wait_for_timeout(150)
            c.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILURES:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
