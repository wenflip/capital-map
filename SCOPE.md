# The Capital Map — Scope

*Status: every branch and every flow written (no stubs, no outlines), including the full failure ladder. Live (open, unlisted: no password, search engines blocked). Last updated 2026-10-26.*

## What it is

A free, independent reference map of finance and investing: money, markets and assets (cash, bonds, stocks, real estate, commodities and gold, crypto) in one connected, clickable tree. It is the sibling of **The Supply Map**, and shares its engine.

Working subtitle: *Money · Markets · Assets*

Education only. Not financial advice.

## Decisions so far

1. **Name:** The Capital Map. Repo: `capital-map`.
2. **Reuse the Supply Map engine.** Content is Markdown files in `pages/`, `flows/`, `jobs/` and `quals/`. A build step validates them (one root, one parent per page, no cycles) and generates the site. Most of the work is content and taxonomy, not code.
3. **The tree is organised by structure, not behaviour.**
   - *Structure* is what an asset **is**: whose liability, and a claim on what. It is stable.
   - *Behaviour* is how it **trades right now** (e.g. "crypto trades like high-beta tech"). It changes with the liquidity regime, so it lives in a cross-cutting place (the Market Regimes page for now), not the tree.
4. **Organising question for money:** "whose liability is it, and what is it a claim on?" Not "backed vs unbacked". References: Perry Mehrling's *hierarchy of money*; John Exter's *inverted pyramid*.
5. **One primary parent per page, plus `[[links]]` for everything else.** For example, gold's home is in Money You Hold and it is linked from Commodities. This is the same model the Supply Map already uses.
6. **Spine: Option A1 (decided 2026-10-25).** Asset-class spine for the tree, because in investing the *objects* differ far more than the *process* does. The process lives in **Flows**.
7. **The Cartography of Wealth is the headline lens and a data layer.** Every store of wealth carries `tier`, `killer` and `traits` in its frontmatter, shown in a box on its page. Placements are labelled as judgments. It sits alongside the conventional framing, not as the site's voice.
8. **Human & Social Capital is a top-level branch.** Standard asset-class trees leave it out; the Cartography treats it as the root store.

## Top-level branches (v6: sixteen branches in four groups)

Groups are labels drawn as clusters on the map, not a tree level (decided 2026-10-25). Inside *What you can own*, branches run from inside you to fully on the record, following the Cartography of Wealth.

| Group | Branch | Covers |
|---|---|---|
| Foundations | Foundation | **Written.** Claims and liabilities, the Cartography of Wealth, the four ways to earn a return, time value, compounding, risk and return, inflation |
| Foundations | How Money Works | **Written.** The machinery: what money is, the hierarchy, central bank money, monetary policy, currencies and exchange rates, eurodollars, liquidity |
| What you can own | Human & Social Capital | **Written.** Human capital, social capital |
| What you can own | Money You Hold | **Written.** The money people keep: cash and fiat, bank deposits, bank backstops (capital and liquidity, lender of last resort, bail-in, deposit insurance, the bank–government loop), gold |
| What you can own | Digital Assets | **Written.** Seven clusters: how blockchains work (consensus, keys, forks, privacy and traceability), native coins (Bitcoin, smart-contract platforms), what gives a coin value (sound money, network effects), tokens (stablecoins, memecoins, governance, wrapped), bridges and layer 2s, DeFi, holding crypto (self-custody, custodial) |
| What you can own | Real Assets | **Written.** Real estate, REITs, commodities, collectibles |
| What you can own | Fixed Income | **Written.** T-bills, bonds, prices and yields, the yield curve, credit risk, inflation-linked bonds, duration |
| What you can own | Equities | **Written.** Shares, indices, funds and ETFs, financial statements, valuation, private business |
| Putting it together | Derivatives | **Written.** Futures, options, swaps, perpetuals, leverage |
| Putting it together | Portfolio & Risk | **Written.** Diversification, correlation, allocation, sizing, asymmetry, rebalancing, market regimes |
| Putting it together | When Things Fail | **Written.** The failure ladder hub and ten rungs: broker, insurer, clearing house, ratings, capital controls, confiscation, financial repression, currency, sovereign default, the market itself. The bank and stablecoin rungs link to Backstops and Stablecoins |
| How it runs | Markets & Plumbing | **Written.** Exchanges, dealers and market making, brokers, custody, settlement, the repo market |
| How it runs | How Markets Move | **Written.** The forces behind price moves: the business cycle, the credit cycle, stability breeds instability, priced in, earnings season, fear gauges, flows and fundamentals, forced sellers, short selling |
| How it runs | Measure | **Written.** Returns, drawdown, volatility, Sharpe ratio |
| How it runs | In Practice | **Written.** Tax, account types, common mistakes, data sources, charting (Tools folded in) |
| How it runs | How to Think | **Written.** The hub: thinking tools that cut across the map, in three clusters (decisions; incentives and systems; thinking with numbers). Pages arrive in batches |

