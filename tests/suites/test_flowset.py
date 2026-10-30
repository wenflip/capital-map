"""The seven flows, all written (no outlines left since 2026-10-26; the outline rules are tested on a throwaway outline). Flow data and order, outline rules, the trade flow's verified
facts, build validation, the flows tables in the SQLite export, and the Flows view. Usage: python3 test_flowset.py <repo> <outdir>"""
import sys, pathlib, json, shutil, subprocess, tempfile, sqlite3
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

# id: (area, status, steps). Update when a flow is added or an outline is written (say so in the PR).
FLOWS = {
    "where-money-comes-from": ("How Money Works", "written", 6),   # 2026-10-27 text sweep: the flows heading follows the branch's new name
    "when-a-bank-fails": ("When Things Fail", "written", 5),   # 2026-10-26 housekeeping: moved from Money & Liquidity to sit with the other failure flows
    "when-a-country-fails": ("When Things Fail", "written", 7),
    "how-a-trade-settles": ("Markets & Plumbing", "written", 6),
    "when-a-broker-fails": ("When Things Fail", "written", 5),   # 2026-10-26 failflows branch: written out (was an outline)
    "a-stablecoin-run": ("When Things Fail", "written", 6),     # 2026-10-26 failflows branch: written out (was an outline)
    "qe-and-qt": ("How Money Works", "written", 7),   # 2026-10-26: was a 6-step outline
}
AREAS = ["How Money Works", "When Things Fail", "Markets & Plumbing"]   # 2026-10-27 text sweep: the flows heading follows the branch's new name   # the Flows tab's headings, in order

# --- data checks (no browser)
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]; F = D["flows"]
check(sorted(F) == sorted(FLOWS), f"seven flows ({sorted(F)})")
check(all((F[f]["area"], F[f]["status"], len(F[f]["steps"])) == v for f, v in FLOWS.items()), "every flow: right heading, status and number of steps")
order = sorted(F, key=lambda f: F[f]["order"])
check(list(dict.fromkeys(F[f]["area"] for f in order)) == AREAS, "headings appear in the expected order")
outlines = [f for f in F if F[f]["status"] == "planned"]
check(all(not F[f]["lanes"] for f in outlines), "outlines have no detail columns")
check(all(F[f]["lanes"] for f in F if F[f]["status"] == "written"), "every written flow has detail columns")
check(all(st["page"] in P for f in outlines for st in F[f]["steps"]), "every outline step opens an existing page")
check(not [st["page"] for f in outlines for st in F[f]["steps"] if P[st["page"]]["adv"]], "outline steps open only Core pages, so they work in Core view")
trade = F["how-a-trade-settles"]
check(trade["lanes"] == ["Who acts", "What you hold", "What can go wrong", "Where it happened"], f"trade flow lanes ({trade['lanes']})")
check([st["page"] for st in trade["steps"]] == ["brokers", "exchanges", "settlement", "settlement", "custody", "shares"], "trade flow steps open broker, exchange, settlement (twice), custody, shares")
check("clearing-house-failure" not in [st["page"] for st in trade["steps"]], "a normal process step never opens a failure page")
cells = " ".join(c for st in trade["steps"] for c in st["cells"])
for fact in ["NSCC", "DTC", "28 May 2024", "T+1", "6 May 2010", "about $3 billion", "11 November 2022"]:
    check(fact in cells, f"trade flow states the verified fact: {fact}")
src = REPO.joinpath("flows/how-a-trade-settles.md").read_text()
check("*Sources:" in src and "DTCC" in src and "Shortening the Securities Transaction Settlement Cycle" in src, "trade flow credits its sources")
check(all(REPO.joinpath(f"flows/{f}.md").read_text().count("[[failure-modes") >= 1 for f in ["when-a-broker-fails", "a-stablecoin-run"]), "the broker and stablecoin flows link the failure ladder")
check(not outlines, "no outlines left: every flow is written")   # 2026-10-26

