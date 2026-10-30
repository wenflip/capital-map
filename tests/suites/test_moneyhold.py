"""Money You Hold (a 14th branch) and How Money Works (the renamed Money & Liquidity): structure, the pages that moved,
the rewritten hub, the root list, stablecoins linked not moved, the first-visit branch, the new pill's colour contrast in
both themes, rendering, depth and search. Usage: python3 test_moneyhold.py <repo> <outdir>"""
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

NEW, OLD = "money-you-hold", "money"
MOVED = ["cash-and-fiat", "bank-deposits", "backstops", "gold"]                      # in order
KEPT = ["what-is-money", "hierarchy-of-money", "central-bank-money", "monetary-policy", "exchange-rates", "eurodollars", "liquidity"]

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
root = P[D["root"]]

# --- structure
check(P[NEW]["parent"] == D["root"] and P[NEW]["group"] == "What you can own", "a top-level branch in What you can own")
own = [b for b in root["children"] if P[b]["group"] == "What you can own"]
check(own[1:4] == ["digital-assets", NEW, "real-assets"], f"between Digital Assets and Real Assets, following the group's tier order ({own})")
check(len(root["children"]) >= 14, f"at least fourteen branches ({len(root['children'])})")   # 2026-10-27 how-markets-move branch: a 15th branch was added; this suite only needs Money You Hold among them
check(P[NEW]["children"] == MOVED, f"cash, deposits, backstops, gold in that order ({P[NEW]['children']})")
check(P[NEW]["title"] == "Money You Hold" and not P[NEW]["stub"] and not P[NEW]["adv"], "titled Money You Hold, written, Core")
check(P["backstops"]["children"] == ["bank-capital-and-liquidity", "lender-of-last-resort", "bail-in", "deposit-insurance", "bank-sovereign-loop"], "Bank Backstops kept its five pages")
check(P["backstops"]["rung"] == 4, "Bank Backstops is still rung 4 of the failure ladder")
check(all(P[k].get("tier") for k in ["cash-and-fiat", "bank-deposits", "gold"]), "the moved stores keep their Cartography fields")
check(P["stablecoins"]["parent"] != NEW and "stablecoins" in P[NEW]["links"], "stablecoins stay in Digital Assets, linked from the new hub")

# --- the renamed hub
check(P[OLD]["title"] == "How Money Works" and P[OLD]["short"] == "How Money Works" and P[OLD]["group"] == "Foundations", "Money & Liquidity is now How Money Works, still in Foundations")
check(P[OLD]["children"] == KEPT, f"it keeps the machinery pages ({P[OLD]['children']})")
old_md = REPO.joinpath("pages/money.md").read_text()
core = old_md.split("## Going deeper")[0]
check("[[money-you-hold|Money You Hold]]" in core, "How Money Works points to Money You Hold")
check(not re.search(r"(?m)^- \[\[(cash-and-fiat|bank-deposits|backstops|gold)\]\]", core), "the moved pages are no longer listed as its own children")
check(NEW in P[OLD]["links"] and OLD in P[NEW]["links"], "the two hubs link each other")

# --- root page lists both
rt = REPO.joinpath("pages/capital-system.md").read_text()
check("[[money-you-hold]]" in rt and rt.index("[[digital-assets]]") < rt.index("[[money-you-hold]]") < rt.index("[[real-assets]]"), "the root page lists Money You Hold between Digital Assets and Real Assets")

# --- the old name is gone from the site's text (SCOPE keeps it only as dated history)
old = [f"{f.parent.name}/{f.name}" for d in ("pages", "flows", "quals", "questions", "paths") for f in REPO.joinpath(d).glob("*.md") if "Money & Liquidity" in f.read_text()]
old += [n for n in ("about.md", "privacy.md", "index.html", "assets/app.js") if "Money & Liquidity" in REPO.joinpath(n).read_text()]
check(not old, f"no page, flow, qual, question or site file still says Money & Liquidity ({old})")
check({D["flows"][f]["area"] for f in ("where-money-comes-from", "qe-and-qt")} == {"How Money Works"}, "the two money flows sit under How Money Works")
check("[[failure-modes]]" in rt and "dealers" in rt, "the root list includes When Things Fail and mentions dealers")

