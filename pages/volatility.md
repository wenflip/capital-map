---
id: volatility
title: Volatility
parent: measure
order: 3
summary: How widely prices swing.
---
## What it is
**Volatility** measures how widely an investment's returns swing around their average. It is usually given as the **standard deviation** of returns per year. A government bond fund might have volatility of a few percent; a broad share index around 15–20%; a single small company or a crypto asset far more.

## Why it matters
Volatility is the most common way to put a number on risk. It is used to compare investments, to size positions, and as the risk input in portfolio maths such as [[diversification]] and the [[sharpe-ratio]].

## How it works
**Fictional example:** five yearly returns of 10%, −5%, 15%, 0% and 5%.
- The average is **5%**.
- Each year's distance from the average: +5, −10, +10, −5 and 0.
- Square them, add them up (250), divide by one less than the number of years (4) and take the square root: **7.91%**.

**Reading it.** If returns were roughly bell-shaped, about two years in three would land within one standard deviation of the average: here, between about −3% and +13%.

**Scaling it.** Volatility grows with the square root of time. A daily volatility of 1% is about 1% × √252 = **15.87%** a year, using about 252 trading days.

## What goes wrong
- **Returns aren't bell-shaped.** Real markets have more extreme days than the bell curve predicts, the so-called **fat tails**. Crashes happen more often than volatility alone suggests.
- **Gains count as risk too.** Volatility treats a sharp rise the same as a sharp fall.
- **Smooth isn't safe.** Assets that are valued rarely, like private property or private businesses, show low volatility because their prices barely update, not because they can't fall.
- **It changes.** Volatility clusters: calm periods are followed by calm, and storms by storms. A figure from a calm decade can be badly out of date.

> **Key rule:** use volatility to compare and size, but never as the whole of risk. Check the drawdowns too.

## Connects to
- [[drawdown]] — the worst stretch, where volatility is the everyday swing.
- [[correlation]] — the other input to a portfolio's volatility.
- [[fear-gauges]] — the volatility the market expects, priced from options.
- [[measure]] — the branch this sits in.
- [[averages-and-distributions]] — the spread that an average can hide.

## Check yourself

**Q:** Two funds have the same average return. Fund A has 5% volatility and fund B has 20%. Which will usually have the lower compound return over time?

**A:** Fund B. Bigger swings drag the compound return further below the average return. See [[returns]].
