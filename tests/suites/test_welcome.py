"""Welcome guide + header About link + working-title rename. Usage: python3 test_welcome.py <repo> <outdir>"""
import sys, pathlib
from playwright.sync_api import sync_playwright
import os as _os
_W = _os.environ.get("CAPMAP_WIDTHS", "1366,390,360").split(",")
def sizes(lst):
    """Screen sizes to test. Set CAPMAP_WIDTHS=1366 for a quick desktop-only run."""
    return [s for s in lst if str(s[0]) in _W]
URL = pathlib.Path(sys.argv[1]).resolve().joinpath("index.html").as_uri()
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
CHROME = __import__("os").environ.get("CAPMAP_CHROME")
fails, errs = [], []
def check(c, m):
    print(("  ok   " if c else "  FAIL ") + m)
    if not c: fails.append(m)

STATE = """() => {
  const w = document.getElementById('welcome'), card = w.querySelector('.wc-card');
  const r = card.getBoundingClientRect(), a = document.activeElement;
  return { open: !w.hidden, hash: location.hash, simple: document.body.classList.contains('simple'),
    mode: localStorage.getItem('mudmap:mode'), welcomed: localStorage.getItem('mudmap:welcomed'),
    focusIn: card.contains(a), focusId: a && a.id, inert: document.querySelector('.topbar').hasAttribute('inert'),
    left: r.left, right: r.right, top: r.top, bottom: r.bottom, vw: innerWidth, vh: innerHeight,
    hscroll: document.documentElement.scrollWidth > innerWidth,
    searchFocused: a && a.id === 'search', panel: document.body.classList.contains('panel-open') };
}"""

