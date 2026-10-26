---
id: exchange-rates
title: Currencies and Exchange Rates
short: Exchange Rates
parent: money
order: 5.5
summary: The price of one currency in another: how it is quoted, who sets it, what moves it, and what it does to anything you own abroad.
tags: money, currency, fx, forex, exchange rate, peg
sources: Bank for International Settlements, Triennial Central Bank Survey of FX and OTC derivatives markets (September 2025); Thomas Jordan, Swiss National Bank, The rationale for discontinuing the minimum exchange rate (15 January 2015); Econlib, Wednesday, Black and White; Borio, McCauley, McGuire and Sushko, Covered interest parity lost (BIS Quarterly Review, September 2016)
---
## What it is
An **exchange rate** is the price of one currency in another. Every country's [[cash-and-fiat|fiat currency]] is valued in its own units at home, so the moment money crosses a border, someone has to swap one promise for another. The market where that happens is the **foreign exchange** market, usually called **FX** or forex.

Rates are quoted as **pairs**. A quote of EUR/USD = 1.25 (an illustrative figure, not a real rate) means one euro costs 1.25 US dollars. The first currency is the one being priced; the second is the one you pay in. Turn it round and one dollar costs 1 ÷ 1.25 = **0.80** euros. Most confusion about "the dollar going up" comes from reading a pair the wrong way round.

By daily trading, it is the largest market in finance. The Bank for International Settlements' survey of April 2025 put FX trading at about **$9.6 trillion a day**, with the US dollar on one side of **89%** of all trades.

## Why it matters
- **Trade.** A firm that sells abroad is paid in one currency and pays its workers in another.
- **Investing abroad.** A foreign share or bond carries two risks at once: the asset's own, and the currency it is priced in.
- **Borrowing.** A loan in a foreign currency must be repaid in that currency, whatever happens to the one you earn in.
- **Your purchasing power.** Imported goods, fuel and holidays get dearer when your currency falls.

## How it works
**Who sets the rate.** Each country chooses a regime:

| Regime | How it works | The trade-off |
|---|---|---|
| **Floating** | The market sets the rate, minute by minute | The rate can swing a lot, but the central bank keeps control of its own interest rates |
| **Managed** | The market sets it, but the central bank leans against big moves | A middle path; the limits are never fully clear |
| **Pegged** | The central bank promises a fixed rate to another currency | Stable while it lasts, but interest rates must follow the anchor country's, and the promise can break |

To hold a peg, a central bank buys its own currency with **foreign reserves** when it is under pressure, and raises interest rates to make holding it more attractive. Both have limits. Reserves run out, and very high rates hurt the economy.

**What moves a floating rate.** Several forces at once, which is why short-term moves are hard to predict:
- **Interest-rate gaps.** Higher rates attract money, at least for a while.
- **Inflation gaps.** Over long periods, a currency that loses buying power faster at home tends to lose value abroad too. See [[inflation]].
- **Trade and investment flows.** Exporters selling foreign earnings, and foreigners buying local assets, both add demand.
- **Fear.** In a panic, money runs to the currencies at the top of the [[hierarchy-of-money|hierarchy of money]], above all the dollar, which many borrowers worldwide owe. See [[eurodollars]].

**What a currency move does to your return.** Returns multiply; they don't add. Say you own a fund of foreign shares that rises 8% in its own currency in a year, while that currency falls 5% against yours (fictional figures):

1.08 × 0.95 = 1.026, so you made **2.6%**, not the 8% the fund reports.

If the currency had risen 5% instead: 1.08 × 1.05 = 1.134, so you made **13.4%**. The same fund, in the same year, gives two owners in two countries two different results.

**The forward rate.** You can fix a rate now for a swap on a future date. This **forward** rate is not a forecast. It is set by the gap in interest rates, because otherwise traders could borrow in one currency, lend in the other, lock in the forward and earn a riskless profit. Say one unit of currency A costs 1.20 of currency B, one-year interest is 2% in A and 5% in B (fictional figures):

forward = 1.20 × 1.05 ÷ 1.02 = **1.235**

The higher-rate currency, B, buys less in the forward than it does now, which exactly offsets its higher interest. **Hedging** with forwards removes the currency swing, but it also gives up, or pays, that interest gap. See [[futures]] for the same idea on other assets.

## What goes wrong
- **Pegs break, and suddenly.** A peg looks stable right up to the day it goes:
  - **United Kingdom, 16 September 1992.** The government raised interest rates twice in one day to keep the pound inside the European Exchange Rate Mechanism, then left it that evening. The pound fell.
  - **Switzerland, 15 January 2015.** The opposite direction: the Swiss National Bank had capped the franc's rise at 1.20 to the euro, and dropped the cap with immediate effect. The franc rose sharply.
- **Borrowing in one currency, earning in another.** When the earning currency falls, the debt grows in the money that pays for it. Households, firms and whole countries have been caught this way. See [[sovereign-default]].
- **The carry trade.** Borrowing in a low-rate currency to hold a high-rate one earns the interest gap while rates are calm. The losses tend to come together, in a rush, when the high-rate currency falls and everyone unwinds at once.
- **Hidden exposure.** A fund of foreign assets is a currency position too, whether or not its name says so.
- **Controls.** In a crisis, governments can limit buying foreign currency at all. See [[capital-controls]] and [[currency-failure]].

> **Key rule:** whenever you own anything abroad, ask which currency it is priced in, which currency you will spend, and what happens to your return if the two move apart.

## Connects to
- [[cash-and-fiat]] — the currencies being exchanged.
- [[hierarchy-of-money]] — why some currencies are wanted in a crisis and others are sold.
- [[eurodollars]] — the dollars owed outside the United States, and the demand they create.
- [[currency-failure]] — the far end: when a currency stops working at all.
- [[capital-controls]] — when the state blocks the exchange.
- [[diversification]] — currency is a layer of risk that a spread of assets can share.

## Check yourself

**Q:** A foreign fund rises 10% in its own currency, while that currency falls 10% against yours. Did you break even?

**A:** No. Returns multiply: 1.10 × 0.90 = 0.99, so you lost **1%**. A rise and a fall of the same size never cancel exactly.

**Q:** A central bank can defend its currency against rising more easily than against falling. Why?

**A:** To stop a rise, it sells its own currency, which it can create without limit. To stop a fall, it must buy its own currency with foreign reserves, which run out. Even so, a cap on a rise can be abandoned, as Switzerland showed in 2015.

## Going deeper
- **Covered interest parity** is the formal name for the forward-rate rule above. Before the 2007–09 financial crisis it held so closely it was treated almost as a law; since then it has been broken persistently. Research at the BIS links the gap to heavy demand for currency hedging and tighter limits on how much banks can arbitrage it away.
- **FX swaps** pair a spot swap with a forward one (see [[swaps]]), and were the most-traded FX instrument in the 2025 survey, at about 31% of turnover. Much of the offshore dollar system is funded this way.
- **Cross rates and arbitrage.** If EUR/USD, USD/JPY and EUR/JPY don't line up, a trader can go round the triangle for a profit, so in practice the three stay consistent.
- **Purchasing power parity** says that, over the long run, rates should move towards the level where the same basket costs the same everywhere. It explains long trends far better than it explains any one year.
