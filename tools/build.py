#!/usr/bin/env python3
"""
Build script for The Capital Map (engine shared with The Supply Map).

Reads every Markdown file in pages/, flows/, jobs/ and quals/, and writes data.js,
which index.html loads. Run from the repo root:

    python3 tools/build.py

Page file format (pages/<id>.md):

    ---
    id: goods-receipt            # unique, lowercase, hyphens
    title: Goods Receipt (GR)
    parent: source               # id of the parent node on the map
    order: 4                     # position among siblings
    summary: One-line description shown on hover and in search
    tcodes: MIGO, MB51           # optional, comma separated
    fiori: Post Goods Movement   # optional, Fiori app names, comma separated
    sources: SAP MM mud map; Standard SAP behaviour   # optional, semicolon separated
    tags: inventory, p2p         # optional
    ---
    ## What it is
    ...

    level: advanced              # optional — hidden in Core view (children inherit it)

Links:  [[page-id]]  or  [[page-id|custom text]]
Depth:  a "## Going deeper" heading starts an advanced block that runs to the
        end of the page; it is hidden in Core view
Quiz:   a paragraph starting **Q:** followed by one starting **A:**

Job file format (jobs/<id>.md) — one job on the job ladder, with its
learning path in priority tiers:

    ---
    id: coordinator
    title: Supply Chain Coordinator
    short: SC Coordinator        # label on chart cards and in the focus menu
    stream: warehouse            # procurement | warehouse | planning | maintenance | all
    level: 4                     # 1 Entry ... 7 Executive (6 and 7 use stream: all)
    next_step: warehouse-manager # the job above on the ladder (optional at the top)
    also_from: other-job-id      # optional: a common move in from another stream
    aliases: Logistics Coordinator, Supply Chain Officer
    quals: sap-mm, cips-l4       # qualification ids that support the job
    summary: One line shown on the chart card
    ---
    Intro paragraph.

    ### What the job does
    - bullet

    ### New at this level
    - bullet

    ## Critical — learn first
    - [[page-id]] — optional short note
    ## High — learn next
    ## Medium — depth

Every page listed is "on the path" for that job: highlighted when the job is
chosen in Job focus, and listed in order on the Jobs tab. Pages also on a
lower job's path are marked with that job, so moving up a level means
learning only what's new.

Qualification file format (quals/<id>.md) — the same as a role file, but each
"## " heading is a module of the qualification (start it with the module code,
e.g. "## L4M3 — Commercial contracting") and a page may appear under several
modules (once per module). Pages show which modules they belong to, and search
matches the module headings.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "pages"
FLOWS_DIR = ROOT / "flows"
JOBS_DIR = ROOT / "jobs"
QUALS_DIR = ROOT / "quals"
ABOUT = ROOT / "about.md"
PRIVACY = ROOT / "privacy.md"
OUT = ROOT / "data.js"

LIST_KEYS = {"tcodes", "fiori", "tags", "aliases", "quals", "traits"}
WIKILINK = re.compile(r"\[\[([a-z0-9\-]+)(?:\\?\|([^\]]+))?\]\]")
STUB_WORDS = 60  # pages with fewer body words are shown as stubs

errors = []
warnings = []
ADVANCED = set()   # ids of advanced pages (filled before rendering)
DEEPER = re.compile(r"(?m)^## Going deeper\b.*$")


def parse_file(path):
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        errors.append(f"{path.name}: missing frontmatter")
        return None, raw
    try:
        _, fm, body = raw.split("---", 2)
    except ValueError:
        errors.append(f"{path.name}: malformed frontmatter")
        return None, raw
    meta = {}
    for line in fm.strip().splitlines():
        line = line.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"{path.name}: bad frontmatter line '{line}'")
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if key in LIST_KEYS:
            meta[key] = [v.strip() for v in val.split(",") if v.strip()]
        elif key == "sources":
            meta[key] = [v.strip() for v in val.split(";") if v.strip()]
        elif key == "order":
            try:
                meta[key] = float(val)
            except ValueError:
                errors.append(f"{path.name}: order must be a number")
                meta[key] = 99
        else:
            meta[key] = val
    return meta, body.strip()


def plain_text(md_body):
    t = WIKILINK.sub(lambda m: m.group(2) or m.group(1), md_body)
    t = re.sub(r"[#*`>|_\-]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


LIST_LINE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def separate_lists(md):
    """Python-Markdown only starts a list after a blank line. Pages often put a
    list straight under a sentence ("Two kinds:" then "- one"), which would
    render as one run-on paragraph — so insert the blank line automatically."""
    out, fence, prev = [], False, ""
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if (not fence and LIST_LINE.match(line) and prev.strip()
                and not LIST_LINE.match(prev) and not prev.lstrip().startswith(("|", ">", "#"))
                and not prev.startswith(" ")):
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def render(md_body, titles, source_id, link_sink):
    def repl(m):
        target, label = m.group(1), m.group(2)
        if target not in titles:
            errors.append(f"{source_id}: broken link [[{target}]]")
            return f'<span class="wl broken" title="Missing page: {target}">{label or target}</span>'
        link_sink.add(target)
        text = label or titles[target]
        adv = ' data-adv="1"' if target in ADVANCED else ""
        return f'<a class="wl" href="#/map/p/{target}" data-page="{target}"{adv}>{text}</a>'

    body = WIKILINK.sub(repl, md_body)
    # Python-Markdown needs 4-space indents for nested lists; accept 2 or 3 as well
    body = re.sub(r"(?m)^( {2,3})(?=(?:[-*+]|\d+\.) )", lambda m: "    " * 1, body)
    body = separate_lists(body)
    html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])

    # Quiz blocks: **Q:** paragraph followed by **A:** paragraph
    html = re.sub(
        r"<p><strong>Q:</strong>\s*(.*?)</p>\s*<p><strong>A:</strong>\s*(.*?)</p>",
        r'<div class="qa"><p class="q">\1</p><details><summary>Show answer</summary><p>\2</p></details></div>',
        html,
        flags=re.S,
    )
    # Tables scroll horizontally on narrow screens
    html = html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    return html


def load_pages():
    pages = {}
    for path in sorted(PAGES_DIR.glob("*.md")):
        meta, body = parse_file(path)
        if meta is None:
            continue
        pid = meta.get("id")
        if not pid:
            errors.append(f"{path.name}: no id")
            continue
        if pid != path.stem:
            warnings.append(f"{path.name}: id '{pid}' differs from file name")
        if pid in pages:
            errors.append(f"{path.name}: duplicate id '{pid}'")
            continue
        pages[pid] = {
            "id": pid,
            "title": meta.get("title", pid),
            "short": meta.get("short", ""),
            "parent": meta.get("parent", ""),
            "order": meta.get("order", 99),
            "summary": meta.get("summary", ""),
            "tcodes": meta.get("tcodes", []),
            "fiori": meta.get("fiori", []),
            "tags": meta.get("tags", []),
            "sources": meta.get("sources", []),
            "level": meta.get("level", "basic"),
            "group": meta.get("group", ""),   # top-level branches only: the cluster it sits in on the map
            # Cartography of Wealth fields (optional)
            "tier": meta.get("tier", ""),
            "killer": meta.get("killer", ""),
            "traits": meta.get("traits", []),
            # Cartography chart (optional): position (x inside->outside, y hidden->recorded, 0-100),
            # an optional vertical span for stores that straddle tiers, and the kind of killer for filtering
            "place": meta.get("place", ""),
            "span": meta.get("span", ""),
            "killerKind": meta.get("killer_kind", ""),
            "_body": body,
        }
    return pages


def load_flows(titles):
    """A flow file is: intro text, one Markdown table, outro text.
    The table's first two columns must be Step and Page; every further column
    becomes a row (lane) in the flow view, labelled with its header text."""
    flows = {}
    plain = lambda v: WIKILINK.sub(lambda m: m.group(2) or titles.get(m.group(1), m.group(1)), v)
    for path in sorted(FLOWS_DIR.glob("*.md")):
        meta, body = parse_file(path)
        if meta is None:
            continue
        fid = meta.get("id", path.stem)
        lines = body.splitlines()
        steps, intro, i = [], [], 0
        while i < len(lines) and not lines[i].lstrip().startswith("|"):
            intro.append(lines[i]); i += 1
        split = lambda line: [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        header = split(lines[i]) if i < len(lines) else []
        if [h.lower() for h in header[:2]] != ["step", "page"]:
            errors.append(f"flow {fid}: table must start with columns Step | Page")
        lanes = header[2:]
        i += 2
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            cells = split(lines[i])
            if len(cells) != len(header):
                errors.append(f"flow {fid}: row {len(steps) + 1} has {len(cells)} cells, header has {len(header)}")
                cells = (cells + [""] * len(header))[: len(header)]
            step = {"label": cells[0], "page": None, "cells": [plain(c) for c in cells[2:]]}
            m = WIKILINK.search(cells[1])
            if m:
                if m.group(1) in titles:
                    step["page"] = m.group(1)
                else:
                    errors.append(f"flow {fid}: broken link [[{m.group(1)}]]")
            steps.append(step)
            i += 1
        outro = lines[i:]
        sink = set()
        flows[fid] = {
            "id": fid,
            "title": meta.get("title", fid),
            "summary": meta.get("summary", ""),
            "area": meta.get("area", ""),
            "adv": meta.get("level", "basic") == "advanced",
            "order": meta.get("order", 99),
            "lanes": lanes,
            "intro": render("\n".join(intro), titles, f"flow {fid}", sink),
            "outro": render("\n".join(outro), titles, f"flow {fid}", sink),
            "steps": steps,
        }
        if not steps:
            errors.append(f"flow {fid}: no step table found")
    return flows


ROLE_ITEM = re.compile(r"^\s*[-*]\s+\[\[([a-z0-9\-]+)\]\]\s*(?:[—–-]\s*(.*))?$")


def load_roles(titles, folder=JOBS_DIR, kind="job", repeat_ok=False):
    """Load study paths from jobs/ (job ladder) or quals/ (qualifications).
    In a qualification a page may sit in several modules, but only once per module."""
    roles = {}
    if not folder.exists():
        return roles
    inline = lambda s: markdown.markdown(s).removeprefix("<p>").removesuffix("</p>")
    for path in sorted(folder.glob("*.md")):
        meta, body = parse_file(path)
        if meta is None:
            continue
        rid = meta.get("id", path.stem)
        intro, stages, seen = [], [], set()
        for line in body.splitlines():
            if line.startswith("## "):
                stages.append({"title": line[3:].strip(), "items": [], "note": ""})
                if repeat_ok:
                    seen = set()
                continue
            m = ROLE_ITEM.match(line)
            if m and stages:
                pid, note = m.group(1), (m.group(2) or "").strip()
                if pid not in titles:
                    errors.append(f"{kind} {rid}: broken link [[{pid}]]"); continue
                if pid in seen:
                    errors.append(f"{kind} {rid}: [[{pid}]] listed twice" + (" in one module" if repeat_ok else "")); continue
                seen.add(pid)
                note = note[:1].upper() + note[1:]
                stages[-1]["items"].append({"page": pid, "note": inline(note) if note else ""})
            elif not stages:
                intro.append(line)
            elif repeat_ok and line.startswith("> "):
                # qualification module note, e.g. why a module is out of scope or not mapped yet
                stages[-1]["note"] = inline(line[2:].strip())
            elif line.strip():
                errors.append(f"{kind} {rid}: unexpected line under '{stages[-1]['title']}': {line.strip()[:60]}")
        roles[rid] = {
            "id": rid,
            "title": meta.get("title", rid),
            "short": meta.get("short", meta.get("title", rid)),
            "order": meta.get("order", 99),
            "summary": meta.get("summary", ""),
            "intro": render("\n".join(intro).strip(), titles, f"{kind} {rid}", set()),
            "meta": meta,
            # qualifications keep every module, mapped or not, so the page shows the whole syllabus
            "stages": stages if repeat_ok else [s for s in stages if s["items"]],
            "pages": list(dict.fromkeys(i["page"] for s in stages for i in s["items"])),
            "status": meta.get("status", "mapped"),
        }
        if roles[rid]["status"] not in ("mapped", "planned"):
            errors.append(f"{kind} {rid}: status must be mapped or planned")
        if not roles[rid]["pages"] and roles[rid]["status"] != "planned":
            errors.append(f"{kind} {rid}: no pages listed (use status: planned for a placeholder)")
        if roles[rid]["pages"] and roles[rid]["status"] == "planned":
            errors.append(f"{kind} {rid}: has pages, so it isn't planned")
        if not stages:
            errors.append(f"{kind} {rid}: no modules")
    return roles


LEVELS = {1: "Entry", 2: "Operational", 3: "Specialist", 4: "Coordinator / Analyst", 5: "Manager", 6: "Director", 7: "Executive"}
STREAMS = [("procurement", "Procurement"), ("warehouse", "Warehouse & Inventory"),
           ("planning", "Planning & Logistics"), ("maintenance", "Maintenance")]
TIERS = [("critical", "Critical"), ("high", "High"), ("medium", "Medium")]


def load_jobs(titles):
    """Jobs are study paths plus a place on the ladder. Validates the ladder and marks, for each
    page on a job's path, the nearest lower job that already covers it."""
    jobs = load_roles(titles, JOBS_DIR, "job")
    stream_ids = {s for s, _ in STREAMS}
    for jid, j in jobs.items():
        m = j.pop("meta")
        j["stream"] = m.get("stream", "")
        try:
            j["level"] = int(m.get("level", ""))
        except ValueError:
            errors.append(f"job {jid}: level must be a number 1-7"); j["level"] = 0
        if j["level"] not in LEVELS:
            errors.append(f"job {jid}: level must be 1-7")
        if j["level"] >= 6 and j["stream"] != "all":
            errors.append(f"job {jid}: levels 6-7 span every stream; use stream: all")
        if j["level"] < 6 and j["stream"] not in stream_ids:
            errors.append(f"job {jid}: stream must be one of {sorted(stream_ids)}")
        j["next"] = m.get("next_step", "") or None
        j["alsoFrom"] = m.get("also_from", "") or None
        j["aliases"] = m.get("aliases", [])
        j["quals"] = m.get("quals", [])
        # tiers, in order
        want = [t for t, _ in TIERS]
        got = []
        for s in j["stages"]:
            tier = s["title"].split()[0].lower().strip("—-–")
            if tier not in want:
                errors.append(f"job {jid}: section '{s['title']}' must start with Critical, High or Medium")
            s["tier"] = tier
            got.append(tier)
        if got != [t for t in want if t in got]:
            errors.append(f"job {jid}: tiers must run Critical, High, Medium")
    for jid, j in jobs.items():
        for key in ("next", "alsoFrom"):
            other = j[key]
            if other and other not in jobs:
                errors.append(f"job {jid}: {key} '{other}' is not a job")
        if j["next"] in jobs and jobs[j["next"]]["level"] <= j["level"]:
            errors.append(f"job {jid}: next step must be a higher level")
        if j["next"] in jobs and j["level"] < 5 and jobs[j["next"]]["stream"] != j["stream"]:
            errors.append(f"job {jid}: next step must stay in the same stream below manager level")
    # the ladder downwards: jobs that lead here (next_step) or commonly move in (also_from)
    for jid, j in jobs.items():
        j["below"] = sorted((k for k, o in jobs.items() if o["next"] == jid), key=lambda k: jobs[k]["order"])
        j["comesFrom"] = [j["alsoFrom"]] if j["alsoFrom"] in jobs else []
    for jid, j in jobs.items():
        # breadth-first down the ladder: nearest lower job first
        lower, seen, frontier = [], {jid}, list(j["below"]) + j["comesFrom"]
        while frontier:
            nxt = []
            for k in frontier:
                if k in seen: continue
                seen.add(k); lower.append(k)
                nxt += jobs[k]["below"] + jobs[k]["comesFrom"]
            frontier = nxt
        for s in j["stages"]:
            for it in s["items"]:
                it["from"] = next((k for k in lower if it["page"] in jobs[k]["pages"]), None)
    return jobs


