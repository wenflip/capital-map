"""How Money Works branch (Money & Liquidity until 2026-10-27), Cartography fields, share image. Usage: python3 test_money.py <repo> <outdir>"""
import sys, pathlib, struct
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

WRITTEN = ["capital-system", "money", "what-is-money", "hierarchy-of-money", "gold", "central-bank-money", "cash-and-fiat",
           "bank-deposits", "liquidity", "eurodollars", "money-creation", "claims-and-liabilities", "cartography-of-wealth"]
ADVANCED = ["eurodollars", "money-creation"]
# page -> (tier label fragment, killer fragment); None = no Cartography box
CART = {"gold": ("Tier 2 · Private / bearer", "physical theft"),
        "cash-and-fiat": ("Tier 2 · Private / bearer ↔ Tier 3", "inflation"),
        "bank-deposits": ("Tier 3 · Legible", "bank failure"),
        "what-is-money": None, "liquidity": None}

# --- static checks (no browser)
html = REPO.joinpath("index.html").read_text()
check('content="https://thecapitalmap.pages.dev/"' in html and 'content="https://thecapitalmap.pages.dev/assets/share.png"' in html, "og:url and og:image point at the live address")
png = REPO.joinpath("assets/share.png").read_bytes()
check(png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630), "share.png is a 1200×630 PNG")
check("Supply" not in html, "no Supply Map wording left in index.html")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        simple = mode == "simple"
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(500)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

            # first visit opens the Money branch on the map
            drawn = pg.evaluate("[...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node)")
            check("monetary-policy" in drawn and "hierarchy-of-money" in drawn, "first visit: Money branch open on the map")   # 2026-10-27 money-you-hold branch: Gold moved to Money You Hold, so check other Money pages
            check(all((a in drawn) != simple for a in ["eurodollars"]), f"advanced Money pages {'hidden in Core' if simple else 'drawn in Everything'}")

            # written pages: real pages, no broken links, no stub note, no sideways scroll
            P = pg.evaluate("(() => { const P = window.MUDMAP.pages, o = {}; for (const k in P) o[k] = { stub: !!P[k].stub, adv: !!P[k].adv }; return o; })()")
            bad = []
            for pid in WRITTEN:
                if pid not in P: bad.append(f"{pid}: missing"); continue
                if P[pid]["stub"]: bad.append(f"{pid}: stub")
                if simple and P[pid]["adv"]: continue
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(150)
                body = pg.locator("#panel-body")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}: broken link")
                if body.locator(".stub-note:visible").count() and not body.locator(".adv-note").count(): bad.append(f"{pid}: stub note")
                if "what it is" not in " | ".join(body.locator("h2:visible").all_inner_texts()).lower(): bad.append(f"{pid}: no 'What it is'")
                if not noscroll(): bad.append(f"{pid}: h-scroll")
            check(not bad, f"written pages complete {bad}")
            check(all(P[a]["adv"] for a in ADVANCED), "eurodollars and money creation are advanced")

            # Cartography box
            for pid, want in CART.items():
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(150)
                box = pg.locator("#panel-body .cart-note")
                if want is None:
                    check(box.count() == 0, f"{pid}: no Cartography box")
                else:
                    t = box.inner_text() if box.count() else ""
                    check(want[0].lower() in t.lower() and want[1] in t.lower() and "judgment" in t.lower(), f"{pid}: Cartography box shows tier and killer")
            if simple and w in (1366, 390):
                pg.goto(URL + "#/map/p/cash-and-fiat"); pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"money-cash-{w}.png"))

            # Cartography table: 10 rows of 4 cells; piped links stay in one cell
            pg.goto(URL + "#/map/p/cartography-of-wealth"); pg.wait_for_timeout(200)
            rows = pg.evaluate("""() => { const t = [...document.querySelectorAll('#panel-body table')].find(t => /Killer/.test(t.innerText));
                return t ? [...t.querySelectorAll('tbody tr')].map(r => r.children.length) : []; }""")
            check(rows == [4] * 12, f"twelve stores table: 12 rows × 4 cells, matching the chart ({rows})")
            a = pg.locator('#panel-body a.wl[data-page="gold"]').first
            check(a.count() == 1 and a.inner_text() == "Precious metals", "piped link in a table keeps its label")
            check("Study notes" in pg.locator("#panel-body").inner_text(), "Cartography credits Study notes")

            # hub: quizzes visible in both depths; Going deeper only in Everything
            pg.goto(URL + "#/map/p/hierarchy-of-money"); pg.wait_for_timeout(200)
            check(pg.locator("#panel-body .qa:visible").count() >= 1, "hierarchy quiz visible at this depth")
            check(pg.locator("#panel-body .deeper:visible").count() == (0 if simple else 1), "Going deeper only in Everything")

            # keyboard: Tab reaches an in-text link with a visible focus ring, Enter follows it
            if not mob:
                pg.goto(URL + "#/map/p/money"); pg.wait_for_timeout(300)
                pg.locator("#panel-close").focus()
                hit = None
                for _ in range(40):
                    pg.keyboard.press("Tab")
                    hit = pg.evaluate("""() => { const a = document.activeElement;
                        if (!a || !a.matches('#panel-body a.wl')) return null;
                        const s = getComputedStyle(a); return { id: a.dataset.page, ring: s.outlineStyle !== 'none' || s.boxShadow !== 'none' }; }""")
                    if hit: break
                check(bool(hit) and hit["ring"], f"Tab reaches an in-text link with a focus ring ({hit})")
                if hit:
                    pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
                    check(pg.evaluate("location.hash") == f"#/map/p/{hit['id']}", "Enter on a focused link opens it")

            # flow
            pg.goto(URL + "#/flows/where-money-comes-from"); pg.wait_for_timeout(300)
            check(pg.locator(".step-card").count() == 6 and noscroll(), "flow: 6 steps, no sideways scroll")

            # search
            for q, want, adv in [("net liquidity", "liquidity", False), ("legal tender", "cash-and-fiat", False), ("swap lines", "eurodollars", True)]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                found = f"#/map/p/{want}" in hrefs
                check(found != (adv and simple), f"search '{q}' {'hides' if adv and simple else 'finds'} {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
