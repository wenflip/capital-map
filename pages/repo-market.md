---
id: repo-market
title: The Repo Market
short: Repo Market
parent: markets
order: 5
summary: The overnight borrowing against safe bonds that funds much of the financial system, and why a small change in its terms can force huge sales.
tags: repo, repurchase agreement, haircut, collateral, sofr, funding, plumbing
sources: Federal Reserve Bank of New York, Secured Overnight Financing Rate; Federal Reserve Bank of Richmond, Econ Focus (Q4 2019)
---
## What it is
A **repo**, short for repurchase agreement, is a loan dressed as a sale. One side sells a security, usually a government bond, and agrees to buy it back the next day, or after a few days, at a slightly higher price. The bond is the security for the loan; the price difference is the interest.

The **repo market** is where these deals happen, in huge volume, every day. Dealers, banks, money market funds, hedge funds and central banks all use it.

## Why it exists
- **Cheap, safe borrowing.** Lending against government bonds is close to risk-free, so it's the cheapest way to borrow cash overnight.
- **A home for spare cash.** Funds with cash to park can lend it overnight with a bond as security.
- **Funding the market.** Dealers pay for the bonds they hold by borrowing against them here. See [[market-making]].

## How it works
**The haircut.** Lenders don't lend the full value of the bond. The gap is the **haircut**, and the borrower has to fund it with their own money.

**Fictional example.** A bond is worth 1,000,000.
- With a 2% haircut, you can borrow 980,000 against it and need only **20,000** of your own money. That's control of a position **50 times** your own money.
- If lenders raise the haircut to 10%, you can borrow only 900,000. You now need **100,000** of your own: you must find another **80,000** overnight, or sell.

That is why repo is both the system's lubricant and one of its weak points. When lenders get nervous, they raise haircuts or stop lending, and borrowers who relied on rolling their loans every night must sell at once. See [[forced-sellers]].

**A benchmark rate.** In the US, the main overnight benchmark, SOFR, is the New York Fed's measure of the cost of borrowing cash overnight against Treasury securities. It is built from repo trades. See [[swaps]].

**When it strains.** On 17 September 2019, the US overnight repo rate averaged 5.25% for the day, against 2.1% paid on bank reserves. Cash for lending had become scarce. See [[liquidity]] and the *QE and QT* flow.

## What goes wrong
- **Overnight funding for long positions.** Borrowing for one day to hold assets for months only works while lenders keep rolling the loan.
- **Haircuts jump in a crisis,** exactly when borrowers can least find the extra cash.
- **Hidden leverage.** Small haircuts allow large positions built on very little of anyone's own money. See [[leverage]].

> **Key rule:** repo turns safe bonds into cash overnight. That works until the lender stops lending, and then everyone who relied on it has to sell the same bonds at once.

## Connects to
- [[central-bank-money]] — the reserves that ultimately settle repo trades.
- [[monetary-policy]] — central banks lend and borrow in repo to steer short-term rates.
- [[t-bills]] and [[bonds]] — the securities used as collateral.
- [[settlement]] — the plumbing the trades run on.

## Check yourself

**Q:** A bond worth 500,000 carries a 4% haircut. How much can you borrow, and how much of your own money is needed?

**A:** You can borrow **480,000**, so you need **20,000** of your own money.
