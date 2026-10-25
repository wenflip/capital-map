---
id: clearing-house-failure
title: Clearing House Failure
short: Clearing House Failure
parent: failure-modes
order: 3
summary: When the central counterparty that guarantees every trade runs short: default funds, rescues, and cancelled trades.
tags: failure, clearing, derivatives, market structure
sources: Securities and Futures Commission (Hong Kong), background chapter 2 (1987 crash); Clarus Financial Technology, Default at Nasdaq Clearing (2018); LME Nickel
---
## What fails
A **clearing house** (central counterparty, or CCP) stands between every buyer and seller, so that neither has to trust the other. See [[settlement]]. If a large member defaults and its losses exceed what the clearing house holds, the guarantee behind every trade on that market is in doubt.

## The backstop
A **default waterfall**, used in order:
1. The defaulter's own **margin**.
2. The defaulter's contribution to the **default fund**.
3. A slice of the clearing house's **own capital**.
4. **Other members' contributions** to the default fund, then calls on members for more.

Clearing houses are tightly regulated because so much risk sits in them.

## Where the backstop runs out
- **Mutualised losses.** When the defaulter's money runs out, honest members pay for its losses.
- **Extreme moves** can exceed every layer of the waterfall.
- **Rule changes under stress.** An exchange can halt trading or cancel trades, protecting the system at the cost of whoever was on the right side of them.

## Cases
- **Hong Kong, October 1987.** After the world crash, the stock and futures exchanges closed for four days from 20 October. The guarantor of futures contracts had about HK$22.5 million of capital and reserves against far larger defaults. The government, brokers and banks put together a HK$2 billion rescue loan, with HK$1 billion from the government's Exchange Fund.
- **Nasdaq Clearing, September 2018.** A single power trader couldn't meet margin calls. Closing his positions cost about €114 million. Over two-thirds of the €166 million default fund was used, mostly other members' money, and members were asked to top it up.
- **London Metal Exchange, March 2022.** Nickel more than doubled to over $100,000 a tonne. The exchange suspended trading and cancelled trades made that morning, about $3.9 billion of them. UK courts later upheld its authority to do so.

## What it kills
Positions in [[futures]], [[options]] and other cleared contracts, and margin held at the clearing house. Because [[shares]] and [[bonds]] trades also settle through clearing houses, a failure would freeze trading far beyond derivatives.

> **Key rule:** a clearing house turns many small counterparty risks into one large one. It's well protected, but in a crisis its rules, including halts and cancellations, decide who bears the loss.

## Check yourself

**Q:** In the Nasdaq Clearing default, why did other members lose money?

**A:** Because the defaulter's own margin and contribution weren't enough, so the default fund, mostly paid in by other members, covered the rest.

**Q:** The LME cancelled nickel trades in 2022. Who gained and who lost?

**A:** Holders of large short positions facing huge losses were spared. Traders who had bought or sold at the cancelled prices lost the profits those trades would have made.
