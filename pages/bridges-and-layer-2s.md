---
id: bridges-and-layer-2s
title: Bridges and Layer 2s
parent: digital-assets
order: 4
summary: How value moves between chains and onto faster networks built on top, and why bridges have been crypto's weakest link.
tags: digital assets, bridges, layer 2
---
## What it is
- A **bridge** moves value between two separate blockchains. Usually it locks coins on one chain and issues matching [[wrapped-tokens]] on the other.
- A **layer 2** is a faster, cheaper network built on top of a main chain (the **layer 1**). It processes transactions itself and periodically settles a summary back to the main chain.

## Why it exists
Each blockchain is its own closed ledger: coins can't simply move from one to another. Main chains like Ethereum also become slow and expensive when busy. Bridges connect chains; layer 2s add capacity.

## How it works
**Bridges** mostly work by *lock and mint*:
1. You send coins to the bridge on chain A, where they are locked.
2. The bridge issues the same amount of wrapped tokens on chain B.
3. To go back, the wrapped tokens are destroyed and the originals released.

Everything depends on who controls the locked coins: a small group of signers, a set of validators, or a contract.

**Layer 2s** often use **rollups**: they bundle many transactions together and post them, or proof of them, to the main chain. Two main designs:
- **Optimistic rollups** assume transactions are valid unless someone challenges them, so withdrawals to the main chain can take days.
- **Zero-knowledge rollups** post a mathematical proof that the transactions are valid, which allows faster withdrawals but is harder to build.

## What goes wrong
- **Bridge hacks.** A bridge is one big pile of locked coins, which makes it a target. Some of the largest crypto thefts have been bridge hacks; in 2022 alone, attacks on Ronin, Wormhole and Nomad each took hundreds of millions of dollars.
- **Few signers.** Many bridges rely on a handful of keys; stealing enough of them unlocks everything.
- **Centralised layer 2s.** Many layer 2s still rely on a single operator to order transactions and have upgrade keys that can change the rules.

> **Key rule:** every bridge adds a party that can fail. Count the hops between you and the original coin.

## Connects to
- [[smart-contract-platforms]] — the main chains that layer 2s extend.
- [[wrapped-tokens]] — what bridges issue.

## Check yourself

**Q:** Why is a bridge a more attractive target for attackers than a single user's wallet?

**A:** Because it holds the locked originals for everyone who has bridged. Breaking one bridge can unlock all of them at once.
