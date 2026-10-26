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

Flow file format (flows/<id>.md): frontmatter (id, title, area, order, summary, optional level and
status), intro text, one table whose first two columns are Step and Page, then outro text. Every further
column is a detail lane in the flow view. status: planned marks an OUTLINE: Step | Page only, every step
linked to a page, shown with a Planned tag until its detail columns are written. A written flow (the
default) needs at least one detail column.

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

Failure ladder (page fields, optional):
    rung: 8                       on a rung page: its place on the ladder, 1..N with no gaps
    rung_name: Confiscation       the rung's name on the ladder (required with rung)
    backstop: Courts, ...         what is supposed to protect you at this rung (required with rung)
    fails_at: confiscation, ...   on a store of wealth (a page with place): the rungs that can hit it
The build inverts fails_at, so every rung also knows the stores it hits (a many-to-many link).

SQLite export: every build also writes data/capital-map.sqlite and data/capital-map.sql (the same
database as text), normalised into tables with foreign keys checked. See SCHEMA below and data/README.md.

Coverage (qualifications only). Every module gets a state, from its pages and its "> " note:
    out      note starts "Outside this site's scope"   listed, but not counted
    none     no pages                                   in scope, not mapped yet
    partial  pages, and note starts "Partly mapped"     counted separately, not in the %
    mapped   pages, and no "Partly mapped" note
