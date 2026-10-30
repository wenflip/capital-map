"""How Markets Move (15th branch) plus The Repo Market and Asymmetry: structure and placement, page sections and quizzes,
links in and out, quals, every worked figure recomputed, every dated fact and its credit, explain-never-signal neutrality,
the pill colour, the collapsed map on small phones, rendering, depth and search. Usage: python3 test_marketsmove.py <repo> <outdir>"""
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

HUB = "how-markets-move"
KIDS = ["business-cycle", "credit-cycle", "stability-breeds-instability", "priced-in", "earnings-season", "fear-gauges",
        "flows-and-fundamentals", "forced-sellers", "short-selling"]
ELSEWHERE = {"repo-market": "markets", "asymmetry": "portfolio"}
ALL = KIDS + list(ELSEWHERE)
SECTIONS = ["What it is", "How it works", "What goes wrong", "Connects to", "Check yourself"]
# linked in from at least one existing page outside the new branch
LINKED_IN = {"business-cycle": "market-regimes", "credit-cycle": "credit-risk", "priced-in": "valuation", "earnings-season": "financial-statements",
             "fear-gauges": "volatility", "flows-and-fundamentals": "indices", "forced-sellers": "leverage", "repo-market": "liquidity", "asymmetry": "options"}

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
md = {k: REPO.joinpath(f"pages/{k}.md").read_text().split("---", 2)[2] for k in ALL + [HUB]}
core = {k: md[k].split("## Going deeper")[0] for k in md}

# --- structure and placement
root = P[D["root"]]
runs = [b for b in root["children"] if P[b]["group"] == "How it runs"]
check(P[HUB]["parent"] == D["root"] and runs[:2] == ["markets", HUB], f"a branch in How it runs, right after Markets & Plumbing ({runs})")
check(len(root["children"]) >= 15, f"at least fifteen branches ({len(root['children'])})")   # 2026-10-27 how-to-think branch: a 16th branch was added; this suite only needs How Markets Move among them
check(P[HUB]["children"][:9] == KIDS, f"the nine original pages first, in order ({P[HUB]['children']})")   # 2026-10-27 how-to-think batch 5: Booms and Busts (10) added after; checked in test_howtothink
check(all(P[k]["parent"] == v for k, v in ELSEWHERE.items()), "Repo sits in Markets & Plumbing and Asymmetry in Portfolio & Risk")
check(P["markets"]["children"][-1] == "repo-market" and P["portfolio"]["children"].index("asymmetry") == P["portfolio"]["children"].index("position-sizing") + 1, "Repo last in Markets; Asymmetry after Position Sizing")
check(all(not P[k]["stub"] and not P[k]["adv"] for k in ALL + [HUB]), "all twelve pages written and Core")
rt = REPO.joinpath("pages/capital-system.md").read_text()
check("[[how-markets-move]]" in rt and rt.index("[[markets]]") < rt.index("[[how-markets-move]]") < rt.index("[[measure]]"), "the root page lists the branch after Markets & Plumbing")
for hub, k in [("markets", "repo-market"), ("portfolio", "asymmetry")]:
    check(f"[[{k}]]" in REPO.joinpath(f"pages/{hub}.md").read_text().split("## Going deeper")[0], f"the {hub} hub lists {k} in its Core part")
check(all(f"[[{k}]]" in core[HUB] for k in ALL), "the new hub links all nine pages and both relatives")

# --- every page: sections, quizzes above Going deeper, length, sources where dated
for k in ALL:
    heads = re.findall(r"(?m)^## (.+)$", md[k])
    check(all(h in heads for h in SECTIONS) and (heads.index("Check yourself") > heads.index("What goes wrong")), f"{k}: has the standard sections ({heads})")
    deep = md[k].split("## Going deeper")[1] if "## Going deeper" in md[k] else ""
    check(core[k].count("**Q:**") >= 1 and core[k].count("**Q:**") == core[k].count("**A:**") and "**Q:**" not in deep, f"{k}: quizzes, all above Going deeper")
    check(len(P[k]["text"].split()) >= 300, f"{k}: substantial ({len(P[k]['text'].split())} words)")
    check("**Key rule:**" in core[k], f"{k}: states a key rule")
    check(not re.search(r"\b(today|currently|right now|at present|nowadays)\b", md[k], re.I), f"{k}: timeless")
    check(not re.search(r"\byou should (buy|sell|hold|short)\b|\b(buy|sell) signal\b|\bstrong buy\b", md[k], re.I), f"{k}: explains, never signals")
