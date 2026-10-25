# The Capital Map

A free, independent reference to money, markets and assets: one connected map of cash, bonds, shares, real estate, gold and crypto, plus the skills and relationships that sit underneath them. Sibling of **The Supply Map**, and built on the same engine.

Status: early build. The tree skeleton is in place; **Money & Liquidity** is the first branch written. See `SCOPE.md` for decisions and open questions.

## How to view it

1. Pull the latest version (`git pull`).
2. Double-click `index.html`. It opens in your browser — no server needed.

Views: **Map**, **Flows**, **Quals** and **Index**, plus **About** and **Privacy**. Jobs exist in the engine but are hidden until there is content for them.

## How it's built

All content is Markdown:

| Folder | What goes in it |
|---|---|
| `pages/` | One concept per file. Frontmatter sets its place on the map (`parent`, `order`). |
| `flows/` | Step-by-step walk-throughs. One table whose first two columns are `Step` and `Page`. |
| `jobs/`, `quals/` | Empty for now. |
| `about.md`, `privacy.md` | Site pages. |

After any change, rebuild the data file:

```
python3 tools/build.py
```

The build checks the tree (exactly one root, every parent exists, no loops) and every `[[link]]`, then writes `data.js`, which `index.html` loads. Commit `data.js` along with your changes — the site is served as plain static files.

Full file formats are documented at the top of `tools/build.py`.

## Page frontmatter

```
---
id: gold                     # unique, lowercase, hyphens; matches the file name
title: Gold
parent: money                # id of the parent page on the map
order: 3                     # position among siblings
summary: One line, shown on hover and in search
tags: gold, money            # optional
level: advanced              # optional — hidden in Core view
sources: Author, Title       # optional, semicolon separated
# Cartography of Wealth (optional — only for stores of wealth)
tier: 2                      # 1 inside you · 2 private/bearer · 3 legible; "2-3" for a store that spans tiers
killer: physical theft — the simplest attack on a bearer asset
traits: private, no yield, bearer, transferable
---
```

Pages with fewer than 60 words show as dashed **stubs** on the map.

## Writing rules

- **Timeless.** No prices, dates of current events or forecasts.
- **Neutral.** Explain how things work; never tell the reader what to buy or sell.
- **One page per concept.** Link with `[[page-id]]` or `[[page-id|custom text]]`.
- **Placement on the Cartography of Wealth is a judgment** and is labelled as one on every page that carries it.

## Qualifications (`quals/`)

Each file is one qualification or course. Every module heading starts with a short code, used for search and the module chips (e.g. `CFA1-FI`). Codes must be unique within a file.

```
---
id: cfa-l1
title: CFA Program — Level I
short: CFA I                 # label on chips and in the focus menu
order: 1
status: planned              # optional: a placeholder with no pages yet
summary: One line for the card
---
Intro paragraph.

## CFA1-FI — Fixed Income
- [[bonds]] — optional short note
> Optional note shown under the module heading (e.g. why it's out of scope or only partly mapped)

## CFA1-ETH — Ethical and Professional Standards
> Outside this site's scope: …
```

- **Every module stays on the page**, mapped or not, so the whole syllabus is visible. An empty module shows *Not mapped yet*, or *Out of scope* when its note starts "Outside this site's scope".
- A **placeholder** (`status: planned`) lists its modules with no pages. Remove the `status` line once the first page is mapped. The build fails if a mapped qualification has no pages, or a planned one has some.
- Module names follow each body's published outline, in our own words for notes. Check the outline when it changes (CFA renamed several topics from February 2027).

## Hub pages

A top-level branch page, once written, is a **hub**. Every hub has the sections *What it is*, *Why it exists*, *How it works*, *What goes wrong*, *Connects to* and *Check yourself* (at least two quiz questions), runs to at least 400 words, and links every child page. Links to **advanced** children go only inside its *Going deeper* section, so Core view never shows them. Quizzes go above *Going deeper*, because that section runs to the end of the page and is hidden in Core.

## Link previews

`assets/share.png` is the 1200×630 image shown when the site is shared. It's rendered from HTML with Playwright (the template lives with the helper tools, outside the repo). `og:url` and `og:image` in `index.html` must be absolute and match the live address: `https://thecapitalmap.pages.dev/`.

## Going public — the switches

The site stays private until these are done:

1. **Address.** If the final address isn't `https://thecapitalmap.pages.dev/`, change `og:url` and `og:image` in `index.html`.
2. **Analytics.** Turn on Cloudflare Web Analytics for the Pages project in the Cloudflare dashboard (no code needed). `privacy.md` already describes it.
3. **Contact.** `privacy.md` names the owner-approved public contact handle. It's the only allowed exception to the no-usernames rule.
4. **Access.** Remove any Cloudflare Access policy from the Pages project.
5. **Search engines** (only when ready to be found): remove the `noindex` meta tag in `index.html`, change `robots.txt` to allow crawling, and delete the `X-Robots-Tag` rule in `_headers`. Some link-preview crawlers also respect `robots.txt`, so previews may not show until this step.
6. **Check the preview** with the social network's link-preview inspector once the site is reachable.

## Content rule

Money, markets and assets only. No personal, career or employer details, and no names, emails or locations. Worked examples use fictional data. Write in your own words; credit outside sources in a page's `sources:` line, and personal study files as `Study notes`.

## Tests

The browser test suites are shared with The Supply Map and kept **outside** this repo (they travel with the privacy scan, which must never be committed). Run every suite before each push and read the results before pushing.
