---
id: time-value-of-money
title: Time Value of Money
parent: foundation
order: 3
summary: A dollar today is worth more than a dollar later, and by how much: present value, future value and the discount rate.
tags: foundation, valuation
---
## What it is
The idea that money available **now** is worth more than the same amount **later**. Money now can be invested and earn a return, it is certain while future money isn't, and prices may rise in between.

## Why it exists
Every financial decision trades money at one time for money at another: saving, borrowing, buying a bond, buying a business. To compare them you need to move all the amounts to the same point in time.

## How it works
Two conversions, using an interest rate *r* per period and *n* periods:

| Conversion | Formula | Question it answers |
|---|---|---|
| **Future value** | FV = PV × (1 + r)ⁿ | What will this sum grow to? |
| **Present value** | PV = FV ÷ (1 + r)ⁿ | What is a future sum worth today? |

**Worked example (fictional figures):** at 5% a year,
- 1,000 today grows to about **1,628.89** in 10 years;
- 1,000 received in 10 years is worth about **613.91** today.

The rate used to bring future money back to today is the **discount rate**. It is made of two parts:
- the reward for **waiting**: roughly, the rate on the safest available asset, which already includes the inflation people expect;
- the reward for **risk**: the less certain the payment, the higher the rate and the lower the present value. See [[risk-and-return]].

## What goes wrong
- **Adding amounts from different years** as if they were the same money.
- **Using the wrong rate.** A safe promise and a risky one should not be discounted at the same rate.
- **Forgetting inflation.** A nominal rate discounts nominal amounts; a real rate discounts amounts in today's prices. Mixing the two gives nonsense. See [[inflation]].

> **Key rule:** move every amount to the same date before you compare, add or subtract.

## Connects to
- [[compounding]] — the future-value formula is compounding.
- [[bonds]] and [[valuation]] — prices are present values of expected future cash.
- [[t-bills]] — the usual stand-in for the reward for waiting.

## Check yourself

**Q:** A friend offers you 1,100 in one year instead of 1,000 today. Safe savings pay 5%. Which is worth more today?

**A:** The 1,100 next year. At 5% its present value is about 1,047.62, which is more than 1,000 — assuming the friend is as reliable as the savings account. If not, a higher discount rate could flip the answer.
