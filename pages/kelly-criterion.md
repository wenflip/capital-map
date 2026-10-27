---
id: kelly-criterion
title: Kelly Criterion
short: Kelly Criterion
parent: portfolio
order: 4.7
level: advanced
summary: A formula for the fraction of capital to risk when there is a known edge, balancing growth against the chance of large losses.
tags: portfolio, kelly, position sizing, edge, advanced
sources: Kelly (1956)
---
## What it is
The Kelly criterion gives the fraction of capital that maximises the expected long-run growth rate when the probabilities and payoffs are known. It is the size that grows capital fastest if the edge is correctly estimated and the activity can be repeated many times. Betting more than this fraction raises the chance of large losses; betting less grows capital more slowly.

## Why it matters
Position size determines both the growth rate and the risk of ruin. An edge that is real can still destroy capital if too much is risked on each trial. The criterion makes the trade-off explicit: the optimal fraction depends on the size of the edge and the odds.

## How it works
For a bet that wins with probability *p* and pays *b* times the stake (net odds), the Kelly fraction is:

f* = p − (1 − p) / b

The fraction is the edge divided by the odds. When the edge is small, the fraction is small. When the payoff is larger, a higher fraction can be justified. In practice many users bet a fraction of the Kelly amount (half-Kelly or less) because estimates of *p* and *b* are uncertain and because full Kelly produces large swings.

**Worked example (fictional figures):** a bet wins 55% of the time (*p* = 0.55) and pays even money (*b* = 1). The Kelly fraction is 0.55 − (1 − 0.55) / 1 = **0.10**, or 10% of capital. Half-Kelly would be 5%. Betting the full 10% maximises expected growth if the probabilities are exact; estimating them too high leads to over-betting and higher chance of large drawdowns.

## What goes wrong
- **Using an overstated edge.** If the true probability is lower than assumed, the calculated fraction is too large and the chance of ruin rises.
- **Treating it as a guarantee.** The formula maximises expected growth; it does not remove the possibility of long losing streaks.
- **Applying it when the edge is not repeatable.** The criterion assumes many independent trials with a stable edge.

> **Key rule:** the fraction that maximises growth is usually smaller than intuition suggests, and estimates of the edge should be treated as uncertain.

## Connects to
- [[edge]] — the advantage the fraction is sized to.
- [[position-sizing]] — the practical decision the formula informs.
- [[risk-of-ruin]] — betting more than the criterion raises the chance of ending the activity.
- [[volatility]] — full Kelly produces large swings even when the edge is real.

## Check yourself

**Q:** The calculated Kelly fraction is 8%. Why might someone bet only 4%?

**A:** Because the estimate of the edge may be too high, and half the fraction still captures most of the growth while reducing the size of the worst streaks.

**Q:** A bet pays 3 to 1 and wins 30% of the time. What is the Kelly fraction?

**A:** f* = 0.30 − (1 − 0.30) / 3 = 0.30 − 0.70 / 3 = 0.30 − 0.233 = **0.067**, or about 6.7% of capital.
