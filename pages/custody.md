---
id: custody
title: Custody
parent: markets
order: 3
summary: Who actually holds the asset, and what you really own.
---
## What it is
**Custody** is the safekeeping of assets on someone else's behalf. When you buy shares through a broker, you rarely hold anything directly. A chain of firms holds them, and what you own is a recorded claim at the end of that chain.

## Why it exists
Modern securities are electronic entries, not paper certificates. Specialist custodians keep the records, collect dividends and interest, handle corporate events such as takeovers, and keep clients' assets apart from their own.

## How it works
**The chain:** you → your broker → (often) a custodian bank → the **central securities depository**, which holds the master record. At each step, assets are usually pooled in **omnibus** accounts, with the firm's own books showing whose share is whose.

**What protects you:**
- **Segregation:** customer assets should be held separately from the firm's own, so the firm's creditors can't claim them if it fails.
- **Records and audits** that show which customer owns what.
- **Protection schemes** that cover missing assets up to a limit. See [[brokers]].

**What weakens it:**
- **Rehypothecation:** some agreements let a firm lend or pledge customers' assets, especially in margin accounts.
- **Mixing:** when firms (as at FTX) don't keep customer assets apart, customers become ordinary creditors in a bankruptcy.

| | Held for you by a custodian | Held yourself |
|---|---|---|
| **Example** | Shares at a broker, a gold fund, crypto on an exchange | Certificates, bars in your safe, [[self-custody]] crypto |
| **Main risk** | The firm and its records | Your own security and mistakes |
| **Cartography tier** | 3 (legible) | 2 (private, bearer) |

## What goes wrong
- **Firm failure with poor segregation.** Customers wait years, and may not get everything back.
- **Long chains.** The more links, the more firms whose failure or error can affect you.
- **Frozen access** during a bankruptcy, even when assets are eventually returned.

> **Key rule:** you own what the records say you own. Choose custodians whose records, segregation and protection you understand.

## Connects to
- [[claims-and-liabilities]] — custody turns an asset into a claim on a chain of firms.
- [[custodial-crypto]] and [[self-custody]] — the same choice in crypto.
- [[gold]] — physical bars against a fund.

## Check yourself

**Q:** Why does segregation of customer assets matter most when a broker fails?

**A:** Because segregated assets belong to the customers, not the broker, so they can be returned. Mixed-in assets may be treated as the broker's, leaving customers as creditors who share whatever is left.
