"""Quals coverage: module states, honest %, build validation, and the coverage view. Usage: python3 test_coverage.py <repo> <outdir>

Definition (tools/build.py): a module is out of scope (note starts "Outside this site's scope", not counted),
not mapped yet (no pages), partly mapped (pages + note starts "Partly mapped") or mapped (pages, no such note).
Coverage % = mapped / in-scope modules. Every figure here is recomputed from the raw notes, not read back from the build.
"""
import sys, pathlib, json, re, shutil, subprocess, tempfile
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

# Expected figures: update when a qualification is mapped or a module changes state (say so in the PR).
EXPECT = {  # qual: (mapped, partial, none, out)
    # 2026-10-26 housekeeping: CFA1-FSA and BTC8 marked Partly mapped (one page each against a wide module); overall 51% -> 48%.
    "cfa-l1": (8, 1, 0, 1), "cfa-l2": (0, 0, 9, 1), "cfa-l3": (0, 0, 5, 1), "money-banking": (6, 0, 0, 0),  # 2026-10-26: MB5 mapped by Swaps, then MB3 by Dealers and Market Making
    "frm-1": (0, 0, 4, 0), "frm-2": (0, 0, 6, 0), "caia-l1": (4, 0, 2, 1), "caia-l2": (4, 0, 3, 1), "princeton-bitcoin": (10, 1, 0, 0),
}
STATES = ("mapped", "partial", "none", "out")

# --- data checks (no browser)
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1])
Q = D["quals"]
def state(st):
    note = re.sub(r"<[^>]+>", "", st["note"]).strip().lower()
    if note.startswith("outside this site"): return "out"
    if st["items"]: return "partial" if note.startswith("partly mapped") else "mapped"
    return "none"
check(all(st.get("state") in STATES for q in Q.values() for st in q["stages"]), "every module has one of the four states")
check(all(st["state"] == state(st) for q in Q.values() for st in q["stages"]), "every state matches its pages and note")
check(all(st["pages"] == len(st["items"]) for q in Q.values() for st in q["stages"]), "every module carries its page count")
check(not [st for q in Q.values() for st in q["stages"] if st["state"] == "out" and st["items"]], "no out-of-scope module lists pages")
for qid, (m, pa, n, o) in EXPECT.items():
    c = Q[qid]["coverage"]
    got = tuple(sum(1 for st in Q[qid]["stages"] if state(st) == k) for k in STATES)
    ins = len(Q[qid]["stages"]) - o
    check(got == (m, pa, n, o) and (c["mapped"], c["partial"], c["none"], c["out"]) == got, f"{qid}: {m} mapped, {pa} partly, {n} not yet, {o} out ({got})")
    check(c["inScope"] == ins and c["modules"] == len(Q[qid]["stages"]) and c["pct"] == round(100 * m / ins), f"{qid}: {c['pct']}% = {m}/{ins} in scope")
T = D["coverage"]
tm, tp, tn, to = (sum(v[i] for v in EXPECT.values()) for i in range(4))
check((T["mapped"], T["partial"], T["none"], T["out"], T["inScope"]) == (tm, tp, tn, to, tm + tp + tn), f"overall: {tm} mapped, {tp} partly, {tn} not yet, {to} out; {tm + tp + tn} in scope")
check(T["pct"] == round(100 * tm / (tm + tp + tn)) == 51 and T["quals"] == 9, f"overall {T['pct']}% across {T['quals']} (partly mapped not counted)")

# --- the build rejects contradictions (on a throwaway copy)
def build_with(path, old, new):
    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp) / "r"
        shutil.copytree(REPO, r, ignore=shutil.ignore_patterns(".git"))
        if path:
            f = r / path; t = f.read_text(); assert old in t, (path, old); f.write_text(t.replace(old, new, 1))
        p = subprocess.run([sys.executable, str(r / "tools/build.py")], capture_output=True, text=True)
        return p.returncode, p.stdout
