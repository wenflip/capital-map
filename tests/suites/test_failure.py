"""Failure ladder: hub, first rungs (one template), the When a country fails flow, figures recomputed. Usage: python3 test_failure.py <repo> <outdir>"""
import sys, pathlib, json, re
from datetime import date
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

RUNGS = ["broker-failure", "insurer-failure", "clearing-house-failure", "ratings-failure", "capital-controls", "confiscation",
         "financial-repression", "currency-failure", "sovereign-default", "market-failure"]
TEMPLATE = ["What fails", "The backstop", "Where the backstop runs out", "Cases", "What it kills", "Check yourself"]
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
branches = sorted((k for k, v in P.items() if v["parent"] == D["root"]), key=lambda k: P[k]["order"])
check("failure-modes" in branches and branches[branches.index("failure-modes") - 1] == "portfolio" and branches[branches.index("failure-modes") + 1] == "markets", f"When Things Fail sits after Portfolio & Risk, before Markets ({branches})")
check(P["failure-modes"]["group"] == "Putting it together" and P["failure-modes"]["title"] == "When Things Fail", "hub title and group")
check(P["failure-modes"]["children"] == RUNGS, f"all ten rungs, bottom to top ({P['failure-modes']['children']})")
check(all(not P[k]["stub"] and not P[k]["adv"] and P[k]["sources"] for k in ["failure-modes"] + RUNGS), "hub and rungs are written, core and sourced")
stores = {k for k, v in P.items() if v.get("place")}
bad = []
for k in RUNGS:
    t = REPO.joinpath(f"pages/{k}.md").read_text()
    heads = re.findall(r"^## (.+)$", t, re.M)
    if not all(h in heads for h in TEMPLATE): bad.append(f"{k}: missing {[h for h in TEMPLATE if h not in heads]}")
    if t.count("**Q:**") < 2: bad.append(f"{k}: fewer than 2 quizzes")
    cases = t.split("## Cases", 1)[1].split("\n## ", 1)[0] if "## Cases" in t else ""
    if len(re.findall(r"\b(19|20)\d\d\b", cases)) < 3: bad.append(f"{k}: cases not dated")
    kills = t.split("## What it kills", 1)[1].split("\n## ", 1)[0] if "## What it kills" in t else ""
    linked = set(re.findall(r"\[\[([a-z0-9-]+)", kills))
    if len(linked & stores) < 2: bad.append(f"{k}: 'What it kills' links {len(linked & stores)} stores")
check(not bad, f"every rung follows the template: sections, 2 quizzes, dated cases, 2+ stores linked {bad}")

# figures recomputed
txt = {k: REPO.joinpath(f"pages/{k}.md").read_text() for k in RUNGS}
yrs = lambda a, b: (b - a).days / 365.25
check(round(yrs(date(2011, 10, 31), date(2014, 4, 3)) * 2) / 2 == 2.5 and "two and a half years" in txt["broker-failure"], "MF Global: two and a half years from failure to full repayment")
check(int(yrs(date(2015, 6, 29), date(2019, 9, 1))) == 4 and "Just over four years" in txt["capital-controls"], "Greece: controls lasted just over four years")
check(int(yrs(date(2008, 10, 1), date(2017, 3, 14))) == 8 and "more than eight years" in txt["capital-controls"], "Iceland: controls lasted more than eight years")
check(round((1 - (1.01 / 1.04) ** 10) * 4) / 4 == 0.25 and "about a quarter less" in txt["financial-repression"], "1% against 4% inflation for ten years loses about a quarter")
check("53.5%" in txt["sovereign-default"] and "€107 billion" in txt["sovereign-default"], "Greece 2012 figures match the ESM")
check(f"HK${15 + 7.5:.1f} million" in txt["clearing-house-failure"] and 107 / 166 < 114 / 166 and 114 / 166 > 2 / 3 and "Over two-thirds of the €166 million" in txt["clearing-house-failure"], "Hong Kong guarantor's capital adds up; Nasdaq loss is over two-thirds of the fund")
check(f"${400_000 - 250_000:,}" in txt["insurer-failure"], "annuity above the guarantee limit: $150,000 at risk")
check((date(1914, 12, 12) - date(1914, 7, 31)).days > 4 * 30 and "more than four months" in txt["market-failure"], "NYSE 1914 closure lasted more than four months")
check(all(x in txt["market-failure"] for x in ["130 basis points", "£19.3 billion", "4.7%", "1.5%"]), "gilt crisis and Jorion–Goetzmann figures match their sources")
hub = REPO.joinpath("pages/failure-modes.md").read_text()
rows = re.findall(r"^\| (\d+) \| ", hub, re.M)
check(rows == [str(i) for i in range(1, 13)] and "still to be written" not in hub, f"hub ladder has twelve rungs, none left unwritten ({rows})")

# flow
F = D["flows"]
check(len(F) == 7 and "when-a-country-fails" in F, f"seven flows, including When a country fails ({list(F)})")   # 2026-10-26: was 3; flows-branch adds a trade flow and three planned outlines
fl = F["when-a-country-fails"]
steps = fl["steps"]
check(len(steps) == 7 and all(st.get("page") in P for st in steps), f"seven steps, each linked to a page ({len(steps)})")
check({"financial-repression", "capital-controls", "currency-failure", "sovereign-default"} <= {st["page"] for st in steps}, "the flow walks the new rungs")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(500)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            check(pg.locator('#map-svg [data-node="failure-modes"]').count() == 1, f"{w}: the map draws the new branch")
            for k in ["failure-modes"] + RUNGS:
                pg.goto(URL + f"#/map/p/{k}"); pg.wait_for_timeout(150)
                body = pg.locator("#panel-body")
                ok = body.locator(".qa:visible").count() >= 2 and body.locator(".wl.broken").count() == 0 and noscroll()
                if not ok: check(False, f"{w}: {k} renders")
            pg.goto(URL + "#/map/p/failure-modes"); pg.wait_for_timeout(150)
            linked = set(pg.eval_on_selector_all("#panel-body a.wl:visible", "els => els.map(e => e.dataset.page)"))
            check(set(RUNGS) | {"backstops", "stablecoins"} <= linked, f"{w}: hub links every rung and the bank rung")
            pg.goto(URL + "#/flows/when-a-country-fails"); pg.wait_for_timeout(400)
            check(pg.locator("#flows-body").inner_text().count("Greece") >= 1 and noscroll(), f"{w}: the country flow renders with its cases")
            pg.goto(URL + "#/flows"); pg.wait_for_timeout(300)
            check(pg.locator('#flows-body [data-flow="when-a-country-fails"]').count() == 1, f"{w}: the flow is listed")
            for q, want in [("capital controls", "capital-controls"), ("financial repression", "financial-repression"), ("hyperinflation", "currency-failure"),
                            ("restructuring", "sovereign-default"), ("mf global", "broker-failure"), ("failure ladder", "failure-modes"),
                            ("annuities", "insurer-failure"), ("default fund", "clearing-house-failure"), ("enron", "ratings-failure"), ("expropriation", "confiscation"), ("survivorship", "market-failure")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"{w}: search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            if mode == "simple" and w in (1366, 390):
                pg.goto(URL + "#/map/p/capital-controls"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"capital-controls-{w}.png"), full_page=True)
                pg.goto(URL + "#/flows/when-a-country-fails"); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / f"country-flow-{w}.png"), full_page=True)
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
