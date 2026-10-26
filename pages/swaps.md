---
id: swaps
title: Swaps
parent: derivatives
order: 2.5
summary: Two parties agree to exchange streams of payments for years: fixed interest for floating, one currency for another, or regular premiums for protection against a default.
tags: derivatives, swaps, interest rate swap, credit default swap, cds, total return swap
sources: FCA, The USD LIBOR panel ceases at end-June 2023 (2023); G20 Leaders' Statement, Pittsburgh Summit (September 2009); Yale Program on Financial Stability, The rescue of AIG: revolving credit facility; ESMA, Leverage and derivatives: the case of Archegos
---
## What it is
A **swap** is a contract in which two parties agree to exchange streams of payments over a period, often years. Each payment is worked out on an agreed amount called the **notional**. In most interest-rate swaps the notional itself never changes hands; it is only the number the payments are calculated on.

There are four main kinds:

| Swap | What is exchanged | Typical use |
|---|---|---|
| **Interest-rate swap** | A fixed rate for a floating rate, in one currency | Turning a floating-rate loan into a fixed one, or the reverse |
| **Currency swap** | Payments in one currency for payments in another | Borrowing in one currency while spending in another |
| **Credit default swap** (CDS) | Regular premiums for a payout if a borrower defaults | Insuring a bond, or taking a view on a borrower's credit |
| **Total return swap** | Everything an asset earns, for a financing fee | Getting an asset's gains and losses without owning it |

## Why it exists
Swaps let a firm keep the funding it can get and change the risk it carries. A company may only be able to borrow at a floating rate but want predictable costs; a pension fund may want long-term interest income without buying more bonds; a bank may want to shed the credit risk of one big borrower without selling the loan. A swap moves that one risk to someone who wants it, and leaves everything else in place.

## How it works
**Interest-rate swap.** Say a company agrees to pay a fixed 4% a year on a notional of 10,000,000 and receive a floating reference rate (fictional figures). Only the difference is paid:
- In a year when the reference rate is 3%, the company pays (4% − 3%) × 10,000,000 = **100,000**.
- In a year when it is 5.5%, the company receives (5.5% − 4%) × 10,000,000 = **150,000**.

Now add the company's floating-rate loan at the reference rate plus 1%. It pays the reference rate plus 1% to the bank, receives the reference rate from the swap and pays 4%. The floating parts cancel, so its cost is 1% + 4% = **5%**, or **500,000** a year, whatever rates do. That is the whole point: the swap turned an unknown cost into a known one.

**Reference rates.** For decades many swaps were tied to LIBOR, a rate set from banks' own estimates of what they could borrow at. Sterling LIBOR's panel ended at the end of 2021 and US dollar LIBOR's on 30 June 2023. Swaps moved to overnight rates built from real trades, such as SOFR for US dollars and SONIA for sterling.

**Currency swaps.** The two sides swap payments in two currencies, often swapping the amounts back at the end. A firm earning in one currency can borrow in another and swap the payments into the money it earns. Short-term **FX swaps** are the most-traded instrument in the currency market, and the US central bank uses them to lend dollars to other central banks in a crisis. See [[exchange-rates]] and [[eurodollars]].

**Credit default swaps.** The buyer pays a regular premium; the seller pays out if a named borrower defaults. Say you buy protection on 10,000,000 of a company's bonds at 2% a year, so **200,000** a year (fictional figures). The company defaults and its bonds recover 40% of their value. The seller pays the loss: 10,000,000 × (1 − 0.40) = **6,000,000**. Unlike insurance, you don't need to own the bonds to buy the protection. See [[credit-risk]].

**Total return swaps.** A bank holds an asset, such as a block of shares, and pays you everything it earns: price gains and dividends. You pay the bank any price losses plus a financing fee. You get the exposure of an owner without owning, and usually for only a small deposit. See [[leverage]].

**Who stands between the sides.** Most swaps are agreed privately rather than on an exchange. After 2008, the G20 agreed in September 2009 that standard contracts should be cleared through central clearing houses, with collateral posted against daily moves. See [[settlement]] and [[clearing-house-failure]].

## What goes wrong
- **The other side can't pay.** A swap is a promise that can last for years. On 16 September 2008 the US central bank announced an emergency credit line of $85 billion for AIG, an insurer that had sold huge amounts of credit protection and faced collateral calls from its CDS buyers. Protection is only worth as much as the seller.
- **Hidden leverage.** Total return swaps give the risk of owning shares without the shares appearing in the owner's name. The family office Archegos built concentrated positions this way through several banks, none of which saw the whole picture. When it failed to meet margin calls in March 2021, the banks lost more than $10 billion. See [[derivatives]].
- **Collateral calls in a fast market.** A swap that is fine over ten years can demand large amounts of cash in a single week if rates jump, and forced selling to raise that cash can push prices further.
- **The notional looks frightening, and misleads both ways.** Total notional amounts are huge, but the money actually at risk is usually far smaller. The reverse also holds: a modest-looking market value can grow fast when prices move.

> **Key rule:** a swap swaps one risk for another. You always keep the risk that the other side won't pay, so ask who they are and what collateral backs the promise.

## Connects to
- [[futures]] — a swap works like a string of forward agreements, one for each payment date.
- [[bonds]] and [[yield-curve]] — what interest-rate swaps change, and where the fixed swap rate comes from.
- [[credit-risk]] — what credit default swaps price.
- [[exchange-rates]] — what currency swaps manage.
- [[leverage]] — what total return swaps can hide.

## Check yourself

**Q:** A bank pays a fixed 3% and receives the floating rate on a notional of 5,000,000. The floating rate is 4.2% this year. What is the net payment, and who pays?

**A:** The bank receives (4.2% − 3%) × 5,000,000 = **60,000**. The side paying fixed gains when floating rates rise above the fixed rate.

**Q:** Why did AIG's sale of credit protection end up needing an emergency loan?

**A:** Because a seller of protection takes on the very risk it is paid for. When credit fears rose all at once, its buyers demanded collateral at the same time. Insurance that fails exactly when it is needed is the core danger of credit derivatives.

## Going deeper
- **The swap rate.** The fixed rate on a new swap is set so the deal is worth zero to both sides at the start. Across maturities, swap rates form a curve that is used, like government bond yields, as a benchmark for pricing loans and bonds.
- **Valuing a swap later.** Once rates move, one side's stream is worth more than the other's. The value of the swap is the difference between the two streams, each discounted back to now. See [[time-value-of-money]].
- **Master agreements.** Privately agreed swaps usually sit under one standard master contract per pair of firms. It sets how payments are netted, what collateral is posted, and what happens if one side defaults.