## Cross-cutting views

- **Start (questions):** the front door. Plain questions grouped by worry, each with a short answer and 3 to 5 pages to read next. It takes the Index tab's slot; the Index stays at its address and is linked from Start and the settings menu.

- **Flows:** seven, all written.
  - **Written:** *Where money comes from* (money created layer by layer), *When a bank fails* (the backstops tested one by one), *When a country fails* (a debt crisis climbing the failure ladder), *How a share trade settles* (order to custody, firm by firm) *QE and QT* (bonds swapped for reserves, and back, with real cases at each step), *When a broker fails* (each protection tested in turn) and *A stablecoin run* (a bank run on a blockchain).
  - **Outlines:** none left. The engine still supports `status: planned`, and the tests check the outline rules on a throwaway outline.
- **Cartography of Wealth:** the model page in Foundation, plus a dedicated **Cartography view** (`#/cartography`): the twelve stores on a two-axis chart, filterable by tier and by kind of killer.
- **Failures view** (`#/failures`): the twelve-rung ladder from top to bottom, each rung with its backstop and the stores it can hit, then a **store × rung matrix** with each store's own killer beside it. Store and rung pages show the same links in their panels.
- **Regimes:** a page for now (Market Regimes).
- **Quals:** live. Nine on the page from the start: CFA Levels I, II and III (core plus the Portfolio Management pathway), Mehrling's *Economics of Money and Banking*, FRM Parts I and II, CAIA Levels I and II, and Princeton's *Bitcoin and Cryptocurrency Technologies*. CFA I, Money & Banking, CAIA I, CAIA II and Princeton are mapped; CFA II, CFA III and FRM I–II are placeholders. Ethics modules are listed but out of scope. The tab shows **coverage**: mapped modules out of in-scope modules, per qualification and overall (51% at launch; 48% once two thin modules were marked partly mapped; 49% once Swaps fully mapped Money & Banking MB5; 51% once Dealers and Market Making completed Money & Banking), with pages per module. Left out on purpose: CMT (charting only), CFP (advice and planning), CIPM (too narrow), the CFA Level III Private Wealth and Private Markets pathways.
- **Jobs:** not used. The engine supports them, but the tab stays hidden (see Decided since).

## Engine changes from The Supply Map

