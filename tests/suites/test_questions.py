"""Questions layer and Start view: the front door for newcomers. Question data and routes, plain language (jargon list and
Flesch-Kincaid), neutrality, answers agreeing with their pages, build validation, the SQLite tables, the Start tab, question pages,
Answers links on routed pages, search, the two-click path from the welcome guide, and the Index still reachable.
Usage: python3 test_questions.py <repo> <outdir>"""
import sys, pathlib, json, re, shutil, subprocess, tempfile, sqlite3
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

# id: (group, route). Update when a question is added or a route changes (say so in the PR).
EXPECT = {
    "bank-safe": ("Is my money safe?", ["bank-deposits", "deposit-insurance", "backstops", "bail-in"]),
    "broker-bust": ("Is my money safe?", ["brokers", "custody", "broker-failure"]),
    "cash-safe": ("Is my money safe?", ["cash-and-fiat", "inflation", "t-bills", "bank-deposits"]),
    "money-from": ("How money works", ["what-is-money", "central-bank-money", "bank-deposits", "hierarchy-of-money"]),
    "prices-rise": ("Why do prices rise?", ["inflation", "central-bank-money", "cash-and-fiat", "financial-repression"]),
    "save-or-invest": ("How investing works", ["four-ways-to-earn", "risk-and-return", "compounding", "bank-deposits"]),
    "fees-cost": ("How investing works", ["compounding", "funds-and-etfs", "common-mistakes"]),
    "bitcoin-worth": ("Crypto", ["bitcoin", "coin-value", "network-effects", "self-custody"]),
    "stablecoin-safe": ("Crypto", ["stablecoins", "deposit-insurance", "custodial-crypto"]),
    "country-broke": ("When things go wrong", ["sovereign-default", "currency-failure", "capital-controls", "bank-sovereign-loop"]),
    # 2026-10-26, branch 2: nine more, including the former Fine Print ideas (own-shares, spread-out, my-inflation)
    "own-shares": ("Is my money safe?", ["shares", "custody", "brokers", "claims-and-liabilities"]),
    "gov-take": ("When things go wrong", ["confiscation", "capital-controls", "gold", "cartography-of-wealth"]),
    "bond-what": ("How investing works", ["bonds", "t-bills", "bond-pricing", "credit-risk"]),
    "index-fund": ("How investing works", ["indices", "funds-and-etfs", "compounding", "diversification"]),
    "spread-out": ("How investing works", ["diversification", "correlation", "cartography-of-wealth", "failure-modes"]),
    "leverage-why": ("When things go wrong", ["leverage", "drawdown", "common-mistakes"]),
    "gold-why": ("How money works", ["gold", "hierarchy-of-money", "inflation", "coin-value"]),
    "wipe-out": ("When things go wrong", ["cartography-of-wealth", "diversification", "failure-modes", "human-capital"]),
    "my-inflation": ("Why do prices rise?", ["inflation", "cash-and-fiat", "inflation-linked-bonds"]),
}
N = len(EXPECT)
GROUPS = ["Is my money safe?", "How money works", "Why do prices rise?", "How investing works", "Crypto", "When things go wrong"]
JARGON = ["liability", "liabilities", "fiat", "sovereign", "bail-in", "rehypothecat", "nominal", "real return", "monetary base",
          "cpi", "etf", "yield", "default", "custodian", "segregat", "counterparty", "solvency", "insolvent", "redenominat", "basis point"]
ADVICE = re.compile(r"\byou should (buy|sell|hold)\b|\binvest in\b|\b(buy|sell) (bitcoin|gold|shares|bonds|stablecoins)\b|\bwe recommend\b", re.I)
MAX_GRADE = 9.0    # Flesch-Kincaid grade 9 ~ reading age 14

def syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w: return 0
    if len(w) <= 3: return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w); w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))
def fk_grade(text):
    sents = max(1, len(re.findall(r"[.!?](?=\s|$)", text)))
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*|\d[\d,.%]*", text)
    syl = sum(syllables(w) if w[0].isalpha() else 1 for w in words)
    return 0.39 * len(words) / sents + 11.8 * syl / len(words) - 15.59

