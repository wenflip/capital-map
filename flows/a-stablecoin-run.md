---
id: a-stablecoin-run
title: A stablecoin run: a bank run on a blockchain
area: When Things Fail
order: 6
summary: Follow a stablecoin losing its dollar peg, from the first doubt to who is left holding the token.
---
Rung 3 of the [[failure-modes|failure ladder]], step by step. A stablecoin is a private dollar promise, and it can suffer the same kind of run as a bank.

> **Key rule:** a stablecoin is worth what its issuer can actually pay, when you need it. Doubt about either the reserves or the timing is enough to start a run.

| Step | Page | What happens | What you hold | What can go wrong | Where it happened |
|---|---|---|---|---|---|
| Holders start to doubt the reserves | [[stablecoins]] | News about the issuer, its bank or its design makes holders ask whether a dollar is really there | A token that promises one dollar | Reserves are only as safe as what they are and where they're kept | USDC, March 2023: its issuer, Circle, said $3.3 billion of its reserves were at Silicon Valley Bank, which had just failed |
| The price slips below one dollar | [[stablecoins]] | Sellers outnumber buyers on exchanges | A token trading at a discount | A small discount can feed on itself as more holders sell | USDC fell below 87 cents on 11 March 2023 |
| Holders rush to redeem or sell | [[liquidity]] | Those who can redeem with the issuer do; everyone else sells on the market | Whatever the market pays | Redemption may be open only to large customers, or wait for banks to open | TerraUSD, May 2022: an algorithmic stablecoin lost its peg and collapsed within days, taking its partner token with it |
| The issuer sells reserve assets to pay them | [[t-bills]] | The issuer sells bonds or withdraws bank deposits to meet redemptions | A claim on a shrinking pool of reserves | Selling in a hurry at a loss, or deposits stuck in a failed bank | — |
| Exchanges and lending protocols holding the token are hit | [[defi]] | Loans backed by the token are liquidated, and other tokens built on it slip too | Exposure you may not know you have | Losses reach people who never held the token directly | DAI, a stablecoin backed partly by USDC, fell as low as 88 cents the same weekend |
| Tokens are frozen, redeemed in full, or left worth less | [[claims-and-liabilities]] | Either the reserves prove good and the peg returns, or holders share what is left | A dollar again, or a fraction of one | Rescues are not promised; the outcome depends on what is behind the token | USDC returned close to one dollar after US authorities said on 12 March 2023 that all the failed bank's depositors would be paid in full. TerraUSD never recovered |

## What to notice
- **Same run, new wrapper.** Doubt, a discount, a rush to the exit and a fire sale of assets: the steps match [[backstops|a bank run]], but with no deposit insurance and no central bank behind the token.
- **A stablecoin can be hit by a bank failure.** USDC's trouble began with its own bank, rung 4, one rung above stablecoins on the ladder. Failures pass between rungs; see [[bank-sovereign-loop]] for the bank-and-government version.
- **Backed by what?** A token backed by cash and short-term government debt can come back; one backed mainly by its own partner token has nothing to fall back on.

*Sources: CNBC, Stablecoin USDC breaks dollar peg after firm reveals it has $3.3 billion in SVB exposure (11 March 2023); The Block, USDC and DAI remain at about $0.90 following Circle's disclosure of funds at SVB (March 2023); Federal Reserve, Joint statement by Treasury, Federal Reserve, and FDIC (12 March 2023); Benzinga, USD Coin returns to $1 peg after nail-biting weekend (13 March 2023).*
