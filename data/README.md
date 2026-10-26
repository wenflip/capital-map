# The Capital Map as a database

`tools/build.py` writes the whole map as a SQLite database every time it runs:

| File | What it is |
|---|---|
| `capital-map.sqlite` | The database. Open it with any SQLite tool. |
| `capital-map.sql` | The same database as plain SQL text, so a change to the map shows up as a readable diff. |

Both are generated: don't edit them by hand. They're rebuilt from scratch with rows in a fixed order, so an unchanged map gives byte-identical files.

## Opening it

- **Command line:** `sqlite3 data/capital-map.sqlite`, then `.tables`, `.schema fails_at`, and `.mode box` for readable output.
- **A desktop app:** DB Browser for SQLite, or any database tool that opens SQLite files.
- **Python:** `import sqlite3; db = sqlite3.connect("data/capital-map.sqlite")`.

`.schema` shows each table with comments that explain the columns.

## Tables

| Table | One row per | Keys |
|---|---|---|
| `pages` | page on the map | `id`; `parent_id` and `branch_id` point back into `pages` |
| `page_tags` | page × tag | (`page_id`, `tag`) |
| `page_links` | `[[link]]` from one page to another | (`from_id`, `to_id`) |
| `stores` | store of wealth on the Cartography chart | `page_id` → `pages` |
| `store_traits` | store × trait | (`store_id`, `trait`) |
| `rungs` | rung on the failure ladder | `page_id` → `pages`; `number` is unique |
| `fails_at` | store × rung that can hit it | (`store_id`, `rung_id`): the **junction table** |
| `quals` | qualification | `id` |
| `modules` | qualification module, with its coverage state | (`qual_id`, `code`) |
| `module_pages` | module × page that covers it | (`qual_id`, `code`, `page_id`) |

Three design choices are worth noticing:

- **Lists become tables.** Tags, traits and links aren't comma-separated text inside a row. Each value gets its own row, so it can be counted, joined and filtered. This is *first normal form*.
- **Ranges become two columns.** A store that spans tiers ("2-3" on the page) has `tier_min` 2 and `tier_max` 3, so `WHERE tier_max = 3` just works.
- **Many-to-many needs a junction table.** One store can be hit by many rungs, and one rung can hit many stores. Neither table can hold the other's ids in a single column, so `fails_at` holds the pairs. `module_pages` does the same for qualifications and pages.

Foreign keys are checked when the database is built, so every id in a junction table is real.

## Starter queries

**1. JOIN: the rungs that can hit one store**

```sql
SELECT s.page_id AS store, r.number, r.name
FROM fails_at f
JOIN stores s ON s.page_id = f.store_id
JOIN rungs  r ON r.page_id = f.rung_id
WHERE s.page_id = 'gold'
ORDER BY r.number;
```

**2. GROUP BY: how many rungs can hit each store**

`LEFT JOIN` keeps stores with no rungs, which `COUNT(f.rung_id)` then counts as 0.

```sql
SELECT s.page_id AS store, COUNT(f.rung_id) AS rungs
FROM stores s
LEFT JOIN fails_at f ON f.store_id = s.page_id
GROUP BY s.page_id
ORDER BY rungs DESC, store;
```

**3. HAVING: rungs that hit four or more stores**

`WHERE` filters rows before grouping; `HAVING` filters the groups after.

```sql
SELECT r.number, r.name, COUNT(*) AS stores_hit
FROM rungs r
JOIN fails_at f ON f.rung_id = r.page_id
GROUP BY r.page_id
HAVING COUNT(*) >= 4
ORDER BY r.number;
```

**4. Finding what's missing: stores no rung reaches**

```sql
SELECT s.page_id
FROM stores s
LEFT JOIN fails_at f ON f.store_id = s.page_id
WHERE f.rung_id IS NULL;
```

**5. Recomputing the Quals tab's coverage**

In SQLite a comparison is 1 or 0, so `SUM(state = 'mapped')` counts the mapped modules.

```sql
SELECT q.short,
       SUM(m.state = 'mapped') AS mapped,
       SUM(m.state <> 'out')   AS in_scope,
       ROUND(100.0 * SUM(m.state = 'mapped') / SUM(m.state <> 'out')) AS pct
FROM quals q
JOIN modules m ON m.qual_id = q.id
GROUP BY q.id
ORDER BY q.sort;
```

## Practice: write these yourself

1. Which branch has the most pages? Which has the most words?
2. Which ten pages have the most other pages linking *to* them?
3. Which pages does nothing link to?
4. For each tier (use `tier_max`), how many rungs on average can hit its stores?
5. Which rung pages are *not* children of the When Things Fail hub? (Join `rungs` to `pages` and look at `parent_id`.)
6. Which pages appear in more than one qualification?
7. Which in-scope modules have exactly one page? These are the thin ones the Quals tab warns about.

## The logistics parallel

This is the same shape as a supply-risk register. `stores` × `rungs` through `fails_at` works like `parts` × `disruptions` (a supplier going bust, a port closing, a lane shutting): many-to-many, with the pairs in their own table.

- **"How many rungs can hit each store?"** is "how many disruptions is each part exposed to?"
- **"Which rung hits the most stores?"** is "which single disruption stops the most parts?" That's the one to plan around.

And as on the ladder, a part exposed to few listed disruptions isn't automatically safe: its main risk may simply be one the register doesn't track.
