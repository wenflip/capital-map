"""Dealers and Market Making (Markets & Plumbing): placement, structure, hub and links in, Money & Banking fully mapped,
every worked figure recomputed, checked facts and their credits, timeless and neutral, rendering, depth and search.
Usage: python3 test_dealers.py <repo> <outdir>"""
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

PID = "market-making"
LINKS = {"brokers", "exchanges", "swaps", "liquidity", "money-creation", "monetary-policy", "lender-of-last-resort", "market-failure", "bonds"}
LINKED_FROM = {"markets", "exchanges", "market-failure"}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
p = P[PID]
md = REPO.joinpath(f"pages/{PID}.md").read_text()
body = md.split("---", 2)[2]
basic, deep = body.split("## Going deeper", 1)

# --- placement and structure
kids = P["markets"]["children"]
check(p["parent"] == "markets" and not p["adv"] and not p["stub"], "a written Core page in Markets & Plumbing")
check(kids.index(PID) == kids.index("exchanges") + 1 and kids.index(PID) + 1 == kids.index("brokers"), f"sits between Exchanges and Brokers ({kids})")
check(p["title"] == "Dealers and Market Making" and p["short"] == "Market Making", "title and short label")
heads = re.findall(r"(?m)^## (.+)$", body)
check(heads == ["What it is", "Why it exists", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"sections in order ({heads})")
check(basic.count("**Q:**") == 2 and basic.count("**A:**") == 2 and "**Q:**" not in deep, "two quizzes, both above Going deeper")
check(len(p["text"].split()) >= 400, f"substantial page ({len(p['text'].split())} words)")
check(LINKS <= set(p["links"]), f"links every page it names ({sorted(LINKS - set(p['links']))} missing)")
check(LINKED_FROM <= set(p["backlinks"]), f"linked from the hub and related pages ({sorted(LINKED_FROM - set(p['backlinks']))} missing)")
check("[[market-making]]" in REPO.joinpath("pages/markets.md").read_text().split("## Going deeper")[0], "the Markets hub links the page in its Core part")
check("broker is your agent" in basic and "*is* the someone else" in basic, "draws the line between a broker and a dealer")

# --- quals: Money & Banking fully mapped
mb = D["quals"]["money-banking"]
mb3 = [st for st in mb["stages"] if st["title"].startswith("MB3")][0]
check(any(i["page"] == PID for i in mb3["items"]) and not mb3["note"], "MB3 lists the page and has no Partly mapped note")
check(mb["coverage"]["mapped"] == 6 and mb["coverage"]["partial"] == 0, f"Money & Banking: all six modules mapped ({mb['coverage']})")

# --- worked figures, recomputed
num = lambda x: f"{x:,.0f}"
check(f"0.20 × 1,000 = **{num((100.10 - 99.90) * 1000)}**" in basic, "spread earned: 0.20 × 1,000 = 200")
check(f"1,000 × 0.50 = **{num(1000 * 0.50)}**" in basic and "more than two round trips" in basic and 500 / 200 > 2, "inventory loss 500, more than two round trips of 200")
check(f"0.10 × 2,000 = **{num(round((50.05 - 49.95) * 2000))}**" in basic, "quiz: a round trip costs 200")
check(basic.count("fictional figures") >= 1, "worked figures are labelled fictional")

# --- checked facts and their credits
for a, b2 in [("March 2020", "balance sheet limits"), ("15 March", "$500 billion"), ("23 March", '"in the amounts needed"'), ("1987", "Jack Treynor")]:
    check(a in body and b2 in body, f"fact present: {a}")
src = " ".join(p["sources"])
for c in ["Treynor", "Mehrling", "Monetary Policy Report"]:
    check(c in src, f"credits {c}")

# --- timeless and neutral
check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", body, re.I), "timeless: no 'today' or 'currently'")
check(not re.search(r"\byou should (buy|sell|hold|use)\b", body, re.I), "no advice")

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
            check(pg.locator(".p-title").inner_text() == "Dealers and Market Making", "the page opens in the panel")
            check(body_el.locator(".qa").count() == 2, "two quizzes render")
            check(body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text(), "no broken links, no raw link syntax")
            check(body_el.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
            check(pg.locator(f'#map-svg [data-node="{PID}"]').count() == 1, "the page is on the map")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"dealers-{w}.png"))
            for q, top in [("market maker", 1), ("market making", 1), ("dealer", 1), ("bid-ask spread", 1), ("inventory", 3)]:
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
