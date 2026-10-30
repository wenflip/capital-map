"""Swaps (Derivatives): placement, structure, hub and links in, MB5 fully mapped, every worked figure recomputed, checked facts
and their credits, timeless and neutral, rendering, depth and search. Usage: python3 test_swaps.py <repo> <outdir>"""
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

PID = "swaps"
LINKS = {"futures", "bonds", "yield-curve", "credit-risk", "exchange-rates", "eurodollars", "leverage", "settlement",
         "clearing-house-failure", "derivatives", "time-value-of-money"}
LINKED_FROM = {"derivatives", "credit-risk", "eurodollars", "exchange-rates"}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
p = P[PID]
md = REPO.joinpath(f"pages/{PID}.md").read_text()
body = md.split("---", 2)[2]
basic, deep = body.split("## Going deeper", 1)

# --- placement and structure
kids = P["derivatives"]["children"]
check(p["parent"] == "derivatives" and not p["adv"] and not p["stub"], "a written Core page in Derivatives")
check(kids.index(PID) == kids.index("options") + 1, f"sits after Options ({kids})")
check(p["title"] == "Swaps", "title")
heads = re.findall(r"(?m)^## (.+)$", body)
check(heads == ["What it is", "Why it exists", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"sections in order ({heads})")
check(basic.count("**Q:**") == 2 and basic.count("**A:**") == 2 and "**Q:**" not in deep, "two quizzes, both above Going deeper")
check(len(p["text"].split()) >= 400, f"substantial page ({len(p['text'].split())} words)")
check(LINKS <= set(p["links"]), f"links every page it names ({sorted(LINKS - set(p['links']))} missing)")
check(LINKED_FROM <= set(p["backlinks"]), f"linked from the hub and related pages ({sorted(LINKED_FROM - set(p['backlinks']))} missing)")
hub = REPO.joinpath("pages/derivatives.md").read_text()
hb, hd = hub.split("## Going deeper")
check("[[swaps]]" in hb and "**Swaps.**" not in hd, "the hub links Swaps in its Core part, and the old Going deeper note is gone")
for k in ["Interest-rate swap", "Currency swap", "Credit default swap", "Total return swap"]:
    check(f"**{k}**" in basic, f"the table names {k}")

# --- quals: MB5 fully mapped, CFA I derivatives
mb5 = [st for st in D["quals"]["money-banking"]["stages"] if st["title"].startswith("MB5")][0]
check(any(i["page"] == PID for i in mb5["items"]) and "partly" not in re.sub(r"<[^>]+>", "", mb5["note"]).lower(), "MB5 lists Swaps and is no longer Partly mapped")
drm = [st for st in D["quals"]["cfa-l1"]["stages"] if st["title"].startswith("CFA1-DRM")][0]
check(any(i["page"] == PID for i in drm["items"]), "CFA I Derivatives lists Swaps")

# --- worked figures, recomputed
N, fixed = 10_000_000, 0.04
num = lambda x: f"{x:,.0f}"
check(f"(4% − 3%) × 10,000,000 = **{num(N * (fixed - 0.03))}**" in basic, f"pay-fixed year at 3%: pays {num(N * (fixed - 0.03))}")
check(f"(5.5% − 4%) × 10,000,000 = **{num(N * (0.055 - fixed))}**" in basic, f"year at 5.5%: receives {num(N * (0.055 - fixed))}")
allin = 0.01 + fixed
check(f"1% + 4% = **{allin * 100:.0f}%**" in basic and f"**{num(N * allin)}** a year" in basic, f"hedged loan: {allin:.0%} all-in, {num(N * allin)} a year")
cds_prem, rec = 0.02, 0.40
check(f"**{num(N * cds_prem)}** a year" in basic, f"CDS premium {num(N * cds_prem)} a year")
check(f"10,000,000 × (1 − 0.40) = **{num(N * (1 - rec))}**" in basic, f"CDS payout {num(N * (1 - rec))}")
qn, qf, qr = 5_000_000, 0.03, 0.042
check(f"(4.2% − 3%) × 5,000,000 = **{num(qn * (qr - qf))}**" in basic, f"quiz: receives {num(qn * (qr - qf))}")
check(basic.count("fictional figures") >= 2, "worked figures are labelled fictional")

# --- checked facts and their credits
facts = [("30 June 2023", "LIBOR"), ("end of 2021", "Sterling LIBOR"), ("SOFR", "SONIA"), ("September 2009", "G20"),
         ("16 September 2008", "$85 billion"), ("March 2021", "more than $10 billion")]
for a, b2 in facts: check(a in body and b2 in body, f"fact present: {a}")
src = " ".join(p["sources"])
for c in ["FCA", "G20", "AIG", "Archegos"]:
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
            check(pg.locator(".p-title").inner_text() == "Swaps", "the page opens in the panel")
            check(body_el.locator("table").count() == 1 and body_el.locator(".qa").count() == 2, "the kinds-of-swap table and two quizzes render")
            check(body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text(), "no broken links, no raw link syntax")
            check(body_el.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
            check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
            check(pg.locator(f'#map-svg [data-node="{PID}"]').count() == 1, "the page is on the map")
            if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"swaps-{w}.png"))
            for q, top in [("swaps", 1), ("interest rate swap", 1), ("credit default swap", 1), ("cds", 1), ("total return swap", 1)]:
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
