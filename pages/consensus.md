---
id: consensus
title: Consensus: Proof of Work and Proof of Stake
short: Consensus
parent: blockchains
order: 1
summary: How a blockchain's computers agree on one history: proof of work, proof of stake, and what it costs to cheat.
tags: digital assets, blockchain, consensus
---
## What it is
**Consensus** is the method a blockchain uses to decide which new block is added, so that every node ends up with the same history. The two main methods are **proof of work** and **proof of stake**.

## Why it exists
Anyone can join a public network, including attackers. Consensus makes adding blocks costly, so that cheating costs more than it could earn.

## How it works
| | Proof of work | Proof of stake |
|---|---|---|
| Who adds blocks | **Miners**, who race to solve a hard computing puzzle | **Validators**, who lock up (stake) the chain's coin |
| What it costs to take part | Hardware and electricity | Capital tied up in the stake |
| Punishment for cheating | Wasted electricity on rejected blocks | Part of the stake can be destroyed ("slashing") |
| Main example | [[bitcoin]] | Ethereum, since its switch in September 2022 (see [[smart-contract-platforms]]) |

**Ethereum's switch.** In September 2022 Ethereum moved from proof of work to proof of stake, an upgrade known as *the Merge*. The Ethereum project estimates this cut the network's energy use by more than 99.9%.

## What goes wrong
- **A 51% attack.** Whoever controls most of the mining power, or most of the stake, can reorder recent transactions and spend coins twice. On large networks this is very expensive; on small ones it has happened.
- **Concentration.** Mining pools and large staking providers can end up controlling a big share of a network.
- **Proof of stake rewards the already-rich**, critics argue, because staking rewards go to those who already hold coins. Supporters reply that proof of work favours those with cheap electricity and hardware.

> **Key rule:** a chain's security is the cost of attacking it. Ask how much it would cost to control most of its mining power or stake.

## Check yourself

**Q:** Why is a 51% attack far harder on a large network than on a small one?

**A:** Because the attacker has to control more mining power or stake than everyone else combined. On a large network that costs far more than the attack could usually earn.

## Going deeper
- **Finality.** On a proof-of-work chain, a payment becomes more certain with every block added on top, but is never absolutely final. Many proof-of-stake chains add a point after which a block is final unless a large share of stake is destroyed.
- **Delegation.** On many proof-of-stake chains, small holders delegate their coins to a validator rather than run one themselves, which spreads rewards but can concentrate control.