for k, src in LINKED_IN.items():
    check(k in P[src]["links"], f"{src} links to {k}")
check(len(P[HUB]["text"].split()) >= 400 and core[HUB].count("**Q:**") == 2, "the hub meets the hub standard's length and quizzes")
check("They don't predict them" in core[HUB], "the hub says outright that these forces explain, not predict")

# --- quals
def mods(q, pid): return {st["title"].split(" — ")[0] for st in D["quals"][q]["stages"] if any(i["page"] == pid for i in st["items"])}
check(mods("cfa-l1", "business-cycle") == {"CFA1-ECON"} and mods("cfa-l1", "credit-cycle") == {"CFA1-ECON"}, "both cycles mapped to CFA I Economics")
check(mods("money-banking", "repo-market") == {"MB2"}, "the repo market mapped to Money & Banking MB2")

# --- worked figures, recomputed
n = lambda x: f"{x:,.0f}"
b = core["business-cycle"]
check("December 2007 to June 2009" in b and f"**{(2009 - 2007) * 12 + (6 - 12)}**" not in b and "18 months" in b and (2009 - 2007) * 12 + (6 - 12) == 18, "business cycle: Dec 2007 to Jun 2009 is 18 months")
c = core["credit-cycle"]
check(f"owes {n(300_000 * .95)}" in c and f"{n(300_000 * .9)}, the loan is {n(300_000 * .95 - 300_000 * .9)}" in c, "credit cycle: 95% loan, 10% fall, 15,000 short")
check(f"owes {n(300_000 * .8)}" in c and f"still {n(300_000 * .9 - 300_000 * .8)}" in c, "credit cycle: 80% loan keeps 30,000")
check(f"loan is {n(200_000 * .9)}" in c and f"worth {n(200_000 * .85)}" in c and f"**{n(200_000 * .9 - 200_000 * .85)}**" in c, "credit cycle quiz: 10,000 short")
m = core["stability-breeds-instability"]
check(f"owes {n(100_000 * .06)} a year" in m and f"interest and {n(15_000 - 6_000)} off" in m and f"falls {n(6_000 - 3_000)} short" in m, "Minsky: the three borrowers at 6%")
check(f"becomes {n(100_000 * .08)}" in m and f"{n(100_000 * .08 - 6_000)} short too" in m, "Minsky: at 8% the second borrower is 2,000 short")
check("Above **7%**" in m and round(100_000 * .07) == 7_000, "Minsky quiz: 7% of 100,000 is 7,000")
pi = core["priced-in"]
check(f"25 × 2.00 = {25 * 2:.0f}" in pi and f"25 × 1.80 = **{25 * 1.8:.0f}**" in pi and f"**{round(100 * (1 - 45 / 50))}%** fall" in pi, "priced in: 50 to 45, a 10% fall")
check(f"25 × 2.20 = {25 * 2.2:.0f}" in pi, "priced in: 2.20 gives 55")
check(f"15 × 4.00 = {15 * 4:.0f}" in pi and f"15 × 4.40 = **{15 * 4.4:.0f}**" in pi and f"**{round(100 * (66 / 60 - 1))}%**" in pi, "priced in quiz: 60 to 66, +10%")
e = core["earnings-season"]
check(f"about **{100 * .05 / 1.20:.1f}%**" in e, "earnings: a 0.05 beat on 1.20 is 4.2%")
check(f"**{round(100 * .04 / .80)}%** of 0.80" in e, "earnings quiz: 0.04 on 0.80 is 5%")
f = core["fear-gauges"]
check(f"32 ÷ 16 = **{32 // 16}%**" in f and f"48 ÷ 16 = **{48 // 16}%**" in f, "fear gauges: the divide-by-16 rule, recomputed")
check(abs(252 ** .5 - 16) < 0.2, "the rule's 16 is the square root of about 252 trading days")
fl = core["flows-and-fundamentals"]
check(f"**{round(100 * 50 / 200)}%**" in fl and f"60 ÷ 400 = **{round(100 * 60 / 400)}%**" in fl, "flows: 50 of 200 is 25%; quiz 60 of 400 is 15%")
fs = core["forced-sellers"]
eq = 70_000 - 50_000
check(f"70,000 − 50,000 = {n(eq)}" in fs and f"about **{100 * eq / 70_000:.1f}%**" in fs, "forced sellers: equity 20,000 is 28.6% at 70,000")
trigger = 50_000 / (1 - .30)
check(f"about {n(trigger)}" in fs and f"fall of about **{100 * (1 - trigger / 100_000):.1f}%**" in fs, f"forced sellers: the call comes below {trigger:,.0f}, a {100 * (1 - trigger / 100_000):.1f}% fall")
check(f"60,000 − 40,000 = **{n(80_000 * .75 - 40_000)}**" in fs and f"about **{100 * 20_000 / 60_000:.1f}%**" in fs, "forced sellers quiz: 20,000 is a third")
ss = core["short-selling"]
check(f"a gain of **{n(100 * (40 - 30))}**" in ss and f"a loss of **{n(100 * (60 - 40))}**" in ss, "short selling: +1,000 at 30, −2,000 at 60")
check(f"loss of **{n(200 * (32 - 25))}**" in ss and f"sold for {n(200 * 25)}" in ss and f"bought back for {n(200 * 32)}" in ss, "short selling quiz: −1,400")
r = core["repo-market"]
check(f"borrow {n(1_000_000 * .98)}" in r and f"only **{n(1_000_000 * .02)}**" in r and f"**{round(1 / .02)} times**" in r, "repo: 2% haircut, 20,000 own money, 50 times")
check(f"only {n(1_000_000 * .9)}" in r and f"need **{n(1_000_000 * .1)}**" in r and f"another **{n(1_000_000 * .1 - 1_000_000 * .02)}**" in r, "repo: 10% haircut needs 80,000 more")
check(f"borrow **{n(500_000 * .96)}**" in r and f"need **{n(500_000 * .04)}**" in r, "repo quiz: 480,000 and 20,000")
a = core["asymmetry"]
check(f"0.9 × 1 − 0.1 × 12 = **{0.9 - 1.2:.1f}**".replace("-", "−") in a and f"−0.9 × 1 + 0.1 × 15 = **+{-0.9 + 1.5:.1f}**" in a, "asymmetry: A loses 0.3, B makes 0.6")
check(f"1.4 − 1.8 = **{1.4 - 1.8:.1f}**".replace("-", "−") in a and abs(0.7 * 2 - 0.3 * 6 + 0.4) < 1e-9, "asymmetry quiz: −0.4")
check(all(md[k].count("Fictional example") >= 1 for k in ["credit-cycle", "stability-breeds-instability", "priced-in", "earnings-season", "flows-and-fundamentals", "forced-sellers", "short-selling", "repo-market", "asymmetry"]), "worked figures are labelled fictional")