code, out = build_with(None, "", "")
check(code == 0 and "Coverage: " in out and "in-scope modules mapped" in out, "clean build passes and prints the coverage line")
for label, (path, old, new, want) in {
    "out of scope with pages": ("quals/cfa-l1.md", "not professional conduct.", "not professional conduct.\n- [[money]]", "out of scope but lists pages"),
    "Partly mapped with no pages": ("quals/caia-l1.md", "> Not mapped yet: the map has no page on hedge funds", "> Partly mapped: the map has no page on hedge funds", "says Partly mapped but lists no pages"),
    # 2026-10-26 dealers branch: Money & Banking has no Partly mapped note left, so this case edits CFA I FSA instead
    "Not mapped yet with pages": ("quals/cfa-l1.md", "> Partly mapped: one page covers", "> Not mapped yet: one page covers", "says Not mapped yet but lists pages"),
}.items():
    code, out = build_with(path, old, new)
    check(code != 0 and want in out, f"build fails on {label}")

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

                # the list: one summary, its numbers, its bar, its definition
                pg.goto(URL + "#/quals"); pg.wait_for_timeout(350)
                summ = pg.locator("#quals-body .cov-summary")
                check(summ.count() == 1, "Quals list has one coverage summary")
                txt = summ.inner_text()
                check(f"{T['pct']}%" in txt and f"all {T['quals']} qualifications" in txt, f"summary states {T['pct']}% across all {T['quals']}")
                check(all(x in txt for x in [f"{tm} mapped", f"{tp} partly mapped", f"{tn} not mapped yet", f"{to} out of scope, not counted"]), "summary key gives every count")
                check("What counts as mapped" in txt and "at least one page" in txt and "don't count toward the percentage" in txt, "summary defines mapped, and says partly mapped isn't counted")
                bw = summ.locator(".cov-bar").evaluate("e => e.clientWidth")
                mw = summ.locator(".cov-bar .cov-mapped").evaluate("e => e.getBoundingClientRect().width")
                check(abs(mw / bw - tm / (tm + tp + tn)) < 0.02, f"bar: mapped segment is {tm}/{tm + tp + tn} of the track ({mw / bw:.3f})")
                al = summ.locator(".cov-bar").get_attribute("aria-label") or ""
                check(summ.locator(".cov-bar").get_attribute("role") == "img" and f"{tm} of {tm + tp + tn}" in al, "bar has an accessible label")
                bg = pg.evaluate("[getComputedStyle(document.querySelector('.cov-summary .cov-mapped')).backgroundColor, getComputedStyle(document.querySelector('.cov-summary .cov-bar')).backgroundColor]")
                check(bg[0] != bg[1], f"mapped segment stands out from the track ({theme})")
                check(pg.locator("#quals-body .flow-card .cov-bar").count() == 5, "a coverage bar on each of the five mapped cards, none on placeholders")
                cfa = pg.locator('#quals-body [data-qual="cfa-l1"] .cov-meta').inner_text()
                check("89% mapped" in cfa and "8 of 9 modules" in cfa and "1 partly" in cfa and "1 out of scope" in cfa,  # 2026-10-26: FSA now partly mapped
                      f"CFA I card: {cfa}")
                mb = pg.locator('#quals-body [data-qual="money-banking"] .cov-meta').inner_text()
                check("100% mapped" in mb and "6 of 6" in mb and "partly" not in mb,  # 2026-10-26: MB3 and MB5 now mapped
                      f"Money & Banking card: {mb}")
                check(noscroll(), "list: no sideways scroll")
                if w in (1366, 390): pg.screenshot(path=str(OUT / f"coverage-list-{w}-{mode}-{theme}.png"), full_page=True)

                # a qualification with partly mapped modules
                # 2026-10-26 dealers branch: Money & Banking is fully mapped, so this example moved to Princeton (BTC8 partly mapped)
                pg.goto(URL + "#/quals/princeton-bitcoin"); pg.wait_for_timeout(350)
                det = pg.locator("#quals-body .cov-detail").inner_text()
                check("91% mapped" in det and "10 mapped" in det and "1 partly mapped" in det, "Princeton detail line and key")
                heads = pg.locator("#quals-body h2.mod-head").all_inner_texts()
                partly = [x.split(" — ")[0] for x in heads if "partly mapped" in x.lower()]   # the label is uppercased by CSS
                check(partly == ["BTC8"], f"Partly mapped label on BTC8 only ({partly})")
                pages = pg.locator("#quals-body h2.mod-head .mod-pages").all_inner_texts()
                want = [f"{len(st['items'])} page{'' if len(st['items']) == 1 else 's'}" for st in Q["princeton-bitcoin"]["stages"]]
                check(pages == want, f"every module shows its page count ({pages})")
                check(pg.locator("#quals-body .mod-jump.st-partial").count() == 1 and pg.locator("#quals-body .mod-jump.st-mapped").count() == 10, "jump chips: 1 partly, 10 mapped")
                check(noscroll(), "Princeton: no sideways scroll")
                if w in (1366, 390): pg.screenshot(path=str(OUT / f"coverage-btc-{w}-{mode}-{theme}.png"))

                # a mixed qualification: chips carry the state and the page count
                pg.goto(URL + "#/quals/caia-l2"); pg.wait_for_timeout(350)
                n = {k: pg.locator(f"#quals-body .mod-jump.st-{k}").count() for k in STATES}
                check(n == {"mapped": 4, "partial": 0, "none": 3, "out": 1}, f"CAIA II chips by state ({n})")
                t = pg.locator('#quals-body .mod-jump[data-jump="mod-caia-l2-2"]').get_attribute("title")
                check("Mapped" in t and "4 pages" in t, f"chip title gives state and pages ({t})")
                check("Out of scope" in pg.locator("#quals-body .mod-jump.st-out").get_attribute("title"), "out-of-scope chip says so")
                check("1 out of scope" in pg.locator("#quals-body .cov-detail").inner_text(), "CAIA II detail counts its out-of-scope module")

                # a placeholder: honest zero
                pg.goto(URL + "#/quals/frm-1"); pg.wait_for_timeout(350)
                fd = pg.locator("#quals-body .cov-detail").inner_text()
                check("0% mapped" in fd and "0 of 4 modules" in fd and "4 not mapped yet" in fd, f"placeholder detail shows 0% ({fd.splitlines()[0]})")
                check(noscroll(), "placeholder: no sideways scroll")
                ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
