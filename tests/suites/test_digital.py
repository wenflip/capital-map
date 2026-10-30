"""Digital Assets branch: structure, written pages, Cartography boxes, concepts-not-coins rule, map, search, quals. Usage: python3 test_digital.py <repo> <outdir>"""
import sys, pathlib, json
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

TREE = {
    "digital-assets": ["blockchains", "native-coins", "coin-value", "tokens", "bridges-and-layer-2s", "defi", "holding-crypto"],   # 2026-10-26: coin-value cluster added
    "blockchains": ["consensus", "keys-and-wallets", "forks", "privacy-and-traceability"],
    "native-coins": ["bitcoin", "smart-contract-platforms"],
    "coin-value": ["sound-money", "network-effects"],   # 2026-10-26
    "tokens": ["stablecoins", "memecoins", "governance-tokens", "wrapped-tokens"],
    "holding-crypto": ["self-custody", "custodial-crypto"],
}
ALL = ["digital-assets"] + [k for ks in TREE.values() for k in ks]
# page -> (tier text or None, killer fragment)
CART = {"bitcoin": ("Tier 2 · Private / bearer ↔ Tier 3", "lost keys"), "self-custody": ("Tier 2", "key loss"),
        "custodial-crypto": ("Tier 3", "custodian failing"), "stablecoins": (None, "loss of the peg"),
        "wrapped-tokens": (None, "bridge or custodian"), "memecoins": (None, "attention")}

# --- data
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
check(all(P[k]["children"] == v for k, v in TREE.items()), "Digital Assets has its seven clusters and their pages, in order")
check(sorted(k for k in P if P[k]["path"][:2] == [D["root"], "digital-assets"]) == sorted(ALL), "no other pages in the branch (concepts, not coins)")
check(all(not P[k]["stub"] for k in ALL), f"all {len(ALL)} pages written ({[k for k in ALL if P[k]['stub']]})")
mentions = sorted(k for k, v in P.items() if "pulsechain" in (v["text"] + v.get("textDeep", "")).lower())
check(mentions == ["forks"] and not any("pulse" in k for k in P), f"PulseChain appears only as an example on Forks ({mentions})")
check(D["quals"]["princeton-bitcoin"]["status"] == "mapped" and len(D["quals"]["princeton-bitcoin"]["pages"]) >= 10, "Princeton Bitcoin is now mapped")