# --- dated facts and their credits
FACTS = {
    "business-cycle": (["December 2007 to June 2009", "February to April 2020"], ["National Bureau of Economic Research"]),
    "credit-cycle": (["every quarter whether they have tightened or eased"], ["Senior Loan Officer Opinion Survey"]),
    "stability-breeds-instability": (["in 1992", "Minsky moment"], ["Working Paper No. 74", "May 1992"]),
    "fear-gauges": (["first published the VIX in 1993", "82.69 on 16 March 2020", "80.74 in November 2008", "next 30 days"], ["Cboe", "CNBC"]),
    "flows-and-fundamentals": (["16 November 2020", "more than 13%", "21 December 2020"], ["CNBC"]),
    "forced-sellers": (["Archegos, March 2021", "more than $10 billion", "28 September 2022"], ["ESMA", "Bank of England"]),
    "short-selling": (["about 123%", "more than 1,600%", "11 and 27 January", "$483 on 28 January", "small part of the buying"], ["SEC Staff Report"]),
    "repo-market": (["17 September 2019", "5.25%", "2.1%", "against Treasury securities"], ["New York", "Richmond"]),
}
for k, (facts, credits) in FACTS.items():
    for x in facts: check(x in md[k], f"{k}: states the checked fact '{x}'")
    srcs = " ".join(P[k]["sources"])
    for c in credits: check(c in srcs, f"{k}: credits {c}")
