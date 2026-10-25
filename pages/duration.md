---
id: duration
title: Duration
parent: fixed-income
order: 7
summary: A single number for how much a bond's price moves when interest rates move.
tags: fixed income, bonds, risk
level: advanced
---
## What it is
**Duration** measures how sensitive a bond's price is to interest rates. **Modified duration** gives the approximate percentage price change for a one-percentage-point change in yield.

## Why it matters
Two bonds can have the same maturity and very different rate risk. Duration lets you compare them, and add them up across a whole portfolio. It's how banks, pension funds and fund managers measure how much a rate rise will hurt.

## How it works
**Macaulay duration** is the average time until you receive the bond's payments, weighted by how much each is worth today. **Modified duration** is Macaulay duration divided by (1 + yield).

**Worked example (fictional figures):** the 3-year, 5% bond from [[bond-pricing]], priced at a 5% yield.
- Macaulay duration ≈ **2.86** years.
- Modified duration ≈ **2.72**.
- So a one-point rise in yield, from 5% to 6%, should cut the price by about **2.72%**. The exact fall is about 2.67%.

For a 10-year version of the same bond, modified duration is about **7.72**, so the same rate rise cuts its price by roughly 7–8%.

| More duration (more rate risk) | Less duration (less rate risk) |
|---|---|
| Longer maturity | Shorter maturity |
| Lower coupon | Higher coupon |
| Lower yields | Higher yields |

## What goes wrong
- **Big moves.** Duration is a straight-line estimate; for large rate changes it overstates losses and understates gains (the gap is **convexity**).
- **Mismatches.** A bank whose assets have far longer duration than its deposits can be badly hurt by a rate rise, as Silicon Valley Bank was in 2023. See [[bank-capital-and-liquidity]].

> **Key rule:** duration × change in rates ≈ change in price. Know your duration before rates move.

## Check yourself

**Q:** A bond fund has a modified duration of 6. Rates rise by half a percentage point. Roughly how much does the fund's value change?

**A:** It falls by about 3% (6 × 0.5).
