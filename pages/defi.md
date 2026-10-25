---
id: defi
title: DeFi: Decentralised Finance
short: DeFi
parent: digital-assets
order: 5
summary: Exchanges, lending and staking run by smart contracts instead of companies — and where the yield actually comes from.
tags: digital assets, defi, yield
---
## What it is
**DeFi** (decentralised finance) means financial services built as [[smart-contract-platforms|smart contracts]]: trading, lending and earning a return, with no company holding your funds in between. You connect a wallet and deal with the program directly.

## Why it exists
DeFi lets anyone with a wallet trade, lend or borrow at any hour, and lets new financial products be built by combining existing programs, like building blocks.

## How it works
| Service | How it works | Where the return comes from |
|---|---|---|
| **Decentralised exchange** | Traders swap against a pool of two tokens supplied by liquidity providers; a formula sets the price | Trading fees paid to the pool |
| **Lending market** | Borrowers lock more collateral than they borrow; if its value falls too far, it is sold automatically (**liquidation**) | Interest paid by borrowers |
| **Staking** | Locking a chain's coin to help run [[consensus]] | New coins and fees paid by the network |
| **Liquid staking** | Staking through a protocol that gives you a token representing your stake | The staking reward, minus the protocol's cut |

**Ask where the yield comes from.** Real yield comes from someone paying: traders, borrowers or the network. If a return is high and nobody can explain who is paying it, it is often paid in newly created tokens, or by later depositors.

## What goes wrong
- **Smart-contract bugs:** the code holds the money, so a bug can drain it.
- **Oracle manipulation:** programs need outside prices; feeding them false prices can trigger wrong liquidations or let attackers borrow too much.
- **Admin keys:** many "decentralised" protocols can still be changed or paused by a small team.
- **Impermanent loss:** liquidity providers can end up worse off than if they had simply held the two tokens, when prices move a lot.
- **Liquidation cascades:** a falling price triggers forced sales, which push the price lower and trigger more.

> **Key rule:** if you can't see who is paying the yield, assume you are.

## Connects to
- [[governance-tokens]] — how many DeFi protocols are run.
- [[leverage]] — borrowing against crypto magnifies both gains and liquidations.

## Check yourself

**Q:** A lending protocol offers depositors 3% while borrowers pay 5%. Where does the 2% go, and where does the depositors' 3% come from?

**A:** The depositors' 3% comes from the interest borrowers pay. The gap covers the protocol's cut and a buffer for bad loans.

**Q:** Why can a sharp price fall cause a liquidation cascade?

**A:** Falling collateral values trigger automatic sales, which push prices down further, which triggers more liquidations.
