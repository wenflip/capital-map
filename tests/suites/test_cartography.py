"""Cartography view: data, build validation, chart points, filters, table, click-through, layout. Usage: python3 test_cartography.py <repo> <outdir>"""
import sys, pathlib, json, shutil, subprocess, tempfile
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

KINDS = ["Concentration", "Counterparty", "Inflation", "Liquidity", "Personal", "State", "Theft and self-error"]
STORES = ["human-capital", "social-capital", "gold", "self-custody", "collectibles", "cash-and-fiat",
          "private-business", "bank-deposits", "custodial-crypto", "bonds", "shares", "real-estate"]

# --- data
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
placed = sorted(k for k, v in P.items() if v.get("place"))
check(placed == sorted(STORES), f"the twelve stores carry a place ({placed})")
check(all(v.get("tier") and v.get("killer") and v.get("killerKind") in KINDS for k, v in P.items() if v.get("place")), "every placed page has a tier, a killer and a known kind of killer")
check(all(len(P[k]["place"]) == 2 and all(0 <= n <= 100 for n in P[k]["place"]) for k in placed), "places are two numbers from 0 to 100")
check(P["cash-and-fiat"]["span"] == [36, 63] and not any(P[k]["span"] for k in placed if k != "cash-and-fiat"), "only cash and fiat has a span")
q = lambda k: (P[k]["place"][0] >= 50, P[k]["place"][1] >= 50)
check(q("human-capital") == (False, False) and q("gold") == (True, False) and q("bonds") == (True, True), "stores sit in the expected quadrants")
check([k for k in placed if q(k) == (False, True)] == ["private-business"], "the inside-you-and-recorded quadrant is nearly empty: only private business")