Coverage % = mapped modules / in-scope modules (everything except "out"). "Mapped" means at least
one page covers the module's core idea, not that the pages cover its whole syllabus; the number
of pages per module is shown next to it so thin modules stay visible. The build fails if a note
contradicts the pages (an out-of-scope or "Not mapped yet" module with pages, or a "Partly
mapped" module with none).
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

LIST_KEYS = {"tcodes", "fiori", "tags", "aliases", "quals", "traits", "fails_at"}
DB_DIR = ROOT / "data"                      # SQLite export of the map, for querying (see data/README.md)
DB_FILE = DB_DIR / "capital-map.sqlite"
SQL_FILE = DB_DIR / "capital-map.sql"       # the same database as plain SQL text, so changes show in a diff
WIKILINK = re.compile(r"\[\[([a-z0-9\-]+)(?:\\?\|([^\]]+))?\]\]")
STUB_WORDS = 60  # pages with fewer body words are shown as stubs

errors = []
warnings = []
ADVANCED = set()   # ids of advanced pages (filled before rendering)
WORDS = {}         # page id -> words in the page body, basic and deeper (filled while rendering)
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
            # Failure ladder (optional): a rung page carries its number, name and typical backstop;
            # a store of wealth lists the rungs that can hit it (fails_at: rung page ids)
            "rung": meta.get("rung", ""),
            "rungName": meta.get("rung_name", ""),
            "backstop": meta.get("backstop", ""),
            "failsAt": meta.get("fails_at", []),
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
        status = meta.get("status", "written")
        if status not in ("written", "planned"):
            errors.append(f"flow {fid}: status must be written or planned")
        # a planned flow is an outline: Step and Page only, every step linked to a page.
        # a written flow has at least one detail column (lane).
        if status == "planned" and lanes:
            errors.append(f"flow {fid}: a planned flow is an outline (Step | Page only); remove its detail columns or the status")
        if status != "planned" and not lanes:
            errors.append(f"flow {fid}: a written flow needs at least one detail column after Step | Page (or status: planned)")
        if status == "planned" and any(not st["page"] for st in steps):
            errors.append(f"flow {fid}: every step of an outline must link a page")
        flows[fid] = {
            "status": status,
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
        if repeat_ok:
            roles[rid]["coverage"] = qual_coverage(rid, stages)
    return roles


COVERAGE_STATES = ("mapped", "partial", "none", "out")


def module_state(rid, s):
    """One qualification module's coverage state, from its pages and its note (see the docstring)."""
    note = re.sub(r"<[^>]+>", "", s["note"]).strip().lower()
    has = bool(s["items"])
    if note.startswith("outside this site"):
        if has:
            errors.append(f"qual {rid}: '{s['title']}' is marked out of scope but lists pages")
        return "out"
    if note.startswith("partly mapped"):
        if not has:
            errors.append(f"qual {rid}: '{s['title']}' says Partly mapped but lists no pages")
        return "partial" if has else "none"
    if note.startswith("not mapped yet") and has:
        errors.append(f"qual {rid}: '{s['title']}' says Not mapped yet but lists pages")
    return "mapped" if has else "none"


def qual_coverage(rid, stages):
    """Counts per state, in-scope total, pages and the coverage %; also sets each module's state and page count."""
    c = {k: 0 for k in COVERAGE_STATES}
    for s in stages:
        s["state"] = module_state(rid, s)
        s["pages"] = len(s["items"])
        c[s["state"]] += 1
    c["modules"] = len(stages)
    c["inScope"] = len(stages) - c["out"]
    c["pct"] = round(100 * c["mapped"] / c["inScope"]) if c["inScope"] else 0
    return c


def total_coverage(quals):
    """Overall coverage across every qualification, placeholders included (they count as not mapped)."""
    t = {k: sum(q["coverage"][k] for q in quals.values()) for k in (*COVERAGE_STATES, "modules", "inScope")}
    t["pct"] = round(100 * t["mapped"] / t["inScope"]) if t["inScope"] else 0
    t["quals"] = len(quals)
    return t


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


SCHEMA = """
CREATE TABLE pages (                -- one row per page on the map
  id        TEXT PRIMARY KEY,
  title     TEXT NOT NULL,
  short     TEXT,                   -- label on the map, if shorter than the title
  parent_id TEXT REFERENCES pages(id),   -- NULL only for the root
  branch_id TEXT REFERENCES pages(id),   -- top-level branch the page sits under; NULL for the root
  depth     INTEGER NOT NULL,       -- 0 root, 1 branch, 2+ below
  level     TEXT NOT NULL CHECK (level IN ('basic', 'advanced')),   -- advanced is inherited from ancestors
  summary   TEXT,
  words     INTEGER NOT NULL        -- words in the body, Going deeper included
);
CREATE TABLE page_tags (
  page_id TEXT NOT NULL REFERENCES pages(id),
  tag     TEXT NOT NULL,
  PRIMARY KEY (page_id, tag)
);
CREATE TABLE page_links (           -- [[links]] in page bodies: from_id links to to_id
  from_id TEXT NOT NULL REFERENCES pages(id),
  to_id   TEXT NOT NULL REFERENCES pages(id),
  PRIMARY KEY (from_id, to_id)
);
CREATE TABLE stores (               -- stores of wealth on the Cartography chart (placements are judgments)
  page_id     TEXT PRIMARY KEY REFERENCES pages(id),
  tier_min    INTEGER NOT NULL CHECK (tier_min BETWEEN 1 AND 3),   -- 1 inside you, 2 private/bearer, 3 legible
  tier_max    INTEGER NOT NULL CHECK (tier_max BETWEEN tier_min AND 3),
  killer      TEXT NOT NULL,
  killer_kind TEXT NOT NULL,
  x           REAL NOT NULL CHECK (x BETWEEN 0 AND 100),   -- inside you (0) to outside you (100)
  y           REAL NOT NULL CHECK (y BETWEEN 0 AND 100)    -- hidden (0) to recorded by authority (100)
);
CREATE TABLE store_traits (
  store_id TEXT NOT NULL REFERENCES stores(page_id),
  trait    TEXT NOT NULL,
  PRIMARY KEY (store_id, trait)
);
CREATE TABLE rungs (                -- the failure ladder, from the firm closest to you (1) to the system itself
  page_id  TEXT PRIMARY KEY REFERENCES pages(id),
  number   INTEGER NOT NULL UNIQUE,
  name     TEXT NOT NULL,
  backstop TEXT NOT NULL            -- what is supposed to protect you at this rung
);
CREATE TABLE fails_at (             -- junction table: which rungs can hit which stores (many-to-many)
  store_id TEXT NOT NULL REFERENCES stores(page_id),
  rung_id  TEXT NOT NULL REFERENCES rungs(page_id),
  PRIMARY KEY (store_id, rung_id)
);
CREATE TABLE flows (               -- step-by-step walk-throughs; planned = an outline still to be written
  id     TEXT PRIMARY KEY,
  title  TEXT NOT NULL,
  area   TEXT NOT NULL,              -- the heading it sits under on the Flows tab
  status TEXT NOT NULL CHECK (status IN ('written', 'planned')),
  sort   REAL NOT NULL
);
CREATE TABLE flow_steps (          -- each step of a flow, and the page it opens
  flow_id TEXT NOT NULL REFERENCES flows(id),
  step    INTEGER NOT NULL,         -- 1, 2, 3 ... in the order they happen
  label   TEXT NOT NULL,
  page_id TEXT REFERENCES pages(id),   -- NULL if the step opens no page
  PRIMARY KEY (flow_id, step)
);
CREATE TABLE quals (
  id     TEXT PRIMARY KEY,
  title  TEXT NOT NULL,
  short  TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('mapped', 'planned')),
  sort   REAL NOT NULL
);
CREATE TABLE modules (              -- qualification modules and their coverage state
  qual_id TEXT NOT NULL REFERENCES quals(id),
  code    TEXT NOT NULL,
  title   TEXT NOT NULL,
  state   TEXT NOT NULL CHECK (state IN ('mapped', 'partial', 'none', 'out')),
  sort    INTEGER NOT NULL,
  PRIMARY KEY (qual_id, code)
);
CREATE TABLE module_pages (         -- junction table: pages that cover each module
  qual_id  TEXT NOT NULL,
  code     TEXT NOT NULL,
  page_id  TEXT NOT NULL REFERENCES pages(id),
  position INTEGER NOT NULL,
  PRIMARY KEY (qual_id, code, page_id),
  FOREIGN KEY (qual_id, code) REFERENCES modules(qual_id, code)
);
"""


def write_sqlite(pages, rung_ids, quals, flows):
    """Write the map as a SQLite database (and the same database as SQL text). Rebuilt from scratch every
    time, rows inserted in a fixed order, so an unchanged map gives an unchanged file. Returns row counts."""
    import sqlite3
    DB_DIR.mkdir(exist_ok=True)
    tmp = DB_DIR / "capital-map.sqlite.tmp"
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    ids = sorted(pages)
    rows = lambda table, data: db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(data[0]))})", data) if data else None
    # tree order (root, then branches, then deeper), so every parent row exists before its children
    rows("pages", [(i, pages[i]["title"], pages[i]["short"] or None, pages[i]["parent"] or None,
                    pages[i]["branch"] if pages[i]["parent"] else None, len(pages[i]["path"]) - 1,
                    "advanced" if pages[i]["adv"] else "basic", pages[i]["summary"], WORDS.get(i, 0))
                   for i in sorted(pages, key=lambda i: (len(pages[i]["path"]), i))])
    rows("page_tags", sorted({(i, t) for i in ids for t in pages[i]["tags"]}))
    rows("page_links", [(i, t) for i in ids for t in pages[i]["links"] if t != i])
    stores = [i for i in ids if pages[i]["place"]]
    def tiers(i):
        t = [int(x) for x in re.findall(r"[1-3]", str(pages[i]["tier"]))]
        return min(t), max(t)
    rows("stores", [(i, *tiers(i), pages[i]["killer"], pages[i]["killerKind"], *pages[i]["place"]) for i in stores])
    rows("store_traits", sorted({(i, t) for i in stores for t in pages[i]["traits"]}))
    rows("rungs", [(r, pages[r]["rung"], pages[r]["rungName"], pages[r]["backstop"]) for r in rung_ids])
    rows("fails_at", [(i, r) for i in stores for r in pages[i]["failsAt"]])
    fids = sorted(flows, key=lambda f: (flows[f]["order"], f))
    rows("flows", [(f, flows[f]["title"], flows[f]["area"], flows[f]["status"], flows[f]["order"]) for f in fids])
    rows("flow_steps", [(f, n, st["label"], st["page"]) for f in fids for n, st in enumerate(flows[f]["steps"], 1)])
    qids = sorted(quals, key=lambda q: quals[q]["order"])
    rows("quals", [(q, quals[q]["title"], quals[q]["short"], quals[q]["status"], quals[q]["order"]) for q in qids])
    code = lambda s: re.split(r"\s+[—–-]\s+", s["title"])[0]
    rows("modules", [(q, code(s), s["title"], s["state"], n) for q in qids for n, s in enumerate(quals[q]["stages"], 1)])
    rows("module_pages", [(q, code(s), it["page"], n) for q in qids for s in quals[q]["stages"] for n, it in enumerate(s["items"], 1)])
    db.commit()
    bad = db.execute("PRAGMA foreign_key_check").fetchall()
    if bad:
        db.close(); tmp.unlink()
        print("BUILD FAILED:\n  ✗ SQLite export: broken references", bad[:5]); sys.exit(1)
    counts = {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for (t,) in db.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY rowid")}
    db.execute("VACUUM")
    sql = "\n".join(db.iterdump())
    db.close()
    tmp.replace(DB_FILE)
    SQL_FILE.write_text("-- GENERATED by tools/build.py: the Capital Map as SQL. Do not edit by hand.\n"
                        "-- Load it with:  sqlite3 capital-map.sqlite < capital-map.sql   (or open capital-map.sqlite directly)\n"
                        + sql + "\n", encoding="utf-8")
    return counts


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

    # Failure ladder: rungs numbered 1..N with no gaps, each with a name and a backstop;
    # fails_at only on stores of wealth (pages on the Cartography chart), naming rungs, no repeats
    rungs = []
    for p in pages.values():
        if p["rung"]:
            try:
                p["rung"] = int(p["rung"])
            except ValueError:
                errors.append(f"{p['id']}: rung must be a whole number"); p["rung"] = 0; continue
            if not (p["rungName"] and p["backstop"]):
                errors.append(f"{p['id']}: a rung needs rung_name and backstop")
            rungs.append(p)
        else:
            p["rung"] = 0
            if p["rungName"] or p["backstop"]:
                errors.append(f"{p['id']}: rung_name and backstop are only used with rung")
    rungs.sort(key=lambda p: p["rung"])
    if [p["rung"] for p in rungs] != list(range(1, len(rungs) + 1)):
        errors.append(f"rungs must be numbered 1 to {len(rungs)} with no gaps or repeats: {[p['rung'] for p in rungs]}")
    rung_ids = [p["id"] for p in rungs]
    for p in pages.values():
        p["hits"] = []
    for p in pages.values():
        if p["failsAt"] and not p["place"]:
            errors.append(f"{p['id']}: fails_at is only used on stores of wealth (pages with place)")
        if len(set(p["failsAt"])) != len(p["failsAt"]):
            errors.append(f"{p['id']}: fails_at lists a rung twice")
        for r in p["failsAt"]:
            if r not in rung_ids:
                errors.append(f"{p['id']}: fails_at '{r}' is not a rung")
        p["failsAt"] = sorted((r for r in set(p["failsAt"]) if r in rung_ids), key=lambda r: pages[r]["rung"])
        for r in p["failsAt"]:
            pages[r]["hits"].append(p["id"])
    for p in rungs:
        p["hits"].sort()

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
        WORDS[p["id"]] = words + len(plain_text(deep_md).split())   # for the SQLite export only
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
        "coverage": total_coverage(quals),
        "rungs": rung_ids,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    OUT.write_text(
        "// GENERATED by tools/build.py from pages/, flows/, jobs/, quals/, about.md and privacy.md. Do not edit by hand.\n"
        "window.MUDMAP = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    tables = write_sqlite(pages, rung_ids, quals, flows)
    stubs = sum(1 for p in pages.values() if p["stub"])
    adv = len(ADVANCED); deeper = sum(1 for p in pages.values() if p["deep"])
    planned = sum(1 for f in flows.values() if f["status"] == "planned")
    print(f"Built data.js: {len(pages)} pages ({len(pages) - stubs} written, {stubs} stubs), "
          f"{len(flows)} flows ({len(flows) - planned} written, {planned} planned)")
    print(f"  Core: {len(pages) - adv} pages · Everything adds {adv} advanced pages and {deeper} 'Going deeper' blocks")
    for r in sorted(roles.values(), key=lambda r: r["order"]):
        core = sum(1 for x in r["pages"] if x not in ADVANCED)
        new = sum(1 for s in r["stages"] for i in s["items"] if not i.get("from"))
        print(f"  Job L{r['level']} {r['short']}: {len(r['pages'])} pages ({core} core, {new} new at this level)")
    for q in sorted(quals.values(), key=lambda q: q["order"]):
        core = sum(1 for x in q["pages"] if x not in ADVANCED)
        c = q["coverage"]
        print(f"  Qual {q['short']}: {len(q['pages'])} pages across {len(q['stages'])} modules ({core} core)"
              f" · coverage {c['mapped']}/{c['inScope']} in scope = {c['pct']}%"
              + (f", {c['partial']} partly" if c["partial"] else "") + (f", {c['out']} out of scope" if c["out"] else ""))
    t = data["coverage"]
    print(f"  Coverage: {t['mapped']} of {t['inScope']} in-scope modules mapped ({t['pct']}%), {t['partial']} partly,"
          f" {t['none']} not yet; {t['out']} out of scope, across {t['quals']} qualifications")
    pairs = sum(len(pages[r]["hits"]) for r in rung_ids)
    stores = [p for p in pages.values() if p["place"]]
    print(f"  Failure ladder: {len(rung_ids)} rungs · {pairs} store-rung links · "
          f"{sum(1 for p in stores if not p['failsAt'])} of {len(stores)} stores on no rung")
    print(f"  SQLite: {DB_FILE.relative_to(ROOT)} and {SQL_FILE.relative_to(ROOT)} · "
          + ", ".join(f"{t} {n}" for t, n in tables.items()))
    for w in warnings:
        print("  !", w)


if __name__ == "__main__":
    main()
