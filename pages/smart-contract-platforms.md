---
id: smart-contract-platforms
title: Smart-Contract Platforms
short: Smart contracts
parent: native-coins
order: 2
summary: Blockchains that run programs, with Ethereum as the reference example: the base layer for tokens and DeFi.
tags: digital assets, ethereum, smart contracts, native coins
---
## What it is
A **smart-contract platform** is a blockchain that runs programs (**smart contracts**) as well as moving coins. **Ethereum**, launched in 2015, is the reference example; many other chains copy or compete with its design.

## Why it matters
Programs on a shared ledger let people create new assets and services without a company in the middle: [[tokens]], exchanges and lending markets (see [[defi]]). The platform's native coin, **ether** on Ethereum, pays for the computation.

## How it works
- **Gas.** Every step a program takes costs a fee, paid in the native coin. Busy periods push fees up.
- **Token standards.** Shared rules (such as ERC-20 for ordinary tokens on Ethereum) let any wallet or exchange handle any token that follows them.
- **Proof of stake.** Ethereum switched from proof of work to proof of stake in September 2022. See [[consensus]].
- **No fixed cap.** Unlike bitcoin, ether has no maximum supply. New ether is issued to validators, and part of every fee is destroyed ("burned"), so supply can rise or fall.
- **Copies and rivals.** Because the code is open, other chains run compatible software, and some started as full copies of Ethereum. See [[forks]].

## What goes wrong
- **Bugs in contracts:** the platform can be sound while a program on it is broken.
- **High fees** price out small users when the network is busy, which pushed activity onto [[bridges-and-layer-2s|layer 2s]] and other chains.
- **Complexity:** more features mean more ways to fail than a simpler chain.

> **Key rule:** the platform and the programs on it are separate risks. A safe chain can host an unsafe contract.

## Check yourself

**Q:** Why can ether's supply fall even though new ether is issued to validators?

**A:** Because part of every transaction fee is burned. When activity is high enough, more ether is burned than issued.
