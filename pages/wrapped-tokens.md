---
id: wrapped-tokens
title: Wrapped and Bridged Tokens
short: Wrapped tokens
parent: tokens
order: 4
summary: Stand-ins for a coin from somewhere else. Same name, but a claim on whoever holds the original.
tags: digital assets, tokens, bridges
killer: the bridge or custodian holding the originals fails or is hacked
traits: someone's liability, same ticker as the original, a claim not the coin
---
## What it is
A **wrapped token** is a token that stands in for another asset, so it can be used where the original can't go. Wrapped bitcoin on Ethereum is the classic example: bitcoin can't run on Ethereum, so a custodian holds real bitcoin and issues a matching token.

## Why it matters
Wrapping is how assets move between chains and into [[defi]]. But a wrapped token is not the original. It is a **claim** on whoever holds the original, which puts it in a different place on the [[cartography-of-wealth|Cartography of Wealth]] and in the [[hierarchy-of-money|hierarchy of money]].

## How it works
| Kind | Who holds the original | Whose liability? |
|---|---|---|
| **Same-chain wrap** (a chain's own coin turned into a standard token) | A simple contract on the same chain | The contract's — low risk if the code is sound |
| **Custodian-wrapped** | A company or group of companies | The custodian's |
| **Bridged** | A bridge contract or its operators | The bridge's. See [[bridges-and-layer-2s]] |

## What goes wrong
- **Bridge or custodian failure:** if the originals are stolen or lost, the wrapped tokens are backed by nothing and fall towards zero.
- **Same ticker, different asset:** a bridged coin, the original and a [[forks|forked]] copy can all carry the same name.
- **Freezes:** custodians can sometimes block redemptions.

> **Key rule:** a wrapped token is only as good as whoever holds the original. Ask where the real coin is.

## Check yourself

**Q:** Why did tokens issued by some bridges lose almost all their value after a hack, even though the original coins kept theirs?

**A:** Because the hack stole the originals the bridge was holding. The bridged tokens were claims on those originals, so with nothing behind them they became worthless.
