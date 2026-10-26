---
id: sound-money
title: Sound Money
parent: coin-value
order: 1
summary: The asset half of a coin's value: a supply no one can quietly expand or hoard, a chain no one can seize, legal standing, and a market deep enough to trade.
tags: digital assets, sound money, supply, security
sources: Study notes; The Block, Ethereum Classic suffers another 51% attack in five days (6 August 2020); AP via OPB, China says all crypto transactions illegal (24 September 2021)
---
## What it is
**Sound money** is money whose value can't be eroded by someone else's choice. For a coin, it's the asset half of [[coin-value|what gives a coin value]]: whether the coin is well built, whoever happens to want it. Four things decide it:

| | The question | When it fails |
|---|---|---|
| **1. Supply** | Are the issuance rules fixed or predictable, and who holds the coins? | New coins are created at will, or most of the supply sits with insiders who can sell |
| **2. Security** | Can any single party seize, censor or rewrite the chain? | An attacker with most of the mining or staking power rewrites recent history |
| **3. Legal standing** | Can it be held and traded where its users live? | A ban or a delisting cuts off buyers overnight |
| **4. Liquidity and access** | Can people get in and out without moving the price? | A thin market, where one large sale crashes the price |

## Why it matters
Each failure hands the coin's value to someone other than its holders: whoever can issue more, the insiders who can sell, an attacker, a government, or the last buyer standing. A sound coin is one where none of them can decide what yours is worth.

## How it works
### 1. Supply
- **Issuance.** The rules for creating new coins sit in the protocol. [[bitcoin]], for example, allows no more than 21 million. A coin whose supply a team or a vote can raise is closer to a currency managed by its issuer.
- **Distribution.** Who holds the coins matters as much as how many exist. If a few wallets hold most of the supply, they can sell into every rise. On a public chain this is visible: anyone can look up the largest holders.

### 2. Security
- **The cost of an attack.** A chain is secure when taking control of most of its mining or staking power costs more than an attack could gain. See [[consensus]].
- **Small chains are cheaper to attack,** especially if they share a mining method with a much larger chain whose miners can rent out their power. **Ethereum Classic** suffered majority attacks on 1 and 6 August 2020. In the first, about 807,000 ETC were spent twice, and exchanges paused deposits.
- **Neutrality.** No single party should be able to block transactions it dislikes. A chain that can be censored puts its users at someone's mercy.

### 3. Legal standing
- **Bans and restrictions.** On 24 September 2021 China's central bank declared all crypto transactions illegal. A ban doesn't change a coin's code, but it removes buyers and businesses in that country at a stroke.
- **Delistings.** When major [[exchanges]] stop trading a coin, the easiest way in and out closes, even where holding it stays legal.

### 4. Liquidity and access
- **Depth.** A deep market absorbs large orders with a small move in price; a thin one doesn't. See [[liquidity]].
- **On-ramps.** Most buyers arrive through exchanges and [[custodial-crypto|custodians]]. A coin that's hard to buy has fewer buyers, however good its design.

## What goes wrong
- **Trusting a supply cap without checking who holds the supply.** A fixed total is no protection if a few holders can sell most of it.
- **Assuming a copy is as secure as the original.** A copied chain has the same code but a fraction of the security behind it.
- **Liquidity that only exists in good times.** Markets that look deep in a rally can thin out fast in a fall.

> **Key rule:** a sound coin is one where no issuer, insider, attacker or government can decide what yours is worth. Check all four before trusting any one.

## Connects to
- [[network-effects]] — the other half: the crowd.
- [[consensus]] — how chains are secured, and what an attack costs.
- [[privacy-and-traceability]] — why holdings on a public chain can be inspected.
- [[capital-controls]] — when the state restricts what you can do with money.

## Check yourself

**Q:** A coin has a hard cap of 1 billion, but five wallets belonging to its founders hold 70% of the supply. Is its supply sound?

**A:** The cap is, but the distribution isn't. Those five wallets can sell into any demand, so the holders who bought from them carry the risk.

**Q:** Why can a small chain that uses the same mining method as a much larger one be cheap to attack?

**A:** Because miners from the large chain can redirect, or rent out, a small fraction of their power and still control most of the small chain's. That's how Ethereum Classic was attacked twice in August 2020.

## Going deeper
- **A cap is only as firm as its community.** Supply rules are code, and code can be changed by a [[forks|fork]]. The rules hold because enough users would refuse a chain that broke them. That's where the asset half meets the crowd half. See [[network-effects]].