- Rebranded shell (title, subtitle, welcome guide with four ways in: ask a question, explore the map, start from the beginning, study a qualification).
- New optional page fields `tier`, `killer`, `traits`, rendered as a Cartography box.
- Branch colours for the new branch ids.
- T-code index hidden when no page has t-codes.
- Bug fix: the welcome guide's flow link was hard-coded to `p2p`; it now reads the flow from the link. **Worth back-porting to The Supply Map.**
- First-visit branch (`FIRST_VISIT_OPEN`) opens How Money Works (id `money`; it was called Money & Liquidity until 2026-10-27).
- New link-preview image (`assets/share.png`, 1200×630), rendered from an HTML template kept with the helper tools.
- **Cartography view** and the `place`, `span`, `killer_kind` fields, validated by the build.
- Search fixes: hyphenated queries match page text, and keep the whole-phrase bonus. **Both worth back-porting to The Supply Map.**
- About shows a Cartography count instead of an empty jobs tile; the Index says "all written" once there are no stubs.
- **Search ranking (2026-10-25):** matches are weighted by where the words appear (title, then summary and tags, then how often in the body); the tree-depth bonus is only a tie-break. **Worth back-porting to The Supply Map.**
- **Quals coverage (2026-10-26):** the build gives each qualification module a state (mapped, partly mapped, not mapped yet, out of scope), fails on a note that contradicts the pages, and writes per-qualification and overall coverage to `data.js`. The Quals tab shows a summary, a bar on each card, and pages per module.
- **Failures view and SQLite export (2026-10-26):** new page fields `rung`, `rung_name`, `backstop` and `fails_at`, validated by the build; a Failures tab ("Ladder" on phones, with tighter phone tabs so six still fit); the build writes `data/capital-map.sqlite` and `.sql` with foreign keys checked.
- **Planned flows (2026-10-26):** flows take `status: planned` for an outline. The build checks that an outline has no detail columns and links every step, and that a written flow has at least one detail column. Planned flows show a Planned tag and an outline note, and drop the empty label column. About counts written and planned flows. Flows are exported as `flows` and `flow_steps`.
- Storage prefix stays `mudmap:` so the shared test suites run unchanged (different site, different browser storage, no clash).

## Open questions

None.

## Decided since

