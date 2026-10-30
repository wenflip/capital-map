"""Measure branch: structure, written pages, worked figures recomputed, Cartography boxes, search. Usage: python3 test_fixed_income.py <repo> <outdir>"""
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


# 2026-10-27 how-to-think batch 4: Fat Tails added after Volatility; checked in test_howtothink
BRANCHES = {"measure": ["returns", "drawdown", "volatility", "fat-tails", "sharpe-ratio"]}
ALL = [x for h, ks in BRANCHES.items() for x in [h] + ks]
import math, statistics
yrs = [10, -5, 15, 0, 5]
sd = statistics.stdev(yrs)
FIGURES = {
    "returns": [f"{(107 - 100 + 3) / 100 * 100:.0f}%", f"{(1.10 / 1.04 - 1) * 100:.2f}%", f"{(1.5 ** 0.25 - 1) * 100:.2f}%", f"{(1 - 150 * 0.5 / 100) * 100:.0f}%", f"−{(1 - math.sqrt(0.75)) * 100:.2f}%", f"{(2 ** 0.1 - 1) * 100:.2f}%", f"{100 * 1.1 ** 10:.0f}"],
    "drawdown": [f"−{(1 - 90 / 120) * 100:.0f}%", f"−{(1 - 110 / 120) * 100:.1f}%", f"−{(1 - 140 / 200) * 100:.0f}%"],
    "volatility": [f"{statistics.mean(yrs):.0f}%", f"{sd:.2f}%", f"{math.sqrt(252):.2f}%"],
    "sharpe-ratio": [f"{(9 - 4) / 10:.2f}", f"{(12 - 4) / 20:.2f}", f"{4 + 2 * (9 - 4):.0f}%", f"{(7 - 4) / 6:.2f}"],
}
BOXES = {}
SP = (676.53 / 1565.15 - 1) * 100
assert round(SP) == -57

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
for h, ks in BRANCHES.items():
    check(P[h]["children"] == ks, f"{h} has its pages in order ({P[h]['children']})")
check(all(not P[k]["stub"] for k in ALL), f"all {len(ALL)} pages written")
check([k for k in ALL if P[k]["adv"]] == ["sharpe-ratio"], "only the Sharpe ratio is advanced")
check(all(P[k]["sources"] for k in ["drawdown", "sharpe-ratio"]), "pages citing outside facts credit them")
cfa = {st["title"].split(" — ")[0]: {i["page"] for i in st["items"]} for st in D["quals"]["cfa-l1"]["stages"]}
check({"returns", "volatility"} <= cfa["CFA1-QM"] and "sharpe-ratio" in cfa["CFA1-PC"], "CFA I maps returns, volatility and the Sharpe ratio")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
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
                if mode == "simple" and P[pid]["adv"]: continue
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(120)
                body = pg.locator("#panel-body")
                if "what it is" not in " | ".join(body.locator("h2:visible").all_inner_texts()).lower(): bad.append(f"{pid}: no 'What it is'")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}: broken link")
                if body.locator(".qa:visible").count() < 1: bad.append(f"{pid}: no visible quiz")
                if not noscroll(): bad.append(f"{pid}: h-scroll")
                text = body.text_content()
                bad += [f"{pid}: figure {fig} missing or wrong" for fig in FIGURES.get(pid, []) if fig not in text]
                if pid in BOXES:
                    box = body.locator(".cart-note").inner_text().lower() if body.locator(".cart-note").count() else ""
                    if not all(x in box for x in BOXES[pid]): bad.append(f"{pid}: Cartography box wrong ({box[:60]})")
            check(not bad, f"pages complete, figures match the maths, boxes right {bad}")

            # hubs link every child; Real Assets also points to Gold on the Money branch
            for hub, ks in BRANCHES.items():
                pg.goto(URL + f"#/map/p/{hub}"); pg.wait_for_timeout(150)
                linked = set(pg.eval_on_selector_all("#panel-body a.wl:visible", "els => els.map(e => e.dataset.page)"))
                core_kids = [k for k in ks if not P[k]["adv"]]
                check(set(core_kids) <= linked, f"{hub} links every child")
                n = pg.locator('#panel-body a.wl[data-page="sharpe-ratio"]:visible').count()
                check((n == 0) if mode == "simple" else (n >= 1), f"hub's link to the Sharpe ratio {'hidden in Core' if mode == 'simple' else 'shown in Everything'} ({n})")

            # from the chart, the fixed stores open written pages
            pg.goto(URL + "#/cartography"); pg.wait_for_timeout(300)
            pg.goto(URL + "#/map/p/position-sizing"); pg.wait_for_timeout(300)
            pg.locator("#panel-body a.wl[data-page='drawdown']").first.click(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash").endswith("/p/drawdown") and pg.locator("#panel-body .qa").count() >= 1, "Position Sizing's link to Drawdown opens a written page")
            if mode == "simple" and w in (1366, 390): pg.goto(URL + "#/map/p/returns"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"returns-{w}.png"), full_page=True)

            for q, want, adv in [("real return", "returns", False), ("annualised", "returns", False), ("underwater", "drawdown", False),
                            ("standard deviation", "volatility", False), ("fat tails", "volatility", False), ("reward-to-variability", "sharpe-ratio", True)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                found = f"#/map/p/{want}" in hrefs
                check(found != (adv and mode == "simple"), f"search '{q}' {'hides' if adv and mode == 'simple' else 'finds'} {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            # hyphenated phrase queries keep their whole-phrase bonus (regression: "risk-free rate" lost T-Bills)
            pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
            if w < 481: pg.locator("#search").click()
            pg.fill("#search", "risk-free rate"); pg.wait_for_timeout(250)
            top = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
            check("#/map/p/t-bills" in top, f"'risk-free rate' puts T-Bills in the top three ({top})")
            pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
