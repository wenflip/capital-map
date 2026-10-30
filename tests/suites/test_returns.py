"""Four Ways to Earn a Return (Foundation): placement, structure, links, worked figures recomputed, neutrality, an IP guard
against the source study notes' wording, rendering and search. Usage: python3 test_returns.py <repo> <outdir>"""
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

PID = "four-ways-to-earn"
LINKS = {"claims-and-liabilities", "human-capital", "risk-and-return", "cartography-of-wealth", "t-bills", "bonds", "bank-deposits",
         "real-estate", "shares", "private-business", "futures", "options", "gold", "time-value-of-money"}
# distinctive wording from the study-notes PDF the idea came from: the page uses the idea only, in our own words
SOURCE_PHRASES = ["costume", "collapses into the grid", "different animal", "same organism", "priced bets", "taken to win",
                  "airtight", "spine of all markets", "loansharking", "supplying it earn", "only your read on price"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
p = P[PID]
md = REPO.joinpath(f"pages/{PID}.md").read_text()
body = md.split("---", 2)[2]
basic, deep = body.split("## Going deeper", 1)

# --- placement and structure
kids = P["foundation"]["children"]
check(p["parent"] == "foundation" and not p["adv"] and not p["stub"], "a written Core page in Foundation")
check(kids.index(PID) == kids.index("cartography-of-wealth") + 1 and kids.index(PID) + 1 == kids.index("time-value-of-money"),
      f"sits after the Cartography and before Time Value of Money ({kids})")
check(p["title"] == "Four Ways to Earn a Return" and p["short"] == "Four Ways to Earn", "title and short label")
heads = re.findall(r"(?m)^## (.+)$", body)
check(heads == ["What it is", "Why it matters", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"sections in order ({heads})")
check(basic.count("**Q:**") == 2 and basic.count("**A:**") == 2 and "**Q:**" not in deep, "two quizzes, both above Going deeper")
check(len(p["text"].split()) >= 400, f"substantial page ({len(p['text'].split())} words)")
check(LINKS <= set(p["links"]), f"links every page it names ({sorted(LINKS - set(p['links']))} missing)")
check({"foundation", "claims-and-liabilities", "risk-and-return"} <= set(p["backlinks"]), f"linked from the hub, Claims and Liabilities, and Risk and Return ({p['backlinks']})")
check("Study notes" in p["sources"] and any("Wealth of Nations" in x and "1776" in x for x in p["sources"]), f"credits Study notes and Smith ({p['sources']})")
hub = REPO.joinpath("pages/foundation.md").read_text()
check("[[four-ways-to-earn]]" in hub.split("## Going deeper")[0], "the Foundation hub links the page in its Core part")
check("twelve stores of wealth" in hub and "ten stores of wealth" not in hub, "the hub's store count is corrected to twelve")

# --- the four ways and transfers
t = p["text"]
for w in ["Labour", "Lending", "Ownership", "Price and risk", "transfer"]:
    check(w in t, f"names {w}")
check("Pure price bets" in t and "Being paid to carry risk" in t, "splits the fourth way into price bets and being paid to carry risk")
check("Classify the mechanism, not the asset" in t, "states the rule: classify the mechanism, not the asset")

# --- worked figures, recomputed
num = lambda x: f"{x:,}"
cost, rent, years, sale = 200_000, 9_000, 5, 230_000
lend, price = years * rent, sale - cost
check(f"{years} × {num(rent)} = **{num(lend)}**" in basic and f"{num(sale)} − {num(cost)} = **{num(price)}**" in basic, f"worked example: rent {lend}, price {price}")
check(f"**{num(lend + price)}**" in basic and f"{round(100 * lend / (lend + price))}% from letting and {round(100 * price / (lend + price))}% from the price" in basic, "worked example: total and the 60/40 split")
alt = 190_000
check(f"sold for {num(alt)}" in basic and f"lost {num(cost - alt)}" in basic and f"earned {num(lend)}" in basic, "worked example: the falling-price case")
qc, qr, qy, qs = 150_000, 6_000, 4, 140_000
check(f"{qy} × {num(qr)} = {num(qy * qr)}" in basic and f"{num(qc)} − {num(qs)} = {num(qc - qs)}" in basic and f"made {num(qy * qr - (qc - qs))}" in basic, "quiz: rent, price loss and total recomputed")

# --- neutrality and IP guard
check("speculation" not in md.lower(), "classifies mechanisms with neutral names (no 'speculation' label)")
check(not re.search(r"(crypto|gold|forex)[^.]{0,40}\bis (a )?(bet|gamble)", md, re.I), "no asset class is called a bet")
hits = [(f.name, ph) for f in REPO.rglob("*") if f.is_file() and f.suffix in (".md", ".js", ".html", ".sql") and ".git" not in f.parts
        for ph in SOURCE_PHRASES if ph.lower() in f.read_text(errors="ignore").lower()]
check(not hits, f"none of the source notes' distinctive wording appears anywhere in the repo ({hits[:3]})")

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
            pg.goto(URL + f"#/map/p/{PID}"); pg.wait_for_timeout(500)
            body_el = pg.locator("#panel-body")
            check(pg.locator(".p-title").inner_text() == "Four Ways to Earn a Return", "the page opens in the panel")
            check(body_el.locator("table").count() == 2 and body_el.locator(".qa").count() == 2, "two tables and two quizzes render")
            check(body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text(), "no broken links, no raw link syntax")
            check(body_el.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
            check(pg.locator(f'#map-svg [data-node="{PID}"]').count() == 1, "the page is on the map")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"four-ways-{w}.png"))
            for q, top in [("ways to earn", 1), ("make money", 1), ("four ways", 1), ("making money", 3)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{PID}" in hrefs[:top], f"search '{q}' puts the page {'first' if top == 1 else 'in the top ' + str(top)} ({hrefs})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
