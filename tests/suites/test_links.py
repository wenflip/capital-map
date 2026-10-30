"""New-tab link tests. Usage: python3 test_links.py <repo>"""
import sys, pathlib, re
from playwright.sync_api import sync_playwright
import os as _os
_W = _os.environ.get("CAPMAP_WIDTHS", "1366,390,360").split(",")
def sizes(lst):
    """Screen sizes to test. Set CAPMAP_WIDTHS=1366 for a quick desktop-only run."""
    return [s for s in lst if str(s[0]) in _W]
BASE = pathlib.Path(sys.argv[1]).resolve().joinpath("index.html").as_uri()
fails, errs = [], []
def check(c, m):
    print(("  ok   " if c else "  FAIL ") + m)
    if not c: fails.append(m)
HREF_OK = re.compile(r"^#/(map|flows|jobs|quals|cartography|index)(/[a-z0-9-]+)?(/p/[a-z0-9-]+)?$")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        print(f"== desktop {mode}")
        ctx = b.new_context(viewport={"width": 1366, "height": 860})
        ctx.on("page", lambda pg: pg.on("pageerror", lambda e: errs.append(str(e))))
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(BASE + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(500)

        def new_tab(action, label, want):
            with ctx.expect_page(timeout=5000) as info:
                action()
            np = info.value; np.wait_for_load_state(); np.wait_for_timeout(500)
            h = np.evaluate("location.hash")
            check(h == want, f"{label} → new tab at {h} (want {want})")
            return np
        def no_new_tab(action, label):
            n0 = len(ctx.pages); action(); pg.wait_for_timeout(500)
            check(len(ctx.pages) == n0, f"{label}: no new tab")

        # every navigation link has a valid address
        for hsh in ["#/map/p/liquidity", "#/index", "#/flows", "#/flows/where-money-comes-from", "#/quals", "#/quals/cfa-l1", "#/quals/frm-1", "#/cartography"]:
            pg.goto(BASE + hsh); pg.wait_for_timeout(350)
            bad = pg.evaluate("""() => [...document.querySelectorAll('a[data-page],a[data-path],a[data-qual],a[data-flow],a[data-mapto]')]
               .filter(a => a.offsetParent || a.closest('.view.active,#panel')).map(a => a.getAttribute('href')).filter(h => !h || !/^#\\/(map|flows|jobs|quals|cartography|index)(\\/[a-z0-9-]+)?(\\/p\\/[a-z0-9-]+)?$/.test(h))""")
            n = pg.evaluate("document.querySelectorAll('a[data-page],a[data-path],a[data-qual],a[data-flow],a[data-mapto]').length")
            check(not bad and n > 0, f"{hsh}: all {n} links have real addresses {bad[:3]}")
        check(pg.evaluate("[...document.querySelectorAll('.view.active button[data-page],#panel button[data-page]')].length") == 0, "no navigation buttons left (only links)")

        # in-text link: Ctrl, middle, Shift; plain click stays in the tab
        pg.goto(BASE + "#/map/p/liquidity"); pg.wait_for_timeout(400)
        wl = pg.locator("#panel-body .content a.wl").first
        target = wl.get_attribute("data-page")
        np = new_tab(lambda: wl.click(modifiers=["Control"]), "Ctrl+click in-text link", f"#/map/p/{target}")
        check(np.locator("#panel-body .p-title").count() == 1 and np.locator("body.panel-open").count() == 1, "new tab opens that page in the panel")
        np.close()
        check(pg.evaluate("location.hash") == "#/map/p/liquidity", "original tab stays where it was")
        new_tab(lambda: wl.click(button="middle"), "middle-click", f"#/map/p/{target}").close()
        new_tab(lambda: wl.click(modifiers=["Shift"]), "Shift+click (new window)", f"#/map/p/{target}").close()
        no_new_tab(lambda: wl.click(), "plain click")
        check(pg.evaluate("location.hash") == f"#/map/p/{target}", "plain click opens the page in this tab")
        # other link kinds
        pg.goto(BASE + "#/map/p/liquidity"); pg.wait_for_timeout(400)
        pill = pg.locator("#panel-body .p-list a[data-page]").first
        new_tab(lambda: pill.click(modifiers=["Control"]), "What links here pill", f"#/map/p/{pill.get_attribute('data-page')}").close()
        crumb = pg.locator("#crumbs a").last
        new_tab(lambda: crumb.click(button="middle"), "breadcrumb", f"#/map/p/{crumb.get_attribute('data-page')}").close()
        pg.goto(BASE + "#/jobs/coordinator"); pg.wait_for_timeout(350)
        pg.goto(BASE + "#/flows"); pg.wait_for_timeout(350)
        new_tab(lambda: pg.locator('#flows-body [data-flow="where-money-comes-from"]').click(modifiers=["Control"]), "flow card", "#/flows/where-money-comes-from").close()
        pg.goto(BASE + "#/flows/where-money-comes-from"); pg.wait_for_timeout(400)
        sc = pg.locator("a.step-card").first
        np = new_tab(lambda: sc.click(modifiers=["Control"]), "flow step", f"#/flows/where-money-comes-from/p/{sc.get_attribute('data-page')}")
        check(np.locator("#flows-view.active").count() == 1 and np.locator("body.panel-open").count() == 1, "step opens in its flow with the page panel")
        np.close()
        no_new_tab(lambda: sc.click(), "plain click on a flow step")
        check("/p/" in pg.evaluate("location.hash") and pg.evaluate("location.hash").startswith("#/flows/where-money-comes-from"), "plain step click opens the page beside the flow")
        pg.goto(BASE + "#/index"); pg.wait_for_timeout(400)
        ix = pg.locator("#index-body .index-group a[data-page]").nth(3)
        new_tab(lambda: ix.click(modifiers=["Control"]), "index entry", f"#/map/p/{ix.get_attribute('data-page')}").close()
        # tabs and other buttons: middle-click
        new_tab(lambda: pg.locator('.tab[data-view="flows"]').click(button="middle"), "middle-click a top tab", "#/flows").close()
        # map cards
        pg.goto(BASE + "#/map/p/gold"); pg.wait_for_timeout(500)
        pg.locator('#panel-body [data-mapto="gold"]').click(); pg.wait_for_timeout(700)
        pg.locator("#panel-close").click(); pg.wait_for_timeout(400)
        cx, cy = pg.evaluate("(() => { const r = document.querySelector('#map-svg [data-node=\"gold\"] .node-box').getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; })()")
        check(0 < cx < 1366 and 60 < cy < 860, f"map card on screen ({int(cx)}, {int(cy)})")
        def ctrl_map():
            pg.keyboard.down("Control"); pg.mouse.click(cx, cy); pg.keyboard.up("Control")
        new_tab(ctrl_map, "Ctrl+click a map card", "#/map/p/gold").close()
        new_tab(lambda: pg.mouse.click(cx, cy, button="middle"), "middle-click a map card", "#/map/p/gold").close()
        no_new_tab(lambda: pg.mouse.click(cx, cy), "plain click on a map card")
        check(pg.evaluate("location.hash") == "#/map/p/gold", "plain map click opens the page here")
        # search
        pg.goto(BASE + "#/map"); pg.wait_for_timeout(300)
        pg.fill("#search", "liquidity"); pg.wait_for_timeout(250)
        res = pg.locator("#results a.result").first
        check(res.get_attribute("href") == "#/map/p/liquidity", f"search result is a link ({res.get_attribute('href')})")
        new_tab(lambda: res.click(modifiers=["Control"]), "Ctrl+click a search result", "#/map/p/liquidity").close()
        pg.fill("#search", "liquidity"); pg.wait_for_timeout(250)
        new_tab(lambda: pg.locator("#search").press("Control+Enter"), "Ctrl+Enter in search", "#/map/p/liquidity").close()
        pg.fill("#search", "liquidity"); pg.wait_for_timeout(250)
        no_new_tab(lambda: pg.locator("#search").press("Enter"), "plain Enter")
        check(pg.evaluate("location.hash") == "#/map/p/liquidity", "plain Enter opens the result here")
        pg.goto(BASE + "#/map"); pg.wait_for_timeout(250)
        pg.fill("#search", "liquidity"); pg.wait_for_timeout(250)
        no_new_tab(lambda: pg.locator("#results a.result").first.click(), "plain click on a result")
        check(pg.evaluate("location.hash") == "#/map/p/liquidity" and pg.locator("#search").input_value() == "", "plain result click opens it here and clears search")
        # deep links open directly
        for hsh, sel in [("#/map/p/gold", "#panel-body .p-title"), ("#/flows/where-money-comes-from/p/gold", "#panel-body .p-title")]:
            t2 = ctx.new_page(); t2.goto(BASE + hsh); t2.wait_for_timeout(500)
            check(t2.locator(sel).count() == 1, f"opening {hsh} directly works"); t2.close()
        # tabs stay in sync
        pg.goto(BASE + "#/map/p/gold"); pg.wait_for_timeout(350)
        other = ctx.new_page(); other.goto(BASE + "#/map/p/gold"); other.wait_for_timeout(500)
        pg.click("#theme-btn"); pg.wait_for_timeout(500)
        check(pg.evaluate("document.documentElement.getAttribute('data-theme')") == other.evaluate("document.documentElement.getAttribute('data-theme')"), "theme follows across tabs")
        other.close(); ctx.close()

    # phones: plain taps unchanged, links valid
    for w, h in sizes([(390, 844), (360, 740)]):
        print(f"== phone {w}")
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True, device_scale_factor=2)
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE + "#/map/p/liquidity"); pg.evaluate("localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true')"); pg.reload(); pg.wait_for_timeout(500)
        wl = pg.locator("#panel-body .content a.wl").first; target = wl.get_attribute("data-page")
        wl.tap(); pg.wait_for_timeout(400)
        check(pg.evaluate("location.hash") == f"#/map/p/{target}" and len(ctx.pages) == 1, "tap on a link opens it here")
        check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no horizontal scroll")
        ctx.close()
    b.close()

# 2026-10-27: the build must reject anything in double brackets that isn't a valid link.
# [[sequence risk]] (batch 5) rendered as raw text because the build's link pattern skipped it.
import shutil, subprocess, tempfile
REPO = pathlib.Path(sys.argv[1]).resolve()
def build_with(extra):
    with tempfile.TemporaryDirectory() as d:
        r = pathlib.Path(d) / "repo"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        if extra:
            f = r / "pages/enough.md"; f.write_text(f.read_text() + "\n" + extra + "\n")
        q = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return q.returncode, q.stdout + q.stderr
code, out = build_with("")
check(code == 0, "clean build passes")
for label, extra, want in [
    ("an id with a space", "See [[sequence risk]].", "malformed link [[sequence risk]]"),
    ("a capitalised id", "See [[Enough]].", "malformed link [[Enough]]"),
    ("a missing page", "See [[no-such-page]].", "broken link [[no-such-page]]"),
    ("a stray bracket", "A stray [[ here.", "stray"),
]:
    code, out = build_with(extra)
    check(code != 0 and want in out, f"build rejects {label}")
code, out = build_with("Placeholder syntax such as `[[Any Thing]]` in code.")
check(code == 0, "the malformed-link check skips code spans")

print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILURES:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
