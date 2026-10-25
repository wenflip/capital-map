---
id: stablecoins
title: Stablecoins
parent: tokens
order: 1
summary: Tokens meant to stay at one unit of a currency: a private dollar promise on a blockchain, and what makes the promise hold or break.
tags: digital assets, stablecoins, money
killer: loss of the peg — the issuer or mechanism can't keep one token worth one dollar
traits: someone's liability, price-stable by design, no yield to holders unless lent out
---
## What it is
A **stablecoin** is a token designed to keep a steady value, usually one US dollar. It brings dollars onto blockchains, where they can move at any hour and be used by programs.

## Why it matters
Stablecoins are the main bridge between crypto and ordinary money. In the [[hierarchy-of-money|hierarchy of money]] they sit high up: a private promise to pay dollars, like a bank deposit but without the same protections in most places.

## How it works
| Design | What keeps it at a dollar | Whose liability? |
|---|---|---|
| **Reserve-backed** | The issuer holds cash and short-term government debt and redeems tokens for dollars | The issuing company's |
| **Crypto-collateralised** | Loans backed by more crypto than they're worth, closed automatically if the collateral falls | A program's, backed by borrowers' collateral |
| **Algorithmic** | A mechanism that mints and burns a partner token to hold the price | Nobody's — it relies on confidence |

**Algorithmic designs have failed badly.** In May 2022 the TerraUSD stablecoin lost its dollar peg and collapsed within days, taking its partner token with it.

## What goes wrong
- **De-peg:** if holders doubt the issuer can pay, they sell, and the price drops below one dollar. That is a run, the same as on a bank.
- **Reserve risk:** the backing may be weaker, less liquid or less transparent than claimed.
- **Freezes:** many reserve-backed issuers can freeze tokens at specific addresses.
- **Copies on other chains:** a stablecoin copied by a fork, or bridged by a third party, is not the issuer's promise. See [[forks]] and [[wrapped-tokens]].

> **Key rule:** a stablecoin is only as good as what it can be redeemed for, and who promises to redeem it.

## Connects to
- [[bank-deposits]] — the closest traditional comparison.
- [[t-bills]] — what many reserve-backed issuers hold.

## Check yourself

**Q:** In hierarchy-of-money terms, what is happening when a stablecoin trades at 0.95 dollars?

**A:** Holders doubt the promise, so they sell the private token (upper layer) to get dollars (lower layer). The 5% gap is the market's discount on the issuer's promise.