- **Contact handle:** keep the Supply Map's approved public contact in `privacy.md`.
- **Commit identity:** all commits use the same public identity as The Supply Map. The first `SCOPE.md` commit on `main` predates this and still carries a personal address in its metadata; fixing it means rewriting `main`, which is the owner's call.
- **Hub standard:** written top-level branches follow the hub rules in the README, checked by the hubs test suite.
- **Access:** the site is open (no password or Zero Trust) but stays out of search engines: the `noindex` tag, `robots.txt` and `X-Robots-Tag` stay until the owner says otherwise.
- **Branch order (done):** Foundation → Digital Assets → When Banks Fail (now Bank Backstops) → Fixed Income → the Cartography view → the remaining eight branches.
- **Geography (2026-10-25):** In Practice is written country-neutral: it explains how tax and accounts work, with a few labelled examples from large markets, and tells readers to check local rules.
- **T-codes (2026-10-25):** dropped. They're a Supply Map feature (logistics transaction codes); the engine hides the index when no page has any.
- **Launch gate:** settled. With every page written, the public test suite passes.
- **Failure ladder (2026-10-25):** a 13th branch, *When Things Fail*, in *Putting it together* after Portfolio & Risk. Rung pages use one template (what fails, the backstop, where it runs out, cases, what it kills). Existing pages keep their parents; the ladder links to them rather than duplicating them (the bank rung is the Backstops page).
- **Neutrality (2026-10-25):** every store of wealth shows how it has failed in history, so the site doesn't read as favouring any one store.
- **Testing (2026-10-25):** 80/20. Content-only branches run their own suite plus a smoke set at desktop width; engine or layout changes run everything at all widths. Suites run in parallel.
- **Outside sources (2026-10-25):** ideas from paid or copyrighted material can be used only in our own words, structure and names, with public cases, credited as `Study notes`. The source's wording, images and named metrics are never used; `test_backstops` guards the bank-failure material.
- **Coverage, defined honestly (2026-10-26):** coverage % = mapped modules ÷ in-scope modules. Out-of-scope modules aren't counted; partly mapped modules are shown but not counted; placeholders count as not mapped. "Mapped" means at least one page covers the module's core idea, so pages per module are shown beside it to keep thin modules visible.
- **Failure ladder as data (2026-10-26):** rungs are explicit (`rung:` on the page), not "children of the hub", because two rungs live elsewhere on the tree. Store × rung is many-to-many, stored once as `fails_at` on each store and inverted by the build. Every link is grounded in the rung page's own text; three pages gained a sentence to make that true (Stablecoins, When Banks Fail, Confiscation). The view says plainly that more rungs means more institutions, not more risk, and shows each store's own killer beside its row.
- **Outline flows, not empty placeholders (2026-10-26):** a placeholder flow lists its real steps, each opening an existing page, so it's useful before it's written; an empty card would show nothing. Same idea as planned qualifications listing every module. A step linking a normal process never opens a failure page (the trade flow's clearing step opens Settlement, not Clearing House Failure).
- **SQLite export (2026-10-26):** the build writes the map as a normalised SQLite database (lists become tables, ranges become two columns, junction tables for many-to-many) for SQL practice and reuse. It's committed and served, and byte-identical on an unchanged rebuild.
- **Four ways to earn (2026-10-26):** a Foundation page sorts every return by what you supply: labour (wages), lending (interest or rent), ownership (profit), and price and risk (gains or premiums). Money with nothing supplied is a transfer. It's a third lens beside the tree (what assets are) and the Cartography (what kills them): how wealth grows. It classifies mechanisms, never assets, because one asset can earn several ways. The fourth way is split into pure price bets and being paid to carry risk, and is never called "speculation". From the owner's study notes, in our own words, credited with Adam Smith's three sources of revenue (1776); a test guards against the notes' wording. Later, maybe: an `earns:` field on stores as data.
- **What gives a coin value (2026-10-26):** a Digital Assets cluster explains where value comes from for assets that are nobody's liability. Code can be copied, so value needs both a well-built asset (**sound money**: supply and who holds it, security, legal standing, liquidity) and a crowd (**network effects**: real users, the default choice, a momentum loop that runs both ways, a lasting community). It's judged by the weaker part, as a way of thinking, not a formula. It doesn't apply to stablecoins or wrapped tokens, which are claims. From the owner's study notes in our own words, without the notes' verdict naming one coin as the winner (it's neither timeless nor neutral). Schelling (1960), Soros (1987) and every dated case were checked against sources. Mapped to Princeton BTC7 and BTC10.
- **Questions as the front door (2026-10-26):** the site was filed the way experts think; newcomers arrive with worries, not topics. Questions are entries linked to pages (many-to-many, like quals), shown on a Start view, in search, as "Answers" links on routed pages, and as `questions` and `question_route` in the SQLite export.
  - **No seventh tab:** six only just fit on a 390px phone. Start takes the Index tab's slot, first in the bar. The map stays home (logo and H).
  - **Welcome guide:** "Ask a question" is the primary option; "Compare stores of wealth" was dropped from the card (the tab remains), so the card is no taller.
  - **Readability is a guide, not a gate:** measured with Flesch–Kincaid in the test kit; honesty wins where they conflict.
  - **The Fine Print is folded in:** its counterintuitive points become questions, so there's one mechanism and no separate layer.
  - **The beginner path (branch 3):** "Start from the beginning", 11 Core pages from what money is to the Cartography of Wealth. It uses the qualifications' loader and the existing per-page ticks (no new storage), not the job-ladder engine. The welcome guide's "Follow the money" option became "Start from the beginning"; the flow is still on the Flows tab.
  - **Built in three branches:** engine and the first 10 questions; about 18 questions in total; then a Start-here path with ticks, using the qualification loader, not the job ladder.
- **Figures (2026-10-26):** four SVG diagrams in `assets/figures/`, embedded where they illustrate the text: the ownership chain on Custody and Shares (Brokers links to it), fee drag on Compounding, the layers of money on Hierarchy of Money, and "your basket" on Inflation. The failure-ladder figure was deleted: it duplicated the live Failures tab and 9 of its 12 backstops had drifted from the data. Convention, validation, tap-to-enlarge and dark-mode dimming are in the README. The chain's US legal terms (UCC Article 8 "security entitlement"; DTC's nominee) were checked and are credited on Custody.
- **Housekeeping (2026-10-26):**
  - **No Jobs view.** The beginner path and the questions already give newcomers a route; a job ladder would be a third way in with no content behind it.
  - **When Banks Fail is now Bank Backstops** (same id, `backstops`), so it no longer clashes with the *When a bank fails* flow. The flow moved under the When Things Fail heading on the Flows tab, beside the other failure flows.
  - **Thin modules marked Partly mapped:** CFA I Financial Statement Analysis and Princeton BTC8 (alternative mining puzzles) each had one page against a much wider module. Coverage drops, but it stays honest.
  - The failure hub links to the Failures tab.