def main():
    pages = load_pages()
    titles = {p["id"]: p["title"] for p in pages.values()}

    roots = [p for p in pages.values() if not p["parent"]]
    if len(roots) != 1:
        errors.append(f"expected exactly 1 root page (no parent), found {len(roots)}: {[r['id'] for r in roots]}")
    root_id = roots[0]["id"] if roots else None

    for p in pages.values():
        if p["parent"] and p["parent"] not in pages:
            errors.append(f"{p['id']}: parent '{p['parent']}' does not exist")

    children = {pid: [] for pid in pages}
    for p in sorted(pages.values(), key=lambda x: (x["order"], x["title"])):
        if p["parent"] in children:
            children[p["parent"]].append(p["id"])

    # path from root, branch (top-level area) and cycle check
    for p in pages.values():
        path, cur, seen = [], p["id"], set()
        while cur:
            if cur in seen:
                errors.append(f"{p['id']}: parent cycle"); break
            seen.add(cur); path.append(cur)
            cur = pages[cur]["parent"] if cur in pages else ""
        p["path"] = list(reversed(path))
        p["branch"] = p["path"][1] if len(p["path"]) > 1 else p["id"]

    # groups: every top-level branch has one (or none do), each group is one unbroken run, and only branches have them
    branches = sorted((p for p in pages.values() if p["parent"] == root_id), key=lambda p: p["order"])
    grouped = [p for p in branches if p["group"]]
    if grouped and len(grouped) != len(branches):
        errors.append(f"top-level branches without a group: {[p['id'] for p in branches if not p['group']]}")
    seen_groups = []
    for p in branches:
        if p["group"] and (not seen_groups or seen_groups[-1] != p["group"]):
            if p["group"] in seen_groups:
                errors.append(f"group '{p['group']}' is split: its branches must sit next to each other in order")
            seen_groups.append(p["group"])
    for p in pages.values():
        if p["group"] and p["parent"] != root_id:
            errors.append(f"{p['id']}: only top-level branches can have a group")

    # Cartography chart fields: numbers 0-100, and only on pages that carry a tier and a killer
    def pair(pid, key, val):
        try:
            a, b = [float(v) for v in val.split(",")]
        except ValueError:
            errors.append(f"{pid}: {key} must be two numbers, e.g. '60, 40'"); return None
        if not (0 <= a <= 100 and 0 <= b <= 100):
            errors.append(f"{pid}: {key} values must be between 0 and 100"); return None
        return [a, b]
    for p in pages.values():
        if p["place"]:
            p["place"] = pair(p["id"], "place", p["place"])
            if not (p["tier"] and p["killer"] and p["killerKind"]):
                errors.append(f"{p['id']}: a page on the Cartography chart needs tier, killer and killer_kind")
        else:
            p["place"] = None
        p["span"] = pair(p["id"], "span", p["span"]) if p["span"] else None
        if p["span"] and not p["place"]:
            errors.append(f"{p['id']}: span needs a place")
        if p["killerKind"] and not p["place"]:
            errors.append(f"{p['id']}: killer_kind is only used with place")

    # advanced level is inherited: anything under an advanced page is advanced too
    for p in pages.values():
        if p["level"] not in ("basic", "advanced"):
            errors.append(f"{p['id']}: level must be basic or advanced")
        p["adv"] = any(pages[a]["level"] == "advanced" for a in p["path"] if a in pages)
        if p["adv"]:
            ADVANCED.add(p["id"])
    if root_id in ADVANCED:
        errors.append("the root page cannot be advanced")

    # backlinks: source id -> True if the link only exists in advanced material
    backlinks = {pid: {} for pid in pages}
    def add_backlink(target, src, adv):
        cur = backlinks[target].get(src)
        backlinks[target][src] = adv if cur is None else (cur and adv)

    for p in pages.values():
        m = DEEPER.search(p["_body"])
        basic_md, deep_md = (p["_body"][: m.start()], p["_body"][m.start():]) if m else (p["_body"], "")
        sink_b, sink_d = set(), set()
        p["html"] = render(basic_md, titles, p["id"], sink_b)
        p["deep"] = ('<section class="deeper"><div class="deeper-tag">Advanced layer</div>'
                     + render(deep_md, titles, p["id"], sink_d) + "</section>") if deep_md else ""
        p["links"] = sorted(sink_b | sink_d)
        for t in sink_b | sink_d:
            if t != p["id"]:
                add_backlink(t, p["id"], p["adv"] or t not in sink_b)
        words = len(plain_text(basic_md).split())
        p["stub"] = words < STUB_WORDS and not deep_md
        p["text"] = plain_text(basic_md)[:12000]
        p["textDeep"] = plain_text(deep_md)[:12000]
        del p["_body"]

    flows = load_flows(titles)
    for f in flows.values():
        for st in f["steps"]:
            if st["page"]:
                add_backlink(st["page"], "flow:" + f["id"], f["adv"] or st["page"] in ADVANCED)

    roles = load_jobs(titles)
    quals = load_roles(titles, QUALS_DIR, "qual", repeat_ok=True)
    for jid, j in roles.items():
        for q in j["quals"]:
            if q not in quals:
                errors.append(f"job {jid}: qualification '{q}' does not exist")
    clash = set(roles) & set(quals)
    if clash:
        errors.append(f"ids used by both a role and a qualification: {sorted(clash)}")

    for pid, p in pages.items():
        p["children"] = children[pid]
        p["jobs"] = [r for r in sorted(roles, key=lambda r: roles[r]["order"]) if pid in roles[r]["pages"]]
        # qualification modules this page covers: [{"q": qual id, "m": module heading}]
        p["quals"] = [{"q": q, "m": s["title"]}
                      for q in sorted(quals, key=lambda q: quals[q]["order"])
                      for s in quals[q]["stages"] if any(i["page"] == pid for i in s["items"])]
        p["backlinks"] = sorted(backlinks[pid])
        p["backlinksAdv"] = sorted(k for k, v in backlinks[pid].items() if v)

    if errors:
        print("BUILD FAILED:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)

    def site_page(path, default_title):
        """about.md, privacy.md: a small frontmatter (title, summary) and a Markdown body."""
        if not path.exists():
            return None
        meta, body = parse_file(path)
        if meta is None:
            return None
        return {"title": meta.get("title", default_title), "summary": meta.get("summary", ""),
                "html": render(body, titles, path.name, set())}

    about = site_page(ABOUT, "About")
    privacy = site_page(PRIVACY, "Privacy")
    if errors:
        print("BUILD FAILED:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)

    data = {
        "root": root_id,
        "about": about,
        "privacy": privacy,
        "pages": pages,
        "flows": flows,
        "jobs": roles,
        "levels": LEVELS,
        "streams": [{"id": s, "title": n} for s, n in STREAMS],
        "quals": quals,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    OUT.write_text(
        "// GENERATED by tools/build.py from pages/, flows/, jobs/, quals/, about.md and privacy.md. Do not edit by hand.\n"
        "window.MUDMAP = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    stubs = sum(1 for p in pages.values() if p["stub"])
    adv = len(ADVANCED); deeper = sum(1 for p in pages.values() if p["deep"])
    print(f"Built data.js: {len(pages)} pages ({len(pages) - stubs} written, {stubs} stubs), {len(flows)} flows")
    print(f"  Core: {len(pages) - adv} pages · Everything adds {adv} advanced pages and {deeper} 'Going deeper' blocks")
    for r in sorted(roles.values(), key=lambda r: r["order"]):
        core = sum(1 for x in r["pages"] if x not in ADVANCED)
        new = sum(1 for s in r["stages"] for i in s["items"] if not i.get("from"))
        print(f"  Job L{r['level']} {r['short']}: {len(r['pages'])} pages ({core} core, {new} new at this level)")
    for q in sorted(quals.values(), key=lambda q: q["order"]):
        core = sum(1 for x in q["pages"] if x not in ADVANCED)
        print(f"  Qual {q['short']}: {len(q['pages'])} pages across {len(q['stages'])} modules ({core} core)")
    for w in warnings:
        print("  !", w)


if __name__ == "__main__":
    main()
