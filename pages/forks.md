---
id: forks
title: Forks
parent: blockchains
order: 3
summary: When a blockchain's rules change, or its whole history is copied onto a new chain, and why a forked coin is a new asset with the old name.
tags: digital assets, blockchain, forks
---
## What it is
A **fork** is a change to a blockchain's rules, or a copy of its history onto a new chain. Because a blockchain's software is usually open source, anyone can copy it, and a whole ledger can be copied too.

## Why it exists
Forks are how open networks upgrade and how disagreements get settled. If a community can't agree on the rules, each side can run its own version.

## How it works
| Kind | What happens | Result |
|---|---|---|
| **Soft fork** | Rules get stricter; old software still accepts new blocks | One chain, upgraded |
| **Hard fork (agreed)** | Rules change in a way old software rejects, but nearly everyone upgrades | One chain, upgraded |
| **Contentious hard fork** | The community splits; both sides keep running | Two chains and two coins, sharing history up to the split |
| **Full-state copy** | A new chain starts from a snapshot of an existing chain's entire state | A new chain where every balance has a copy |

**Examples:**
- **Ethereum Classic (2016):** after a large theft from a smart contract called The DAO, Ethereum changed its history to reverse it. Those who opposed changing history kept the original chain, which became Ethereum Classic.
- **Bitcoin Cash (2017):** a split from Bitcoin over how large blocks should be.
- **PulseChain (2023):** launched from a snapshot of Ethereum's state, so holders of ether and Ethereum tokens found matching copies on the new chain.

## What goes wrong
**Same name, different asset.** After a fork, a coin or token can exist on both chains under the same ticker. They are separate assets with separate prices:
- A **copied coin** on the new chain is worth only what buyers there will pay.
- A **copied token** is not backed by its original issuer. A dollar stablecoin copied onto a fork is just a number on the new chain; the issuer only redeems the original.
- **Replay risk:** without protection, a transaction signed on one chain could also be valid on the other.

> **Key rule:** a fork creates new assets, not more of the old ones. Check which chain a coin lives on before you value it.

## Connects to
- [[wrapped-tokens]] — another way the same name ends up on a different chain.
- [[consensus]] — what the two sides of a split each have to secure afterwards.

## Check yourself

**Q:** You held a dollar stablecoin on Ethereum before a full-state copy launched. You now have the same balance on the new chain too. Do you have twice as many dollars?

**A:** No. The copy on the new chain isn't backed or redeemed by the issuer. It is a separate token, worth whatever the new chain's market will pay — possibly very little.
