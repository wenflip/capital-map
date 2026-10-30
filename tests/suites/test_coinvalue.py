"""What Gives a Coin Value (Digital Assets cluster): structure, the four aspects of each half, verified facts and credits,
scope, neutrality (no verdict naming a winner), an IP guard against the source study notes, Princeton mapping, rendering and
search. Usage: python3 test_coinvalue.py <repo> <outdir>"""
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

PAGES = ["coin-value", "sound-money", "network-effects"]
ASPECTS = {"sound-money": ["1. Supply", "2. Security", "3. Legal standing", "4. Liquidity and access"],
           "network-effects": ["1. Real users", "2. The default choice", "3. The momentum loop", "4. A lasting community"]}
# facts checked against sources before they went in (see each page's sources line)
FACTS = {"coin-value": ["1 August 2017", "20 July 2016", "about $50 million", "about 85% of miners"],
         "sound-money": ["21 million", "1 and 6 August 2020", "about 807,000 ETC", "24 September 2021"],
         "network-effects": ["Thomas Schelling", "1960", "George Soros", "1987", "20 July 2016", "1 August 2017", "about $50 million"]}
# distinctive wording from the study-notes PDF: the pages use the idea only, in our own words
SOURCE_PHRASES = ["anatomy of a successful coin", "successful coin", "fades to dust", "stays dust", "ticks nearly every box",
                  "dead-center", "dead centre", "two independent pillars", "multiplication, not a sum", "quietly debased",
                  "credibly neutral", "belief-driven", "community didn't follow", "withered", "none of the community saves"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
md = {pid: REPO.joinpath(f"pages/{pid}.md").read_text() for pid in PAGES}

# --- structure
kids = P["digital-assets"]["children"]
check(kids.index("coin-value") == kids.index("native-coins") + 1 and kids.index("coin-value") + 1 == kids.index("tokens"), "the cluster sits between Native Coins and Tokens")
check(P["coin-value"]["children"] == ["sound-money", "network-effects"], "Sound Money, then Network Effects, under the parent")
for pid in PAGES:
    body = md[pid].split("---", 2)[2]
    basic, _, deep = body.partition("## Going deeper")
    heads = re.findall(r"(?m)^## (.+)$", body)
    check(heads == ["What it is", "Why it matters", "How it works", "What goes wrong", "Connects to", "Check yourself", "Going deeper"], f"{pid}: sections in order")
    check(basic.count("**Q:**") == 2 and "**Q:**" not in deep, f"{pid}: two quizzes above Going deeper")
    check(not P[pid]["stub"] and not P[pid]["adv"] and len(P[pid]["text"].split()) >= 400, f"{pid}: a written Core page ({len(P[pid]['text'].split())} words)")
    check("Study notes" in P[pid]["sources"], f"{pid}: credits Study notes")
    for f in FACTS[pid]:
        check(f in md[pid], f"{pid}: states the checked fact '{f}'")
for pid, asp in ASPECTS.items():
    found = re.findall(r"(?m)^### (.+)$", md[pid])
    check(found == asp, f"{pid}: the four aspects in order ({found})")
    check(all(f"**{a}**" in md[pid] for a in asp), f"{pid}: the summary table names all four")
check(any("Schelling" in x and "1960" in x for x in P["network-effects"]["sources"]) and any("Soros" in x and "1987" in x for x in P["network-effects"]["sources"]), "Schelling and Soros credited in sources")

# --- the model's substance
cv = P["coin-value"]["text"]
check("weakest link" in cv and "not a formula" in P["coin-value"]["textDeep"], "both parts needed: weakest link, and not a formula")
check("doesn't apply to a stablecoin" in cv and "wrapped token" in cv, "scope: not for stablecoins or wrapped tokens, which are claims")
check("Distribution" in P["sound-money"]["text"] and "who holds" in P["sound-money"]["text"], "sound money: distribution is part of supply")
ne = P["network-effects"]["text"]
check("runs in reverse" in ne and "falling price" in ne, "network effects: the momentum loop runs both ways")
check({"forks", "memecoins", "claims-and-liabilities", "four-ways-to-earn", "gold"} <= set(P["coin-value"]["links"]), "the parent links Forks, Memecoins, Claims and Liabilities, Four Ways to Earn and Gold")
check("coin-value" in P["forks"]["links"] and "network-effects" in P["memecoins"]["links"] and "coin-value" in P["digital-assets"]["links"], "Forks, Memecoins and the hub link in")
mods = {x["m"].split(" — ")[0] for pid in PAGES for x in P[pid]["quals"] if x["q"] == "princeton-bitcoin"}
check(mods == {"BTC7", "BTC10"}, f"mapped to Princeton BTC7 and BTC10 ({sorted(mods)})")

# --- neutrality and IP guard
alltext = " ".join(md.values()).lower()
check(not re.search(r"\b(today|currently|right now)\b", alltext), "timeless: no 'today' or 'currently'")
check(not re.search(r"bitcoin[^.]{0,60}\b(best|winner|clearest|strongest)\b", alltext), "no verdict naming a winning coin")
hits = [(f.name, ph) for f in REPO.rglob("*") if f.is_file() and f.suffix in (".md", ".js", ".html", ".sql") and ".git" not in f.parts
        for ph in SOURCE_PHRASES if ph in f.read_text(errors="ignore").lower()]
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
            for pid in PAGES:
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(450)
                body_el = pg.locator("#panel-body")
                ok = (pg.locator(".p-title").inner_text() == P[pid]["title"] and body_el.locator(".qa").count() == 2
                      and body_el.locator(".wl.broken").count() == 0 and "[[" not in body_el.inner_text())
                check(ok and pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{pid}: renders with two quizzes, no broken links, no page scroll")
                check(body_el.locator(".deeper").is_visible() == (mode == "normal"), f"{pid}: Going deeper follows the depth setting")
                check(pg.locator(f'#map-svg [data-node="{pid}"]').count() == 1, f"{pid}: on the map")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"{pid}-{w}.png"))
            pg.goto(URL + "#/map/p/coin-value"); pg.wait_for_timeout(400)
            check(pg.locator('#panel-body .p-list [data-page="sound-money"], #panel-body .p-list [data-page="network-effects"]').count() >= 2, "the parent lists its two pages under Inside this topic")
            for q, want in [("what gives a coin value", "coin-value"), ("sound money", "sound-money"), ("network effect", "network-effects"), ("schelling", "network-effects")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 3).map(e => e.getAttribute('href'))")
                check(hrefs[:1] == [f"#/map/p/{want}"], f"search '{q}' puts {want} first ({hrefs})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