# --- build validation (throwaway copy)
def build_with(edits):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        for path, old, new in edits:
            f = r / path
            if old is None: f.write_text(new); continue   # 2026-10-26: add a throwaway file (e.g. an outline flow)
            t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout
code, out = build_with([])
# 2026-10-26 qe branch: QE and QT is now written (7 steps), so 5 written / 2 planned; outline build checks moved to A stablecoin run
check(code == 0 and "7 flows (7 written, 0 planned)" in out and "flows 7, flow_steps 42" in out, "clean build: 7 flows (7 written, 0 planned), flows exported")   # 2026-10-26: was 5 / 2
# 2026-10-26 failflows branch: no outlines are left in the repo, so the outline rules are tested on a throwaway outline file
OUTLINE = ("---\nid: zz-outline-check\ntitle: Outline check\narea: When Things Fail\norder: 99\nstatus: planned\nsummary: A throwaway outline.\n---\n"
           "Intro.\n\n| Step | Page |\n|---|---|\n| First | [[money]] |\n| Second | [[liquidity]] |\n| Third | [[bonds]] |\n")
OPATH = "flows/zz-outline-check.md"
code, out = build_with([(OPATH, None, OUTLINE)])
check(code == 0 and "8 flows (7 written, 1 planned)" in out, "a well-formed outline still builds")
for label, edits, want in [
    ("an outline with a detail column", [(OPATH, None, OUTLINE.replace("| Step | Page |\n|---|---|", "| Step | Page | Who acts |\n|---|---|---|").replace("[[money]] |", "[[money]] | x |"))], "a planned flow is an outline"),
    ("a written flow with no detail columns", [(OPATH, None, OUTLINE.replace("status: planned\n", ""))], "a written flow needs at least one detail column"),
    ("an outline step with no page", [(OPATH, None, OUTLINE.replace("| Second | [[liquidity]] |", "| Second | — |"))], "every step of an outline must link a page"),
    ("an unknown status", [(OPATH, None, OUTLINE.replace("status: planned", "status: draft"))], "status must be written or planned"),
    ("a written flow marked planned", [("flows/a-stablecoin-run.md", "order: 6\n", "order: 6\nstatus: planned\n")], "a planned flow is an outline"),
]:
    c2, o2 = build_with(edits)
    check(c2 != 0 and want in o2, f"build fails on {label}")

# --- SQLite export
db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
check(db.execute("SELECT COUNT(*), SUM(status = 'planned') FROM flows").fetchone() == (7, 0), "flows table: 7 flows, none planned")   # 2026-10-26: was 3, then 2
check(db.execute("SELECT COUNT(*) FROM flow_steps").fetchone()[0] == sum(v[2] for v in FLOWS.values()), "flow_steps: one row per step")
check(db.execute("SELECT GROUP_CONCAT(page_id, ',') FROM (SELECT page_id FROM flow_steps WHERE flow_id = 'how-a-trade-settles' ORDER BY step)").fetchone()[0]
      == "brokers,exchanges,settlement,settlement,custody,shares", "flow_steps keeps step order")
check(not db.execute("PRAGMA foreign_key_check").fetchall(), "no broken foreign keys")
db.close()
check("`flow_steps`" in REPO.joinpath("data/README.md").read_text(), "data/README.md documents the flow tables")

