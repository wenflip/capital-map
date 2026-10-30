"""Launch gate (open, unlisted): About, Privacy, licence, legend, link previews, source labels, and the search-engine blocks KEPT. Stubs are allowed. Usage: python3 test_public.py <repo> <outdir>"""
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

# --- files: blocks kept, preview tags, share image
html = REPO.joinpath("index.html").read_text()
check('name="robots" content="noindex' in html, "index.html still has the noindex meta tag")
check("Disallow: /" in REPO.joinpath("robots.txt").read_text(), "robots.txt still blocks crawlers")
check("X-Robots-Tag: noindex" in REPO.joinpath("_headers").read_text(), "_headers still sends noindex")
og = dict(re.findall(r'<meta (?:property|name)="((?:og|twitter):[a-z:]+)" content="([^"]*)"', html))
check(all(k in og for k in ["og:title", "og:description", "og:url", "og:image", "og:type", "twitter:card"]), f"link-preview tags present ({sorted(og)})")
check(og.get("og:image", "").startswith("https://") and og.get("og:url", "").startswith("https://"), "og:image and og:url are absolute")
check(REPO.joinpath("assets/share.png").exists(), "share image exists")
check('<meta name="description"' in html, "meta description present")
# --- data: privacy page built, no personal source labels
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1])
check(bool(D.get("privacy")) and "Cloudflare Web Analytics" in D["privacy"]["html"], "privacy.md built into the data")
srcs = [x for p in D["pages"].values() for x in (p.get("sources") or [])]
bad = sorted({x for x in srcs if re.search(r"own notes|mud map|study plan|build plan|\(course notes\)|topic list", x, re.I)})
check(not bad, f"no personal source labels ({bad[:5]})")
HAS_STUBS = any(p.get("stub") for p in D["pages"].values())

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(450)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            # legend: the stub key shows while stubs exist, and hides once none are left
            if not mob:
                check((pg.locator(".legend-stub:visible").count() > 0) == HAS_STUBS and pg.locator(".legend-adv").count() == 1, f"stub legend matches the content (stubs: {HAS_STUBS}); other legend keys kept")
            # About for the public
            pg.goto(URL + "#/about"); pg.wait_for_timeout(350)
            t = pg.locator("#about-body").inner_text()
            for want in ["free, independent", "Not financial advice", "CC BY-NC-SA 4.0", "isn't affiliated with", "Accuracy and corrections"]:
                check(want.lower() in t.lower(), f"About has '{want}'")
            check("not public" not in t.lower() and "private" not in t.lower(), "About no longer says private / not public")
            check(pg.locator('#about-body a[href="https://x.com/KernelYard"]').count() == 1, "About names the contact for corrections")
            check(pg.locator('#about-body a[href="https://creativecommons.org/licenses/by-nc-sa/4.0/"]').count() >= 1, "About links the licence")
            check(noscroll(), "About: no horizontal scroll")
            pg.locator('#about-body a[href="#/privacy"]').click(); pg.wait_for_timeout(350)
            check(pg.evaluate("location.hash") == "#/privacy" and pg.locator("#privacy-view.active").count() == 1, "About → Privacy link opens Privacy")
            # Privacy view
            pt = pg.locator("#privacy-body").inner_text()
            check(pg.locator("#privacy-body h1").inner_text() == "Privacy", "Privacy page title")
            for want in ["never leaves your device", "Cloudflare Web Analytics", "doesn't use cookies", "No sign-up", "Hosting", "@KernelYard"]:
                check(want.lower() in pt.lower(), f"Privacy has '{want}'")
            check(noscroll(), "Privacy: no horizontal scroll")
            if w in (1366, 390) and mode == "simple": pg.screenshot(path=str(OUT / f"privacy-{w}.png"))
            pg.locator("#privacy-body a.about-link").click(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/about", "Privacy → About link")
            pg.go_back(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/privacy", "Back returns to Privacy")
            # direct load
            pg.goto(URL + "#/privacy"); pg.reload(); pg.wait_for_timeout(400)
            check(pg.locator("#privacy-view.active").count() == 1, "#/privacy opens directly")
            # settings menu link
            pg.goto(URL + "#/map"); pg.wait_for_timeout(250)
            pg.click("#settings-btn"); pg.wait_for_timeout(150)
            pg.locator("#settings-menu .sm-privacy").click(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/privacy" and pg.locator("#settings-menu").is_hidden(), "settings menu Privacy link opens Privacy and closes the menu")
            # Index link
            pg.goto(URL + "#/index"); pg.wait_for_timeout(300)
            pg.locator('#index-body a.about-link[data-view="privacy"]').click(); pg.wait_for_timeout(300)
            check(pg.evaluate("location.hash") == "#/privacy", "Index Privacy link")
            # root page no longer mentions stubs
            pg.goto(URL + "#/map/p/capital-system"); pg.wait_for_timeout(250)
            check("dashed cards" not in pg.locator("#panel-body").inner_text().lower(), "root page no longer explains stubs")
            # a page's sources line shows the neutral label
            pg.goto(URL + "#/map/p/gold"); pg.wait_for_timeout(250)
            gt = pg.locator("#panel-body").inner_text().lower()
            check("own notes" not in gt and "mud map" not in gt, "page shows no personal source labels")
            ctx.close()
    # welcome guide footer has Privacy (fresh visitor)
    ctx = b.new_context(viewport={"width": 1366, "height": 860}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(450)
    pg.locator('#welcome [data-wc="privacy"]').click(); pg.wait_for_timeout(350)
    check(pg.evaluate("location.hash") == "#/privacy" and pg.locator("#welcome").is_hidden(), "welcome guide Privacy link opens Privacy and closes the guide")
    # share image size
    pg.goto(REPO.joinpath("assets/share.png").as_uri()); pg.wait_for_timeout(200)
    dims = pg.evaluate("[document.images[0].naturalWidth, document.images[0].naturalHeight]")
    check(dims == [1200, 630], f"share image is 1200×630 ({dims})")
    ctx.close(); b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
