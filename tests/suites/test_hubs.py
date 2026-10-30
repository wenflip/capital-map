"""Hub pages: every written top-level branch meets the hub standard. Usage: python3 test_hubs.py <repo> <outdir>"""
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
SD = []
STD = ["What it is", "Why it exists", "How it works", "What goes wrong", "Connects to", "Check yourself"]
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
            P = pg.evaluate("(() => { const P = window.MUDMAP.pages; const o = {}; for (const k in P) o[k] = { adv: !!P[k].adv, kids: P[k].children, stub: !!P[k].stub, words: (P[k].text || '').split(/\\s+/).length }; return o; })()")
            ROOT = pg.evaluate("window.MUDMAP.root")
            HUBS = [k for k in P[ROOT]["kids"] if not P[k]["stub"]]   # written top-level branches are hubs
            check(len(HUBS) >= 1, f"written hubs found ({HUBS})")
            simple = mode == "simple"
            bad = []
            for pid in HUBS + SD:
                if simple and P[pid]["adv"]: continue
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(150)
                body = pg.locator("#panel-body")
                heads = " | ".join(body.locator("h2:visible").all_inner_texts()).lower()
                if pg.locator("#panel-body .p-title").count() != 1: bad.append(f"{pid}:title")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}:broken")
                miss = [s for s in STD if s.lower() not in heads]
                if miss: bad.append(f"{pid}:sections {miss}")
                if body.locator(".qa").count() < 2: bad.append(f"{pid}:quiz")
                if P[pid]["words"] < 400: bad.append(f"{pid}:short {P[pid]['words']}")
                # every child visible at this depth is linked from the page
                for kid in P[pid]["kids"]:
                    vis = not (simple and P[kid]["adv"])
                    n = body.locator(f'a.wl[data-page="{kid}"]:visible').count()
                    if vis and n == 0: bad.append(f"{pid}: child {kid} not linked")
                    if not vis and n: bad.append(f"{pid}: advanced child {kid} shown in Core")
                # Going deeper only in Everything
                deep_vis = body.locator(".deeper:visible").count()
                if simple and deep_vis: bad.append(f"{pid}: Going deeper shown in Core")
                if not simple and not deep_vis: bad.append(f"{pid}: Going deeper missing in Everything")
                if not noscroll(): bad.append(f"{pid}:h-scroll")
                if w in (1366, 390) and pid == "money":
                    pg.screenshot(path=str(OUT / f"hub-{pid}-{mode}-{w}.png"))
            check(not bad, f"all hub pages complete at this depth {bad}")
            # in-text link from a hub works
            pg.goto(URL + "#/map/p/money"); pg.wait_for_timeout(200)
            pg.locator('#panel-body a.wl[data-page="gold"]').first.click(); pg.wait_for_timeout(300)
            check("gold" in pg.evaluate("location.hash"), "Money hub link opens Gold")
            # advanced Going deeper links appear only in Everything
            pg.goto(URL + "#/map/p/money"); pg.wait_for_timeout(200)
            n = pg.locator('#panel-body a.wl[data-page="eurodollars"]:visible').count()
            check((n == 0) if simple else (n >= 1), f"Money: advanced link to eurodollars {'hidden in Core' if simple else 'shown in Everything'} ({n})")
            # search finds the new content
            for q, want in [("whose promise", "money"), ("dash for cash", "money")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} in the top 5 ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
