"""Accuracy branch: doc drift fixed, corrected facts, and a 'How it has failed' history on every store of wealth. Usage: python3 test_accuracy.py <repo> <outdir>"""
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

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
stores = sorted(k for k, v in P.items() if v.get("place"))
check(len(stores) == 12, f"twelve stores on the chart ({len(stores)})")

# --- doc drift
scope = REPO.joinpath("SCOPE.md").read_text(); readme = REPO.joinpath("README.md").read_text()
check("later build" not in scope and "Written: Money & Liquidity, Foundation" not in scope, "SCOPE no longer calls the Cartography view a later build or lists two branches written")
nb = len(P[D["root"]]["children"])
check(scope.count("**Written.**") == nb, f"SCOPE marks all {nb} branches written ({scope.count('**Written.**')})")
check("Empty for now" not in readme and "first branch written" not in readme, "README no longer says quals are empty or one branch is written")
model = REPO.joinpath("pages/cartography-of-wealth.md").read_text()
rows = re.findall(r"^\| \d+ \| \[\[([a-z0-9-]+)", model, re.M)
check("Ten stores" not in model and "## The twelve stores" in model and sorted(rows) == stores, f"the model page lists the same twelve stores as the chart ({len(rows)})")

# --- corrected facts
bail = REPO.joinpath("pages/bail-in.md").read_text(); back = REPO.joinpath("pages/backstops.md").read_text()
check("October 2025" in bail and "Federal Supreme Court" in bail and "unlawful" in back, "Credit Suisse cases carry the 2025 court ruling and the appeal")
check("about 14 times" in back and "over 11 times" not in back, "Iceland's banks sized at about 14 times output (CRS)")
check("ruled unlawful" in REPO.joinpath("flows/when-a-bank-fails.md").read_text(), "the bank-failure flow carries the caveat")

# --- neutrality: every store shows its own failure history
bad = []
for k in stores:
    t = REPO.joinpath(f"pages/{k}.md").read_text()
    if "## How it has failed" not in t: bad.append(f"{k}: no history"); continue
    sec = t.split("## How it has failed", 1)[1].split("\n## ", 1)[0]
    items = [ln for ln in sec.splitlines() if ln.startswith("- **")]
    dated = [ln for ln in items if re.search(r"\b(1[89]\d\d|20[0-2]\d)\b", ln)]
    if len(items) < 3 or len(dated) < 1: bad.append(f"{k}: {len(items)} cases, {len(dated)} dated")
    if t.index("## How it has failed") > t.index("## Check yourself"): bad.append(f"{k}: history below the quiz")
    if not P[k]["sources"]: bad.append(f"{k}: no sources")
check(not bad, f"every store has 3+ failure cases, at least one dated, above its quiz, with sources {bad}")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(450)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            vis_bad = []
            for k in stores:
                pg.goto(URL + f"#/map/p/{k}"); pg.wait_for_timeout(120)
                heads = [x.lower() for x in pg.locator("#panel-body h2:visible").all_inner_texts()]
                if "how it has failed" not in heads: vis_bad.append(k)
                if pg.locator("#panel-body .wl.broken").count() or not noscroll(): vis_bad.append(k + ":render")
            check(not vis_bad, f"history section visible on every store page in {'Core' if mode == 'simple' else 'Everything'} {vis_bad}")
            pg.goto(URL + "#/map/p/gold"); pg.wait_for_timeout(150)
            check(pg.locator("#panel-body .qa:visible").count() >= 1, "Gold now has a quiz")
            for q, want in [("6102", "gold"), ("corralito", "bank-deposits"), ("nikkei", "shares"), ("carillion", "private-business"), ("weimar", "cash-and-fiat")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            if mode == "simple" and w in (1366, 390): pg.goto(URL + "#/map/p/bonds"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"bonds-history-{w}.png"), full_page=True)
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
