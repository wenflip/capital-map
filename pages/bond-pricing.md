---
id: bond-pricing
title: Bond Prices and Yields
short: Prices and yields
parent: fixed-income
order: 3
summary: Why bond prices fall when interest rates rise, what "yield" means, and why longer bonds move more.
tags: fixed income, bonds, valuation
---
## What it is
A bond's **price** is what the market will pay for its remaining payments today. Its **yield** is the return you would earn by buying at that price and holding to maturity. Price and yield move in opposite directions.

## Why it matters
Most people expect a "safe" bond to hold its value. It does if held to the end and the issuer pays. But its market price moves every day with interest rates, and anyone who has to sell before maturity takes whatever price is on offer.

## How it works
A bond's price is the [[time-value-of-money|present value]] of its future payments, discounted at the current market yield.

**Worked example (fictional figures):** a 3-year bond with a face value of 1,000 and a 5% annual coupon pays 50, 50 and then 1,050.

| Market yield | Price | Why |
|---|---|---|
| 4% | **1,027.75** | Its 5% coupon beats new bonds, so buyers pay more |
| 5% | **1,000.00** | Coupon equals the market rate: priced at face value |
| 6% | **973.27** | New bonds pay more, so this one must sell for less |

**Longer bonds move more.** The same change hits a 10-year version of this bond much harder: at a 6% yield it is worth about **926.40**, and at 4% about **1,081.11**. The further away the payments, the more a change in the discount rate changes their value today. See [[duration]].

**Yield to maturity** is the single rate that makes the present value of all the bond's payments equal its price. It's the standard way to compare bonds with different coupons and maturities.

## What goes wrong
- **Selling at the wrong time.** A rate rise turns a safe bond into a paper loss, and a forced sale makes it a real one.
- **Hidden losses.** Bonds held "to maturity" on a balance sheet aren't marked to market, so losses can build up unseen.
- **Comparing coupons instead of yields.** A high coupon bought at a high price can yield less than a low coupon bought cheaply.

> **Key rule:** when interest rates go up, existing bond prices go down — and the longer the bond, the bigger the fall.

## Check yourself

**Q:** Market yields fall from 5% to 4%. What happens to the price of a 5%-coupon bond priced at 1,000?

**A:** It rises above 1,000 (to about 1,027.75 for the 3-year example), because its 5% coupon is now better than what new bonds pay.

**Q:** Why did bonds that were certain to be repaid cause losses at Silicon Valley Bank?

**A:** Because rates rose sharply, cutting the market value of the bank's long-dated bonds. When depositors ran, it had to sell some of them at those lower prices, turning paper losses into real ones.
