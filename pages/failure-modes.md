---
id: failure-modes
title: When Things Fail
short: When Things Fail
parent: capital-system
order: 9.5
group: Putting it together
summary: The failure ladder: every layer between you and your wealth, what is meant to protect you, and where that protection runs out.
tags: risk, failure, backstops, history
sources: Carmen Reinhart and Kenneth Rogoff, This Time Is Different (2009); Study notes
---
## What it is
Every store of wealth sits behind a stack of institutions: a broker, a bank, a clearing house, a currency, a government. **When Things Fail** walks that stack as a ladder. Each rung is one layer that can fail. Each page asks the same four questions:
- **What fails**, and what it promised you.
- **The backstop:** what is supposed to protect you.
- **Where the backstop runs out:** limits, exclusions, delays and discretion.
- **What it kills:** which stores on the [[cartography-of-wealth|Cartography of Wealth]] it hits.

## Why it exists
[[diversification]] protects against things that fail for different reasons. To use it, you have to know the reasons. A portfolio of ten funds at one broker, in one currency, in one country, is spread across names but not across failures. The ladder makes the shared layers visible.

It also keeps the picture honest. Most failures are partly cushioned: customers of failed brokers have often been repaid, and depositors are usually protected. The question is never "is there a backstop?" but "how big is it, and when does it stop?"

## How it works
The rungs run from the firm closest to you up to the system itself. The higher the rung, the more stores it hits at once, and the fewer places there are to hide.

| # | Rung | Page | Typical backstop |
|---|---|---|---|
| 1 | Broker, exchange or custodian | [[broker-failure]] | Segregated client assets; investor protection schemes |
| 2 | Insurer or guarantor | [[insurer-failure]] | Reserves; guarantee schemes up to a limit |
| 3 | Stablecoin issuer | [[stablecoins]] | Reserves, if they're there |
| 4 | Bank | [[backstops]] | Capital, the central bank, deposit insurance, bail-in |
| 5 | Clearing house | [[clearing-house-failure]] | Margin and a default fund |
| 6 | Ratings and gatekeepers | [[ratings-failure]] | None: they inform, they don't insure |
| 7 | Capital controls and freezes | [[capital-controls]] | None: the state is the one acting |
| 8 | Confiscation | [[confiscation]] | Courts, constitutions, compensation |
| 9 | Quiet default through inflation | [[financial-repression]] | Real assets and inflation-linked bonds, partly |
| 10 | The currency | [[currency-failure]] | Other currencies, real assets |
| 11 | The country | [[sovereign-default]] | IMF lending and debt restructuring |
| 12 | The market itself | [[market-failure]] | Central bank buying; time |

The bank and stablecoin rungs link to pages elsewhere on the map, where they're covered in depth.

**Two patterns repeat.**
- **Backstops are layered and linked.** Deposit insurance relies on the government; the government's bonds sit inside the banks. When a lower rung fails, it leans on the one above. See [[bank-sovereign-loop]].
- **Whoever runs the backstop decides.** Above-limit deposits were protected in the US in 2023 and not in Cyprus in 2013. Discretion cuts both ways.

## What goes wrong
- **Counting names instead of rungs.** Many accounts at one broker, or many banks in one country, share the same rungs.
- **Treating a backstop as a guarantee.** Limits, delays, exclusions and changing rules decide what you actually get back.
- **Ignoring the top of the ladder.** Currency and country failures are rare in rich countries over any one decade, and common across history. Reinhart and Rogoff's study of eight centuries found sovereign default to be routine, not exceptional.
- **Doom instead of design.** The aim isn't to fear every rung but to make sure no single one can clear the board.

> **Key rule:** for every store you own, name the rungs it sits behind. Spread across rungs, not just across names.

## Connects to
- [[cartography-of-wealth]] — each store's killer, which the ladder sorts by layer.
- [[backstops]] — the bank rung in depth.
- [[diversification]] and [[correlation]] — why shared rungs make holdings fail together.
- [[claims-and-liabilities]] — every rung above you is someone's promise.

## Check yourself

**Q:** You hold shares in three different funds, all through one broker. Which rung do all three share?

**A:** The broker. If it fails, all three holdings are affected at once, however different the funds are. See [[broker-failure]].

**Q:** Why do higher rungs on the ladder do more damage?

**A:** Because they sit behind more stores at once. A broker failure hits what that broker holds; a currency collapse or a closed market hits every store priced, held or sold there.

## Going deeper
- **Failure mode and effects analysis.** Engineers list every way a system can fail, how likely and how severe each is, and what detects it. The ladder is the same exercise applied to wealth: each rung is a failure mode, each backstop a control, and each page's limits section is where the control stops working.
- **Correlation at the top.** Rungs high on the ladder tend to fail together: a country in crisis often brings currency loss, capital controls and bank failures at once. See the flow *When a country fails*.
