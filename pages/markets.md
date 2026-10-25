---
id: markets
title: Markets & Plumbing
parent: capital-system
order: 10
group: How it runs
summary: Where and how assets change hands: exchanges, brokers, custody and settlement.
short: Markets & Plumbing
sources: CNBC, Robinhood CEO on trading restrictions (1 February 2021); SEC and CFTC, Findings Regarding the Market Events of May 6, 2010
---
## What it is
**Markets & Plumbing** covers how assets actually change hands, and who holds them afterwards. Every trade runs along the same chain: an order goes through a **broker** to an **exchange**, where it meets another order; the trade is **settled** when money and asset swap; and from then on the asset sits with a **custodian** on your behalf.

## Why it exists
Most of the time this plumbing is invisible, which is the point: it lets millions of strangers trade safely without knowing or trusting each other. It matters when it breaks. Many of the worst losses in finance came not from a bad investment but from a broker, custodian or counterparty failing in the middle of the chain.

## How it works
- [[exchanges]] — where buy and sell orders meet, and how prices are set.
- [[brokers]] — the firm that takes your orders and holds your account.
- [[settlement]] — how a trade becomes final, and the clearing house that guarantees it.
- [[custody]] — who actually holds the asset, and what you really own.

| Step | Who | What can go wrong |
|---|---|---|
| Order | You → broker | Poor prices, outages, restrictions |
| Trade | Exchange | Thin markets, sudden crashes |
| Settlement | Clearing house | Delays, failed deliveries |
| Holding | Custodian | Misuse or loss of customer assets |

On the [[cartography-of-wealth|Cartography of Wealth]], this chain is why tier 3 assets are "legible": each step keeps a record, and each step is an intermediary you depend on.

## What goes wrong
- **Intermediary failure.** When a firm in the chain fails, customers find out how well their assets were kept apart. FTX is the crypto example. See [[custodial-crypto]].
- **Trading halts and restrictions.** In January 2021 the US broker Robinhood limited buying of GameStop shares after its clearing house demanded a deposit of about $3 billion, later reduced.
- **Flash crashes.** On 6 May 2010 the Dow Jones index fell about 9%, most of it within minutes, then recovered much of the loss the same afternoon.

> **Key rule:** every asset you don't hold yourself sits at the end of a chain of firms. Know the chain, and how your assets are protected if one link fails.

## Connects to
- [[claims-and-liabilities]] — what you own at the end of the chain is usually a claim.
- [[shares]] and [[bonds]] — the assets that travel along it.
- [[self-custody]] — the crypto way of skipping most of the chain.
- [[deposit-insurance]] — the bank-account version of investor protection.

## Check yourself

**Q:** Your shares are held through a broker. Name two links in the chain other than the broker.

**A:** For example, the exchange where the trade happened and the clearing house that settled it. A custodian bank or central securities depository holds the record of ownership.

**Q:** Why can a broker restrict trading in a share even when the exchange is open?

**A:** Because the broker has to post collateral with the clearing house for its customers' trades. If that requirement jumps, the broker may limit trading until it can meet it.

## Going deeper
- **Central securities depositories** hold the master record of who owns which securities, usually in electronic form; brokers and custodians hold their customers' shares through accounts there.
- **Dark pools** are private trading venues where large orders are matched without being shown publicly first.