# 2026-10-26 failflows branch: a throwaway copy of the site with one outline, so the outline view is still tested in the browser
OREPO = pathlib.Path(tempfile.mkdtemp()) / "r"
shutil.copytree(REPO, OREPO, ignore=shutil.ignore_patterns(".git"))
(OREPO / OPATH).write_text(OUTLINE)
subprocess.run([sys.executable, str(OREPO / "tools/build.py")], capture_output=True, text=True, check=True)
OURL = OREPO.joinpath("index.html").as_uri()

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
                pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
                noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

                pg.goto(URL + "#/flows"); pg.wait_for_timeout(350)
                heads = [x.strip().lower() for x in pg.locator("#flows-body h2.flow-area").all_inner_texts()]
                check(heads == [a.lower() for a in AREAS], f"three headings in order ({heads})")
                # 2026-10-26: no outlines left, so no Planned markings anywhere on the real site
                check(pg.locator("#flows-body .flow-card.planned").count() == 0 and pg.locator("#flows-body .planned-tag").count() == 0, "no Planned cards or tags")
                check("Planned" not in pg.locator("#flows-body .view-sub").inner_text(), "the Flows intro no longer mentions Planned")
                trade_area = pg.locator('#flows-body .flow-cards:has([data-flow="how-a-trade-settles"])').evaluate("e => e.previousElementSibling.textContent")
                check(trade_area.strip().lower() == "markets & plumbing", "the trade flow sits under Markets & Plumbing")
                check(noscroll(), "list: no sideways scroll")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"flows-list-{w}-{theme}.png"), full_page=True)

                # the written trade flow
                pg.goto(URL + "#/flows/how-a-trade-settles"); pg.wait_for_timeout(350)
                check(pg.locator(".step-card").count() == 6 and pg.locator(".planned-tag").count() == 0 and pg.locator(".flow-outline-note").count() == 0, "trade flow: 6 steps, no Planned tag, no outline note")
                check(pg.locator(".lane-label:not(.head)").count() == 4, "trade flow: four detail rows")
                check(pg.locator("#flows-body .wl.broken").count() == 0 and noscroll(), "trade flow: links ok, no page scroll")
                pg.locator('.step-card[data-page="custody"]').click(); pg.wait_for_timeout(400)
                check("p/custody" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, "a trade step opens its page beside the flow")
                check(pg.locator('#panel-body .p-list [data-flow="how-a-trade-settles"]').count() == 1, "the page lists the trade flow under What links here")
                if w in (1366, 390) and mode == "normal": pg.goto(URL + "#/flows/how-a-trade-settles"); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / f"flow-trade-{w}-{theme}.png"))

                # an outline
                # 2026-10-26: the outline view, on the throwaway copy with one outline
                pg.goto(OURL + "#/flows"); pg.wait_for_timeout(350)
                planned = pg.locator("#flows-body .flow-card.planned").evaluate_all("els => els.map(e => e.dataset.flow)")
                check(planned == ["zz-outline-check"] and pg.locator("#flows-body .planned-tag").count() == 1, f"throwaway copy: one Planned card with its tag ({planned})")
                check(all("outline" in x for x in pg.locator("#flows-body .flow-card.planned .meta").all_inner_texts()), "outline cards say so in their step count")
                check("Flows marked Planned are outlines" in pg.locator("#flows-body .view-sub").inner_text(), "with an outline present, the Flows intro explains Planned")
                pg.goto(OURL + "#/flows/zz-outline-check"); pg.wait_for_timeout(300)
                ok = (pg.locator(".view-title .planned-tag").count() == 1 and pg.locator(".flow-outline-note").count() == 1
                      and pg.locator(".step-card.linked[data-page]").count() == 3 and pg.locator(".lane-label").count() == 0)
                check(ok and noscroll(), "outline view: Planned tag, outline note, every step linked, no empty label column")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"flow-outline-{w}-{theme}.png"))

                # About counts written and planned flows
                pg.goto(URL + "#/about"); pg.wait_for_timeout(300)
                tile = pg.locator(".about-stat", has_text="flows").inner_text()
                check(tile.startswith("7") and "processes end to end" in tile and "planned" not in tile, f"About: 7 flows, processes end to end ({tile.splitlines()})")   # 2026-10-26: was 4 · 3, then 5 · 2; with none planned the tile drops the split

                # search finds the new flows
                for q, want in [("share trade settles", "how-a-trade-settles"), ("stablecoin run", "a-stablecoin-run"), ("QE and QT", "qe-and-qt")]:
                    pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                    if w < 481: pg.locator("#search").click()
                    pg.fill("#search", q); pg.wait_for_timeout(250)
                    hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                    check(f"#/flows/{want}" in hrefs, f"search '{q}' finds the flow ({hrefs[:3]})")
                    pg.keyboard.press("Escape")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
