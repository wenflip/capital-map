"""Failures view: the failure ladder as data (rung fields, fails_at), its grounding in the rung pages, build validation,
the SQLite export, and the view (ladder, store x rung matrix, panels, phone header). Usage: python3 test_failures.py <repo> <outdir>"""
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

RUNGS = ["broker-failure", "insurer-failure", "stablecoins", "backstops", "clearing-house-failure", "ratings-failure",
         "capital-controls", "confiscation", "financial-repression", "currency-failure", "sovereign-default", "market-failure"]
# The matrix, store -> rung numbers. Update when a rung page's "What it kills" changes (say so in the PR).
EXPECT = {
    "bank-deposits": [4, 6, 7, 8, 9, 10, 11], "bonds": [1, 2, 4, 5, 6, 7, 9, 10, 11, 12], "cash-and-fiat": [7, 9, 10, 11],
    "collectibles": [12], "custodial-crypto": [1, 3], "gold": [8], "human-capital": [2, 11], "private-business": [8],
    "real-estate": [2, 8], "self-custody": [3], "shares": [1, 4, 5, 6, 7, 8, 11, 12], "social-capital": [],
}
# links on a rung page that say the rung does NOT touch a store: never a dot
NOT_HIT = {"broker-failure": ["self-custody", "gold", "real-estate"]}

# --- data checks (no browser)
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
check(D.get("rungs") == RUNGS, f"twelve rungs in ladder order ({D.get('rungs')})")
check([P[r]["rung"] for r in RUNGS] == list(range(1, 13)), "rungs numbered 1 to 12")
check(all(P[r]["rungName"] and P[r]["backstop"] for r in RUNGS), "every rung has a name and a backstop")
check(not [p for p in P if P[p]["rung"] and p not in RUNGS], "no other page is a rung")
# 2026-10-27 money-you-hold branch: Bank Backstops moved with Bank Deposits
check({P[p]["parent"] for p in ("stablecoins", "backstops")} == {"tokens", "money-you-hold"}, "Stablecoins and Bank Backstops keep their own parents")

# the hub's ladder table agrees with the rung fields
hub = REPO.joinpath("pages/failure-modes.md").read_text()
rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in hub.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
check(len(rows) == 12, f"hub ladder table has 12 rows ({len(rows)})")
check(all(int(r[0]) == P[RUNGS[i]]["rung"] and r[1] == P[RUNGS[i]]["rungName"] and f"[[{RUNGS[i]}]]" in r[2] and r[3] == P[RUNGS[i]]["backstop"]
          for i, r in enumerate(rows)), "hub table: number, name, page and backstop match every rung")

stores = sorted(p for p in P if P[p]["place"])
check(stores == sorted(EXPECT), f"twelve stores of wealth ({len(stores)})")
got = {st: [P[r]["rung"] for r in P[st]["failsAt"]] for st in stores}
check(got == EXPECT, "fails_at matches the expected matrix" + ("" if got == EXPECT else f" ({ {k: v for k, v in got.items() if v != EXPECT[k]} })"))
check(sum(len(v) for v in got.values()) == 39, "39 store-rung links")
check(all(sorted(P[r]["hits"]) == sorted(st for st in stores if r in P[st]["failsAt"]) for r in RUNGS), "every rung's hits is the exact inverse of fails_at")
check(not [p for p in P if P[p]["failsAt"] and not P[p]["place"]], "fails_at only on stores")

# grounding: every dot is a link to the store on the rung's own page; template rungs: inside What it kills
def kills(pid):
    t = REPO.joinpath(f"pages/{pid}.md").read_text()
    m = re.search(r"(?ms)^## What it kills\s*$(.*?)(?=^## |\Z)", t)
    return m.group(1) if m else t
ungrounded = [(st, r) for st in stores for r in P[st]["failsAt"] if not re.search(r"\[\[" + re.escape(st) + r"(\\?\||\]\])", kills(r))]
check(not ungrounded, f"every dot is grounded in a link on the rung's page ({ungrounded[:4]})")
check(all(re.search(r"\[\[" + st, kills(r)) and r not in P[st]["failsAt"] for r, sts in NOT_HIT.items() for st in sts),
      "a 'doesn't touch' link on a rung page is never a dot (broker failure: self-custody, gold, real estate)")

# --- build validation (throwaway copy)
def build_with(edits):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        for path, old, new in edits:
            f = r / path; t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout, r.joinpath("data/capital-map.sql").read_text() if p.returncode == 0 else ""
