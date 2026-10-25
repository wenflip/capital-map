---
id: settlement
title: Settlement
parent: markets
order: 4
summary: The moment a trade becomes final: money and asset swap hands, guaranteed by a clearing house.
sources: SEC, Shortening the Securities Transaction Settlement Cycle (2023)
---
## What it is
**Settlement** is the moment a trade becomes final: the buyer receives the asset and the seller receives the money. The trade itself happens in an instant; settlement follows a short time later. Most US share trades now settle one business day after the trade, called **T+1**. The US moved from two days to one on 28 May 2024.

## Why it exists
Between the trade and settlement, each side is exposed to the other failing to deliver. The settlement system exists to make that gap short and safe.

## How it works
**Clearing first.** A **central counterparty** (CCP), or clearing house, steps in between buyer and seller. It becomes the buyer to every seller and the seller to every buyer, so neither has to trust the other, only the clearing house.

**Netting.** The clearing house adds up each firm's trades and settles only the difference. Fictional example: broker X buys 1,000 shares of a company from broker Y in the morning and sells 700 back to Y in the afternoon. Instead of two deliveries, only **300** shares move, from Y to X.

**Margin.** Clearing members post collateral, sized by how risky their positions are. When markets swing wildly, those requirements can jump overnight.

**Delivery versus payment.** The asset and the money swap at the same time, so neither side can end up having handed over its half and received nothing.

## What goes wrong
- **Failed deliveries** when a seller can't produce the shares on time.
- **Margin spikes** that squeeze brokers and their customers in volatile markets. See [[brokers]].
- **Clearing house risk.** Concentrating risk in one firm makes that firm critical; clearing houses hold default funds and are closely regulated for this reason.
- **Faster isn't free.** Shorter settlement cuts risk but gives firms less time to fix errors, especially across time zones.

> **Key rule:** a trade isn't done until it's settled. The clearing house is what lets strangers trade without trusting each other.

## Connects to
- [[exchanges]] — where trades are made before they settle.
- [[custody]] — where settled assets are held.
- [[credit-risk]] — the counterparty risk settlement removes.

## Check yourself

**Q:** Why does a clearing house reduce risk for traders?

**A:** Because each trader only needs to trust the clearing house, which is well capitalised and holds collateral from every member, instead of trusting every other trader it deals with.
