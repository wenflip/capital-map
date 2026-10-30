"""QE and QT flow, written out: status, lanes and steps, every dated case in its cells and credited, links both ways
with Monetary Policy, timeless and neutral, the SQLite export, the flow view at both depths and search. Usage: python3 test_qe.py <repo> <outdir>"""
import sys, pathlib, json, re, sqlite3
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

FID = "qe-and-qt"
LANES = ["What happens", "Who holds what", "What can go wrong", "Where it happened"]
PAGES = ["monetary-policy", "bank-deposits", "bond-pricing", "yield-curve", "liquidity", "central-bank-money", "liquidity"]
FACTS = ["5 March 2009", "£75 billion", "0.5%", "25 November 2008", "$500 billion", "$100 billion", "1 June 2022",
         "29 October 2025", "1 December 2025", "28 September 2022", "17 September 2019", "5.25%", "2.1%"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
F = D["flows"][FID]
src = REPO.joinpath(f"flows/{FID}.md").read_text()

# --- structure
check(F["status"] == "written" and "status:" not in src.split("---", 2)[1], "written, with no planned status left in the file")
check(F["area"] == "How Money Works", "under the How Money Works heading")   # 2026-10-27 text sweep: the flows heading follows the branch's new name
check(F["lanes"] == LANES, f"four detail columns ({F['lanes']})")
check([st["page"] for st in F["steps"]] == PAGES, f"seven steps open the right pages ({[st['page'] for st in F['steps']]})")
check(all(len(st["cells"]) == len(LANES) and all(c.strip() for c in st["cells"][:3]) for st in F["steps"]), "every step fills its first three columns")
check(not [st["page"] for st in F["steps"] if P[st["page"]]["adv"]], "every step opens a Core page, so the flow works in Core view")
check("clearing-house-failure" not in PAGES and "market-failure" not in PAGES, "a normal process step never opens a failure page")

# --- dated cases, all in the Where it happened column, all credited
where = " ".join(st["cells"][3] for st in F["steps"])
for f in FACTS: check(f in where, f"verified case in Where it happened: {f}")
srcs = src.split("*Sources:", 1)[1] if "*Sources:" in src else ""
for c in ["Bank of England", "£75bn", "Federal Reserve, press release (25 November 2008)", "policy normalization", "gilt market operation", "Richmond"]:
    check(c in srcs, f"credits {c}")

# --- links both ways, timeless and neutral
check("[[monetary-policy]]" in src and "*QE and QT*" in REPO.joinpath("pages/monetary-policy.md").read_text(), "the flow links Monetary Policy, and the page names the flow")
check({"duration", "market-failure", "central-bank-money"} <= set(re.findall(r"\[\[([^\]|]+)", src.split("## What to notice")[1])), "What to notice links Duration, Market Failure and Central Bank Money")
check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", src, re.I), "timeless: no 'today' or 'currently'")
check(not re.search(r"\b(you should|will (rise|fall)|is (good|bad) for)\b", src, re.I), "no advice, forecast or verdict")

# --- SQLite export
db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
check(db.execute("SELECT status FROM flows WHERE id = ?", (FID,)).fetchone() == ("written",), "SQLite: the flow is written")
check(db.execute("SELECT COUNT(*) FROM flow_steps WHERE flow_id = ?", (FID,)).fetchone() == (7,), "SQLite: seven steps")
db.close()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

            pg.goto(URL + "#/flows"); pg.wait_for_timeout(350)
            check(pg.locator(f'#flows-body .flow-card[data-flow="{FID}"]:not(.planned)').count() == 1, "the card is no longer marked Planned")
            pg.goto(URL + f"#/flows/{FID}"); pg.wait_for_timeout(350)
            check(pg.locator(".step-card").count() == 7 and pg.locator(".planned-tag").count() == 0 and pg.locator(".flow-outline-note").count() == 0, "7 steps, no Planned tag, no outline note")
            check(pg.locator(".lane-label:not(.head)").count() == 4, "four detail rows")
            check(pg.locator("#flows-body .wl.broken").count() == 0 and noscroll(), "links ok, no page scroll")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"flow-qe-{w}.png"), full_page=True)
            pg.locator('.step-card[data-page="yield-curve"]').click(); pg.wait_for_timeout(400)
            check("p/yield-curve" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, "a step opens its page beside the flow")
            for q in ["QE and QT", "quantitative easing", "quantitative tightening"]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/flows/{FID}" in hrefs, f"search '{q}' finds the flow ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
