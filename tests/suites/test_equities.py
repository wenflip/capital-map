"""Equities branch: structure, written pages, worked figures recomputed, Cartography boxes, search. Usage: python3 test_fixed_income.py <repo> <outdir>"""
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


# 2026-10-27 how-to-think batch 5: The Arithmetic of Active Management added after Funds and ETFs; checked in test_howtothink
BRANCHES = {"equities": ["shares", "indices", "funds-and-etfs", "active-management", "financial-statements", "valuation", "private-business"]}
ALL = [x for h, ks in BRANCHES.items() for x in [h] + ks]
f2 = lambda x: f"{x:,.2f}"
gg = lambda d, r, g: d / (r - g)
rev, cogs, opex, intr, tax = 500_000, 300_000, 120_000, 10_000, 14_000
net = rev - cogs - opex - intr - tax
caps = {"A": 100 * 10, "B": 50 * 40, "C": 20 * 50}
FIGURES = {
    "indices": [f"{caps['A'] / sum(caps.values()) * 10:.2f}%", f"{100 * 0.10 / 170 * 100:.2f}%", f"{10 / 3:.2f}%"],
    "funds-and-etfs": [f"{10000 * 1.07 ** 30:,.0f}", f"{10000 * 1.06 ** 30:,.0f}", f"{10000 * 1.07 ** 30 - 10000 * 1.06 ** 30:,.0f}"],
    "financial-statements": [f"{rev - cogs:,}", f"{rev - cogs - opex:,}", f"{net:,}", f"{net / rev * 100:.1f}%", f"{120_000 / 80_000:.1f} times", f"−{abs(net + 10_000 - 40_000 - 30_000):,}"],
    "valuation": [f2(gg(2, 0.08, 0.03)), f2(gg(2, 0.08, 0.04)), f2(gg(2, 0.09, 0.03)), f"{40 / 2.5:.0f}", f"{2.5 / 40 * 100:.2f}%", f2(gg(3, 0.08, 0.02))],
    "shares": ["$500,000", "$250,000"],
    "private-business": ["79.6%", "50.6%", "34.7%"],
}
BOXES = {"shares": ("tier 3", "custodian"), "private-business": ("tier 3", "concentration")}
SP_FALL = (676.53 - 1565.15) / 1565.15
assert round(SP_FALL * 100) == -57

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
for h, ks in BRANCHES.items():
    check(P[h]["children"] == ks, f"{h} has its pages in order ({P[h]['children']})")
check(all(not P[k]["stub"] for k in ALL), f"all {len(ALL)} pages written")
check(not any(P[k]["adv"] for k in ALL), "none of them advanced")
check(all(P[k]["sources"] for k in ["equities", "shares", "funds-and-etfs", "private-business"]), "pages citing outside facts credit them")
check(not [k for k, v in P.items() if v.get("place") and v["stub"]], "every store on the Cartography chart opens a written page")
cfa = {st["title"].split(" — ")[0]: {i["page"] for i in st["items"]} for st in D["quals"]["cfa-l1"]["stages"]}
check("financial-statements" in cfa["CFA1-FSA"], "CFA I Financial Statement Analysis is now mapped")
check({"shares", "indices", "funds-and-etfs", "valuation"} <= cfa["CFA1-EQ"], "CFA I Equities maps the branch")

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
                check(set(ks) <= linked, f"{hub} links every child")

            # from the chart, the fixed stores open written pages
            pg.goto(URL + "#/cartography"); pg.wait_for_timeout(300)
            pg.locator(".cart-pt[data-page='private-business']").click(force=True); pg.wait_for_timeout(400)
            check(pg.locator("#panel-body .qa").count() >= 1, "chart → Private Business opens a written page")
            if mode == "simple" and w in (1366, 390): pg.goto(URL + "#/map/p/financial-statements"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"financial-statements-{w}.png"), full_page=True)

            for q, want in [("residual claim", "shares"), ("price weighted", "indices"), ("authorised participant", "funds-and-etfs"),
                            ("balance sheet", "financial-statements"), ("p/e", "valuation"), ("private equity", "private-business")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
