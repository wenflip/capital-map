---
id: digital-assets
title: Digital Assets
parent: capital-system
order: 4
group: What you can own
summary: Bearer assets and promises recorded on public ledgers: how blockchains work, native coins, tokens, bridges, DeFi, and how to hold them.
tags: digital assets, crypto
---
## What it is
**Digital assets** are units of value recorded on a **blockchain**: a shared ledger that many computers keep in agreement without a central owner. The branch covers the whole machine, from how the ledger stays honest to how people actually hold and use what's on it.

This map covers **concepts, not coins**. A few chains appear as reference examples because they define a category. Everything else is an instance of a concept explained here.

## Why it exists
Before blockchains, any digital money needed a trusted middleman to stop the same unit being spent twice. A blockchain replaces that middleman with rules that thousands of independent computers enforce. The result is a new kind of asset: one that can be **nobody's liability**, like gold, but moved across the world in minutes.

Not everything on a blockchain is like that. Many tokens are promises from a company, a bridge or a program. Telling the two apart is the most important skill in this branch.

## How it works
The branch runs from the machinery up to how you hold it:
- [[blockchains]] — ledgers, consensus, keys and forks: the machinery underneath everything else.
- [[native-coins]] — each chain's own coin, used to pay for the network: [[bitcoin]] and smart-contract platforms such as Ethereum.
- [[tokens]] — assets created by programs running on a chain: stablecoins, memecoins, governance tokens and wrapped tokens.
- [[bridges-and-layer-2s]] — how value moves between chains, and why that's the riskiest step.
- [[defi]] — exchanges, lending and staking run by code instead of companies.
- [[holding-crypto]] — holding your own keys or letting someone hold them for you.

**The two lenses this map uses fit crypto well:**

| Question | Native coin (bitcoin, ether) | Token (stablecoin, bridged coin) |
|---|---|---|
| Whose liability is it? | Nobody's | An issuer's, a bridge's, or a program's |
| What can kill it? | Protocol failure, lost keys | The issuer, bridge or contract failing |

## What goes wrong
| Failure | What it looks like |
|---|---|
| **Lost keys** | Coins still exist on the ledger, but nobody can ever move them |
| **Custodian failure** | An exchange holding your coins collapses; you become a creditor |
| **Bridge or contract hack** | A bug lets an attacker drain the funds backing a token |
| **De-peg** | A token meant to equal one dollar trades below it |
| **Same ticker, different asset** | A copied or bridged coin carries the same name as the original but is a different thing |
| **Liquidity drain** | When system liquidity falls, the most speculative tokens fall first and hardest |

> **Key rule:** for anything on a blockchain, ask two questions before anything else: is it a native coin or someone's token, and who holds the keys?

## Connects to
- [[hierarchy-of-money]] — stablecoins and wrapped coins as private promises high up the hierarchy.
- [[cartography-of-wealth|The Cartography of Wealth]] — self-custody sits in Tier 2, coins held on an exchange in Tier 3.
- [[claims-and-liabilities]] — the test that separates a native coin from a token.
- [[market-regimes]] — why crypto has often moved with high-growth tech shares.
- [[perpetuals]] — the crypto futures that drive much of the trading.

## Check yourself

**Q:** A coin on one chain and a token with the same name on another chain both trade under the same ticker. Are they the same asset?

**A:** Not necessarily. The token may be a bridged claim on the original, or a copy made by a fork. Each has its own killer: the original depends on its own network; a bridged token depends on the bridge; a forked copy depends on demand on the new chain.

**Q:** Why can bitcoin be nobody's liability while a dollar stablecoin can't?

**A:** Bitcoin is created by the network's own rules and isn't anyone's promise to pay. A dollar stablecoin is a promise by its issuer, or by a program, to be worth one dollar, so it depends on that promise being kept.

## Going deeper
- **Security budgets.** A public blockchain pays for its own security through new coins and fees. As new issuance shrinks over time, fees have to carry more of that cost. Whether they can is an open question for several chains.
- **Most of crypto's risk sits in the layers, not the base.** Base-layer protocols have proved hard to break; most large losses have come from exchanges, bridges and smart contracts built on top.
