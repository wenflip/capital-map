# The Capital Map — Scope

*Status: scoping. No code yet. Last updated 2026-10-25.*

## What it is

A free, independent reference map of finance and investing: money, markets and assets (cash, bonds, stocks, real estate, commodities and gold, crypto) in one connected, clickable tree. It is the sibling of **The Supply Map** (`wenflip/logistics-mud-map`, thesupplymap.pages.dev).

Working subtitle: *Money · Markets · Assets*

Education only. Not financial advice.

## Decisions so far

1. **Name:** The Capital Map. Repo: `capital-map`.
2. **Reuse the Supply Map engine.** Content is Markdown files in `pages/`, `flows/`, `jobs/` and `quals/`. A build step validates them (one root, one parent per page, no cycles) and generates the site. Most of the work is content and taxonomy, not code.
3. **The tree is organised by structure, not behaviour.**
   - *Structure* is what an asset **is**: whose liability, and a claim on what. It is stable.
   - *Behaviour* is how it **trades right now** (e.g. "crypto trades like high-beta tech"). It changes with the liquidity regime, so it lives in a cross-cutting view, not the tree.
4. **Organising question for money:** "whose liability is it, and what is it a claim on?" Not "backed vs unbacked". References: Perry Mehrling's *hierarchy of money*; John Exter's *inverted pyramid*.
5. **One primary parent per page, plus `[[links]]` for everything else.** For example, gold's home is in one branch and it is linked from the other. This is the same model the Supply Map already uses.

## Draft top-level branches (v0, for discussion)

| Branch | Covers |
|---|---|
| Foundation | Money, time value, compounding, risk vs return, inflation |
| Money & Liquidity | The hierarchy: gold → central bank money → bank deposits → stablecoins → eurodollars; central bank balance sheets, liquidity |
| Cash & Fixed Income | T-bills, government and corporate bonds, the yield curve |
| Equities | Stocks, indices, ETFs, sectors, valuation |
| Real Assets | Real estate (direct, REITs), commodities, gold as a commodity |
| Digital Assets | Bitcoin, smart-contract platforms, stablecoins, memecoins |
| Derivatives | Futures, options, perpetuals, leverage |
| Portfolio & Risk | Allocation, diversification, correlation, position sizing |
| Markets & Plumbing | Exchanges, brokers, custody, settlement, on-chain vs off-chain |
| Measure | Returns, drawdown, volatility, Sharpe |
| In Practice | Tax, account types, common mistakes, case studies |
| Tools | Data sources, charting, screeners, our own bots |

## Cross-cutting views (equivalents of Flows / Jobs / Quals)

- **Regimes:** risk-on/off, liquidity cycles, why correlations shift.
- **Flows:** how money moves (central bank → banks → markets; fiat on-ramp → exchange → wallet).
- **Jobs:** a finance career ladder (to be defined).
- **Quals:** CFA Levels I–III as the reference curriculum to cross-check coverage against.

## Open questions

1. **Spine:** object spine (asset classes, as above) or process spine (Goals → Research → Allocate → Execute → Monitor → Exit), the way the Supply Map uses SCOR?
2. **Geography:** global, or Australia-specific for In Practice (tax, super, account types)?
3. **The t-code index has no finance equivalent.** Drop it, or repurpose it for tickers or ISINs?
4. **Is a Jobs view worth it here,** or is a learning path enough?

## Logistics parallel

Single parent plus many-to-many links is the material master pattern: one material group, many classifications. The build step is a master-data load with validation rules.
