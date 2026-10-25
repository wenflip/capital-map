---
id: perpetuals
title: Perpetual Futures
parent: derivatives
order: 3
summary: Crypto futures with no expiry, held to the spot price by funding payments.
short: Perpetuals
level: advanced
sources: BitMEX, Five years ago the perpetual swap was born (2021)
---
## What it is
A **perpetual future** (or **perpetual swap**) is a futures-like contract with no expiry date, traded mainly on crypto exchanges. It lets traders hold a leveraged long or short position for as long as they like. The crypto exchange BitMEX introduced it in May 2016; perpetuals are now among the most traded contracts in crypto.

## Why it exists
Ordinary futures expire and must be rolled. A perpetual removes the roll, which suits round-the-clock crypto markets and traders who want simple, continuous exposure with leverage.

## How it works
**Funding payments** keep the contract's price close to the spot price. At regular intervals, often every eight hours:
- if the perpetual trades **above** spot, holders of long positions pay holders of short positions;
- if it trades **below** spot, shorts pay longs.

That payment makes it costly to push the price away from spot, so arbitrageurs pull it back.

**Fictional example:** a funding rate of 0.01% every eight hours on a 10,000 position is **1** per period. Three periods a day for a year adds up to **10.95%** a year. In euphoric markets funding can run much higher, which makes holding a leveraged long expensive.

## What goes wrong
- **Liquidation.** Exchanges close positions automatically when losses eat the margin, often in cascades that push prices further.
- **Funding costs** quietly drain long-held positions.
- **Exchange risk.** Positions sit on one exchange; its failure takes your margin with it. See [[custodial-crypto]].
- **Very high leverage** is routinely on offer, which turns ordinary moves into total losses.

> **Key rule:** a perpetual is leverage with a running cost. Check the funding rate and the liquidation price before opening one.

## Connects to
- [[futures]] — the contract a perpetual is built from.
- [[leverage]] — what makes perpetuals dangerous.
- [[digital-assets]] — where perpetuals mostly trade.

## Check yourself

**Q:** A perpetual trades above the spot price. Who pays funding, and why does that help?

**A:** Longs pay shorts. Paying to hold a long makes it less attractive, and being paid to hold a short makes that more attractive, which pushes the perpetual's price back towards spot.