code, out, fresh_sql = build_with([])
check(code == 0 and "Failure ladder: 12 rungs · 39 store-rung links" in out and "SQLite: data/capital-map.sqlite" in out, "clean build passes and reports the ladder and the export")
for label, edits, want in [
    ("a gap in the rung numbers", [("pages/market-failure.md", "rung: 12", "rung: 13")], "numbered 1 to 12"),
    ("fails_at naming a page that isn't a rung", [("pages/gold.md", "fails_at: confiscation", "fails_at: confiscation, money")], "fails_at 'money' is not a rung"),
    ("fails_at on a page that isn't a store", [("pages/money.md", "\n---", "\nfails_at: confiscation\n---")], "only used on stores"),
    ("a rung with no backstop", [("pages/confiscation.md", "backstop: Courts, constitutions, compensation\n", "")], "needs rung_name and backstop"),
]:
    c2, o2, _ = build_with(edits)
    check(c2 != 0 and want in o2, f"build fails on {label}")

# --- the SQLite export
dbf, sqlf = REPO / "data/capital-map.sqlite", REPO / "data/capital-map.sql"
check(dbf.exists() and sqlf.exists(), "data/capital-map.sqlite and .sql are committed")
check(sqlf.read_text() == fresh_sql, "the committed export matches a fresh build (not stale)")
db = sqlite3.connect(f"file:{dbf}?mode=ro", uri=True)
one = lambda q: db.execute(q).fetchone()[0]
counts = {t: one(f"SELECT COUNT(*) FROM {t}") for t in ["pages", "stores", "rungs", "fails_at", "quals", "modules"]}
check(counts == {"pages": len(P), "stores": 12, "rungs": 12, "fails_at": 39, "quals": 9, "modules": 68}, f"row counts ({counts})")
check(not db.execute("PRAGMA foreign_key_check").fetchall(), "no broken foreign keys")
check(one("SELECT COUNT(*) FROM pages WHERE parent_id IS NULL") == 1, "exactly one root in pages")
check(one("SELECT tier_min || '-' || tier_max FROM stores WHERE page_id = 'cash-and-fiat'") == "2-3", "a tier range is split into tier_min and tier_max")
pairs = sorted(db.execute("SELECT f.store_id, r.number FROM fails_at f JOIN rungs r ON r.page_id = f.rung_id").fetchall())
check(pairs == sorted((st, n) for st, ns in EXPECT.items() for n in ns), "fails_at in the database matches the matrix")
cov = db.execute("SELECT q.id, SUM(m.state = 'mapped'), SUM(m.state <> 'out') FROM quals q JOIN modules m ON m.qual_id = q.id GROUP BY q.id").fetchall()
check(all((D["quals"][q]["coverage"]["mapped"], D["quals"][q]["coverage"]["inScope"]) == (a, b) for q, a, b in cov), "modules table reproduces the Quals coverage")
readme = REPO.joinpath("data/README.md").read_text()
queries = re.findall(r"```sql\n(.*?)```", readme, re.S)
ran = []
for q in queries:
    try: ran.append(db.execute(q).fetchall())
    except sqlite3.Error as e: ran.append(e)
