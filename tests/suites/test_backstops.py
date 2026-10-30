"""When Banks Fail: backstop pages, the bank-failure flow, links, search, and an IP guard against the source's distinctive wording. Usage: python3 test_backstops.py <repo> <outdir>"""
import sys, pathlib, json, re
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

KIDS = ["bank-capital-and-liquidity", "lender-of-last-resort", "bail-in", "deposit-insurance", "bank-sovereign-loop"]   # real failure order
ALL = ["backstops"] + KIDS
# distinctive wording and named metrics from the source report: the idea is general, the expression isn't ours to copy
BANNED = ["domino", "conservative liquidity", "jupiter", "unpaid spies", "black paper", "sovereign man"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
check(P["backstops"]["parent"] == "money-you-hold" and   # 2026-10-27 money-you-hold branch: moved with Bank Deposits
       P["backstops"]["children"] == KIDS, f"When Banks Fail sits under Money with five pages in failure order ({P['backstops']['children']})")
check(all(not P[k]["stub"] for k in ALL), "all six pages written")
check("Study notes" in P["backstops"]["sources"], "the idea is credited as Study notes")
corpus = " ".join((v["text"] + " " + v.get("textDeep", "") + " " + v["title"]).lower() for v in P.values()) + " " + \
         " ".join((f["intro"] + f["outro"] + " ".join(" ".join(st["cells"]) + st["label"] for st in f["steps"])).lower() for f in D["flows"].values())
hits = [w for w in BANNED if w in corpus]
check(not hits, f"none of the source's distinctive wording appears anywhere on the site ({hits})")
F = D["flows"].get("when-a-bank-fails")
check(F and [st["page"] for st in F["steps"]] == KIDS, f"the flow walks the five backstops in failure order ({[st['page'] for st in F['steps']] if F else None})")
check(F and F["lanes"] == ["Who stands behind you", "What breaks it", "Where a real crisis stopped"], "the flow has its three lanes")

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
            check(not bad, f"every page complete {bad}")
            pg.goto(URL + "#/map/p/backstops"); pg.wait_for_timeout(200)
            missing = [k for k in KIDS if pg.locator(f'#panel-body .content a.wl[data-page="{k}"]').count() == 0]
            check(not missing, f"When Banks Fail links all five pages ({missing})")
            if mode == "simple" and w in (1366, 390): pg.screenshot(path=str(OUT / f"backstops-{w}.png"))
            for src in ["money", "bank-deposits"]:
                pg.goto(URL + f"#/map/p/{src}"); pg.wait_for_timeout(150)
                check(pg.locator('#panel-body .content a.wl[data-page="backstops"]').count() >= 1, f"{src} links to When Banks Fail")

            # the flow
            pg.goto(URL + "#/flows"); pg.wait_for_timeout(300)
            check(pg.locator('#flows-body [data-flow="when-a-bank-fails"]').count() == 1, "the flow is listed")
            pg.goto(URL + "#/flows/when-a-bank-fails"); pg.wait_for_timeout(400)
            cards = pg.locator(".step-card").evaluate_all("els => els.map(e => e.dataset.page)")
            check(cards == KIDS and noscroll(), f"five step cards in order, no sideways scroll ({cards})")
            txt = pg.locator("#flows-body").inner_text()
            check(all(c in txt for c in ["Silicon Valley Bank", "Credit Suisse", "Cyprus", "Iceland", "Lebanon"]), "the flow names its real cases")
            if mode == "simple" and w in (1366, 390): pg.screenshot(path=str(OUT / f"flow-bank-fails-{w}.png"), full_page=True)
            pg.locator(".step-card").nth(2).click(); pg.wait_for_timeout(400)
            check("/p/bail-in" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, "a step opens its page beside the flow")

            # search
            for q, want in [("bail-in", "#/map/p/bail-in"), ("lender of last resort", "#/map/p/lender-of-last-resort"), ("doom loop", "#/map/p/bank-sovereign-loop"),
                            ("deposit insurance", "#/map/p/deposit-insurance"), ("insolvent", "#/map/p/bank-capital-and-liquidity"), ("bank fails", "#/flows/when-a-bank-fails")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 6).map(e => e.getAttribute('href'))")
                check(want in hrefs, f"search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
