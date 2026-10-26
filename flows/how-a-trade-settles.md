---
id: how-a-trade-settles
title: How a share trade settles
area: Markets & Plumbing
order: 4
summary: Follow one share purchase from the tap on your app to the record that says you own it, and see what each firm in the chain does.
---
Buying a share feels instant. Behind the tap, a chain of firms takes over: one routes the order, one matches it, one guarantees it, one moves the shares and the money, and one keeps the record. This flow follows one purchase through all of them.

> **Key rule:** the trade happens in a second, but ownership takes a business day. Until settlement, what you hold is a promise that the chain will deliver.

| Step | Page | Who acts | What you hold | What can go wrong | Where it happened |
|---|---|---|---|---|---|
| You place a buy order | [[brokers]] | You and your broker | Cash in your account: a claim on the broker | Outages and restrictions when markets are busiest | — |
| The order is routed and matched | [[exchanges]] | Your broker, an exchange or other venue, and market makers | An order, not yet a trade | In thin or fast markets an order can fill far from the last price | US flash crash, 6 May 2010 |
| The clearing house steps in | [[settlement]] | The clearing house (for US shares, NSCC) becomes buyer to the seller and seller to the buyer | A trade the clearing house guarantees | Margin demands on brokers jump when markets swing | Robinhood, January 2021: a clearing deposit demand of about $3 billion led it to limit GameStop buying |
| Shares and money swap, one business day later | [[settlement]] | The depository (for US shares, DTC) moves both at once | The shares, once delivery and payment have both happened | A seller fails to deliver on time | The US moved from two days (T+2) to one (T+1) on 28 May 2024 |
| The shares are held for you | [[custody]] | Your broker, often a custodian bank, and the depository | A record in your broker's books, at the end of a chain | A firm fails without keeping customer assets apart | FTX, a crypto exchange, filed for bankruptcy on 11 November 2022 with customer assets not kept apart |
| Dividends and votes come back down the chain | [[shares]] | The company, the depository, custodians and your broker | Your share's rights, passed down the chain | Delays and lost votes in long chains | — |

## What to notice
- **Most trades cancel out.** The clearing house nets each firm's buys and sells, so only the differences actually move. See [[settlement]] for a worked example.
- **You own a claim at the end of a chain,** not a certificate. Each link is someone's promise to the next. See [[claims-and-liabilities]].
- **Every firm in the chain is a rung on the [[failure-modes|failure ladder]]:** the broker is rung 1, the clearing house rung 5, and the market itself rung 12. A long chain is efficient, and each link is one more place it can break.

*Sources: SEC, Shortening the Securities Transaction Settlement Cycle (2023); DTCC, Continuous Net Settlement (NSCC as central counterparty, settlement at DTC); SEC and CFTC, Findings Regarding the Market Events of May 6, 2010; CNBC, Robinhood CEO on trading restrictions (1 February 2021); FTX Chapter 11 filing (11 November 2022).*
