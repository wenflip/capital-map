# The Capital Map — Scope

*Status: every branch written (no stubs). Live (open, unlisted: no password, search engines blocked). Next: the failure ladder. Last updated 2026-10-25.*

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
5. **One primary parent per page, plus `[[links]]` for everything else.** For example, gold's home is in Money & Liquidity and it is linked from Commodities. This is the same model the Supply Map already uses.
6. **Spine: Option A1 (decided 2026-10-25).** Asset-class spine for the tree, because in investing the *objects* differ far more than the *process* does. The process lives in **Flows**.
7. **The Cartography of Wealth is the headline lens and a data layer.** Every store of wealth carries `tier`, `killer` and `traits` in its frontmatter, shown in a box on its page. Placements are labelled as judgments. It sits alongside the conventional framing, not as the site's voice.
8. **Human & Social Capital is a top-level branch.** Standard asset-class trees leave it out; the Cartography treats it as the root store.

## Top-level branches (v2: twelve branches in four groups)

Groups are labels drawn as clusters on the map, not a tree level (decided 2026-10-25). Inside *What you can own*, branches run from inside you to fully on the record, following the Cartography of Wealth.

| Group | Branch | Covers |
|---|---|---|
| Foundations | Foundation | **Written.** Claims and liabilities, the Cartography of Wealth, time value, compounding, risk and return, inflation |
| Foundations | Money & Liquidity | **Written.** What money is, the hierarchy, gold, central bank money, cash and fiat, bank deposits, when banks fail (capital and liquidity, lender of last resort, bail-in, deposit insurance, the bank–government loop), eurodollars, liquidity, money creation |
| What you can own | Human & Social Capital | **Written.** Human capital, social capital |
| What you can own | Digital Assets | **Written.** Six clusters: how blockchains work (consensus, keys, forks, privacy and traceability), native coins (Bitcoin, smart-contract platforms), tokens (stablecoins, memecoins, governance, wrapped), bridges and layer 2s, DeFi, holding crypto (self-custody, custodial) |
| What you can own | Real Assets | **Written.** Real estate, REITs, commodities, collectibles |
| What you can own | Fixed Income | **Written.** T-bills, bonds, prices and yields, the yield curve, credit risk, inflation-linked bonds, duration |
| What you can own | Equities | **Written.** Shares, indices, funds and ETFs, financial statements, valuation, private business |
| Putting it together | Derivatives | **Written.** Futures, options, perpetuals, leverage |
| Putting it together | Portfolio & Risk | **Written.** Diversification, correlation, allocation, sizing, rebalancing, market regimes |
| How it runs | Markets & Plumbing | **Written.** Exchanges, brokers, custody, settlement |
| How it runs | Measure | **Written.** Returns, drawdown, volatility, Sharpe ratio |
| How it runs | In Practice | **Written.** Tax, account types, common mistakes, data sources, charting (Tools folded in) |

## Cross-cutting views

- **Flows:** built. *Where money comes from* (money created layer by layer) and *When a bank fails* (the backstops tested one by one).
- **Cartography of Wealth:** the model page in Foundation, plus a dedicated **Cartography view** (`#/cartography`): the twelve stores on a two-axis chart, filterable by tier and by kind of killer.
- **Regimes:** a page for now (Market Regimes).
- **Quals:** live. Nine on the page from the start: CFA Levels I, II and III (core plus the Portfolio Management pathway), Mehrling's *Economics of Money and Banking*, FRM Parts I and II, CAIA Levels I and II, and Princeton's *Bitcoin and Cryptocurrency Technologies*. CFA I, Money & Banking, CAIA I, CAIA II and Princeton are mapped; CFA II, CFA III and FRM I–II are placeholders. Ethics modules are listed but out of scope. Left out on purpose: CMT (charting only), CFP (advice and planning), CIPM (too narrow), the CFA Level III Private Wealth and Private Markets pathways.
- **Jobs:** engine supports them; tab hidden until there is content.

## Engine changes from The Supply Map

- Rebranded shell (title, subtitle, welcome guide with four ways in: map, a flow, the Cartography chart, quals).
- New optional page fields `tier`, `killer`, `traits`, rendered as a Cartography box.
- Branch colours for the new branch ids.
- T-code index hidden when no page has t-codes.
- Bug fix: the welcome guide's flow link was hard-coded to `p2p`; it now reads the flow from the link. **Worth back-porting to The Supply Map.**
- First-visit branch (`FIRST_VISIT_OPEN`) opens Money & Liquidity.
- New link-preview image (`assets/share.png`, 1200×630), rendered from an HTML template kept with the helper tools.
- **Cartography view** and the `place`, `span`, `killer_kind` fields, validated by the build.
- Search fixes: hyphenated queries match page text, and keep the whole-phrase bonus. **Both worth back-porting to The Supply Map.**
- About shows a Cartography count instead of an empty jobs tile; the Index says "all written" once there are no stubs.
- Storage prefix stays `mudmap:` so the shared test suites run unchanged (different site, different browser storage, no clash).

## Open questions

1. **Is a Jobs view worth it here,** or is a learning path enough?
2. **Search ranking:** every page containing a word scores the same, so a common word can push the best page down. Weight by where the word appears (title and summary before body) and how often.

## Decided since

- **Contact handle:** keep the Supply Map's approved public contact in `privacy.md`.
- **Commit identity:** all commits use the same public identity as The Supply Map. The first `SCOPE.md` commit on `main` predates this and still carries a personal address in its metadata; fixing it means rewriting `main`, which is the owner's call.
- **Hub standard:** written top-level branches follow the hub rules in the README, checked by the hubs test suite.
- **Access:** the site is open (no password or Zero Trust) but stays out of search engines: the `noindex` tag, `robots.txt` and `X-Robots-Tag` stay until the owner says otherwise.
- **Branch order (done):** Foundation → Digital Assets → When Banks Fail → Fixed Income → the Cartography view → the remaining eight branches.
- **Geography (2026-10-25):** In Practice is written country-neutral: it explains how tax and accounts work, with a few labelled examples from large markets, and tells readers to check local rules.
- **T-codes (2026-10-25):** dropped. They're a Supply Map feature (logistics transaction codes); the engine hides the index when no page has any.
- **Launch gate:** settled. With every page written, the public test suite passes.
- **Neutrality (2026-10-25):** every store of wealth shows how it has failed in history, so the site doesn't read as favouring any one store.
- **Testing (2026-10-25):** 80/20. Content-only branches run their own suite plus a smoke set at desktop width; engine or layout changes run everything at all widths. Suites run in parallel.
- **Outside sources (2026-10-25):** ideas from paid or copyrighted material can be used only in our own words, structure and names, with public cases, credited as `Study notes`. The source's wording, images and named metrics are never used; `test_backstops` guards the bank-failure material.
- **Concepts, not coins (2026-10-25):** the map explains kinds of digital asset, not individual chains. Bitcoin and Ethereum appear because they define a category; other chains appear only as examples inside concept pages (e.g. PulseChain on Forks).

## Logistics parallel

Single parent plus many-to-many links is the material master pattern: one material group, many classifications. The Cartography fields are material classification characteristics (like hazard class or criticality): attributes on each item that later drive filters and risk views. The build step is a master-data load with validation rules.
