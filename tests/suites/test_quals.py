"""Quals view: nine qualifications, mapped and placeholder, modules, focus, chips, search. Usage: python3 test_quals.py <repo> <outdir>"""
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

ORDER = ["cfa-l1", "cfa-l2", "cfa-l3", "money-banking", "frm-1", "frm-2", "caia-l1", "caia-l2", "princeton-bitcoin"]
MAPPED = {"cfa-l1", "money-banking", "caia-l1", "caia-l2", "princeton-bitcoin"}
# module counts and names from the official outlines (CFA 2027 Level I/II, Level III core; GARP FRM; CAIA; Princeton textbook)
MODULES = {"cfa-l1": 10, "cfa-l2": 10, "cfa-l3": 6, "money-banking": 6, "frm-1": 4, "frm-2": 6, "caia-l1": 7, "caia-l2": 8, "princeton-bitcoin": 11}
CFA1 = ["Ethical and Professional Standards", "Quantitative Methods", "Economics", "Financial Statement Analysis", "Corporate Finance",
        "Equities", "Fixed Income", "Derivatives and Risk Management", "Alternative Investments", "Portfolio Construction"]

# --- data checks (no browser)
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1])
Q = D["quals"]
check(sorted(Q, key=lambda q: Q[q]["order"]) == ORDER, f"nine qualifications in order ({sorted(Q, key=lambda q: Q[q]['order'])})")
check({q for q in Q if Q[q]["pages"]} == MAPPED and all(Q[q]["status"] == "planned" for q in Q if q not in MAPPED), "five mapped, four placeholders")
check({q: len(Q[q]["stages"]) for q in Q} == MODULES, "every qualification lists its full module set")
check([re.sub(r"^\S+\s+—\s+", "", st["title"]) for st in Q["cfa-l1"]["stages"]] == CFA1, "CFA I modules use the 2027 topic names, in outline order")
eth = [st for q in Q for st in Q[q]["stages"] if "Ethic" in st["title"]]
check(eth and all(not st["items"] and "scope" in st["note"] for st in eth), f"every ethics module is listed, unmapped and marked out of scope ({len(eth)})")
codes = [(q, st["title"].split(" — ")[0]) for q in Q for st in Q[q]["stages"]]
check(len({c for _, c in codes}) == len(codes), "module codes are unique across all qualifications")
check(not [p for q in MAPPED for p in Q[q]["pages"] if p not in D["pages"]], "every mapped page exists")

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

            # the tab is visible and opens the list
            tab = pg.locator('.tab[data-view="quals"]')
            check(tab.is_visible(), "Quals tab is visible")
            tab.click(); pg.wait_for_timeout(400)
            cards = pg.locator("#quals-body .flow-card")
            check(cards.count() == 9 and pg.evaluate("location.hash") == "#/quals", f"nine qualification cards ({cards.count()})")
            check(pg.locator("#quals-body .flow-card .planned-tag").count() == 4, "four cards marked Planned")
            check(pg.locator('#quals-body [data-qual="cfa-l1"] [data-progress]').count() == 1 and pg.locator('#quals-body [data-qual="frm-1"] [data-progress]').count() == 0, "progress bars only on mapped qualifications")
            check(noscroll(), "list: no sideways scroll")
            if simple and w in (1366, 390): pg.screenshot(path=str(OUT / f"quals-list-{w}.png"), full_page=True)

            # a mapped qualification
            pg.locator('#quals-body [data-qual="cfa-l1"]').click(); pg.wait_for_timeout(400)
            heads = pg.locator("#quals-body h2.mod-head").all_inner_texts()
            check(len(heads) == 10, f"CFA I shows all ten modules ({len(heads)})")
            check("Out of scope" in heads[0] and "Not mapped yet" not in heads[3] and "Not mapped yet" not in " ".join(heads[1:]), "ethics is out of scope; every other CFA I module, financial statements included, is mapped")
            check(pg.locator("#quals-body [data-setrole]").count() == 1, "mapped qualification has a focus button")
            pg.goto(URL + "#/quals/princeton-bitcoin"); pg.wait_for_timeout(400)
            bh = pg.locator("#quals-body h2.mod-head").all_inner_texts()
            check(len(bh) == 11 and not any("Not mapped yet" in x for x in bh), "Princeton: every module mapped, BTC6 included")
            pg.goto(URL + "#/quals/caia-l1"); pg.wait_for_timeout(400)
            ch = pg.locator("#quals-body h2.mod-head").all_inner_texts()
            check(len(ch) == 7 and "Not mapped yet" in ch[3] and "Out of scope" in ch[0], "an empty module on a mapped qualification shows Not mapped yet (CAIA I hedge funds)")
            check("[[" not in pg.locator("#quals-body").inner_text(), "module notes show no raw link syntax")
            pg.goto(URL + "#/quals/cfa-l1"); pg.wait_for_timeout(400)
            first = pg.locator('#quals-body .path-item a.pi-title').first
            pid = first.get_attribute("data-page")
            first.click(); pg.wait_for_timeout(400)
            check(pg.locator("body.panel-open").count() == 1 and pid in pg.evaluate("location.hash"), f"a module item opens its page beside the list ({pid})")
            check(pg.locator(f'#panel-body .chip.qual[data-qual="cfa-l1"]').count() >= 1, "the page shows its CFA I chip")
            if not mob:
                pg.locator("#panel-close").click(); pg.wait_for_timeout(250)
                pg.locator('#quals-body .mod-jump[data-jump="mod-cfa-l1-6"]').click(); pg.wait_for_timeout(700)
                top = pg.evaluate("document.getElementById('mod-cfa-l1-6').getBoundingClientRect().top")
                check(0 <= top < 200, f"module jump scrolls to Fixed Income ({int(top)})")
            if simple and w == 1366: pg.goto(URL + "#/quals/cfa-l1"); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / "quals-cfa1-1366.png"))
            check(noscroll(), "CFA I: no sideways scroll")

            # tick a page: progress updates
            pg.goto(URL + "#/quals/money-banking"); pg.wait_for_timeout(400)
            box = pg.locator('#quals-body input[data-known="hierarchy-of-money"]').first
            box.check(); pg.wait_for_timeout(300)
            txt = pg.locator('#quals-body .path-progress').inner_text()
            check(txt.startswith("1 of "), f"ticking a page updates progress ({txt.splitlines()[-1] if txt else ''})")
            box.uncheck(); pg.wait_for_timeout(200)

            # a placeholder qualification
            pg.goto(URL + "#/quals/frm-1"); pg.wait_for_timeout(400)
            check(pg.locator("#quals-body .planned-tag").count() == 1 and pg.locator("#quals-body [data-setrole]").count() == 0, "placeholder: Planned tag, no focus button")
            check(pg.locator("#quals-body h2.mod-head").count() == 4 and pg.locator("#quals-body .path-item").count() == 0, "placeholder lists its four modules with no pages")
            check(noscroll(), "placeholder: no sideways scroll")
            if simple and w == 390: pg.screenshot(path=str(OUT / "quals-frm1-390.png"), full_page=True)

            # focus: only mapped qualifications in the menu; focusing CFA I highlights its pages on the map
            pg.goto(URL + "#/map"); pg.wait_for_timeout(300)
            pg.click("#settings-btn"); pg.wait_for_timeout(200)
            roles = pg.locator("#qual-seg [data-role]").evaluate_all("els => els.map(e => e.dataset.role)")
            check(roles == ["", "cfa-l1", "money-banking", "caia-l1", "caia-l2", "princeton-bitcoin"], f"focus menu lists only mapped qualifications ({roles})")
            pg.locator('#qual-seg [data-role="cfa-l1"]').click(); pg.wait_for_timeout(400)
            pg.mouse.click(5, h - 5); pg.wait_for_timeout(150)
            pg.locator('.map-controls [data-act="expand"]').evaluate("b => b.click()"); pg.wait_for_timeout(500)
            check(pg.locator("body.role-on").count() == 1 and pg.locator("#map-svg .node.focus").count() >= 10, "CFA I focus highlights its pages on the map")
            if w > 860:   # the focus chip is hidden on phones by design
                check(pg.locator("#focus-chip-label").inner_text() == "CFA I", "focus chip says CFA I")
            pg.evaluate("document.getElementById('settings-menu').hidden = true"); pg.click("#settings-btn"); pg.wait_for_timeout(200)
            pg.locator('#qual-seg [data-role=""]').click(); pg.wait_for_timeout(300)
            check(pg.locator("body.role-on").count() == 0, "focus cleared from the settings menu")
            pg.mouse.click(5, h - 5); pg.wait_for_timeout(150)

            # search by module code and by module name
            for q, want in [("CFA1-FI", "#/quals/cfa-l1"), ("FRM1-VRM", "#/quals/frm-1"), ("advance clearing", "#/quals/money-banking")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(any(x and x.startswith(want) for x in hrefs), f"search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
