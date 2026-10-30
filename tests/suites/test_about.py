"""About page tests. Usage: python3 test_about.py <repo> <outdir>"""
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
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(450)
            # from the settings menu
            pg.click("#settings-btn"); pg.wait_for_timeout(150)
            link = pg.locator("#settings-menu .sm-about")
            check(link.is_visible() and link.get_attribute("href") == "#/about", "About link in the settings menu")
            link.click(); pg.wait_for_timeout(450)
            check(pg.evaluate("location.hash") == "#/about" and pg.locator("#about-view.active").count() == 1, "settings link opens About")
            check(pg.locator("#settings-menu").is_hidden(), "settings menu closes")
            body = pg.locator("#about-body").inner_text()
            for s in ["What it is", "Ways in", "What it isn't", "Licence", "One system, several lenses", "Not financial advice"]:
                check(s.lower() in body.lower(), f"About has '{s}'")
            n = pg.evaluate("Object.keys(window.MUDMAP.pages).length")
            check(pg.locator(".about-stat b").first.inner_text() == str(n), f"live page count ({n})")
            check(pg.locator(".about-stat").count() == 4, "four stat tiles")
            st = pg.locator(".about-stat").all_inner_texts()
            check(not any("jobs" in x for x in st) and any("stores of wealth" in x and x.strip().startswith("12") for x in st), f"no empty jobs tile; the Cartography count shows 12 stores ({[x.split(chr(10))[1] for x in st]})")
            check(pg.locator("#about-body a.wl.broken").count() == 0 and pg.locator("#about-body a.wl").count() >= 2, "About links work")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no horizontal scroll")
            check(pg.locator(".tab.active").count() == 0, "no tab highlighted on About")
            if mode == "simple" and w in (1366, 390): pg.screenshot(path=str(OUT / f"about-{w}.png"), full_page=False)
            # in-text link from About opens a page
            pg.locator('#about-body a.wl[data-page="capital-system"]').click(); pg.wait_for_timeout(400)
            check("capital-system" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, "link from About opens the page")
            # from the Index page
            pg.goto(URL + "#/index"); pg.wait_for_timeout(400)
            pg.locator('#index-body a.about-link[data-view="about"]').click(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash") == "#/about", "Index link opens About")
            # direct, Home, back
            pg.goto(URL + "#/about"); pg.reload(); pg.wait_for_timeout(450)
            check(pg.locator("#about-view.active").count() == 1, "#/about opens directly")
            pg.locator("body").press("h"); pg.wait_for_timeout(450)
            check(pg.evaluate("location.hash") == "#/map", "Home from About")
            pg.go_back(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash") == "#/about", "Back returns to About")
            if not mob:
                with ctx.expect_page() as info:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(300); pg.click("#settings-btn"); pg.wait_for_timeout(150)
                    pg.locator("#settings-menu .sm-about").click(modifiers=["Control"])
                np = info.value; np.wait_for_timeout(500)
                check(np.evaluate("location.hash") == "#/about", "Ctrl+click About opens a new tab")
                np.close()
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILURES:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
