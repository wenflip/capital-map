"""The broker-failure and stablecoin-run flows, written out: status, lanes and steps, every dated case in its Where it
happened column and credited, links to the ladder and the right pages, the rung order stated correctly, timeless and
neutral, the SQLite export, the flow views and search. Usage: python3 test_failflows.py <repo> <outdir>"""
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

LANES = ["What happens", "What you hold", "What can go wrong", "Where it happened"]
SPEC = {
    "when-a-broker-fails": {
        "pages": ["brokers", "broker-failure", "custody", "broker-failure", "claims-and-liabilities"],
        "facts": ["31 October 2011", "$1.6 billion", "11 December 2008", "$500,000", "$250,000", "2014", "November 2022"],
        "credits": ["MF Global", "Madoff", "What SIPC Protects", "FTX"],
        "notice": {"custody", "custodial-crypto"},
        "search": ["broker fails", "getting your assets back"],
    },
    "a-stablecoin-run": {
        "pages": ["stablecoins", "stablecoins", "liquidity", "t-bills", "defi", "claims-and-liabilities"],
        "facts": ["$3.3 billion", "87 cents", "11 March 2023", "May 2022", "88 cents", "12 March 2023"],
        "credits": ["CNBC", "The Block", "Joint statement", "Benzinga"],
        "notice": {"backstops", "bank-sovereign-loop"},
        "search": ["stablecoin run", "dollar peg"],
    },
}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
for fid, sp in SPEC.items():
    F = D["flows"][fid]
    src = REPO.joinpath(f"flows/{fid}.md").read_text()
    check(F["status"] == "written" and "status:" not in src.split("---", 2)[1], f"{fid}: written, no planned status left")
    check(F["area"] == "When Things Fail", f"{fid}: under When Things Fail")
    check(F["lanes"] == LANES, f"{fid}: four detail columns ({F['lanes']})")
    check([st["page"] for st in F["steps"]] == sp["pages"], f"{fid}: steps open the same pages as the outline did")
    check(all(len(st["cells"]) == 4 and all(c.strip() for c in st["cells"][:3]) for st in F["steps"]), f"{fid}: every step fills its first three columns")
    check(not [st["page"] for st in F["steps"] if P[st["page"]]["adv"]], f"{fid}: every step opens a Core page")
    where = " ".join(st["cells"][3] for st in F["steps"])
    for f in sp["facts"]: check(f in where, f"{fid}: verified case in Where it happened: {f}")
    srcs = src.split("*Sources:", 1)[1] if "*Sources:" in src else ""
    for c in sp["credits"]: check(c in srcs, f"{fid}: credits {c}")
    check("[[failure-modes|failure ladder]]" in src and "**Key rule:**" in src, f"{fid}: links the failure ladder and states a key rule")
    notice = set(re.findall(r"\[\[([^\]|]+)", src.split("## What to notice")[1].split("*Sources:")[0]))
    check(sp["notice"] <= notice, f"{fid}: What to notice links {sorted(sp['notice'])}")
    check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", src, re.I), f"{fid}: timeless")
    check(not re.search(r"\b(you should|is (safe|safer|the best))\b", src, re.I), f"{fid}: no advice and no verdict")
    check(db.execute("SELECT status FROM flows WHERE id = ?", (fid,)).fetchone() == ("written",)
          and db.execute("SELECT COUNT(*) FROM flow_steps WHERE flow_id = ?", (fid,)).fetchone() == (len(sp["pages"]),), f"{fid}: SQLite rows")
db.close()

# the rung order is stated the right way round: banks are rung 4, stablecoins rung 3, so the bank sits above
st = REPO.joinpath("flows/a-stablecoin-run.md").read_text()
check(P["backstops"]["rung"] == 4 and P["stablecoins"]["rung"] == 3 and "one rung above stablecoins" in st and "lower rung" not in st, "stablecoin flow places the bank one rung above")
check("backed partly by USDC" in st, "DAI described as backed partly (not mainly) by USDC, as the source says")

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
            for fid, sp in SPEC.items():
                pg.goto(URL + f"#/flows/{fid}"); pg.wait_for_timeout(350)
                n = len(sp["pages"])
                check(pg.locator(".step-card").count() == n and pg.locator(".planned-tag").count() == 0 and pg.locator(".flow-outline-note").count() == 0, f"{fid}: {n} steps, no Planned tag, no outline note")
                check(pg.locator(".lane-label:not(.head)").count() == 4 and pg.locator("#flows-body .wl.broken").count() == 0 and noscroll(), f"{fid}: four detail rows, links ok, no page scroll")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"flow-{fid}-{w}.png"), full_page=True)
                pg.locator(f'.step-card[data-page="{sp["pages"][-1]}"]').first.click(); pg.wait_for_timeout(400)
                check(f"p/{sp['pages'][-1]}" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, f"{fid}: a step opens its page beside the flow")
                for q in sp["search"]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(250)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                    check(f"#/flows/{fid}" in hrefs, f"search '{q}' finds {fid} ({hrefs[:3]})")
                    pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
