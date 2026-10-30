"""Portfolio & Risk branch: structure, written pages, worked figures recomputed, Cartography boxes, search. Usage: python3 test_fixed_income.py <repo> <outdir>"""
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


# 2026-10-27 how-markets-move branch: Asymmetry added after Position Sizing (its own checks are in test_marketsmove)
# 2026-10-27 how-to-think batch 4: Risk of Ruin and Kelly Criterion (advanced) added after Asymmetry; checked in test_howtothink
BRANCHES = {"portfolio": ["diversification", "correlation", "asset-allocation", "position-sizing", "asymmetry", "risk-of-ruin", "kelly-criterion", "rebalancing", "market-regimes"]}
ALL = [x for h, ks in BRANCHES.items() for x in [h] + ks]
import math
vol = lambda rho, s=0.20: math.sqrt(2 * 0.25 * s * s + 2 * 0.25 * rho * s * s) * 100
rec = lambda loss: (1 / (1 - loss) - 1) * 100
FIGURES = {
    "diversification": [f"{vol(1):.2f}%", f"{vol(0.5):.2f}%", f"{vol(0):.2f}%", f"{vol(-1):.2f}%", f"{20 / math.sqrt(4):.2f}%", f"{20 / math.sqrt(10):.2f}%", f"{20 / math.sqrt(100):.2f}%"],
    "asset-allocation": [f"{60_000 * 0.7:,.0f}", f"{40_000 * 1.05:,.0f}", f"{(60_000 * 0.7 + 40_000 * 1.05):,.0f} (−{100 - (60_000 * 0.7 + 40_000 * 1.05) / 1000:.0f}%)", f"{0.8 * 25:.0f}%"],
    "position-sizing": [f"+{rec(0.1):.1f}%", f"+{rec(0.2):.1f}%", f"+{rec(0.5):.1f}%", f"+{rec(0.9):.1f}%", f"{50_000 * 0.01:,.0f}", f"{50_000 * 0.01 / 0.10:,.0f}"],
    "rebalancing": [f"{75_000 / 115_000 * 100:.1f}%", f"{40_000 / 115_000 * 100:.1f}%", f"{115_000 * 0.6:,.0f}", f"{115_000 * 0.4:,.0f}", f"{75_000 - 115_000 * 0.6:,.0f}", f"{(80_000 + 100_000) / 2:,.0f}"],
}
BOXES = {}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
for h, ks in BRANCHES.items():
    check(P[h]["children"] == ks, f"{h} has its pages in order ({P[h]['children']})")
check(all(not P[k]["stub"] for k in ALL), f"all {len(ALL)} pages written")
check([k for k in ALL if P[k]["adv"]] == ["kelly-criterion"], "only Kelly Criterion is advanced")   # 2026-10-27 batch 4: Kelly is advanced by design
check(all(P[k]["sources"] for k in ["portfolio", "correlation", "market-regimes"]), "pages citing outside facts credit them")
cfa = {st["title"].split(" — ")[0]: {i["page"] for i in st["items"]} for st in D["quals"]["cfa-l1"]["stages"]}
check({"diversification", "correlation", "asset-allocation", "rebalancing"} <= cfa["CFA1-PC"], "CFA I Portfolio Construction maps the branch")
# every link to diversification / correlation across the site now lands on a written page
check(not P["diversification"]["stub"] and not P["correlation"]["stub"], "the two most-linked stubs are written")

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
                # 2026-10-27 batch 4: advanced children are linked from Going deeper, so they show only in Everything mode
                want = {k for k in ks if mode == "normal" or not P[k]["adv"]}
                check(want <= linked, f"{hub} links every child shown at this depth ({sorted(want - linked)})")

            # from the chart, the fixed stores open written pages
            pg.goto(URL + "#/cartography"); pg.wait_for_timeout(300)
            pg.goto(URL + "#/map/p/cartography-of-wealth"); pg.wait_for_timeout(300)
            pg.locator("#panel-body a.wl[data-page='diversification']").first.click(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash").endswith("/p/diversification") and pg.locator("#panel-body .qa").count() >= 1, "the model page's link to Diversification opens a written page")
            if mode == "simple" and w in (1366, 390): pg.goto(URL + "#/map/p/diversification"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"diversification-{w}.png"), full_page=True)

            for q, want in [("specific risk", "diversification"), ("correlation", "correlation"), ("60/40", "asset-allocation"),
                            ("gain needed to recover", "position-sizing"), ("threshold", "rebalancing"), ("risk-off", "market-regimes")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} ({hrefs[:3]})")
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
