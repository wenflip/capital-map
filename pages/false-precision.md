---
id: false-precision
title: False Precision
short: False Precision
parent: how-to-think
order: 11
summary: A number can look exact while resting on rough estimates, small samples or arbitrary choices.
tags: mental models, thinking, numbers, precision, uncertainty
---
## What it is
False precision is presenting a figure with more exactness than the underlying information supports. A result reported to one decimal place can come from a small sample, an assumption, or a model whose inputs are themselves estimates.

## Why it matters
Precise-looking numbers are treated as more reliable than round ones. A forecast of 6.3% can feel more trustworthy than “about 6%” even when both rest on the same uncertain inputs. The extra digits do not add information; they only hide the uncertainty.

## How it works
Ask what the number is built from. How many observations? How sensitive is it to a change in one assumption? Could the same process have produced a different figure? If the inputs are rough, the output cannot be precise. Rounding to a level that matches the real uncertainty is more accurate than keeping extra digits.

**Worked example (fictional figures):** a survey of 40 people finds that 25 prefer one option. The share is 25 / 40 = 0.625, or 62.5%. Reporting “62.5% of people” implies more certainty than 40 observations support. A change of two responses moves the figure by 5 percentage points (2 / 40 = 0.05). The result is better stated as roughly 60%.

## What goes wrong
- **Keeping extra decimal places.** The digits suggest accuracy the data do not have.
- **Treating a model output as a measurement.** A calculated figure inherits the uncertainty of its inputs.
- **Comparing precise-looking numbers that are not comparable.** Small differences in the last digit can be noise.

> **Key rule:** match the precision of the number to the quality of the information behind it.

## Connects to
- [[absolute-and-relative-risk]] — a precise relative figure can still describe a tiny absolute chance.
- [[averages-and-distributions]] — an average reported to many decimals can hide a wide spread.
- [[measure]] — how results are summarised and reported.
- [[luck-and-skill]] — a precise short-term result can still be mostly luck.

## Check yourself

**Q:** A model outputs 7.84%. The main input is an estimate that could easily be 1 percentage point higher or lower. How should the output be treated?

**A:** As roughly 8%. The extra digits do not survive a 1-point change in the input. Reporting 7.84% overstates the precision.

**Q:** Two polls of 30 people each report 53.3% and 56.7%. Is the difference meaningful?

**A:** Not on these sample sizes. A swing of one response changes the share by about 3.3 percentage points (1 / 30 ≈ 0.033). The reported difference sits inside ordinary sampling variation.
