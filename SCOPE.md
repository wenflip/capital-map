# The Capital Map — Scope

*Status: building. Live (open, unlisted: no password, search engines blocked). Written: Money & Liquidity, Foundation. Last updated 2026-10-25.*

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

## Top-level branches (v1, built)

| Branch | Covers |
|---|---|
| Foundation | **Written.** Claims and liabilities, the Cartography of Wealth, time value, compounding, risk and return, inflation |
| Money & Liquidity | **Written.** What money is, the hierarchy, gold, central bank money, cash and fiat, bank deposits, eurodollars, liquidity, money creation |
| Human & Social Capital | Human capital, social capital |
| Fixed Income | T-bills, bonds, yield curve, duration |
| Equities | Shares, indices, funds and ETFs, valuation, private business |
| Real Assets | Real estate, REITs, commodities, collectibles |
| Digital Assets | Bitcoin, smart-contract platforms, stablecoins, memecoins, self-custody, custodial crypto |
| Derivatives | Futures, options, perpetuals, leverage |
| Portfolio & Risk | Diversification, correlation, allocation, sizing, rebalancing, market regimes |
| Markets & Plumbing | Exchanges, brokers, custody, settlement |
| Measure | Returns, drawdown, volatility, Sharpe ratio |
| In Practice | Tax, account types, common mistakes |
| Tools | Data sources, charting |

## Cross-cutting views

- **Flows:** built. First flow: *Where money comes from*.
- **Cartography of Wealth:** a page now; a dedicated view (the two-axis chart, filterable by tier and killer) is a later build.
- **Regimes:** a page for now (Market Regimes).
- **Quals:** live. Nine on the page from the start: CFA Levels I, II and III (core plus the Portfolio Management pathway), Mehrling's *Economics of Money and Banking*, FRM Parts I and II, CAIA Levels I and II, and Princeton's *Bitcoin and Cryptocurrency Technologies*. CFA I and Money & Banking are mapped; the rest are placeholders. Ethics modules are listed but out of scope. Left out on purpose: CMT (charting only), CFP (advice and planning), CIPM (too narrow), the CFA Level III Private Wealth and Private Markets pathways.
- **Jobs:** engine supports them; tab hidden until there is content.

## Engine changes from The Supply Map

- Rebranded shell (title, subtitle, welcome guide with two ways in).
- New optional page fields `tier`, `killer`, `traits`, rendered as a Cartography box.
- Branch colours for the new branch ids.
- T-code index hidden when no page has t-codes.
- Bug fix: the welcome guide's flow link was hard-coded to `p2p`; it now reads the flow from the link. **Worth back-porting to The Supply Map.**
- First-visit branch (`FIRST_VISIT_OPEN`) opens Money & Liquidity.
- New link-preview image (`assets/share.png`, 1200×630), rendered from an HTML template kept with the helper tools.
- Storage prefix stays `mudmap:` so the shared test suites run unchanged (different site, different browser storage, no clash).

## Open questions

1. **Geography:** global, or one country's rules for In Practice (tax, retirement accounts, account types)? Decide privately; the repo must not name the owner's country.
2. **T-codes:** drop for good, or repurpose for tickers or ISINs?
3. **Is a Jobs view worth it here,** or is a learning path enough?
4. **Launch gate:** the shared "public" test suite expects no stubs and Supply Map wording in About. It stays failing until we're ready to go public, then gets adapted.

## Decided since

- **Contact handle:** keep the Supply Map's approved public contact in `privacy.md`.
- **Commit identity:** all commits use the same public identity as The Supply Map. The first `SCOPE.md` commit on `main` predates this and still carries a personal address in its metadata; fixing it means rewriting `main`, which is the owner's call.
- **Hub standard:** written top-level branches follow the hub rules in the README, checked by the hubs test suite.
- **Access:** the site is open (no password or Zero Trust) but stays out of search engines: the `noindex` tag, `robots.txt` and `X-Robots-Tag` stay until the owner says otherwise.
- **Branch order:** Foundation → Fixed Income → Digital Assets → the Cartography view.

## Logistics parallel

Single parent plus many-to-many links is the material master pattern: one material group, many classifications. The Cartography fields are material classification characteristics (like hazard class or criticality): attributes on each item that later drive filters and risk views. The build step is a master-data load with validation rules.
