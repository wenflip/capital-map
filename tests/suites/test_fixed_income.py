"""Fixed Income branch: structure, written pages, worked figures recomputed, depth rules, search. Usage: python3 test_fixed_income.py <repo> <outdir>"""
import sys, pathlib, json
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

KIDS = ["t-bills", "bonds", "bond-pricing", "yield-curve", "credit-risk", "inflation-linked-bonds", "duration"]
ALL = ["fixed-income"] + KIDS
f2 = lambda x: f"{x:,.2f}"
def price(c, y, n, f=1000): return sum(c * f / (1 + y) ** t for t in range(1, n + 1)) + f / (1 + y) ** n
def durations(c, y, n, f=1000):
    cfs = [(t, c * f) for t in range(1, n)] + [(n, c * f + f)]
    p = sum(cf / (1 + y) ** t for t, cf in cfs); mac = sum(t * cf / (1 + y) ** t for t, cf in cfs) / p
    return mac, mac / (1 + y)
mac3, mod3 = durations(0.05, 0.05, 3); _, mod10 = durations(0.05, 0.05, 10)
# every worked figure is recomputed from its formula, so a typo on a page fails the test
FIGURES = {
    "t-bills": [f"{(10000 / 9800 - 1) * 100:.2f}%"],
    "bond-pricing": [f2(price(0.05, 0.04, 3)), f2(price(0.05, 0.05, 3)), f2(price(0.05, 0.06, 3)), f2(price(0.05, 0.06, 10)), f2(price(0.05, 0.04, 10))],
    "duration": [f"{mac3:.2f}", f"{mod3:.2f}", f"{(1 - price(0.05, 0.06, 3) / 1000) * 100:.2f}%", f"{mod10:.2f}"],
    "credit-risk": [f"{round((0.065 - 0.045) * 10000)} basis points"],
    "inflation-linked-bonds": [f"{1000 * 1.03:,.0f}", f2(1030 * 0.01), f"{4 - 1.5:.1f}%"],
}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
check(P["fixed-income"]["children"] == KIDS, f"Fixed Income has its seven pages in order ({P['fixed-income']['children']})")
check(all(not P[k]["stub"] for k in ALL), "all eight pages written")
check(P["duration"]["adv"] and not any(P[k]["adv"] for k in ALL if k != "duration"), "only Duration is advanced")
cfa_fi = next(st for st in D["quals"]["cfa-l1"]["stages"] if st["title"].startswith("CFA1-FI"))
check({"bond-pricing", "credit-risk", "inflation-linked-bonds"} <= {i["page"] for i in cfa_fi["items"]}, "CFA I Fixed Income maps the new pages")

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

            bad = []
            for pid in ALL:
                if simple and P[pid]["adv"]: continue
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(120)
                body = pg.locator("#panel-body")
                if "what it is" not in " | ".join(body.locator("h2:visible").all_inner_texts()).lower(): bad.append(f"{pid}: no 'What it is'")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}: broken link")
                if body.locator(".qa:visible").count() < 1: bad.append(f"{pid}: no visible quiz")
                if not noscroll(): bad.append(f"{pid}: h-scroll")
                text = body.text_content()
                bad += [f"{pid}: figure {fig} missing or wrong" for fig in FIGURES.get(pid, []) if fig not in text]
            check(not bad, f"pages complete, figures match the maths {bad}")

            pg.goto(URL + "#/map/p/bonds"); pg.wait_for_timeout(150)
            t = pg.locator("#panel-body .cart-note").inner_text().lower() if pg.locator("#panel-body .cart-note").count() else ""
            check("tier 3" in t and "counterparty default" in t, "Bonds carries its Cartography box")
            pg.goto(URL + "#/map/p/fixed-income"); pg.wait_for_timeout(150)
            n = pg.locator('#panel-body a.wl[data-page="duration"]:visible').count()
            check((n == 0) if simple else (n >= 1), f"hub's link to Duration {'hidden in Core' if simple else 'shown in Everything'} ({n})")
            if simple and w in (1366, 390): pg.goto(URL + "#/map/p/bond-pricing"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"fixed-income-pricing-{w}.png"), full_page=True)

            for q, want, adv in [("yield to maturity", "bond-pricing", False), ("inverted", "yield-curve", False), ("investment grade", "credit-risk", False),
                                 ("breakeven", "inflation-linked-bonds", False), ("risk-free rate", "t-bills", False), ("convexity", "duration", True)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                found = f"#/map/p/{want}" in hrefs
                check(found != (adv and simple), f"search '{q}' {'hides' if adv and simple else 'finds'} {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