# --- hub content: the comparison table and neutrality
hub = REPO.joinpath(f"pages/{NEW}.md").read_text().split("---", 2)[2]
check(all(x in hub for x in ["| **Whose promise** |", "The central bank's", "Your bank's", "Nobody's"]), "the table compares whose promise each form is")
check(not re.search(r"\b(today|currently|right now|nowadays)\b", hub, re.I), "timeless")
check(not re.search(r"\byou should (buy|sell|hold|keep)\b", hub, re.I), "no advice")

def lum(rgb):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])
def ratio(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return (x + 0.05) / (y + 0.05)
nums = lambda css: [int(float(v)) for v in re.findall(r"[\d.]+", css)[:3]]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            for theme in (["light", "dark"] if mode == "normal" else ["light"]):
                print(f"== {mode} @ {w} {theme}")
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1, color_scheme=theme)
                pg = ctx.new_page()
                pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
                pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(600)
                drawn = pg.evaluate("[...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node)")
                check(NEW in drawn and "monetary-policy" in drawn and "cash-and-fiat" not in drawn, "first visit: How Money Works open, Money You Hold drawn closed")
                # the pill is an SVG rect and its label an SVG text: their colours are in the computed fill
                st = pg.evaluate(f"""(() => {{ const g = document.querySelector('#map-svg [data-node="{NEW}"]');
                  return [getComputedStyle(g.querySelector('.node-box')).fill, getComputedStyle(g.querySelector('.node-label')).fill]; }})()""")
                r = ratio(nums(st[0]), nums(st[1]))
                check(r >= 4.5, f"{theme}: the new pill's label contrast is at least 4.5:1 ({r:.2f}; {st})")
                # 2026-10-27: with 14 branches the collapsed column is taller than a small phone. fit() pins it to the top
                # when the root still shows, so the first branch isn't hidden under the top bar (it was, at 360 px)
                pg.locator('.map-controls [data-act="collapse"]').click(); pg.wait_for_timeout(900)
                pos = pg.evaluate("""(() => { const top = document.querySelector('#map-view').getBoundingClientRect().top,
                    bottom = document.querySelector('.map-controls').getBoundingClientRect().top,
                    f = document.querySelector('#map-svg [data-node="foundation"]').getBoundingClientRect(),
                    r = document.querySelector('#map-svg [data-node="capital-system"]').getBoundingClientRect();
                    return [f.top >= top, r.top >= top && r.bottom <= bottom]; })()""")
                check(pos == [True, True], f"after Collapse all, Foundation is below the top bar and the root is on screen ({pos})")
                pg.goto(URL + f"#/map/p/{NEW}"); pg.wait_for_timeout(500)
                body = pg.locator("#panel-body")
                check(pg.locator(".p-title").inner_text() == "Money You Hold", "the hub opens in the panel")
                check(body.locator("table").count() == 1 and body.locator(".qa").count() == 2 and body.locator(".wl.broken").count() == 0, "table, two quizzes, no broken links")
                check(body.locator(".deeper").is_visible() == (mode == "normal"), "Going deeper shows in Everything and hides in Core")
                check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"moneyhold-{w}-{theme}.png"))
                pg.goto(URL + f"#/map/p/{OLD}"); pg.wait_for_timeout(400)
                check(pg.locator(".p-title").inner_text() == "How Money Works", "the old hub opens under its new name")
                for q, want in [("money you hold", NEW), ("savings", NEW), ("how money works", OLD), ("cash", "cash-and-fiat")]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(250)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                    check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} in the top 5 ({hrefs})")   # questions about cash may rank above the hub
                    pg.keyboard.press("Escape")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