SIZES = [(1366, 860, False), (390, 844, True), (360, 740, True)]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, channel="chromium")

    def fresh(w, h, mob, hash_="", store=None, scheme="light"):
        """A brand-new browser: nothing saved, unless `store` seeds some settings first."""
        c = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob,
                          device_scale_factor=2 if mob else 1, color_scheme=scheme)
        pg = c.new_page()
        pg.on("console", lambda m: errs.append(f"{w}: {m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(f"{w}: {e}"))
        pg.goto(URL + hash_); pg.wait_for_timeout(450)
        if store:   # seed saved settings the way the other suites do: clear, write, reload
            js = "; ".join(f"localStorage.setItem('mudmap:{k}', '{v}')" for k, v in store.items())
            pg.evaluate("localStorage.clear(); " + js); pg.reload(); pg.wait_for_timeout(450)
        return c, pg

    for (w, h, mob) in sizes(SIZES):
        print(f"== {w}px")
        st = None

        # 1. Brand-new visitor on the home page (no hash): guide opens, Core depth, focus inside, page behind inert
        c, pg = fresh(w, h, mob)
        st = pg.evaluate(STATE)
        check(st["open"], "fresh visit to home: guide opens")
        check(st["simple"] and st["mode"] == '"simple"', "brand-new visitor starts in Core depth")
        check(st["focusIn"], "focus moves into the guide")
        check(st["inert"], "page behind the guide is inert")
        check(st["left"] >= 0 and st["right"] <= st["vw"] + 0.5 and not st["hscroll"], f"guide fits the width, no sideways scroll ({st['left']:.0f}–{st['right']:.0f} of {st['vw']})")
        check(st["top"] >= 0 and st["bottom"] <= st["vh"] + 0.5, f"guide fits the height ({st['top']:.0f}–{st['bottom']:.0f} of {st['vh']})")
        if mob: check(abs(st["bottom"] - st["vh"]) < 1, "phone: guide is a bottom sheet")
        check(pg.locator(".wc-choice").count() == 4, "four ways in")
        check([pg.locator(".wc-choice").nth(i).get_attribute("href") for i in range(4)] == ["#/start", "#/map", "#/start/start-here", "#/quals"], "ways in are real links (new-tab safe)")   # 2026-10-26: "Ask a question" (#/start) is first; Cartography left the card; "Follow the money" became "Start from the beginning" (the flow and the tab remain)
        check("primary" in (pg.locator(".wc-choice").first.get_attribute("class") or "") and pg.locator(".wc-choice.primary").count() == 1, "Ask a question is the one primary way in")
        check(pg.locator("#wc-title").inner_text() == "The Capital Map", "guide shows the working title")
        check(pg.locator(".wc-kbd").is_visible() == (w > 860), "the / hint shows only on wide screens")
        pg.screenshot(path=str(OUT / f"welcome-{w}.png"))

        # shortcuts wait while it is open; Tab stays inside
        pg.keyboard.press("/"); pg.wait_for_timeout(100)
        pg.keyboard.press("h"); pg.wait_for_timeout(200)
        st = pg.evaluate(STATE)
        check(st["open"] and not st["searchFocused"], "/ and H do nothing while the guide is open")
        inside = True
        for _ in range(9):
            pg.keyboard.press("Tab"); inside = inside and pg.evaluate(STATE)["focusIn"]
        for _ in range(4):
            pg.keyboard.press("Shift+Tab"); inside = inside and pg.evaluate(STATE)["focusIn"]
        check(inside, "Tab and Shift+Tab stay inside the guide")

        # Esc closes and remembers; reload and H don't bring it back
        pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
        st = pg.evaluate(STATE)
        check(not st["open"] and st["welcomed"] == "true" and not st["inert"], "Esc closes it, remembers, page usable again")
        check(st["hash"] == "#/map" and not st["panel"], "closing leaves you on the map")
        pg.reload(); pg.wait_for_timeout(400)
        check(not pg.evaluate(STATE)["open"], "doesn't come back after reload")
        pg.keyboard.press("h"); pg.wait_for_timeout(300)
        check(not pg.evaluate(STATE)["open"], "H (home) doesn't reopen it")
        if w > 480:
            pg.locator("#home-btn").click(); pg.wait_for_timeout(300)
            check(not pg.evaluate(STATE)["open"], "logo (home) doesn't reopen it")
        c.close()

        # 2. Deep links never show it, and don't change depth
        for hsh in ["#/flows/where-money-comes-from", "#/map/p/gold", "#/quals/cfa-l1", "#/about", "#/index", "#/cartography"]:
            c, pg = fresh(w, h, mob, hsh)
            st = pg.evaluate(STATE)
            check(not st["open"] and st["mode"] is None, f"deep link {hsh}: no guide, depth untouched")
            c.close()
        c, pg = fresh(w, h, mob, "#/map")
        check(pg.evaluate(STATE)["open"], "fresh visit to #/map: guide opens")
        c.close()

        # 3. Returning visitor who never saw it (settings saved): guide opens, depth kept in both depths
        for mode in ["normal", "simple"]:
            c, pg = fresh(w, h, mob, "#/map", store={"mode": f'"{mode}"', "known": '["gold"]'})
            st = pg.evaluate(STATE)
            check(st["open"] and st["simple"] == (mode == "simple") and st["mode"] == f'"{mode}"', f"returning visitor ({'Core' if mode == 'simple' else 'Everything'}): guide opens, depth kept")
            c.close()

        # 4. Each way in goes to the right place and closes the guide
        for wc, want in [("start", "#/start"), ("map", "#/map"), ("path", "#/start/start-here"), ("quals", "#/quals"), ("about", "#/about")]:   # 2026-10-26: start replaces cartography; path replaces the flow option
            c, pg = fresh(w, h, mob)
            pg.locator(f'[data-wc="{wc}"]').click(); pg.wait_for_timeout(400)
            st = pg.evaluate(STATE)
            view_ok = pg.locator(f"#{want.split('/')[1]}-view").evaluate("e => e.classList.contains('active')")
            check(not st["open"] and st["hash"] == want and view_ok and st["welcomed"] == "true", f"'{wc}' → {want}")
            c.close()

        # 5. × and backdrop close it
        c, pg = fresh(w, h, mob)
        pg.locator("#wc-close").click(); pg.wait_for_timeout(200)
        check(not pg.evaluate(STATE)["open"], "× closes it")
        c.close()
        c, pg = fresh(w, h, mob)
        pg.mouse.click(8, 8); pg.wait_for_timeout(200)
        check(not pg.evaluate(STATE)["open"], "backdrop click closes it")
        c.close()

        # 6. Reopen from About; Esc returns focus to the button; depth isn't changed by reopening
        c, pg = fresh(w, h, mob, "#/about", store={"mode": '"normal"', "welcomed": "true"})
        pg.locator("#wc-reopen").scroll_into_view_if_needed(); pg.locator("#wc-reopen").click(); pg.wait_for_timeout(250)
        st = pg.evaluate(STATE)
        check(st["open"] and st["focusIn"] and not st["simple"], "About → Show the welcome guide reopens it (depth kept)")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
        st = pg.evaluate(STATE)
        check(not st["open"] and st["focusId"] == "wc-reopen", "Esc returns focus to the reopen button")
        pg.locator("#wc-reopen").click(); pg.wait_for_timeout(200)
        pg.locator('[data-wc="map"]').click(); pg.wait_for_timeout(400)
        check(pg.evaluate(STATE)["hash"] == "#/map", "reopened guide: 'Explore the map' goes to the map from About")
        c.close()

        # 7. Two tabs: dismissing in one closes it in the other
        c, pg = fresh(w, h, mob)
        pg2 = c.new_page(); pg2.on("pageerror", lambda e: errs.append(f"{w} tab2: {e}"))
        pg2.goto(URL + "#/map"); pg2.wait_for_timeout(400)
        check(pg2.evaluate(STATE)["open"], "second tab (not yet dismissed): guide open")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
        check(not pg2.evaluate(STATE)["open"], "dismissing in one tab closes it in the other")
        c.close()

        # 8. Header About link: visible above 860px only; marks itself active
        c, pg = fresh(w, h, mob, "#/map", store={"welcomed": "true"})
        vis = pg.locator("#about-btn").is_visible()
        check(vis == (w > 860), f"header About link visible only above 860px ({vis})")
        if vis:
            pg.locator("#about-btn").click(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/about" and pg.locator("#about-btn").get_attribute("aria-current") == "page", "About link opens About and marks itself current")
            pg.locator('.tab[data-view="flows"]').click(); pg.wait_for_timeout(200)
            check(pg.locator("#about-btn").get_attribute("aria-current") is None, "About link un-marks when leaving About")
        check(pg.title() == "The Capital Map", "browser tab title is the working title")
        pg.goto(URL + "#/about"); pg.wait_for_timeout(300)
        check(pg.locator("#about-body h1").inner_text() == "About The Capital Map", "About page title renamed")
        c.close()

    # 9. Dark mode screenshots of the guide
    for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True)]):
        c, pg = fresh(w, h, mob, scheme="dark")
        pg.screenshot(path=str(OUT / f"welcome-{w}-dark.png"))
        c.close()
    b.close()

print("Console errors:", len(errs))
for e in errs[:10]: print("  ", e)
print("FAILS:", len(fails))