check(len(queries) == 5 and not [r for r in ran if isinstance(r, Exception)], f"all {len(queries)} starter queries in data/README.md run")
check(len(ran) == 5 and ran[3] == [("social-capital",)], "starter query 4 finds the store no rung reaches")
db.close()

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

                # the header still fits with six tabs
                right = pg.evaluate("Math.round(document.querySelector('#theme-btn').getBoundingClientRect().right)")
                check(right <= w, f"header fits: theme button at {right} of {w}")
                tab = pg.locator('.tab[data-view="failures"]')
                check(tab.is_visible() and tab.inner_text().strip() == ("Ladder" if w <= 480 else "Failures"), f"Failures tab visible, labelled '{tab.inner_text().strip()}'")
                tab.click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/failures" and pg.locator("#failures-view.active").count() == 1, "tab opens #/failures")

                # the ladder, top rung first
                nums = pg.locator("#failures-body .rung .rung-n").all_inner_texts()
                check(nums == [str(n) for n in range(12, 0, -1)], f"ladder runs 12 down to 1 ({nums[:3]}…)")
                chips = pg.locator("#failures-body .rung").evaluate_all("els => els.map(e => e.querySelectorAll('.store-chip').length)")
                check(chips == [len(P[r]["hits"]) for r in reversed(RUNGS)], "each rung shows a chip for every store it hits")
                check("Backstop: Courts, constitutions, compensation" in pg.locator("#failures-body .rung").nth(4).inner_text(), "rung 8 shows its backstop")

                # the matrix
                check(pg.locator(".fail-matrix tbody tr").count() == 12 and pg.locator(".fail-matrix thead .fm-rung").count() == 12, "matrix: 12 stores x 12 rungs")
                check(pg.locator(".fail-matrix .fm-dot").count() == 39, f"39 dots ({pg.locator('.fail-matrix .fm-dot').count()})")
                rows = pg.locator(".fail-matrix tbody tr").evaluate_all("rs => rs.map(r => [r.querySelector('[data-page]').dataset.page, [...r.querySelectorAll('td')].slice(0, 12).map((c, i) => c.classList.contains('hit') ? i + 1 : 0).filter(Boolean), r.querySelector('.fm-count').textContent, r.querySelector('.fm-killer').textContent])")
                check(all(EXPECT[st] == dots and str(len(dots)) == n and k == P[st]["killer"] for st, dots, n, k in rows), "every row: right dots, right count, the store's own killer")
                foot = pg.locator(".fail-matrix tfoot .fm-count").all_inner_texts()
                check(foot == [str(len(P[r]["hits"])) for r in RUNGS], "footer counts the stores each rung hits")
                note = pg.locator("#failures-body .fm-note").inner_text()
                check("More dots doesn't mean more risk" in note and "judgments" in note, "neutrality note: more dots isn't more risk; placements are judgments")
                al = pg.locator(".fail-matrix .fm-dot").first.get_attribute("aria-label") or ""
                check(al.startswith("Rung ") and "can hit" in al, f"dots have accessible labels ({al})")
                bg = pg.evaluate("[getComputedStyle(document.querySelector('.fm-dot')).backgroundColor, getComputedStyle(document.querySelector('.fm-wrap')).backgroundColor]")
                check(bg[0] != bg[1], f"dots stand out from the table ({theme})")
                hrefs = pg.locator("#failures-body .fm-data a[download]").evaluate_all("as => as.map(a => a.getAttribute('href'))")
                check(hrefs == ["data/capital-map.sqlite", "data/capital-map.sql"] and all(REPO.joinpath(x).exists() for x in hrefs), "download links point at the committed export")
                check(noscroll(), "no sideways page scroll")
                if w <= 480:
                    wrap = pg.locator(".fm-wrap")
                    check(wrap.evaluate("e => e.scrollWidth > e.clientWidth"), "phone: the matrix scrolls inside its box")
                    check(pg.locator(".fm-hint").is_visible(), "phone: a hint says to scroll sideways")
                    wrap.evaluate("e => { e.scrollLeft = 500 }"); pg.wait_for_timeout(100)
                    x = pg.locator(".fail-matrix tbody .fm-store").first.evaluate("e => e.getBoundingClientRect().left - e.closest('.fm-wrap').getBoundingClientRect().left")
                    check(abs(x) < 3, f"phone: the store column stays pinned while scrolling ({x:.0f})")
                if w in (1366, 390): pg.screenshot(path=str(OUT / f"failures-{w}-{mode}-{theme}.png"), full_page=True)

                # matrix links open pages; a rung header opens the rung
                pg.locator('.fail-matrix tbody [data-page="gold"]').click(); pg.wait_for_timeout(400)
                check("p/gold" in pg.evaluate("location.hash") and pg.locator("body.panel-open").count() == 1, "a store in the matrix opens its page")
                lad = pg.locator("#panel-body .cart-ladder").inner_text()
                check("failure ladder" in lad and "Confiscation" in lad, "store panel lists its rungs (gold: confiscation)")
                pg.goto(URL + "#/failures/p/social-capital"); pg.wait_for_timeout(400)
                check("no rung" in pg.locator("#panel-body .cart-ladder").inner_text(), "a store on no rung says so")
                pg.goto(URL + "#/failures"); pg.wait_for_timeout(300)
                pg.locator('.fail-matrix thead [data-page="stablecoins"]').click(); pg.wait_for_timeout(400)
                rn = pg.locator("#panel-body .rung-note")
                check(rn.count() == 1 and "rung 3 of 12" in rn.inner_text().lower() and rn.locator(".store-chip").count() == 2, "a rung header opens the rung, whose panel shows Rung 3 of 12 and its stores")
                rn.locator('[data-view="failures"]').click(); pg.wait_for_timeout(300)
                check(pg.evaluate("location.hash").startswith("#/failures"), "the panel links back to the ladder")
                check(pg.locator("#panel-body .rung-note, #panel-body .cart-ladder").count() >= 1, "panel still open beside the ladder")
                pg.goto(URL + "#/map/p/money"); pg.wait_for_timeout(300)
                check(pg.locator("#panel-body .rung-note, #panel-body .cart-ladder").count() == 0, "pages that are neither store nor rung show no ladder box")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