# --- build validation: a broken place must fail the build
def build_with(edit):
    with tempfile.TemporaryDirectory() as d:
        t = pathlib.Path(d) / "r"
        shutil.copytree(REPO, t, ignore=shutil.ignore_patterns(".git"))
        f = t / "pages" / "gold.md"; f.write_text(edit(f.read_text()))
        r = subprocess.run([sys.executable, "tools/build.py"], cwd=t, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
code, _ = build_with(lambda x: x)
check(code == 0, "an unchanged copy builds")
for label, edit in [("place without killer_kind", lambda x: x.replace("killer_kind: Theft and self-error\n", "")),
                    ("place out of range", lambda x: x.replace("place: 72, 24", "place: 72, 140")),
                    ("place with one number", lambda x: x.replace("place: 72, 24", "place: 72")),
                    ("killer_kind without place", lambda x: x.replace("place: 72, 24\n", ""))]:
    code, out = build_with(edit)
    check(code != 0 and "gold" in out, f"build fails on {label}")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for theme in ["light", "dark"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            if theme == "dark" and w != 1366: continue
            print(f"== {theme} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, color_scheme=theme, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate("localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true')"); pg.reload(); pg.wait_for_timeout(400)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            header_fits = lambda: pg.evaluate("[...document.querySelectorAll('header button, header a, header input')].every(e => { const r = e.getBoundingClientRect(); return !r.width || r.right <= innerWidth + 1; })")

            # reach it from the tab
            pg.locator('.tab[data-view="cartography"]').click(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/cartography" and pg.locator("#cartography-view").is_visible(), f"{w}: tab opens #/cartography")
            check(pg.locator('.tab[data-view="cartography"]').evaluate("e => e.classList.contains('active') || e.getAttribute('aria-current') !== null || e.getAttribute('aria-selected') === 'true'"), f"{w}: Cartography tab marked current")
            check(header_fits(), f"{w}: every header control fits on screen")
            check(noscroll(), f"{w}: no sideways scroll")

            pts = pg.locator(".cart-pt")
            check(pts.count() == 12, f"{w}: twelve points plotted ({pts.count()})")
            ids = sorted(pg.eval_on_selector_all(".cart-pt", "els => els.map(e => e.dataset.page)"))
            check(ids == sorted(STORES), f"{w}: every placed page is on the chart")
            check(pg.locator(".cart-pt[data-page='cash-and-fiat'] .c-span").count() == 1, f"{w}: cash and fiat draws its span")
            check(pg.locator(".cq-label").count() == 4, f"{w}: four quadrant labels")
            check(pg.locator(".cart-table tbody tr").count() == 12, f"{w}: table lists twelve stores")
            check(pg.eval_on_selector_all(".cart-pt", "els => els.every(e => (e.getAttribute('href') || '').startsWith('#/'))"), f"{w}: points have real link addresses")
            # labels inside the chart's frame
            inside = pg.evaluate("""() => { const svg = document.querySelector('.cart-chart svg'), vb = svg.viewBox.baseVal;
                return [...svg.querySelectorAll('.c-pt-label, .cq-label')].every(t => { const b = t.getBBox(); return b.x >= 0 && b.y >= 0 && b.x + b.width <= vb.width && b.y + b.height <= vb.height; }); }""")
            check(inside, f"{w}: every label sits inside the chart")

            # filters
            chips_t = pg.locator("[data-ctier]"); chips_k = pg.locator("[data-ckind]")
            check(chips_t.count() == 4 and chips_k.count() == 1 + len(KINDS), f"{w}: tier and killer chips present ({chips_t.count()}, {chips_k.count()})")
            on = lambda: sorted(pg.eval_on_selector_all(".cart-pt:not(.off)", "els => els.map(e => e.dataset.page)"))
            rows_on = lambda: pg.locator(".cart-table tbody tr:not(.off)").count()
            pg.locator("[data-ctier='1']").click(); pg.wait_for_timeout(100)
            check(on() == ["human-capital", "social-capital"] and rows_on() == 2, f"{w}: Tier 1 leaves the two inside-you stores")
            pg.locator("[data-ctier='2']").click(); pg.wait_for_timeout(100)
            check("cash-and-fiat" in on() and "gold" in on() and "bonds" not in on(), f"{w}: Tier 2 includes cash (tier 2-3) and gold")
            pg.locator("[data-ctier='3']").click(); pg.wait_for_timeout(100)
            check("cash-and-fiat" in on() and "gold" not in on() and len(on()) == 7, f"{w}: Tier 3 includes cash and the legible stores ({len(on())})")
            pg.locator("[data-ckind='Counterparty']").click(); pg.wait_for_timeout(100)
            check(on() == sorted(["bank-deposits", "custodial-crypto", "bonds", "shares"]), f"{w}: Tier 3 + Counterparty combine")
            check(pg.locator("[data-ckind='Counterparty']").evaluate("e => e.classList.contains('on')") and pg.locator("[data-ctier='3']").evaluate("e => e.classList.contains('on')"), f"{w}: both chosen chips show as on")
            pg.locator("[data-ctier='']").click(); pg.locator("[data-ckind='']").click(); pg.wait_for_timeout(100)
            check(len(on()) == 12 and rows_on() == 12, f"{w}: All resets the filters")
            pg.screenshot(path=str(OUT / f"cart-{theme}-{w}.png"))

            # click-through from the chart and from the table
            pg.locator(".cart-pt[data-page='gold']").click(force=True); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash") == "#/cartography/p/gold", f"{w}: clicking a point opens its page beside the chart ({pg.evaluate('location.hash')})")
            check(pg.locator("#cartography-view").is_visible() or mob, f"{w}: chart stays in place behind the page")
            pg.goto(URL + "#/cartography"); pg.wait_for_timeout(300)
            pg.locator(".cart-table a[data-page='bonds']").click(); pg.wait_for_timeout(400)
            check(pg.evaluate("location.hash").endswith("/p/bonds"), f"{w}: table row opens its page")

            # back to it from the model page
            pg.goto(URL + "#/map/p/cartography-of-wealth"); pg.wait_for_timeout(400)
            lnk = pg.locator("a[href='#/cartography']:visible")
            check(lnk.count() >= 1, f"{w}: model page links to the chart")
            if lnk.count():
                lnk.first.click(); pg.wait_for_timeout(400)
                check(pg.evaluate("location.hash") == "#/cartography" and pg.locator(".cart-pt").count() == 12, f"{w}: that link opens the chart")
            ctx.close()

print("Console errors:", len(errs)); [print("  ", e) for e in errs]
if errs: fails.append("console errors")
print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
