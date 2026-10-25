---
id: derivatives
title: Derivatives
parent: capital-system
order: 8
group: Putting it together
summary: Contracts whose value depends on something else: futures, options, perpetuals and leverage.
sources: Fortune, How much big banks have lost from the Archegos collapse (27 April 2021)
---
## What it is
A **derivative** is a contract whose value depends on something else: the price of oil, a share, a currency, an interest rate or a coin. You don't own the underlying thing; you own a promise about it, made with someone on the other side.

## Why it exists
- **Hedging.** A farmer, an airline or a pension fund can lock in a price or cap a loss, moving a risk it doesn't want to someone willing to take it.
- **Speculation.** Traders can bet on a price moving, often with a small deposit controlling a large exposure.
- **Cheaper, faster exposure.** One contract can stand in for buying and storing the underlying asset.

Derivatives don't create or destroy risk overall. They move it from people who want less of it to people who want more.

## How it works
- [[futures]] — an agreement to buy or sell later at a price fixed now, traded on an exchange.
- [[options]] — the right, but not the duty, to buy or sell at a set price.
- [[leverage]] — how a small deposit controls a large position, and why that cuts both ways.

| | Futures | Options |
|---|---|---|
| **Obligation** | Both sides must complete | The buyer can walk away |
| **Upfront cost** | A deposit (margin) | A price (the premium) |
| **Most a buyer can lose** | Far more than the deposit | The premium |
| **Typical use** | Locking in a price | Insurance against a move |

**Zero-sum between the two sides.** Before costs, one side's gain on a derivative is the other side's loss. Value comes from the risk transferred, not from the contract itself.

## What goes wrong
- **Leverage.** Small price moves become large gains or losses on the deposit, and losses can exceed it.
- **Counterparty failure.** A contract is only as good as the side that must pay. Exchanges reduce this with a central clearing house; private contracts rely on collateral. See [[settlement]].
- **Hidden size.** In 2021 the family office Archegos built huge positions through banks using derivatives and borrowing. When its bets fell, banks lost more than $10 billion between them, and Credit Suisse alone about $5.5 billion.
- **Complexity.** Contracts that are hard to value are easy to misprice and hard to exit.

> **Key rule:** a derivative is a promise about a price. Know what you can lose, and who has to pay you if you win.

## Connects to
- [[commodities]] — the original home of futures.
- [[leverage]] — the feature that makes derivatives powerful and dangerous.
- [[credit-risk]] — the counterparty side of every contract.
- [[exchanges]] — where standard contracts trade.

## Check yourself

**Q:** An airline buys oil futures. Is it speculating?

**A:** No, it's hedging. It needs fuel anyway, so locking in the price removes a risk from its business instead of taking one on.

**Q:** Why can't derivatives make the economy as a whole less risky?

**A:** Because they move risk between parties rather than removing it. One side's protection is the other side's exposure.

## Going deeper
- [[perpetuals]] — crypto futures with no expiry date, kept close to the spot price by regular funding payments between the two sides.
- **Swaps.** Two parties exchange streams of payments, such as a fixed interest rate for a floating one. Most swaps are agreed privately between institutions, not on an exchange.
