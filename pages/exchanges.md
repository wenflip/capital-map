---
id: exchanges
title: Exchanges
parent: markets
order: 1
summary: Venues where buyers and sellers meet.
sources: SEC and CFTC, Findings Regarding the Market Events of May 6, 2010
---
## What it is
An **exchange** is a marketplace where buyers and sellers of shares, bonds, futures, options or crypto meet under a common set of rules. Well-known examples include the New York Stock Exchange, Nasdaq, the London Stock Exchange and futures exchanges such as CME.

## Why it exists
Bringing all buyers and sellers to one place makes it easier to find someone to trade with and to find a fair price. Exchanges also set listing rules for companies, publish prices, and supervise trading.

## How it works
**The order book.** Buy orders (**bids**) and sell orders (**asks**) are listed by price. A trade happens when a bid meets an ask.
- The gap between the highest bid and the lowest ask is the **spread**. A tight spread means a liquid market.
- A **market order** buys or sells immediately at the best available price.
- A **limit order** sets the worst price you'll accept, and waits until it can be filled.

**Market makers** post bids and asks all day, earning the spread in return for being ready to trade. They're why you can usually sell a large share in seconds. See [[market-making]].

**Fictional order book:**

| Bids (buyers) | Price | Asks (sellers) |
|---|---|---|
| | 100.20 | 500 shares |
| | 100.10 | 300 shares |
| 400 shares | 100.00 | |
| 600 shares | 99.90 | |

The spread is 0.10. A market order to buy 500 shares fills 300 at 100.10 and 200 at 100.20, so its average price is 100.14: bigger orders "walk the book".

## What goes wrong
- **Liquidity vanishes in stress.** Market makers step back, spreads widen and prices gap.
- **Flash crashes.** On 6 May 2010 US share prices plunged and rebounded within minutes. Exchanges now use **circuit breakers** that pause trading after very large moves.
- **Market orders in thin markets** can fill far from the last price.

> **Key rule:** in thin or fast markets, use limit orders, so you decide the worst price you'll accept.

## Connects to
- [[brokers]] — who sends your orders to the exchange.
- [[settlement]] — what happens after the trade.
- [[liquidity]] — what an exchange provides, and what can disappear.

## Check yourself

**Q:** The best bid is 50.00 and the best ask is 50.05. What is the spread, and what does a small market buy order pay?

**A:** The spread is 0.05, and a small market buy order pays 50.05, the lowest ask.