# --- data
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]; Q = D["questions"]
check(sorted(Q) == sorted(EXPECT), f"{N} questions ({sorted(Q)})")
check(D["questionGroups"] == GROUPS, f"six groups, in order ({D['questionGroups']})")
check(all((Q[q]["group"], [st["page"] for st in Q[q]["route"]]) == v for q, v in EXPECT.items()), "every question: right group and route, in order")
check(all(Q[q]["question"].endswith("?") for q in Q), "every question ends with a question mark")
check(all(st["page"] in P and not P[st["page"]]["adv"] for q in Q for st in Q[q]["route"]), "every route page exists and is a Core page")
check(all(st["note"] for q in Q for st in Q[q]["route"]), "every route step has a reason to read it")
check(all(q in P[st["page"]]["answers"] for q in Q for st in Q[q]["route"]), "every routed page knows the questions it answers")
check(not [p for p in P if P[p].get("answers") and not any(p in [st["page"] for st in Q[q]["route"]] for q in P[p]["answers"])], "no page claims a question that doesn't route to it")
for q in Q:
    qt, at = Q[q]["question"].lower(), Q[q]["answerText"].lower()
    jq = [j for j in JARGON if re.search(r"\b" + j, qt)]
    ja = [j for j in JARGON if re.search(r"\b" + j, at)]
    check(not jq and not ja, f"{q}: no jargon in the question or answer ({jq + ja})")
    g = fk_grade(Q[q]["answerText"])
    check(g <= MAX_GRADE, f"{q}: plain enough (Flesch-Kincaid grade {g:.1f} <= {MAX_GRADE})")
    check(not ADVICE.search(Q[q]["answerText"]), f"{q}: neutral, tells no one what to buy, sell or hold")
    check(not re.search(r"\b(today|currently|this year)\b", at), f"{q}: timeless")
    n = len(re.findall(r"[.!?](?=\s|$)", Q[q]["answerText"]))
    check(3 <= n <= 6, f"{q}: 3 to 6 sentences ({n})")
grades = [fk_grade(Q[q]["answerText"]) for q in Q]
print(f"  info Flesch-Kincaid grades: mean {sum(grades) / len(grades):.1f}, max {max(grades):.1f}")

# answers agree with their pages
infl = P["inflation"]["text"]
check("2%" in Q["prices-rise"]["answerText"] and "around 2% a year" in infl, "prices-rise: the 2% target matches Inflation")
check("almost half" in Q["cash-safe"]["answerText"] and "20 years" in Q["cash-safe"]["answerText"] and round(1.03 ** -20, 2) == 0.55 and "55%" in infl,
      "cash-safe: 'almost half in 20 years at 3%' matches Inflation's worked example (55% left)")
check("21 million" in Q["bitcoin-worth"]["answerText"] and "21 million" in P["bitcoin"]["text"], "bitcoin-worth: 21 million matches Bitcoin")
check("limit" in Q["bank-safe"]["answerText"] and "limit" in P["deposit-insurance"]["text"], "bank-safe: the limit matches Deposit Insurance")
check("50%" in Q["leverage-why"]["answerText"] and "10%" in Q["leverage-why"]["answerText"] and "a 50% fall wipes you out" in P["leverage"]["text"] and "just **10%**" in REPO.joinpath("pages/leverage.md").read_text(),
      "leverage-why: 2x/50% and 10x/10% match Leverage")
check("1980" in Q["gold-why"]["answerText"] and "2008" in Q["gold-why"]["answerText"] and "January 1980" in P["gold"]["text"] and "until 2008" in P["gold"]["text"], "gold-why: the 1980 high and 2008 match Gold")
check("1933" in Q["gov-take"]["answerText"] and "1933" in P["confiscation"]["text"], "gov-take: the 1933 gold order matches Confiscation")
check("US funds" in Q["index-fund"]["answerText"] and "SPIVA" in P["funds-and-etfs"]["text"], "index-fund: the evidence is labelled as US, as on Funds and ETFs")
check("basket" in Q["my-inflation"]["answerText"] and "basket" in P["inflation"]["text"], "my-inflation: the typical basket matches Inflation")
check("price" in Q["broker-bust"]["answerText"] and "market losses" in REPO.joinpath("pages/broker-failure.md").read_text(), "broker-bust: schemes don't cover price falls, as Broker Failure says")

# --- build validation (throwaway copy)
def build_with(edits):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        for path, old, new in edits:
            f = r / path; t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout
code, out = build_with([])
check(code == 0 and f"Questions: {N} in 6 groups" in out and f"questions {N}, question_route" in out, f"clean build: {N} questions in 6 groups, exported")
F = "questions/fees-cost.md"
for label, edits, want in [
    ("a broken route link", [(F, "[[funds-and-etfs]]", "[[no-such-page]]")], "broken link [[no-such-page]]"),
    ("a question without '?'", [(F, "cost me over time?", "cost me over time")], "end with '?'"),
    ("an unknown group", [(F, "group: How investing works", "group: Misc")], "group must be one of"),
    ("a route of two pages", [(F, "- [[common-mistakes]] — the errors that cost the most over time\n", "")], "3 to 5 pages"),
    ("a route step with no reason", [(F, "[[common-mistakes]] — the errors that cost the most over time", "[[common-mistakes]]")], "needs a one-line reason"),
    ("an answer of one sentence", [(F, "More than they look. A fee", "More than they look, as a fee")] + [(F, ". So a fee", ", so a fee"), (F, " not just 1%. The fee", " not just 1%, and the fee")], "2 to 7 sentences"),
]:
    c2, o2 = build_with(edits)
    check(c2 != 0 and want in o2, f"build fails on {label}")

