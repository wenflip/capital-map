"""New flows tests. Usage: python3 test_flows.py <repo> <outdir>"""
import sys, pathlib
from playwright.sync_api import sync_playwright
import os as _os
_W = _os.environ.get("CAPMAP_WIDTHS", "1366,390,360").split(",")
def sizes(lst):
    """Screen sizes to test. Set CAPMAP_WIDTHS=1366 for a quick desktop-only run."""
    return [s for s in lst if str(s[0]) in _W]
URL = pathlib.Path(sys.argv[1]).resolve().joinpath("index.html").as_uri()
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
NEW = {"where-money-comes-from": 6, "when-a-bank-fails": 5, "how-a-trade-settles": 6}   # 2026-10-26: trade flow added
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
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            pg.goto(URL + "#/flows"); pg.wait_for_timeout(350)
            check(pg.locator("#flows-body .flow-card").count() == 7, f"7 flow cards ({pg.locator('#flows-body .flow-card').count()})")   # 2026-10-26: was 3; trade flow + three planned outlines added
            body = pg.locator("#flows-body").inner_text()
            check(all(t in body for t in ["Where money comes from", "When a bank fails"]), "new flows listed")
            if mode == "simple" and w == 1366: pg.screenshot(path=str(OUT / "flows-1366.png"), full_page=True)
            for fid, n in NEW.items():
                pg.goto(URL + f"#/flows/{fid}"); pg.wait_for_timeout(300)
                cnt = pg.locator(".step-card").count()
                check(cnt == n and pg.locator("#flows-body .wl.broken").count() == 0 and noscroll(), f"{fid}: {cnt}/{n} steps, links ok, no h-scroll")
                if mode == "simple" and w in (1366, 390) and fid == "where-money-comes-from": pg.screenshot(path=str(OUT / f"{fid}-{w}.png"))
            # a step card opens its page
            pg.goto(URL + "#/flows/where-money-comes-from"); pg.wait_for_timeout(300)
            pg.locator("#flows-body a.wl[data-page='hierarchy-of-money']").first.click(); pg.wait_for_timeout(400)
            check("hierarchy-of-money" in pg.evaluate("location.hash"), "link from a flow opens the page")
            # search finds the flows
            for q, want in [("money comes from", "money comes from"), ("to your account", "money comes from")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(200)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                t = [x.splitlines()[0] for x in pg.locator("#results .result").all_inner_texts()]
                check(any(("Flow" in x and want.lower() in x.lower()) for x in t[:5]), f"search {q} finds the flow {t[:3]}")
                pg.keyboard.press("Escape")
            if not mob:
                pg.goto(URL + "#/flows"); pg.wait_for_timeout(300)
                with ctx.expect_page() as info:
                    pg.locator('#flows-body [data-flow="where-money-comes-from"]').first.click(modifiers=["Control"])
                np = info.value; np.wait_for_timeout(500)
                check("where-money-comes-from" in np.evaluate("location.hash"), "Ctrl+click a flow card opens a new tab")
                np.close()
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
