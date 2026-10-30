"""Branch groups: data, map clusters and headings, Index headings, Tools folded into In Practice. Usage: python3 test_groups.py <repo> <outdir>"""
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

# 2026-10-27 money-you-hold branch: Money You Hold added after Human & Social
GROUPS = [("Foundations", ["foundation", "money"]),
          ("What you can own", ["personal-capital", "digital-assets", "money-you-hold", "real-assets", "fixed-income", "equities"]),
          ("Putting it together", ["derivatives", "portfolio", "failure-modes"]),
          ("How it runs", ["markets", "how-markets-move", "measure", "practice", "how-to-think"])]   # 2026-10-27 how-to-think branch   # 2026-10-27 how-markets-move branch
ORDER = [b for _, bs in GROUPS for b in bs]

# --- data
s = REPO.joinpath("data.js").read_text(); D = json.loads(s[s.index("{"):s.rindex("}") + 1]); P = D["pages"]
branches = sorted((k for k, v in P.items() if v["parent"] == D["root"]), key=lambda k: P[k]["order"])
check(branches == ORDER, f"sixteen branches in group order ({branches})")
check(all(P[b]["group"] == g for g, bs in GROUPS for b in bs), "every branch carries its group")
check(not any(v["group"] for k, v in P.items() if v["parent"] != D["root"]), "only top-level branches have a group")
check("tools" not in P and P["data-sources"]["parent"] == "practice" and P["charting"]["parent"] == "practice", "Tools folded into In Practice")
# Cartography order inside "What you can own": inside you (1) -> bearer (2) -> legible (3)
tiers = {"personal-capital": 1, "digital-assets": 2, "money-you-hold": 2.5, "real-assets": 2.5, "fixed-income": 3, "equities": 3}   # 2026-10-27 money-you-hold branch: notes and gold bearer (2), deposits on the record (3)
own = GROUPS[1][1]
check([tiers[b] for b in own] == sorted(tiers[b] for b in own), "What you can own runs from inside you to on the record")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    for mode in ["simple", "normal"]:
        for (w, h, mob) in sizes([(1366, 860, False), (390, 844, True), (360, 740, True)]):
            print(f"== {mode} @ {w}")
            ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)
            pg = ctx.new_page()
            pg.on("console", lambda m: errs.append(f"{w} {mode}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"{w} {mode}: {e}"))
            pg.goto(URL + "#/map"); pg.evaluate(f"localStorage.clear(); localStorage.setItem('mudmap:welcomed', 'true'); localStorage.setItem('mudmap:mode', '\"{mode}\"')"); pg.reload(); pg.wait_for_timeout(500)
            noscroll = lambda: pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")

            def geometry():
                return pg.evaluate("""() => {
                  const r = (el) => { const b = el.getBoundingClientRect(); return { top: b.top, bottom: b.bottom, left: b.left, right: b.right, cy: (b.top + b.bottom) / 2 }; };
                  const labels = [...document.querySelectorAll('#map-svg .group-label')].map(t => ({ text: t.dataset.group, ...r(t) }));
                  const kids = window.MUDMAP.pages[window.MUDMAP.root].children;
                  const nodes = {}; kids.forEach(k => { const n = document.querySelector(`#map-svg [data-node="${k}"] .node-box`); if (n) nodes[k] = r(n); });
                  const boxes = [...document.querySelectorAll('#map-svg [data-node] .node-box')].map(r);
                  return { labels, nodes, boxes };
                }""")

            for state in ["collapsed", "expanded"]:
                if state == "collapsed":
                    pg.locator('.map-controls [data-act="collapse"]').click()
                else:
                    pg.locator('.map-controls [data-act="expand"]').click()
                pg.wait_for_timeout(500)
                g = geometry()
                check([l["text"] for l in g["labels"]] == [n for n, _ in GROUPS], f"{state}: four group headings in order ({[l['text'] for l in g['labels']]})")
                # each heading sits above the first branch of its group and below the last branch of the group before
                bad = []
                for i, (name, bs) in enumerate(GROUPS):
                    lab = next((l for l in g["labels"] if l["text"] == name), None)
                    if not lab or bs[0] not in g["nodes"]: bad.append(f"{name}: missing"); continue
                    if not lab["bottom"] <= g["nodes"][bs[0]]["top"] + 1: bad.append(f"{name}: not above {bs[0]}")
                    if i and not lab["top"] >= g["nodes"][GROUPS[i - 1][1][-1]]["bottom"] - 1: bad.append(f"{name}: overlaps the group above")
                    if abs(lab["left"] - g["nodes"][bs[0]]["left"]) > 6: bad.append(f"{name}: not aligned with its branches")
                check(not bad, f"{state}: headings sit above their clusters {bad}")
                # headings never overlap a card
                # 2026-10-27 how-to-think branch: use each card's real right edge, not an assumed 400 px width. With sixteen
                # branches the root card sits level with a heading, 41 px to its left: no overlap, but the old box flagged it
                hit = [l["text"] for l in g["labels"] for bx in g["boxes"] if l["top"] < bx["bottom"] - 1 and l["bottom"] > bx["top"] + 1 and l["left"] < bx["right"] - 1 and l["right"] > bx["left"] + 1]
                check(not hit, f"{state}: no heading overlaps a card ({hit[:3]})")
                if state == "collapsed":
                    # gaps between groups are larger than gaps inside a group
                    ys = [g["nodes"][k]["cy"] for k in ORDER]
                    inner = max(ys[i + 1] - ys[i] for i in range(len(ys) - 1) if P[ORDER[i]]["group"] == P[ORDER[i + 1]]["group"])
                    across = min(ys[i + 1] - ys[i] for i in range(len(ys) - 1) if P[ORDER[i]]["group"] != P[ORDER[i + 1]]["group"])
                    check(across > inner, f"clusters are visibly separated ({across:.0f} > {inner:.0f})")
                    if mode == "simple" and w in (1366, 390): pg.screenshot(path=str(OUT / f"groups-map-{w}.png"))
            check(noscroll(), "map: no sideways scroll")

            # In Practice holds the two former Tools pages
            pg.goto(URL + "#/map/p/practice"); pg.wait_for_timeout(300)
            kids = pg.locator('#panel-body .p-list a[data-page]').evaluate_all("els => els.map(e => e.dataset.page)")
            check("data-sources" in kids and "charting" in kids, "In Practice lists Data Sources and Charting")
            check(pg.locator("#panel-body .wl.broken").count() == 0, "no broken links on In Practice")

            # root page lists the branches under the four group names
            pg.goto(URL + "#/map/p/capital-system"); pg.wait_for_timeout(300)
            txt = pg.locator("#panel-body").inner_text()
            check(all(n in txt for n, _ in GROUPS) and pg.locator("#panel-body .wl.broken").count() == 0, "root page explains the four groups")

            # Index shows a heading before each group
            pg.goto(URL + "#/index"); pg.wait_for_timeout(400)
            heads = pg.locator("#index-body .index-grouphead").all_inner_texts()
            check([x.lower() for x in heads] == [n.lower() for n, _ in GROUPS], f"Index has the four group headings ({heads})")
            check(noscroll(), "Index: no sideways scroll")
            ctx.close()
    b.close()
print("Console errors:", len(errs)); [print("  ", e) for e in errs]
print("FAILS:", len(fails)); [print("  ", f) for f in fails]
sys.exit(1 if fails or errs else 0)
