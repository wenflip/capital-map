---
id: sharpe-ratio
title: Sharpe Ratio
parent: measure
order: 4
summary: Return per unit of risk.
level: advanced
sources: William F. Sharpe, Mutual Fund Performance (1966); William F. Sharpe, The Sharpe Ratio (1994)
---
## What it is
The **Sharpe ratio** measures return per unit of risk. It takes the return an investment earned above a risk-free rate, usually short-term government bills, and divides it by its volatility:

> **Sharpe ratio = (return − risk-free rate) ÷ volatility**

The economist William Sharpe introduced it in 1966 as the "reward-to-variability ratio".

## Why it matters
A higher return isn't better if it came from taking far more risk. The Sharpe ratio puts strategies with different levels of risk on the same scale, so you can see which one paid better for the risk it took.

## How it works
Fictional example, with a risk-free rate of 4%:

| | Return | Volatility | Sharpe ratio |
|---|---|---|---|
| Portfolio A | 9% | 10% | 0.50 |
| Portfolio B | 12% | 20% | 0.40 |

B made more money, but A earned more for each unit of risk. In theory, an investor could borrow to double A's exposure (taking it to 20% volatility, like B) and earn about 4% + 2 × 5% = **14%**, more than B, before the cost of borrowing above the risk-free rate.

**Rough scale:** for a broad share market over long periods, the ratio has typically been well below 1. Figures far above that, sustained for years, deserve scrutiny.

## What goes wrong
- **It inherits volatility's blind spots.** Strategies that earn small steady gains and then lose heavily (selling insurance against crashes, for example) can show a high Sharpe ratio until the crash arrives.
- **Smoothed prices flatter it.** Assets valued rarely look less volatile, so their ratio looks better than it is.
- **It depends on the period.** A ratio from a calm bull market says little about a crisis.
- **Leverage isn't free.** The "borrow to scale up" argument assumes you can borrow cheaply and won't be forced to sell. See [[leverage]].

> **Key rule:** use the Sharpe ratio to compare, then check the worst drawdown. A high ratio with a hidden crash risk is not a good deal.

## Connects to
- [[volatility]] — the denominator.
- [[t-bills]] — the usual risk-free rate.
- [[risk-and-return]] — the trade-off it measures.

## Check yourself

**Q:** A fund returned 7% with 6% volatility while the risk-free rate was 4%. What is its Sharpe ratio?

**A:** (7 − 4) ÷ 6 = 0.50.
