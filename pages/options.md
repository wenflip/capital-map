---
id: options
title: Options
parent: derivatives
order: 2
summary: The right, but not the duty, to buy or sell at a set price.
---
## What it is
An **option** gives its buyer the right, but not the duty, to buy or sell something at a set price (the **strike**) on or before a set date. The buyer pays the seller a price for that right, called the **premium**.
- A **call** is the right to buy.
- A **put** is the right to sell.

## Why it exists
- **Insurance.** A put works like insurance on something you own: if the price falls below the strike, you can still sell at the strike.
- **Limited-loss bets.** A call lets you profit from a rise while risking only the premium.
- **Income.** Sellers collect premiums in return for taking on the risk.

## How it works
**Fictional example: a call option** with a strike of 100, bought for a premium of 5.

| Price at expiry | Exercise? | Profit or loss for the buyer |
|---|---|---|
| 90 | No, buying at 100 would be worse | −5 (the premium) |
| 105 | Yes | 0 (break-even) |
| 120 | Yes | +15 |

The buyer's loss is capped at 5; the gain grows with the price. The **seller** has the opposite position: their best case is keeping the 5, and their loss grows the further the price rises.

**What sets the premium:** how far the current price is from the strike, how long until expiry, interest rates and, above all, how much the price is expected to swing ([[volatility]]). More expected movement means a higher premium.

## What goes wrong
- **Time decay.** An option loses value as expiry nears if the price doesn't move. Most bought options expire worthless.
- **Sellers' hidden risk.** Selling options pays a small, steady income and can then lose heavily in a sharp move.
- **Paying for fear.** In a panic, insurance gets expensive just when people want it most.

> **Key rule:** an option buyer risks the premium; an option seller risks the move. Know which side you're on.

## Connects to
- [[futures]] — the contract with obligations on both sides.
- [[volatility]] — the main driver of an option's price.
- [[sharpe-ratio]] — why option-selling strategies can look safer than they are.

## Check yourself

**Q:** You own a share at 50 and buy a put with a strike of 45 for a premium of 2. The share falls to 30. What is the lowest your position can be worth, per share, before counting the premium?

**A:** 45. The put lets you sell at 45 however far the price falls. After the 2 premium, your worst outcome is 43.
