---
id: fat-tails
title: Fat Tails
short: Fat Tails
parent: measure
order: 3.5
summary: Outcomes far from the average occur more often than a normal distribution predicts, so rare events dominate long-run results.
tags: measure, risk, tails, distribution
---
## What it is
Fat tails describe a distribution in which extreme outcomes — very large gains or losses — occur more frequently than they would under a normal (bell-shaped) distribution. Most observations still cluster near the centre, but the probability of results many standard deviations away does not fall as quickly.

## Why it matters
Models and rules of thumb built on normal distributions understate the chance of large moves. A strategy that looks safe because large losses are “unlikely” under normal assumptions can still experience them often enough to dominate the long-run result. The average can be positive while a few extreme losses determine whether capital survives.

## How it works
In a normal distribution the chance of a move larger than three standard deviations is very small. In distributions with fat tails that chance is higher, and the chance of even larger moves declines more slowly. Financial returns commonly show this pattern: most days are ordinary, but the largest daily moves account for a disproportionate share of total variation. Measures that assume normality, such as simple volatility, therefore understate the risk of extremes.

**Worked example (fictional figures):** under a normal assumption a daily move larger than 4% has a chance of about 0.3%. In a fat-tailed series the same threshold is crossed on 2% of days. Over 250 trading days the expected number of such moves rises from 0.75 to 5. The extremes are no longer rare enough to ignore.

## What goes wrong
- **Using normal-based risk limits.** A limit set at three standard deviations can be breached far more often than the model suggests.
- **Treating the average as sufficient.** A positive average does not protect against the few large losses that fat tails make more likely.
- **Assuming extremes cancel.** Large losses and large gains do not offset evenly when leverage or spending needs force exits after the losses.

> **Key rule:** expect extremes more often than a normal distribution implies, and size positions so that those extremes do not end the activity.

## Connects to
- [[volatility]] — the ordinary measure that understates tail risk.
- [[drawdown]] — the large falls that fat tails make more common.
- [[risk-of-ruin]] — the chance that a tail event ends the ability to continue.
- [[averages-and-distributions]] — why the average can hide the extremes that matter.

## Check yourself

**Q:** A risk model says a 5% daily loss should occur once every few years. The same loss has occurred three times in the last two years. What does that suggest?

**A:** The distribution has fatter tails than the model assumes. The extremes are more common than the normal calculation predicted.

**Q:** Why can a strategy with a positive average return still fail because of fat tails?

**A:** A small number of large losses, more frequent than a normal model expects, can reduce capital enough that recovery on the original terms is no longer possible.
