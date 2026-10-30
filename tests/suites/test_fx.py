"""Currencies and Exchange Rates (How Money Works): placement, structure, links in and out, quals, every worked figure
recomputed, checked facts and their credits, timeless and neutral, rendering, depth and search. Usage: python3 test_fx.py <repo> <outdir>"""
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

PID = "exchange-rates"
LINKS = {"cash-and-fiat", "hierarchy-of-money", "eurodollars", "currency-failure", "capital-controls", "diversification",
         "inflation", "futures", "sovereign-default"}
LINKED_FROM = {"money", "cash-and-fiat", "eurodollars", "currency-failure"}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
p = P[PID]
md = REPO.joinpath(f"pages/{PID}.md").read_text()
body = md.split("---", 2)[2]
basic, deep = body.split("## Going deeper", 1)

# --- placement and structure
kids = P["money"]["children"]
check(p["parent"] == "money" and not p["adv"] and not p["stub"], "a written Core page in Money & Liquidity")
# 2026-10-27 money-you-hold branch: Cash and Fiat and Bank Deposits moved to Money You Hold
check(kids.index(PID) == kids.index("monetary-policy") + 1 and kids.index(PID) + 1 == kids.index("eurodollars"),
      f"sits after Monetary Policy and before Eurodollars ({kids})")
check(p["title"] == "Currencies and Exchange Rates" and p["short"] == "Exchange Rates", "title and short label")
heads = re.findall(r"(?m)^## (.+)$", body)
check(heads == ["What it is", "Why it matters", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"sections in order ({heads})")
check(basic.count("**Q:**") == 2 and basic.count("**A:**") == 2 and "**Q:**" not in deep, "two quizzes, both above Going deeper")
check(len(p["text"].split()) >= 400, f"substantial page ({len(p['text'].split())} words)")
check(LINKS <= set(p["links"]), f"links every page it names ({sorted(LINKS - set(p['links']))} missing)")
check(LINKED_FROM <= set(p["backlinks"]), f"linked from the hub and related pages ({sorted(LINKED_FROM - set(p['backlinks']))} missing)")
hub = REPO.joinpath("pages/money.md").read_text()
check("[[exchange-rates]]" in hub.split("## Going deeper")[0], "the Money hub links the page in its Core part")
# 2026-10-26 swaps branch: the Swaps page now exists, so the FX swaps note links it (was: "no link to a page that doesn't exist yet")
check("[[swaps]]" in deep, "the FX swaps note in Going deeper links the Swaps page")

# --- quals
def mods(q): return {st["title"].split(" — ")[0] for st in D["quals"][q]["stages"] if any(i["page"] == PID for i in st["items"])}
check(mods("money-banking") == {"MB4"} and mods("cfa-l1") == {"CFA1-ECON"}, f"mapped to MB4 and CFA1-ECON ({mods('money-banking')}, {mods('cfa-l1')})")

# --- worked figures, recomputed
check("1 ÷ 1.25 = **0.80**" in basic and abs(1 / 1.25 - 0.80) < 1e-9, "inverting a quote: 1 / 1.25 = 0.80")
fund, down, up = 0.08, 0.05, 0.05
r1, r2 = (1 + fund) * (1 - down) - 1, (1 + fund) * (1 + up) - 1
check(f"1.08 × 0.95 = {1 + r1:.3f}" in basic and f"**{100 * r1:.1f}%**" in basic, f"currency loss: 1.08 × 0.95 → {100 * r1:.1f}%")
check(f"1.08 × 1.05 = {1 + r2:.3f}" in basic and f"**{100 * r2:.1f}%**" in basic, f"currency gain: 1.08 × 1.05 → {100 * r2:.1f}%")
spot, ia, ib = 1.20, 0.02, 0.05
fwd = spot * (1 + ib) / (1 + ia)
check(f"1.20 × 1.05 ÷ 1.02 = **{fwd:.3f}**" in basic, f"forward rate recomputed ({fwd:.4f})")
check(fwd > spot and "buys less in the forward" in basic, "the higher-rate currency buys less in the forward")
q = 1.10 * 0.90 - 1
check(f"1.10 × 0.90 = {1 + q:.2f}" in basic and f"lost **{-100 * q:.0f}%**" in basic, f"quiz: 1.10 × 0.90 → lost {-100 * q:.0f}%")
check(basic.count("fictional figures") >= 2 and "illustrative figure, not a real rate" in basic, "worked figures are labelled fictional or illustrative")

# --- checked facts and their credits
facts = [("$9.6 trillion a day", "April 2025"), ("89%", "one side"), ("16 September 1992", "European Exchange Rate Mechanism"),
         ("15 January 2015", "1.20 to the euro"), ("31%", "FX swaps")]
for a, b in facts: check(a in body and b in body, f"fact present: {a}")
src = " ".join(p["sources"])
for c in ["Triennial Central Bank Survey", "Swiss National Bank", "Econlib", "Covered interest parity lost"]:
    check(c in src, f"credits {c}")

# --- timeless and neutral
check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", body, re.I), "timeless: no 'today' or 'currently'")
check(not re.search(r"\byou should (buy|sell|hold|hedge)\b", body, re.I) and not re.search(r"\b(best|safest) currency\b", body, re.I), "no advice and no currency named a winner")

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
            check(pg.locator(".p-title").inner_text() == "Currencies and Exchange Rates", "the page opens in the panel")
            check(body_el.locator("table").count() == 1 and body_el.locator(".qa").count() == 2, "the regimes table and two quizzes render")
            check(body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text(), "no broken links, no raw link syntax")
            check(body_el.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
            check(pg.locator(f'#map-svg [data-node="{PID}"]').count() == 1, "the page is on the map")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"fx-{w}.png"))
            for q, top in [("exchange rate", 1), ("forex", 1), ("fx", 1), ("currency peg", 1), ("carry trade", 3)]:
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