check("Ethereum" not in md["fear-gauges"] and "S&P 500, a US share index" in md["fear-gauges"], "fear gauges: the US example is labelled as one")

def lum(rgb):
    g = lambda v: (v / 255) / 12.92 if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * g(rgb[0]) + 0.7152 * g(rgb[1]) + 0.0722 * g(rgb[2])
def ratio(x, y):
    p_, q_ = sorted([lum(x), lum(y)], reverse=True); return (p_ + 0.05) / (q_ + 0.05)
nums = lambda css: [int(float(v)) for v in re.findall(r"[\d.]+", css)[:3]]

TITLES = {HUB: "How Markets Move", "business-cycle": "The Business Cycle", "short-selling": "Short Selling and Squeezes", "repo-market": "The Repo Market", "asymmetry": "Asymmetry"}
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
                check(rr >= 4.5, f"{theme}: the new pill's label contrast is at least 4.5:1 ({rr:.2f})")
                pg.locator('.map-controls [data-act="collapse"]').click(); pg.wait_for_timeout(900)
                pos = pg.evaluate("""(() => { const top = document.querySelector('#map-view').getBoundingClientRect().top,
                    bottom = document.querySelector('.map-controls').getBoundingClientRect().top,
                    f = document.querySelector('#map-svg [data-node="foundation"]').getBoundingClientRect(),
                    r = document.querySelector('#map-svg [data-node="capital-system"]').getBoundingClientRect();
                    return [f.top >= top, r.top >= top && r.bottom <= bottom]; })()""")
                check(pos == [True, True], f"after Collapse all with fifteen branches, Foundation is below the top bar and the root on screen ({pos})")
                for k, t in TITLES.items():
                    pg.goto(URL + f"#/map/p/{k}"); pg.wait_for_timeout(350)
                    body = pg.locator("#panel-body")
                    check(pg.locator(".p-title").inner_text() == t and body.locator(".wl.broken").count() == 0 and "[[" not in body.inner_text(), f"{k}: opens, no broken links")
                    check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{k}: no sideways scroll")
                    if w in (1366, 390) and mode == "normal" and theme == "light" and k in (HUB, "forced-sellers"): pg.screenshot(path=str(OUT / f"mm-{k}-{w}.png"))
                pg.goto(URL + f"#/map/p/{HUB}"); pg.wait_for_timeout(350)
                check(pg.locator("#panel-body .deeper").is_visible() == (mode == "normal"), "hub: Going deeper shows in Everything and hides in Core")
                for q, want in [("business cycle", "business-cycle"), ("credit cycle", "credit-cycle"), ("minsky", "stability-breeds-instability"),
                                ("priced in", "priced-in"), ("earnings season", "earnings-season"), ("vix", "fear-gauges"), ("forced selling", "forced-sellers"),
                                ("margin call", "forced-sellers"), ("short squeeze", "short-selling"), ("repo", "repo-market"), ("asymmetry", "asymmetry"),
                                ("how markets move", HUB), ("index inclusion", "flows-and-fundamentals")]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(120)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(220)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
                    check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} in the top 3 ({hrefs})")
                    pg.keyboard.press("Escape")
                ctx.close()
    br.close()
print("Console errors:", len(errs)); [print("  ", e_) for e_ in errs]
print("FAILS:", len(fails)); [print("  ", f_) for f_ in fails]
sys.exit(1 if fails or errs else 0)
