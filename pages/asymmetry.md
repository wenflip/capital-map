---
id: asymmetry
title: Asymmetry
short: Asymmetry
parent: portfolio
order: 4.5
summary: The shape of what you can win against what you can lose, and why being right most of the time can still lose money.
tags: asymmetry, payoff, risk, convexity, tail risk, expected value
---
## What it is
**Asymmetry** is the shape of a bet: how big the possible gain is compared with the possible loss, and how often each happens. Two positions with the same average return can feel and end completely differently, depending on that shape.
- **Positive asymmetry:** small, limited losses and occasional large gains. Buying an option is an example: the most you can lose is what you paid. See [[options]].
- **Negative asymmetry:** small, steady gains and occasional large losses. Selling insurance, or selling options, works like this. The saying for it is "picking up pennies in front of a steamroller".

## Why it matters
People judge strategies by how often they win. But how much you win or lose each time matters as much as how often. A strategy that wins nine times in ten can still lose money, and the nine wins make it feel safe right up to the tenth.

## How it works
**Fictional example: two strategies over ten rounds.**
- **Strategy A** gains 1 nine times and loses 12 once. Average per round: 0.9 × 1 − 0.1 × 12 = **−0.3**. It wins 90% of the time and still loses money.
- **Strategy B** loses 1 nine times and gains 15 once. Average per round: −0.9 × 1 + 0.1 × 15 = **+0.6**. It loses 90% of the time and still makes money.

**Losses are asymmetric too.** A 50% loss needs a 100% gain to get back to where you started. Big losses cost more than equal-sized gains repay. See [[drawdown]].

**Where negative asymmetry hides.**
- **Leverage:** steady returns until a fall large enough to wipe you out. See [[leverage]].
- **High yields:** extra income that's really payment for a rare large loss. See [[credit-risk]].
- **Short positions:** a capped gain and an open-ended loss. See [[short-selling]].

## What goes wrong
- **Judging by the win rate.** A long run of small wins says nothing about the size of the loss that hasn't happened yet.
- **Short histories.** Negative-asymmetry strategies look best in exactly the records too short to include their bad year. See [[stability-breeds-instability]].
- **Paying too much for positive asymmetry.** Protection has a price, and constant small losses add up.

> **Key rule:** for any position, ask how much you can lose, how often, and whether you'd survive it, before asking how often it wins.

## Connects to
- [[position-sizing]] — keeping any one loss survivable.
- [[risk-and-return]] — the trade-off asymmetry reshapes.
- [[fear-gauges]] — the price of protection against the rare large move.
- [[insurer-failure]] — what happens to a business that sells protection and meets the big loss.

## Check yourself

**Q:** A strategy gains 2 with a 70% chance and loses 6 with a 30% chance. What is its average result per round?

**A:** 0.7 × 2 − 0.3 × 6 = 1.4 − 1.8 = **−0.4**. It wins most of the time and still loses on average.
