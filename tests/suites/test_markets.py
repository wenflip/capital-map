"""Markets & Plumbing branch: structure, written pages, worked figures recomputed, Cartography boxes, search. Usage: python3 test_fixed_income.py <repo> <outdir>"""
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


# 2026-10-26 dealers branch: Dealers and Market Making added after Exchanges (its own suite, test_dealers)
# 2026-10-27 how-markets-move branch: The Repo Market added after Settlement (its own checks are in test_marketsmove)
BRANCHES = {"markets": ["exchanges", "market-making", "brokers", "custody", "settlement", "repo-market"]}
ALL = [x for h, ks in BRANCHES.items() for x in [h] + ks]
avg = (300 * 100.10 + 200 * 100.20) / 500
FIGURES = {
    "exchanges": [f"{100.20 - 100.10:.2f}", f"{avg:.2f}", f"{50.05 - 50.00:.2f}"],
    "settlement": [f"{1000 - 700}", "28 May 2024"],
    "brokers": ["$500,000", "$250,000", "$3 billion", "$1.4 billion"],
}
BOXES = {}
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
for h, ks in BRANCHES.items():
    check(P[h]["children"] == ks, f"{h} has its pages in order ({P[h]['children']})")
check(all(not P[k]["stub"] for k in ALL), f"all {len(ALL)} pages written")
check(not any(P[k]["adv"] for k in ALL), "none of them advanced")
check(all(P[k]["sources"] for k in ['markets', 'exchanges', 'brokers', 'settlement']), "pages citing outside facts credit them")
cfa = {st["title"].split(" — ")[0]: {i["page"] for i in st["items"]} for st in D["quals"]["cfa-l1"]["stages"]}
check({"exchanges", "brokers", "settlement"} <= cfa["CFA1-EQ"], "CFA I Equities maps exchanges, brokers and settlement")

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
                pass

            # from the chart, the fixed stores open written pages
            pg.goto(URL + "#/cartography"); pg.wait_for_timeout(300)
            pg.goto(URL + "#/map/p/shares"); pg.wait_for_timeout(300)
            pg.locator("#panel-body a.wl[data-page='brokers']").first.click(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash").endswith("/p/brokers") and pg.locator("#panel-body .qa").count() >= 1, "shares → brokers opens a written page")
            if mode == "simple" and w in (1366, 390): pg.goto(URL + "#/map/p/custody"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"custody-{w}.png"), full_page=True)

            for q, want, adv in [('order book', 'exchanges', False), ('limit order', 'exchanges', False), ('payment for order flow', 'brokers', False), ('segregation', 'custody', False), ('clearing house', 'settlement', False), ('netting', 'settlement', False)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                found = f"#/map/p/{want}" in hrefs
                check(found != (adv and mode == "simple"), f"search '{q}' {'hides' if adv and mode == 'simple' else 'finds'} {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
