"""Monetary Policy (How Money Works): placement, structure, hub and links in, quals, every worked figure recomputed,
checked facts and their credits, timeless and neutral, rendering, depth and search. Usage: python3 test_monpol.py <repo> <outdir>"""
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

PID = "monetary-policy"
LINKS = {"central-bank-money", "lender-of-last-resort", "inflation", "t-bills", "bonds", "time-value-of-money", "exchange-rates",
         "liquidity", "yield-curve", "financial-repression", "currency-failure", "money-creation", "market-regimes"}
LINKED_FROM = {"money", "central-bank-money", "inflation", "yield-curve"}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
p = P[PID]
md = REPO.joinpath(f"pages/{PID}.md").read_text()
body = md.split("---", 2)[2]
basic, deep = body.split("## Going deeper", 1)

# --- placement and structure
kids = P["money"]["children"]
check(p["parent"] == "money" and not p["adv"] and not p["stub"], "a written Core page in Money & Liquidity")
# 2026-10-27 money-you-hold branch: Cash and Fiat moved to Money You Hold
check(kids.index(PID) == kids.index("central-bank-money") + 1 and kids.index(PID) + 1 == kids.index("exchange-rates"),
      f"sits after Central Bank Money and before Exchange Rates ({kids})")
check(p["title"] == "Monetary Policy", "title")
heads = re.findall(r"(?m)^## (.+)$", body)
check(heads == ["What it is", "Why it exists", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"sections in order ({heads})")
check(basic.count("**Q:**") == 2 and basic.count("**A:**") == 2 and "**Q:**" not in deep, "two quizzes, both above Going deeper")
check(len(p["text"].split()) >= 400, f"substantial page ({len(p['text'].split())} words)")
check(LINKS <= set(p["links"]), f"links every page it names ({sorted(LINKS - set(p['links']))} missing)")
check(LINKED_FROM <= set(p["backlinks"]), f"linked from the hub and related pages ({sorted(LINKED_FROM - set(p['backlinks']))} missing)")
check("[[monetary-policy]]" in REPO.joinpath("pages/money.md").read_text().split("## Going deeper")[0], "the Money hub links the page in its Core part")
check("*QE and QT*" in basic, "names the QE and QT flow")

# --- quals
def mods(q): return {st["title"].split(" — ")[0] for st in D["quals"][q]["stages"] if any(i["page"] == PID for i in st["items"])}
check(mods("cfa-l1") == {"CFA1-ECON"} and mods("money-banking") == {"MB6"}, f"mapped to CFA1-ECON and MB6 ({mods('cfa-l1')}, {mods('money-banking')})")

# --- worked figures, recomputed
check(f"200,000 × 2% = **{200_000 * 0.02:,.0f}**" in basic, "loan: 2 points on 200,000 is 4,000 a year")
r = 1.05 / 1.03
check(f"5% − 3% = 2%" in basic and f"1.05 ÷ 1.03 = {r:.3f}" in basic and f"**{100 * (r - 1):.1f}%**" in basic, f"real rate: {100 * (r - 1):.2f}%")
q = 1.01 / 1.04
check("1% − 4% = −3%" in basic and f"1.01 ÷ 1.04 = {q:.3f}" in basic and f"**−{100 * (1 - q):.1f}%**" in basic, f"quiz real rate: {100 * (q - 1):.2f}%")
taylor = 2 + 3 + 0.5 * (3 - 2) + 0.5 * 1
check(f"2% + 3% + 0.5 × (3% − 2%) + 0.5 × 1% = **{taylor:.0f}%**" in deep, f"Taylor rule example: {taylor}%")
check(body.count("fictional figures") >= 3, "worked figures are labelled fictional")

# --- checked facts and their credits
facts = [("February 1990", "New Zealand"), ("January 2012", "2%"), ("11 June 2014", "−0.10%"), ("19 March 2024", "seventeen years"),
         ("11.6% in March 1980", "October 1979"), ("record 20% in late 1980", "federal funds"), ("1993", "John Taylor")]
for a, b2 in facts: check(a in body and b2 in body, f"fact present: {a}")
src = " ".join(p["sources"])
for c in ["FOMC", "McDermott and Williams", "European Central Bank", "Bank of Japan", "Volcker", "Taylor"]:
    check(c in src, f"credits {c}")

# --- timeless and neutral
check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", body, re.I), "timeless: no 'today' or 'currently'")
check(not re.search(r"\byou should (buy|sell|hold)\b", body, re.I), "no advice")
check(not re.search(r"\b(rates will|the next (cut|hike)|expect(s|ed)? rates to)\b", body, re.I), "no forecast of rates")

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
            check(pg.locator(".p-title").inner_text() == "Monetary Policy", "the page opens in the panel")
            check(body_el.locator(".qa").count() == 2, "two quizzes render")
            check(body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text(), "no broken links, no raw link syntax")
            check(body_el.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
            check(pg.locator(f'#map-svg [data-node="{PID}"]').count() == 1, "the page is on the map")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"monpol-{w}.png"))
            for q, top in [("monetary policy", 1), ("policy rate", 1), ("negative rates", 1), ("forward guidance", 1), ("real rate", 3)]:
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
