---
id: market-making
title: Dealers and Market Making
short: Market Making
parent: markets
order: 1.5
summary: The firms that stand ready to buy from you and sell to you, quoting two prices, holding the stock in between, and pulling back when that gets dangerous.
tags: markets, dealers, market maker, bid-ask spread, liquidity, inventory
sources: Jack Treynor, The Economics of the Dealer Function (1987); Perry Mehrling, Economics of Money and Banking (course); Federal Reserve, Monetary Policy Report, Part 2 (June 2020)
---
## What it is
A **dealer**, or **market maker**, is a firm that trades from its own account. It quotes two prices at once: a **bid**, at which it will buy from you, and an **ask**, at which it will sell to you. The gap between them is the **spread**.

That makes a dealer different from a [[brokers|broker]]. A broker is your agent: it finds someone else to trade with you. A dealer *is* the someone else. When you sell a bond to a dealer, the dealer owns it until it can sell it on.

Shares mostly trade on [[exchanges]], where market makers post prices in the order book. Many other markets have no central exchange at all and run almost entirely through dealers: most bonds, currencies and [[swaps]], for example.

## Why it exists
Buyers and sellers rarely turn up at the same moment. A pension fund may want to sell a bond on Tuesday; the natural buyer may not arrive until Friday. Without a dealer, the seller waits, or accepts whatever price the first passer-by offers. The dealer bridges that gap in time: it buys now, holds the bond, and sells later. The spread is its payment for being there and for carrying the risk in between.

This is what people usually mean by a **liquid** market: one where you can trade a reasonable size, quickly, without moving the price much. Much of that liquidity is dealers' balance sheets at work. See [[liquidity]].

## How it works
**Earning the spread.** Say a dealer quotes a bond at 99.90 bid and 100.10 ask (fictional figures). It buys 1,000 from one client at 99.90 and sells 1,000 to another at 100.10. It earns 0.20 × 1,000 = **200**.

**Carrying inventory.** The catch is the time in between. If the bond's price falls by 0.50 before the dealer can sell, it loses 1,000 × 0.50 = **500**, more than two round trips of spread. A dealer is always holding something it would rather not, waiting for the other side to turn up.

**Moving the quotes.** So a dealer sets its prices by what it is holding. Holding too much, it lowers both its bid and its ask: buyers are tempted in, sellers are put off, and the stock runs down. Holding too little, or short, it raises both. The price you see is partly the dealer managing its own stock. Jack Treynor set this out in 1987, and it is the backbone of Perry Mehrling's course on money and banking.

**Funding the inventory.** A dealer rarely pays for its stock with its own money. It borrows, often overnight against the securities themselves. That ties the market for an asset to the money market: when borrowing gets dearer or harder, dealers hold less, and spreads widen. See [[money-creation]] for how that borrowing is created, and [[monetary-policy]] for what sets its price.

**The cost to you.** If you buy at the ask and sell straight back at the bid, you lose the whole spread. On a liquid share the spread is tiny; on a thinly traded bond, or in a panic, it can be large.

## What goes wrong
- **Liquidity vanishes when it's needed most.** In a sell-off everyone wants to sell at once. Dealers' stock piles up, their risk limits bite, and they step back or widen spreads sharply. The market that was liquid on a calm day isn't on a stressed one.
- **Even the safest market can jam.** In March 2020, investors sold US Treasury bonds in huge amounts to raise cash. The Federal Reserve reported that some dealers faced balance sheet limits that stopped them buying more. On 15 March it said it would buy at least $500 billion of Treasuries, and on 23 March it widened that to purchases "in the amounts needed".
- **The dealer is not on your side.** A dealer is your counterparty, not your adviser. Its quote reflects what suits its own book.
- **Concentration.** In markets served by a handful of dealers, one or two pulling back can drain liquidity for everyone.

> **Key rule:** market liquidity is someone's balance sheet. When the dealers who provide it are full, or can't fund what they hold, the price of trading jumps.

## Connects to
- [[exchanges]] — where market makers post their prices in an order book.
- [[liquidity]] — dealers turn funding liquidity into market liquidity.
- [[lender-of-last-resort]] — the central bank's role when banks can't borrow; its counterpart for markets is buying when dealers can't.
- [[market-failure]] — what happens when dealers step back from a whole market.
- [[bonds]] — the biggest market that runs through dealers.

## Check yourself

**Q:** A market maker quotes a share at 49.95 bid and 50.05 ask. You buy 2,000 shares and sell them straight back. What does that round trip cost you, and who earns it?

**A:** You pay 50.05 and get 49.95, losing 0.10 × 2,000 = **200**. The market maker earns it, for having stood ready on both sides.

**Q:** Why do spreads widen in a crisis, even on very safe assets?

**A:** Because dealers are already holding more than they want, prices are moving fast, and borrowing to fund more stock is harder. Each extra trade adds risk, so they charge more for it, or step back altogether.

## Going deeper
- **The dealer of last resort.** Mehrling argues that a central bank in a crisis does more than lend to banks. By buying the assets dealers can't hold, it stands behind market prices themselves. The Fed's Treasury purchases in March 2020 are an example of that role.
- **Value traders at the edges.** In Treynor's picture, dealers can only absorb so much. Beyond that, the price has to move far enough to bring in long-term investors who buy because the asset looks cheap, and sell because it looks dear. Where they step in sets the outer edges of the market.
- **Designated market makers.** Some exchanges appoint firms that must keep quoting in particular shares, within limits, in return for advantages such as lower fees.
