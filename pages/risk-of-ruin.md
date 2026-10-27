---
id: risk-of-ruin
title: Risk of Ruin
short: Risk of Ruin
parent: portfolio
order: 4.6
summary: The chance that losses become large enough to end the ability to continue, not merely to reduce wealth.
tags: portfolio, risk, ruin, survival
---
## What it is
Risk of ruin is the chance that a series of losses reduces capital to a point where the activity cannot continue. It is not the chance of a loss. It is the chance that losses become large enough, or arrive in a sequence that forces an exit, so that recovery is no longer possible on the original terms.

## Why it matters
A strategy can have a positive expected return and still carry a material chance of ruin if the losses are large relative to capital or if leverage forces sales. Surviving to realise the expected return requires that ruin remains unlikely. Once ruin occurs, the expected return is no longer available.

## How it works
Ruin depends on the size of the edge, the size of the typical loss, and how much capital is risked each time. Larger bets raise the chance that a run of losses exhausts capital before the edge can recover it. The same edge that is safe at small size can produce ruin at large size. Anything that forces an exit — margin calls, redemptions, spending needs — turns a temporary loss into ruin.

**Worked example (fictional figures):** a process wins 55% of bets and loses 45%, with equal sized wins and losses. Betting 1% of capital each time, five losses in a row leave 0.99 × 0.99 × 0.99 × 0.99 × 0.99 ≈ **0.951** of the start: a scratch. Betting 20% each time, the same five losses leave 0.8 × 0.8 × 0.8 × 0.8 × 0.8 ≈ **0.328**: two-thirds gone. Further losses or a forced exit can end the activity even though the edge remains positive.

## What goes wrong
- **Focusing only on expected return.** A positive expectation does not protect against a sequence that ends the game.
- **Increasing size after losses.** Larger bets when capital is already reduced raise the chance of ruin.
- **Ignoring forced exits.** Leverage or spending needs can create ruin even when the underlying process would have recovered.

> **Key rule:** size positions so that a realistic run of losses cannot end the ability to continue.

## Connects to
- [[asymmetry]] — the balance of what can be won against what can be lost.
- [[drawdown]] — the fall from peak that must be survived.
- [[position-sizing]] — how much is risked each time.
- [[leverage]] — borrowing that turns a temporary fall into a forced exit.

## Check yourself

**Q:** A strategy has a positive expected return but a 15% chance of a 60% loss in any year. Why can that still produce ruin?

**A:** A single 60% loss leaves 40% of capital. If spending, leverage or further losses prevent recovery on the original terms, the activity ends even though the long-run expectation was positive.

**Q:** Reducing the fraction of capital risked each time lowers the chance of ruin. What else does it change?

**A:** It also lowers the rate at which capital grows when the edge is realised. The trade-off is between growth and the chance of being unable to continue.
