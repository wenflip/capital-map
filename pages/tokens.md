---
id: tokens
title: Tokens
parent: digital-assets
order: 3
summary: Assets created by programs on a blockchain. What backs a token, and who can make it worthless, varies from one to the next.
tags: digital assets, tokens
---
## What it is
A **token** is an asset recorded inside a smart contract on a chain, rather than built into the chain's rules. Anyone can create one. The contract keeps the list of who holds how many.

## Why it matters
"Token" covers very different things. Some are claims on real dollars, some are copies of coins on other chains, and some are backed by nothing at all. The name and the ticker tell you nothing about which.

## How it works
| Kind | What it is | Whose liability? | Page |
|---|---|---|---|
| **Stablecoin** | A token meant to be worth one unit of a currency | The issuer's, or a program's | [[stablecoins]] |
| **Memecoin** | A token whose value is attention | Nobody's | [[memecoins]] |
| **Governance token** | A token that carries votes over a protocol | Nobody's, but tied to a protocol | [[governance-tokens]] |
| **Wrapped or bridged token** | A stand-in for a coin from somewhere else | The bridge's or custodian's | [[wrapped-tokens]] |

## What goes wrong
- **The contract can be changed** by whoever holds its admin keys, including minting more tokens or freezing balances.
- **Fake copies** use the same name and ticker. Only the contract address identifies the real one.
- **Liquidity can vanish:** a token you can't sell is worth little, whatever its quoted price.

> **Key rule:** a token is defined by its contract address, not its name. Check what backs it and who can change it.

## Check yourself

**Q:** Two tokens on the same chain have the same name and ticker. How can you tell which is real?

**A:** By the contract address. The issuer or project publishes the official address; anyone can create a token with the same name.