- **Money You Hold (2026-10-27):** a 14th branch in *What you can own*, between Digital Assets and Real Assets. The heading "What you can own" left out the money people hold most, so cash and fiat, bank deposits (with Bank Backstops) and gold moved there from the old Money & Liquidity branch. That branch is now **How Money Works** (same id, `money`): the machinery, not the holdings.
  - Gold sits with the money you hold because people keep it as money and it is nobody's liability; Commodities still links to it.
  - Stablecoins stay in Digital Assets, linked from the new hub.
  - **Placement follows the group's rule** (inside you → bearer → on the record): banknotes and gold are bearer (tier 2) and deposits are on the record (tier 3), so the branch sits at about 2.5, after Digital Assets (2) and beside Real Assets (2.5). It was first placed straight after Human & Social; the groups test caught that this broke the rule.
  - The new branch's map colour (hue 320) was chosen by measured contrast: white label text at 6.1:1 in light mode, against 2.4:1 for the first candidate (a yellow-green).
- **How Markets Move (2026-10-27):** a 15th branch in *How it runs*, after Markets & Plumbing. It gathers what professionals use daily and almost nobody else is taught, in three families: cycles, expectations and flows. The first nine pages are the business cycle, the credit cycle, stability breeds instability (Minsky), priced in, earnings season, fear gauges, flows and fundamentals, forced sellers, and short selling. Two close relatives sit where they belong: the repo market in Markets & Plumbing, and asymmetry in Portfolio & Risk.
  - **Explain, never signal:** every page describes a mechanism with a reason behind it, never a trading rule. The hub's key rule says so outright.
  - **Later candidates** for the branch: calendar rhythms (central bank days, options expiry, index rebalancing, quarter-end), behaviour (herding, loss aversion), sector rotation, long debt cycles, booms and busts, volatility clustering, fat tails, liquidity and sequence risk, shadow banking, collateral and haircuts, who's on the other side, price ratios, and a margin-call spiral flow.
  - Map colour hue 10, chosen by measured contrast (white label 5.9:1 light, 6.2:1 dark).
- **How to Think (2026-10-27):** a 16th branch, last in *How it runs*, for the mental models that cut across every page. It's placed last because it's the most abstract: it's easier to use once the rest of the map is familiar. Three clusters: **decisions** (second-order thinking, opportunity cost, edge, luck versus skill, time horizons, margin of safety), **incentives and systems** (incentives, externalities and the commons) and **thinking with numbers** (averages and distributions, absolute and relative risk, false precision).
  - **Written with a second AI.** Grok drafts the pages on this branch; Claude reviews them against the house rules, verifies every dated fact from the source links in the PR, runs the tests and the privacy scan, and approves before the owner merges.
  - **Ideas, not a book's stories.** The ideas are standard; the pages use public, checkable cases and our own words, not anecdotes or branded terms from any one book.
  - **Related pages in other branches:** risk of ruin and the Kelly criterion (Portfolio & Risk), the arithmetic of active management (Equities), fat tails (Measure), booms and busts (How Markets Move), and withdrawal rates, fraud warning signs and "enough" (In Practice).
  - Map colour hue 280, chosen by measured contrast (white label 7.3:1 light, 5.4:1 dark).
- **Concepts, not coins (2026-10-25):** the map explains kinds of digital asset, not individual chains. Bitcoin and Ethereum appear because they define a category; other chains appear only as examples inside concept pages (e.g. PulseChain on Forks).

## Logistics parallel

Single parent plus many-to-many links is the material master pattern: one material group, many classifications. The Cartography fields are material classification characteristics (like hazard class or criticality): attributes on each item that later drive filters and risk views. The build step is a master-data load with validation rules.
