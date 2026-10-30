"""How to Think (16th branch) and its related pages elsewhere on the map. Checks the structure now, and checks every
planned page automatically once it exists (pages are written in batches by a second AI and reviewed): the right parent and
order, the standard sections, quizzes above Going deeper, length, a key rule, timeless and neutral voice, sources for any
dated fact, fictional labels on worked figures, links in, the hub linking its children, and no lifted book anecdotes.
Worked figures and dated facts on each new page are also checked by hand at review.
Usage: python3 test_howtothink.py <repo> <outdir>"""
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

HUB = "how-to-think"
# id: (parent, order, level). The plan agreed on 2026-10-27; update here if the plan changes (say so in the PR).
PLAN = {
    "second-order-thinking": (HUB, 1, ""), "opportunity-cost": (HUB, 2, ""), "edge": (HUB, 3, ""), "luck-and-skill": (HUB, 4, ""),
    "time-horizons": (HUB, 5, ""), "margin-of-safety": (HUB, 6, ""), "incentives": (HUB, 7, ""), "externalities": (HUB, 8, ""),
    "averages-and-distributions": (HUB, 9, ""), "absolute-and-relative-risk": (HUB, 10, ""), "false-precision": (HUB, 11, ""),
    "risk-of-ruin": ("portfolio", 4.6, ""), "kelly-criterion": ("portfolio", 4.7, "advanced"),
    "active-management": ("equities", 3.5, ""), "fat-tails": ("measure", 3.5, ""), "booms-and-busts": ("how-markets-move", 10, ""),
    "withdrawal-rates": ("practice", 2.5, ""), "fraud-warning-signs": ("practice", 3.5, ""), "enough": ("practice", 6, ""),
}
SECTIONS = ["What it is", "How it works", "What goes wrong", "Connects to", "Check yourself"]
# anecdotes, branded terms and unverified attributions that must not be lifted from source books
BANNED = [r"scared rabbit", r"\bThorp'?s friend\b", r"stray screw", r"\bHeller\b", r"\bVonnegut\b", r"red[- ]light", r"fundamental attribution error"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
root = P[D["root"]]

# --- the branch
runs = [b for b in root["children"] if P[b]["group"] == "How it runs"]
check(P[HUB]["parent"] == D["root"] and runs[-1] == HUB, f"a branch, last in How it runs ({runs})")
check(len(root["children"]) == 16, f"sixteen branches ({len(root['children'])})")
check(P[HUB]["title"] == "How to Think" and not P[HUB]["stub"] and not P[HUB]["adv"], "titled How to Think, written, Core")
hub = REPO.joinpath(f"pages/{HUB}.md").read_text().split("---", 2)[2]
core = hub.split("## Going deeper")[0]
check(len(P[HUB]["text"].split()) >= 400 and core.count("**Q:**") == 2 and "## Going deeper" in hub, "the hub meets the hub standard (400+ words, 2 quizzes, Going deeper)")
check(all(x in core for x in ["**Decisions:**", "**Incentives and systems:**", "**Thinking with numbers:**"]), "the hub names its three clusters")
check("never point to a particular asset or a particular trade" in core, "the hub says the tools never point to an asset or a trade")
rt = REPO.joinpath("pages/capital-system.md").read_text()
check("[[how-to-think]]" in rt and rt.index("[[practice]]") < rt.index("[[how-to-think]]"), "the root page lists How to Think after In Practice")

# --- planned pages, checked as they arrive
present = [k for k in PLAN if k in P]
print(f"  info planned pages present: {len(present)} of {len(PLAN)} ({present})")
kids = P[HUB]["children"]
check(all(k in PLAN for k in kids), f"every page under How to Think is in the agreed plan ({[k for k in kids if k not in PLAN]})")
check(kids == sorted(kids, key=lambda k: PLAN[k][1]), f"How to Think's pages sit in the planned order ({kids})")
check(all(f"[[{k}]]" in core for k in kids), f"the hub links every page it has ({[k for k in kids if f'[[{k}]]' not in core]})")
for k in present:
    par, order, level = PLAN[k]
    f = REPO.joinpath(f"pages/{k}.md").read_text()
    fm, body = f.split("---", 2)[1], f.split("---", 2)[2]
    meta = dict(re.findall(r"(?m)^(\w+):\s*(.*)$", fm))
    check(P[k]["parent"] == par and float(meta.get("order", -1)) == order, f"{k}: parent {par}, order {order} (got {P[k]['parent']}, {meta.get('order')})")
    check(P[k]["adv"] == (level == "advanced"), f"{k}: level {'advanced' if level else 'Core'}")
    check(not P[k]["stub"], f"{k}: written, not a stub")
    pcore = body.split("## Going deeper")[0]
    deep = body.split("## Going deeper")[1] if "## Going deeper" in body else ""
    heads = re.findall(r"(?m)^## (.+)$", body)
    check(all(h in heads for h in SECTIONS) and heads.index("Check yourself") > heads.index("What goes wrong") and (not deep or heads[-1] == "Going deeper"), f"{k}: standard sections, Going deeper last if present ({heads})")
    check(pcore.count("**Q:**") >= 1 and pcore.count("**Q:**") == pcore.count("**A:**") and "**Q:**" not in deep, f"{k}: quizzes, all above Going deeper")
    words = len(P[k]["text"].split())
    check(280 <= words <= 700, f"{k}: about 300 to 500 words ({words})")
    check("**Key rule:**" in pcore, f"{k}: states a key rule")
    check(not re.search(r"\b(today|currently|right now|recently|nowadays|at present|this year|last year)\b", body, re.I), f"{k}: timeless")
    check(not re.search(r"\byou should (buy|sell|hold|invest|short)\b|\b(buy|sell) signal\b|\bstrong buy\b|\bguaranteed\b(?! returns are a warning)", body, re.I), f"{k}: explains, never advises or signals")
    years = re.findall(r"\b(1[6-9]\d\d|20\d\d)\b", body)
    check(not years or P[k]["sources"], f"{k}: any dated fact has a sources line ({sorted(set(years))[:5]})")
    if re.search(r"\d\s*[×÷]\s*\d|= \*\*\d", pcore):
        check("fictional" in pcore.lower(), f"{k}: worked figures are labelled fictional")
    check(not [b for b in BANNED if re.search(b, f, re.I)], f"{k}: no lifted anecdotes, branded terms or unverified attributions ({[b for b in BANNED if re.search(b, f, re.I)]})")
    check(all(l in P for l in P[k]["links"]), f"{k}: no broken links")
    others = [b for b in P[k]["backlinks"] if b != par]
    check(par in P[k]["backlinks"] and others, f"{k}: linked from its hub and at least one other page ({P[k]['backlinks']})")

# --- worked figures, recomputed (added as each batch is reviewed)
from math import comb
def body_of(k): return REPO.joinpath(f"pages/{k}.md").read_text() if k in P else None
n = lambda x: f"{x:,.0f}"
b = body_of("second-order-thinking")
if b:   # batch 1, reviewed 2026-10-27
    rev, cost = 1_000_000 * 0.9 * 1.15, 800_000 * 1.15 * 1.05
    check(f"= **{n(rev)}**" in b and f"= **{n(cost)}**" in b and f"= **{n(rev - cost)}**" in b and f"**{100 * (1 - (rev - cost) / 200_000):.1f}%**" in b, "second-order thinking: revenue up, profit down 65.5%")
b = body_of("opportunity-cost")
if b: check(f"10,000 × 0.04 = **{n(10_000 * 0.04)}**" in b, "opportunity cost: 10,000 at 4% is 400")
b = body_of("edge")
if b: check("0.55 × 1 − 0.45 × 1 = **0.1**" in b and abs(0.55 - 0.45 - 0.1) < 1e-9 and "0.1 − 0.02 = **0.08**" in b, "edge: 0.1 before costs, 0.08 after")
b = body_of("luck-and-skill")
if b:
    tail = lambda q: 100 * sum(comb(10, k) * q ** k * (1 - q) ** (10 - k) for k in range(6, 11))
    check(all(f"**{tail(q):.1f}%**" in b for q in (0.5, 0.52, 0.55)), f"luck and skill: at least 6 of 10 years at 50/52/55% ({tail(.5):.1f}, {tail(.52):.1f}, {tail(.55):.1f})")

b = body_of("time-horizons")
if b:   # batch 2, reviewed 2026-10-27
    from statistics import NormalDist
    z = NormalDist(); p1 = z.cdf(-7 / 15); p20 = z.cdf(-7 / (15 / 20 ** 0.5)); anyl = 1 - (1 - p1) ** 20
    check(f"about **{100 * p1:.0f}%**" in b and f"about **{100 * p20:.1f}%**" in b and "over **99%**" in b and anyl > 0.99, f"time horizons: {100 * p1:.0f}% one year, {100 * p20:.1f}% average over twenty, {100 * anyl:.2f}% at least one losing year")
b = body_of("margin-of-safety")
if b: check(f"85 − 70 = **{85 - 70}**" in b and f"85 − 100 = **−{100 - 85}**" in b, "margin of safety: +15 at 70, −15 at 100")
b = body_of("externalities")
if b: check(f"2 − 0.03 = **{2 - 3 / 100:.2f}**" in b and f"200 − 300 = **{100 * 2 - 100 * 3}**".replace("-", "−") in b, "externalities: private +1.97, group −100")

b = body_of("averages-and-distributions")
if b:   # batch 3, reviewed 2026-10-27
    check(f"= **{(9 * 50_000 + 10_000_000) / 10:,.0f}**" in b and "**50,000**" in b, "averages: mean 1,045,000 against median 50,000")
    check(f"0.8 × 1.4 = **{0.8 * 1.4:.2f}**" in b and f"about **{100 * ((0.8 * 1.4) ** 0.5 - 1):.1f}%**" in b, "averages quiz: 10% average compounds to 5.8% a year")
b = body_of("absolute-and-relative-risk")
if b: check("2 in 1,000,000, or 0.0002%" in b and abs(2 / 1e6 * 100 - 0.0002) < 1e-12 and "0.03% (0.01 × 3)" in b and "10 percentage points (20% × 0.5)" in b, "absolute and relative risk: figures recomputed")
b = body_of("false-precision")
if b: check(f"25 / 40 = {25 / 40}" in b and f"(2 / 40 = {2 / 40:.2f})" in b and f"about {100 / 30:.1f} percentage points" in b, "false precision: 62.5%, 5 points, 3.3 points")

b = body_of("risk-of-ruin")
if b:   # batch 4, reviewed 2026-10-27
    check(f"≈ **{0.99 ** 5:.3f}**" in b and f"≈ **{0.8 ** 5:.3f}**" in b, "risk of ruin: five losses at 1% and at 20%")
b = body_of("kelly-criterion")
if b:
    from math import log
    g = lambda f, p=0.55: p * log(1 + f) + (1 - p) * log(1 - f)
    check("0.55 − (1 − 0.55) / 1 = **0.10**" in b and abs(0.55 - 0.45 - 0.10) < 1e-9, "Kelly: 10% on a 55% even-money bet")
    check(f"about **{round(100 * g(0.05) / g(0.10))}%**" in b and g(0.20) < 0 and "**below zero**" in b, f"Kelly: half-Kelly keeps {100 * g(.05) / g(.1):.0f}% of growth; double Kelly shrinks ({g(.2):.5f})")
    check(f"= **{0.30 - 0.70 / 3:.3f}**" in b, "Kelly quiz: 3 to 1 at 30% gives 6.7%")
    check("Bell System Technical Journal, July 1956" in " ".join(P["kelly-criterion"]["sources"]), "Kelly: the 1956 paper is credited")
    hubm = REPO.joinpath("pages/portfolio.md").read_text().split("## Going deeper")
    check("[[kelly-criterion]]" not in hubm[0] and "[[kelly-criterion]]" in hubm[1], "Kelly (advanced) is linked only from Going deeper on the Portfolio hub")
b = body_of("fat-tails")
if b:
    from statistics import NormalDist
    pz = 2 * NormalDist().cdf(-3)
    check(f"about **{100 * pz:.2f}%**" in b and f"≈ **{250 * pz:.1f}**" in b and f"250 × 0.02 = **{250 * 0.02:.0f}**" in b, "fat tails: 0.27% and 0.7 days normal, 5 days fat-tailed")

b = body_of("active-management")
if b:   # batch 5, reviewed 2026-10-27
    check("8% − 0.1% = **7.9%**" in b and "8% − 1% = **7%**" in b, "active management: 7.9% passive against 7% active after costs")
    check("average **dollar**" in b and "Pedersen" in b and "Sharpe" in " ".join(P["active-management"]["sources"]), "active management: dollar-weighted, Sharpe credited, Pedersen's critique included")
b = body_of("booms-and-busts")
if b: check(f"≈ **{350 / 150:.2f}**" in b and f"≈ **{round(100 * (120 - 350) / 350)}%**".replace("-", "−") in b, "booms and busts: 2.33 times, −66%")
b = body_of("withdrawal-rates")
if b: check(f"40,000 × 1.03 = **{40_000 * 1.03:,.0f}**" in b and "33 years" in b and "Journal of Financial Planning" in " ".join(P["withdrawal-rates"]["sources"]), "withdrawal rates: 41,200; Bengen's 33 years; credited")
b = body_of("fraud-warning-signs")
if b:   # batch 6, reviewed 2026-10-27
    check(f"1.01^12 ≈ **{1.01 ** 12:.4f}**" in b and "4 of 139" in b and "OIG-509" in " ".join(P["fraud-warning-signs"]["sources"]), "fraud warning signs: 1.1268; Madoff 4 of 139 months; SEC Inspector General credited")
b = body_of("enough")
if b: check(f"= **{550_000 - 500_000:,}**" in b and f"= **{500_000 - 300_000:,}**" in b and f"= **{500_000 - 470_000:,}**" in b, "enough: 50,000 above, 200,000 and 30,000 short")
# 2026-10-27 batch 5: a link id with a space (e.g. [[sequence risk]]) isn't matched by the build and shows raw on the page
raw = [k for k in present if "[[" in P[k]["html"]]
check(not raw, f"no raw [[link]] text left on any planned page ({raw})")

def lum(rgb):
    g = lambda v: (v / 255) / 12.92 if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * g(rgb[0]) + 0.7152 * g(rgb[1]) + 0.0722 * g(rgb[2])
def ratio(x, y):
    a, b = sorted([lum(x), lum(y)], reverse=True); return (a + 0.05) / (b + 0.05)
nums = lambda css: [int(float(v)) for v in re.findall(r"[\d.]+", css)[:3]]

with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            for theme in (["light", "dark"] if mode == "normal" else ["light"]):
                print(f"== {mode} @ {w} {theme}")
                ctx = br.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1, color_scheme=theme)
                pg = ctx.new_page()
                pg.on("console", lambda m_: errs.append(f"{w} {mode}: {m_.text}") if m_.type == "error" else None)
                pg.on("pageerror", lambda e_: errs.append(f"{w} {mode}: {e_}"))
                pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(600)
                st = pg.evaluate(f"""(() => {{ const g = document.querySelector('#map-svg [data-node="{HUB}"]');
                  return [getComputedStyle(g.querySelector('.node-box')).fill, getComputedStyle(g.querySelector('.node-label')).fill]; }})()""")
                rr = ratio(nums(st[0]), nums(st[1]))
                check(rr >= 4.5, f"{theme}: the pill's label contrast is at least 4.5:1 ({rr:.2f})")
                pg.locator('.map-controls [data-act="collapse"]').click(); pg.wait_for_timeout(900)
                pos = pg.evaluate("""(() => { const top = document.querySelector('#map-view').getBoundingClientRect().top,
                    bottom = document.querySelector('.map-controls').getBoundingClientRect().top,
                    f = document.querySelector('#map-svg [data-node="foundation"]').getBoundingClientRect(),
                    r = document.querySelector('#map-svg [data-node="capital-system"]').getBoundingClientRect();
                    return [f.top >= top, r.top >= top && r.bottom <= bottom]; })()""")
                check(pos == [True, True], f"after Collapse all with sixteen branches, Foundation is below the top bar and the root on screen ({pos})")
                for k in [HUB] + present:
                    pg.goto(URL + f"#/map/p/{k}"); pg.wait_for_timeout(300)
                    body = pg.locator("#panel-body")
                    ok = pg.locator(".p-title").count() == 1 and body.locator(".wl.broken").count() == 0 and "[[" not in body.inner_text()
                    check(ok and pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{k}: opens, no broken links, no sideways scroll")
                if w in (1366, 390) and mode == "normal" and theme == "light": pg.goto(URL + f"#/map/p/{HUB}"); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / f"howtothink-{w}.png"))
                pg.goto(URL + f"#/map/p/{HUB}"); pg.wait_for_timeout(300)
                check(pg.locator("#panel-body .deeper").is_visible() == (mode == "normal"), "hub: Going deeper shows in Everything and hides in Core")
                for q in ["how to think", "mental models"]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(120)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(220)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
                    check(f"#/map/p/{HUB}" in hrefs, f"search '{q}' finds the hub in the top 3 ({hrefs})")
                    pg.keyboard.press("Escape")
                ctx.close()
    br.close()
print("Console errors:", len(errs)); [print("  ", e_) for e_ in errs]
print("FAILS:", len(fails)); [print("  ", f_) for f_ in fails]
sys.exit(1 if fails or errs else 0)