# --- SQLite
db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
check(db.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == N, f"questions table: {N} rows")
check(db.execute("SELECT COUNT(*) FROM question_route").fetchone()[0] == sum(len(v[1]) for v in EXPECT.values()), "question_route: one row per step")
check(not db.execute("PRAGMA foreign_key_check").fetchall(), "no broken foreign keys")
db.close()
about = REPO.joinpath("about.md").read_text()
check("**Start**" in about and "**Failures**" in about, "About's Ways in lists Start and Failures")

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            for theme in (["light", "dark"] if mode == "normal" else ["light"]):
                print(f"== {mode} @ {w} {theme}")
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1, color_scheme=theme)
                pg = ctx.new_page()
                pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))

                # a newcomer: welcome guide -> Ask a question (click 1) -> a question (click 2) -> the answer
                pg.goto(URL + "#/map"); pg.wait_for_timeout(500)
                check(pg.locator("#welcome").is_visible(), "a first visit shows the welcome guide")
                pg.locator('[data-wc="start"]').click(); pg.wait_for_timeout(400)
                pg.locator('.q-card[data-question="bank-safe"]').click(); pg.wait_for_timeout(400)
                ans = pg.locator("#start-body .q-answer")
                check(pg.evaluate("location.hash") == "#/start/bank-safe" and ans.is_visible() and "loan" in ans.inner_text(), "two clicks from the welcome guide to a plain answer")
                pg.evaluate(f"localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
                right = pg.evaluate("Math.round(document.querySelector('#theme-btn').getBoundingClientRect().right)")
                check(right <= w, f"header fits ({right} of {w})")
                tabs = pg.locator(".tabs .tab:not([hidden])").evaluate_all("els => els.map(e => e.dataset.view)")
                check(tabs[0] == "start" and "index" not in tabs and len(tabs) == 6, f"Start is the first of six tabs; no Index tab ({tabs})")

                # the list
                pg.goto(URL + "#/start"); pg.wait_for_timeout(350)
                heads = [x.strip().lower() for x in pg.locator("#start-body h2.flow-area").all_inner_texts()]
                check(heads == ["new to all of this?"] + [g.lower() for g in GROUPS], f"the beginner path's heading, then six groups in order ({heads})")   # 2026-10-26 branch 3: the path sits above the groups
                check(pg.locator("#start-body .q-card").count() == N, f"{N} question cards")
                check("Nothing here tells you what to buy or sell" in pg.locator("#start-body .view-sub").inner_text(), "the intro says it's neutral")
                check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"start-{w}-{theme}.png"), full_page=True)

                # a question page: route opens pages beside it; more in the group
                pg.goto(URL + "#/start/country-broke"); pg.wait_for_timeout(350)
                check(pg.locator(".q-route .q-step").count() == 4 and pg.locator("#start-body .q-group").inner_text().lower() == "when things go wrong", "a question shows its group and its four route steps")
                pg.locator('.q-step a[data-page="capital-controls"]').click(); pg.wait_for_timeout(450)
                check(pg.evaluate("location.hash") == "#/start/country-broke/p/capital-controls" and pg.locator("body.panel-open").count() == 1, "a route step opens its page beside the question")
                chips = pg.locator("#panel-body .answer-chip").evaluate_all("els => els.map(e => e.dataset.question)")
                check(chips == ["country-broke", "gov-take"], f"the page shows which questions it answers, in Start order ({chips})")   # 2026-10-26 branch 2: gov-take also routes here
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"question-{w}-{theme}.png"))
                pg.goto(URL + "#/map/p/bank-deposits"); pg.wait_for_timeout(450)
                chips = pg.locator("#panel-body .answer-chip").evaluate_all("els => els.map(e => e.dataset.question)")
                check(chips == ["bank-safe", "cash-safe", "money-from", "save-or-invest"], f"Bank Deposits answers four questions, in Start order ({chips})")
                pg.locator('#panel-body .answer-chip[data-question="cash-safe"]').click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash").startswith("#/start/cash-safe"), "an Answers link opens the question")
                pg.goto(URL + "#/start/cash-safe"); pg.wait_for_timeout(300)
                more = pg.locator("#start-body .p-list [data-question]").evaluate_all("els => els.map(e => e.dataset.question)")
                check(sorted(more) == ["bank-safe", "broker-bust", "own-shares"], f"'More in' lists the rest of the group ({more})")   # 2026-10-26 branch 2: own-shares joins the group
                pg.locator('#start-body .back[data-question=""]').click(); pg.wait_for_timeout(300)
                check(pg.evaluate("location.hash") == "#/start", "back to all questions")

                # the Index is still reachable
                pg.locator('#start-body .start-more [data-view="index"]').click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/index" and pg.locator("#index-view.active").count() == 1, "Start links the A-Z index")
                pg.goto(URL + "#/map"); pg.wait_for_timeout(200)
                pg.click("#settings-btn"); pg.wait_for_timeout(200)
                pg.locator('#settings-menu .sm-index').click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/index" and pg.locator("#settings-menu").is_hidden(), "the settings menu links the index and closes")

                # search finds questions
                for q, want in [("is my money safe", "bank-safe"), ("cost more every year", "prices-rise"), ("country go broke", "country-broke")]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(250)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
                    check(hrefs[:1] == [f"#/start/{want}"], f"search '{q}' puts the question first ({hrefs})")
                    pg.keyboard.press("Escape")
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", "is my money safe"); pg.wait_for_timeout(250); pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/start/bank-safe", "Enter on a question result opens it")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
