"""The beginner path ("Start from the beginning"): data, Core-only pages with reasons, build validation, SQLite tables, the Start card,
the path view, ticks updating progress and Continue, persistence across reload, ticks shared with qualification lists, and the
welcome option. Usage: python3 test_path.py <repo> <outdir>"""
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

PATH = ["what-is-money", "bank-deposits", "claims-and-liabilities", "inflation", "compounding", "four-ways-to-earn",
        "risk-and-return", "bonds", "shares", "diversification", "cartography-of-wealth"]   # update if the path changes (say so in the PR)

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
sp = D["paths"]
check(list(sp) == ["start-here"], f"one path, start-here ({list(sp)})")
items = [it for st in sp["start-here"]["stages"] for it in st["items"]]
check([it["page"] for it in items] == PATH, "the eleven pages, in reading order")
check(PATH[0] == "what-is-money" and PATH[-1] == "cartography-of-wealth", "from what money is to the risks to your own wealth")
check(all(not P[x]["adv"] for x in PATH), "Core pages only")
check(all(it["note"] for it in items), "every step has a reason")
check(not (set(sp) & set(D["questions"])), "path ids don't clash with question ids")

def build_with(edits):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        for path, old, new in edits:
            f = r / path; t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout
code, out = build_with([])
check(code == 0 and "Path Beginner path: 11 pages" in out and "paths 1, path_steps 11" in out, "clean build reports and exports the path")
F = "paths/start-here.md"
for label, edits, want in [
    ("an advanced page", [(F, "[[compounding]]", "[[money-creation]]")], "is an advanced page"),
    ("a step without a reason", [(F, "[[bonds]] — lending: what a bond is, and whose promise you hold", "[[bonds]]")], "needs a one-line reason"),
    ("too few pages (seven)", [(F, "- [[risk-and-return]] — why higher returns come with a wider range of outcomes\n", ""), (F, "- [[shares]] — owning: what a share is, and why it can rise or fall so much\n- [[diversification]] — spreading what you own so one failure can't take everything\n- [[cartography-of-wealth]] — what is most likely to kill each kind of wealth you might hold\n", "")], "8 to 12 pages"),
    ("a broken link", [(F, "[[inflation]]", "[[no-such-page]]")], "broken link [[no-such-page]]"),
]:
    c2, o2 = build_with(edits)
    check(c2 != 0 and want in o2, f"build fails on {label}")

db = sqlite3.connect(f"file:{REPO / 'data/capital-map.sqlite'}?mode=ro", uri=True)
rows = [r[0] for r in db.execute("SELECT page_id FROM path_steps WHERE path_id = 'start-here' ORDER BY step")]
check(rows == PATH, "path_steps keeps the reading order")
check(not db.execute("PRAGMA foreign_key_check").fetchall(), "no broken foreign keys")
db.close()
check("beginner path" in REPO.joinpath("privacy.md").read_text(), "Privacy says path ticks are kept in the browser")

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
                # first visit: the welcome option opens the path
                pg.goto(URL + "#/map"); pg.wait_for_timeout(500)
                pg.locator('[data-wc="path"]').click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/start/start-here" and pg.locator("#start-view.active").count() == 1, "the welcome guide's 'Start from the beginning' opens the path")
                pg.evaluate(f"localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(400)
                check(pg.locator(".spath-list .path-item").count() == 11, "the path lists eleven pages")
                check(pg.locator(".path-progress").inner_text().startswith("0 of 11"), "progress starts at 0 of 11")
                check(pg.locator(".path-actions .btn.primary").inner_text().startswith("Start: What Money Is"), "the button starts at page 1")
                boxes = pg.locator(".spath-list input[data-known]")
                boxes.nth(0).check(); boxes.nth(1).check(); pg.wait_for_timeout(250)
                check(pg.locator(".path-progress").inner_text().startswith("2 of 11"), "ticking two pages updates progress")
                check(pg.locator(".path-actions .btn.primary").inner_text().startswith("Continue: Claims and Liabilities"), "Continue moves to the first unticked page")
                pg.reload(); pg.wait_for_timeout(450)
                check(pg.locator(".spath-list input:checked").count() == 2 and pg.locator(".path-progress").inner_text().startswith("2 of 11"), "ticks and progress survive a reload")
                pg.locator(".path-actions .btn.primary").click(); pg.wait_for_timeout(450)
                check(pg.evaluate("location.hash") == "#/start/start-here/p/claims-and-liabilities" and pg.locator("body.panel-open").count() == 1, "Continue opens the next page beside the path")
                check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways page scroll")
                if w in (1366, 390) and mode == "normal": pg.screenshot(path=str(OUT / f"path-{w}-{theme}.png"))
                # the Start card shows the same progress; ticks are shared with qualification lists
                pg.goto(URL + "#/start"); pg.wait_for_timeout(350)
                card = pg.locator(".spath-card")
                check(card.count() == 1 and "2 of 11" in card.inner_text(), "the Start card shows the path's progress")
                pg.goto(URL + "#/quals/money-banking"); pg.wait_for_timeout(350)
                shared = pg.locator('#quals-body input[data-known="what-is-money"]')
                check(shared.count() == 0 or shared.first.is_checked(), "a page ticked on the path is ticked everywhere it appears")
                card_link = None
                pg.goto(URL + "#/start"); pg.wait_for_timeout(300)
                card.click(); pg.wait_for_timeout(350)
                check(pg.evaluate("location.hash") == "#/start/start-here", "the Start card opens the path")
                pg.locator('#start-body .back[data-question=""]').click(); pg.wait_for_timeout(300)
                check(pg.evaluate("location.hash") == "#/start", "back to Start")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