def tap_toggle(pg, mob, tid):
    """Tap a map toggle once it has stopped moving and is the thing under the finger (the map animates after collapse and panel close)."""
    loc = pg.locator(f'#map-svg [data-toggle="{tid}"] circle')
    prev = None
    for _ in range(30):
        bx = loc.bounding_box()
        if bx and prev and abs(bx["x"] - prev["x"]) < 0.5 and abs(bx["y"] - prev["y"]) < 0.5:
            x, y = bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2
            if pg.evaluate(f"(() => {{ const e = document.elementFromPoint({x}, {y}); return !!(e && e.closest('[data-toggle=\"{tid}\"]')); }})()"):
                break
        prev = bx; pg.wait_for_timeout(100)
    if mob: pg.touchscreen.tap(x, y)
    else: pg.mouse.click(x, y)
    pg.wait_for_timeout(600)

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

            bad = []
            for pid in ALL:
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(120)
                body = pg.locator("#panel-body")
                if "what it is" not in " | ".join(body.locator("h2:visible").all_inner_texts()).lower(): bad.append(f"{pid}: no 'What it is'")
                if body.locator(".wl.broken").count(): bad.append(f"{pid}: broken link")
                if body.locator(".qa:visible").count() < 1: bad.append(f"{pid}: no visible quiz")
                if body.locator(".stub-note:visible").count(): bad.append(f"{pid}: stub note")
                kids = TREE.get(pid, [])
                missing = [k for k in kids if body.locator(f'.content a.wl[data-page="{k}"]').count() == 0]
                if missing: bad.append(f"{pid}: doesn't link {missing}")
                if not noscroll(): bad.append(f"{pid}: h-scroll")
            check(not bad, f"every page complete, every cluster links its pages {bad}")

            for pid, (tier, killer) in CART.items():
                pg.goto(URL + f"#/map/p/{pid}"); pg.wait_for_timeout(120)
                box = pg.locator("#panel-body .cart-note")
                t = box.inner_text().lower() if box.count() else ""
                ok = killer in t and (tier is None or tier.lower() in t) and (tier is not None or "tier" not in t.split("killer")[0])
                check(ok, f"{pid}: Cartography box shows {'tier and ' if tier else ''}killer")
            pg.goto(URL + "#/map/p/blockchains"); pg.wait_for_timeout(120)
            check(pg.locator("#panel-body .cart-note").count() == 0, "machinery pages carry no Cartography box")

            # the hub's native coin vs token table
            pg.goto(URL + "#/map/p/digital-assets"); pg.wait_for_timeout(200)
            check("nobody's" in pg.locator("#panel-body table").first.inner_text().lower(), "hub compares native coins and tokens")
            check(pg.locator("#panel-body .deeper:visible").count() == (0 if simple else 1), "hub's Going deeper only in Everything")
            if simple and w in (1366, 390): pg.screenshot(path=str(OUT / f"digital-hub-{w}.png"))

            # map: open Digital Assets, then How Blockchains Work
            pg.goto(URL + "#/map"); pg.wait_for_timeout(250)
            pg.locator('.map-controls [data-act="collapse"]').click(); pg.wait_for_timeout(300)
            tap = lambda i: tap_toggle(pg, mob, i)
            tap("digital-assets")
            drawn = pg.evaluate("[...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node)")
            check(all(k in drawn for k in TREE["digital-assets"]), "opening Digital Assets draws its seven clusters")
            if mob:   # on phones the cluster is off-screen once the branch opens: centre on it first, as a user would
                pg.goto(URL + "#/map/p/blockchains"); pg.wait_for_timeout(300)
                pg.locator('#panel-body [data-mapto="blockchains"]').click(); pg.wait_for_timeout(600)
                pg.locator("#panel-close").click(); pg.wait_for_timeout(400)
            tap("blockchains")
            drawn = pg.evaluate("[...document.querySelectorAll('#map-svg [data-node]')].map(n => n.dataset.node)")
            check(all(k in drawn for k in TREE["blockchains"]), "opening How Blockchains Work draws its three pages")
            if simple and w == 1366: pg.screenshot(path=str(OUT / "digital-map-1366.png"))

            # qualification chip
            pg.goto(URL + "#/map/p/consensus"); pg.wait_for_timeout(200)
            check(pg.locator('#panel-body .chip.qual[data-qual="princeton-bitcoin"]').count() >= 1, "Consensus shows its Princeton chips")

            # keyboard
            if not mob:
                pg.goto(URL + "#/map/p/digital-assets"); pg.wait_for_timeout(300)
                pg.locator("#panel-close").focus(); hit = None
                for _ in range(40):
                    pg.keyboard.press("Tab")
                    hit = pg.evaluate("""() => { const a = document.activeElement;
                        if (!a || !a.matches('#panel-body a.wl')) return null;
                        const s = getComputedStyle(a); return { id: a.dataset.page, ring: s.outlineStyle !== 'none' || s.boxShadow !== 'none' }; }""")
                    if hit: break
                check(bool(hit) and hit["ring"], f"Tab reaches a link on the hub with a focus ring ({hit})")

            # search
            for q, want in [("proof of stake", "consensus"), ("seed phrase", "keys-and-wallets"), ("rug pull", "memecoins"),
                            ("liquidation", "defi"), ("rollup", "bridges-and-layer-2s"), ("pulsechain", "forks"),
                            ("de-peg", "stablecoins"), ("self-custody", "self-custody"), ("layer-2", "bridges-and-layer-2s"), ("not your keys", "custodial-crypto")]:
                pg.goto(URL + "#/map"); pg.wait_for_timeout(150)
                if w < 481: pg.locator("#search").click()
                pg.fill("#search", q); pg.wait_for_timeout(250)
                hrefs = pg.locator("#results .result").evaluate_all("els => els.slice(0, 5).map(e => e.getAttribute('href'))")
                check(f"#/map/p/{want}" in hrefs, f"search '{q}' finds {want} ({hrefs[:3]})")
                pg.keyboard.press("Escape")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
