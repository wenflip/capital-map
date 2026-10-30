"""Search ranking: the page most about a topic ranks first or second, in both depths. Usage: python3 test_search.py <repo> <outdir>"""
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
# (query, page, best acceptable rank). The first three broke earlier as pages were added.
CASES = [("mortgage", "real-estate", 2), ("risk-free rate", "t-bills", 3), ("clearing house", "settlement", 2),
         ("contango", "commodities", 1), ("bail-in", "bail-in", 1), ("stablecoin", "stablecoins", 1), ("leverage", "leverage", 1),
         ("capital controls", "capital-controls", 1), ("diversification", "diversification", 1), ("hyperinflation", "currency-failure", 2),
         ("annuity", "insurer-failure", 2), ("default fund", "clearing-house-failure", 2), ("self-custody", "self-custody", 1),
         ("yield curve", "yield-curve", 1), ("deposit insurance", "deposit-insurance", 1)]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(450)
            for q, want, best in CASES:
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(200)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.map(e => e.getAttribute('href'))")
                r = next((i + 1 for i, h in enumerate(hrefs) if h == f"#/map/p/{want}"), None)
                check(r is not None and r <= best, f"{w} {mode}: '{q}' ranks {want} at {r} (needs ≤ {best})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
