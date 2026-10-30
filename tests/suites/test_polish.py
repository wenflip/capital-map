"""Polish branch: Privacy and Traceability page, CAIA mapped, Index and About when everything is written, link-preview image. Usage: python3 test_polish.py <repo> <outdir>"""
import sys, pathlib, json, struct
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

s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]; Q = D["quals"]
pt = P["privacy-and-traceability"]
check(pt["parent"] == "blockchains" and not pt["stub"] and not pt["adv"] and pt["sources"], "Privacy and Traceability: under Blockchains, written, core, sourced")
check(P["blockchains"]["children"][-1] == "privacy-and-traceability", "it is the last page under Blockchains")
btc6 = next(st for st in Q["princeton-bitcoin"]["stages"] if st["title"].startswith("BTC6"))
check("privacy-and-traceability" in {i["page"] for i in btc6["items"]}, "Princeton BTC6 maps it")
for q in ["caia-l1", "caia-l2"]:
    check(Q[q]["status"] == "mapped" and len(Q[q]["pages"]) >= 10, f"{q} is mapped ({len(Q[q]['pages'])} pages)")
empty = {q: [st["title"].split(" — ")[0] for st in Q[q]["stages"] if not st["items"]] for q in ["caia-l1", "caia-l2"]}
check(empty == {"caia-l1": ["CAIA1-ETH", "CAIA1-HF", "CAIA1-SP"], "caia-l2": ["CAIA2-ETH", "CAIA2-CIT", "CAIA2-HF", "CAIA2-SP"]}, f"only ethics and the true gaps stay unmapped ({empty})")
check(not any("[[" in st["note"] for q in Q for st in Q[q]["stages"]), "no module note contains raw link syntax")
check(not [k for k, v in P.items() if v["stub"]], "still no stubs")
png = REPO.joinpath("assets/share.png").read_bytes()
w, h = struct.unpack(">II", png[16:24])
check(png[:8] == b"\x89PNG\r\n\x1a\n" and (w, h) == (1200, 630), f"share.png is a 1200×630 PNG ({w}×{h})")
html = REPO.joinpath("index.html").read_text()
check('content="https://thecapitalmap.pages.dev/assets/share.png"' in html and 'content="1200"' in html and 'content="630"' in html, "preview tags point at the image with its size")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
        print(f"== {w}")
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
        pg.goto(URL + "#/map"); pg.evaluate("localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true')"); pg.reload(); pg.wait_for_timeout(450)
        noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

        pg.goto(URL + "#/map/p/privacy-and-traceability"); pg.wait_for_timeout(300)
        body = pg.locator("#panel-body")
        check(body.locator(".qa:visible").count() >= 2 and body.locator(".wl.broken").count() == 0 and noscroll(), f"{w}: privacy page renders with two quizzes, no broken links")
        check(body.locator(".quals a, .qual-chip, [data-qual]").filter(has_text="Princeton").count() >= 1 or "BTC6" in body.inner_text(), f"{w}: privacy page shows its Princeton module")
        pg.goto(URL + "#/map/p/blockchains"); pg.wait_for_timeout(200)
        check(pg.locator("#panel-body a.wl[data-page='privacy-and-traceability']:visible").count() >= 1, f"{w}: Blockchains hub links it")
        for q in ["pseudonymous", "travel rule", "chain analysis"]:
            pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
            if w < 481: pg.locator("#search").click()
            pg.fill("#search", q); pg.wait_for_timeout(250)
            hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
            check("#/map/p/privacy-and-traceability" in hrefs, f"{w}: search '{q}' finds it ({hrefs[:3]})")
            pg.keyboard.press("Escape")

        pg.goto(URL + "#/index"); pg.wait_for_timeout(300)
        sub = pg.locator("#index-view .view-sub").inner_text()
        check("all written" in sub and "stubs" not in sub, f"{w}: Index says all written, no stub count ({sub[-60:]})")
        check(all(not el.is_visible() for el in pg.locator(".legend-stub").all()), f"{w}: map legend hides the stub key")
        pg.goto(URL + "#/about"); pg.wait_for_timeout(300)
        check("dated figures are history" in pg.locator("#about-body").inner_text().lower(), f"{w}: About explains dated figures")
        pg.goto(URL + "#/quals/caia-l2"); pg.wait_for_timeout(300)
        check(pg.locator("#quals-body .planned-tag").count() == 0 and pg.locator("#quals-body [data-setrole]").count() == 1 and noscroll(), f"{w}: CAIA II is a mapped qualification with a focus button")
        if w == 1366: pg.screenshot(path=str(OUT / "caia-l2-1366.png"), full_page=True)
        ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
