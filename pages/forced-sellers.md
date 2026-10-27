---
id: forced-sellers
title: Forced Sellers
short: Forced Sellers
parent: how-markets-move
order: 8
summary: Margin calls, fund redemptions and rules make some holders sell whatever the price, which is how good assets end up sold at bad prices.
tags: forced selling, margin call, redemptions, liquidation, collateral, fire sale
sources: ESMA, Leverage and derivatives: the case of Archegos; Bank of England, Bank of England announces gilt market operation (28 September 2022)
---
## What it is
A **forced seller** sells not because they think the price is right, but because they have no choice. Their lender, their investors or their rules demand cash or a smaller position, now.

## Why it matters
Forced selling ignores value. A forced seller takes whatever price the market offers, so prices can fall far below what the asset is worth, and stay there until the forced selling ends. On the other side of every forced sale is a buyer who can wait.

## How it works
**The main sources.**
- **Margin calls.** Borrowers who used their holdings as security must add cash or sell when prices fall. See [[leverage]].
- **Collateral calls.** Derivative positions demand more security when prices move against them. See [[swaps]].
- **Redemptions.** When investors pull money from a fund, the fund must sell holdings to pay them, often the easiest ones to sell rather than the worst.
- **Rules.** A fund that may only hold investment-grade bonds must sell a bond that's downgraded below that line. See [[credit-risk]].

**The spiral.** Forced selling pushes prices down, which triggers more margin and collateral calls, which forces more selling. Each round makes the next one bigger.

**Fictional example: when the call comes.** You buy 100,000 of shares with 50,000 of your own money and 50,000 borrowed. The lender requires your own money to stay at least 30% of the position.
- If the shares fall to 70,000, your equity is 70,000 − 50,000 = 20,000, which is about **28.6%** of the position. That's below 30%: margin call.
- The call comes when the position falls below about 71,429, a fall of about **28.6%**.

**Real cases.**
- **Archegos, March 2021.** A family office that had borrowed heavily through several banks couldn't meet margin calls. The banks sold its positions, with losses of more than $10 billion. See [[swaps]].
- **UK pension funds, September 2022.** Funds using borrowed hedges faced collateral calls as UK government bond prices fell, and sold bonds to raise cash, pushing prices down further. On 28 September 2022 the Bank of England stepped in to buy long-dated bonds. See [[market-failure]].

## What goes wrong
- **Being the forced seller.** Leverage, too little cash and promises to repay on demand all take away the choice to wait.
- **Fire sales spread.** Forced sellers sell what they can, not what they want, so unrelated assets fall too. See [[correlation]].
- **Rules all trigger together.** When many holders follow the same limits, one downgrade or one price level sets off everyone at once.

> **Key rule:** the most important question about any position is not "will it go up?" but "could anything force me to sell it at the bottom?"

## Connects to
- [[leverage]] — the main reason people get forced out.
- [[stability-breeds-instability]] — how the borrowing builds up.
- [[market-making]] — the dealers who absorb the selling, until they're full.
- [[liquidity]] — what you have when you aren't forced.

## Check yourself

**Q:** You hold 80,000 of shares, bought with 40,000 of your own money and 40,000 borrowed. The shares fall 25%. What is your equity now, and what share of the position is it?

**A:** The position is worth 60,000, so your equity is 60,000 − 40,000 = **20,000**, which is a third (about **33.3%**) of the position.
