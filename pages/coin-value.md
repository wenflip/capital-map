---
id: coin-value
title: What Gives a Coin Value
short: Coin Value
parent: digital-assets
order: 2.5
summary: A coin that is nobody's liability has no issuer to pay you. Its value rests on two things at once: being a well-built asset, and a crowd that wants it.
tags: digital assets, value, network effects, sound money
sources: Study notes; Ethereum Classic, The DAO Hard Fork Completed (20 July 2016); Bitcoin Cash fork (1 August 2017)
---
## What it is
A bond is worth what its issuer will pay. A coin such as [[bitcoin]] or a [[memecoins|memecoin]] has no issuer: it's [[claims-and-liabilities|nobody's liability]]. So where does its value come from?

Not from the code, because code is free to copy. Anyone can launch an identical chain tomorrow. What the copy can't take with it is the reason people valued the original, and that reason has two parts:

| Part | The question | Page |
|---|---|---|
| **The asset** | Is it well built: a supply no one can quietly inflate or hoard, a chain no one can seize, legal to hold, easy to trade? | [[sound-money]] |
| **The crowd** | Do people use it, expect everyone else to keep using it, and stay through bad times? | [[network-effects]] |

## Why it matters
- **Both parts are needed.** A well-built coin that nobody uses is worth little. So is a popular coin whose supply sits with a handful of insiders ready to sell. The weaker part sets the limit: think weakest link, not average.
- **It explains why copies are worth less.** Two chains can share every line of code and still be worth very different amounts.
- **It says what to look at besides the price.** A price can rise for many reasons. These two parts are why a price holds, or doesn't.

## How it works
**The copy test.** When a chain is copied, the copy gets the same code and often the same history. It doesn't automatically get the crowd. See [[forks]].
- **Bitcoin Cash.** On 1 August 2017 a group split from Bitcoin to allow larger blocks. Both chains kept running and both kept the shared history, but most users, miners and money stayed with the original. The copy has remained a far smaller network.
- **Ethereum and Ethereum Classic.** In 2016 a flaw in The DAO, a large program running on Ethereum, let an attacker drain about $50 million of ether. On 20 July 2016 Ethereum changed its own history to return the funds, and about 85% of miners went with the change. Those who refused kept the original, unchanged chain, which carried on as Ethereum Classic. The same code became two coins, and value followed the larger crowd.

**What the model covers.** It applies to assets that are nobody's liability: native coins and memecoins. It doesn't apply to a [[stablecoins|stablecoin]], which is worth what its issuer will redeem it for, or a [[wrapped-tokens|wrapped token]], which is worth what its custodian holds. Their value comes from a claim, so ask the claim's questions instead.

## What goes wrong
- **Valuing the code.** Clever technology that anyone can copy isn't, by itself, a reason for a coin to hold value.
- **Reading the crowd from the price.** A rising price can be a momentum loop rather than real users. See [[network-effects]].
- **Ignoring the weaker part.** A strong crowd doesn't fix a supply held by insiders, and a perfect design doesn't create users.

> **Key rule:** a coin that nobody owes you is worth what a crowd will pay for a well-built asset. Check both parts, and judge it by the weaker one.

## Connects to
- [[sound-money]] and [[network-effects]] — the two parts, four questions each.
- [[claims-and-liabilities]] — why "nobody's liability" means value must come from somewhere else.
- [[four-ways-to-earn]] — a coin that isn't lent or staked earns only through price and risk.
- [[gold]] — the oldest asset that is nobody's liability, held up by the same two parts.

## Check yourself

**Q:** A developer copies a popular coin's code exactly and launches a new chain with the same rules. Why isn't the copy worth the same?

**A:** It has the code but not the crowd. Users, exchanges and developers still expect each other to stay with the original, so the copy starts with almost no network behind it, however well it's built.

**Q:** Coin A has a fixed supply and a careful design but almost no users. Coin B is hugely popular, but its founders hold 80% of the supply. Which part is each missing?

**A:** Coin A is missing the crowd (network effects). Coin B fails the asset test (sound money), because its founders can sell into any demand. Either weakness can take a coin close to zero.

## Going deeper
- **Gold fits the same model.** It's scarce, durable and hard to fake (the asset), and it has been accepted by convention for thousands of years (the crowd). See [[what-is-money]].
- **A way of thinking, not a formula.** "Value needs the asset *and* the crowd" is the point. Neither part can be measured precisely, and multiplying scores together would give a false sense of precision.
