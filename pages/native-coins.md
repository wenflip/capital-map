---
id: native-coins
title: Native Coins
parent: digital-assets
order: 2
summary: Each chain's own coin, built into its rules and used to pay for the network. Nobody's liability.
tags: digital assets, native coins
---
## What it is
A **native coin** is the currency built into a blockchain's own rules: bitcoin on Bitcoin, ether on Ethereum, and so on. It is created by the protocol itself, not issued by a company.

## Why it exists
Native coins do two jobs:
- **Pay for the network.** Every transaction pays a fee in the native coin.
- **Pay for security.** Miners or validators are rewarded in it, which is what makes attacking the chain expensive.

## How it works
Two reference examples cover the main designs:
- [[bitcoin]] — a fixed-supply coin on a deliberately simple chain, secured by proof of work.
- [[smart-contract-platforms]] — chains such as Ethereum that run programs, where the native coin pays for computation.

| Native coin | Token |
|---|---|
| Built into the chain's rules | Created by a program running on the chain |
| Pays fees and security | Pays fees *in* the native coin |
| Nobody's liability | Often someone's promise |

## What goes wrong
- **Protocol risk:** a flaw in the chain's rules or a loss of security.
- **Issuance changes:** some chains can change how many new coins are created.
- **No cash flow:** a native coin pays nothing just for being held, unless it is staked.

> **Key rule:** a native coin is the one asset on a chain that isn't somebody's promise. Everything else built on top adds a party that can fail.

## Check yourself

**Q:** Why does every transaction on Ethereum need some ether, even when you are only moving a different token?

**A:** Because fees are paid in the native coin. The token runs on Ethereum, and Ethereum charges for the computation in ether.
