---
id: blockchains
title: How Blockchains Work
short: How blockchains work
parent: digital-assets
order: 1
summary: A shared ledger kept in agreement by many computers: the machinery under every digital asset.
tags: digital assets, blockchain
---
## What it is
A **blockchain** is a ledger of transactions grouped into blocks. Each block points to the one before it, so the history forms a chain that is very hard to alter. Thousands of computers (**nodes**) keep their own copy and check every new block against the same rules.

## Why it exists
A digital file can be copied endlessly, so digital money needs a way to stop the same unit being spent twice. Traditionally a bank's ledger does that. A blockchain does it without a single owner: the network agrees on one history, and anyone can check it.

## How it works
Three ideas explain almost everything:
- [[consensus]] — how thousands of strangers agree on one history, and what it costs to cheat.
- [[keys-and-wallets]] — what you actually own: a secret key that lets you move coins recorded on the ledger.
- [[forks]] — what happens when the rules change, or someone copies the whole ledger onto a new chain.
- [[privacy-and-traceability]] — why a public ledger is pseudonymous, not anonymous, and how coins get linked back to people.

| Part | What it does |
|---|---|
| Transactions | Signed instructions to move coins or call a program |
| Blocks | Batches of transactions, each linked to the one before |
| Nodes | Computers that keep a copy and check the rules |
| Consensus | The method for deciding which new block is accepted |

## What goes wrong
- **Weak consensus.** A small network can be attacked by anyone who controls enough mining power or stake.
- **Bugs in the rules.** Software errors in the protocol itself are rare on large chains but possible.
- **Centralised control.** If a few parties run most of the nodes or validators, the network can be pressured or halted.

> **Key rule:** a blockchain is only as trustless as its consensus is expensive to attack and widely spread.

## Check yourself

**Q:** What problem does a blockchain solve that a simple shared spreadsheet doesn't?

**A:** It lets strangers agree on one history without trusting any single keeper, and it makes rewriting that history very expensive, which stops the same coin being spent twice.
