---
id: privacy-and-traceability
title: Privacy and Traceability
short: Privacy
parent: blockchains
order: 4
summary: Why a public ledger is pseudonymous, not anonymous, and how coins get linked back to people.
tags: digital assets, privacy, anonymity, chain analysis, regulation
sources: Narayanan et al., Bitcoin and Cryptocurrency Technologies (Princeton), ch. 6; FATF, Interpretive Note to Recommendation 15 (2019); US Treasury OFAC, Tornado Cash designation (2022) and delisting (2025)
---
## What it is
A public blockchain records every transaction forever, where anyone can read it. It doesn't record names; it records **addresses**. That makes it **pseudonymous**, not anonymous: your identity is hidden only until something links an address to you. Once it is linked, your whole history on that address, and often on the addresses connected to it, becomes visible.

## Why it matters
Bank records are private by default, but the bank and the state can see them. A public ledger is the reverse: anyone can see every payment, but not, at first, who made it. That sits behind the [[cartography-of-wealth|Cartography of Wealth]] placing self-held crypto as "private if done right". Done carelessly, it can be the most traceable money there is, because the record can't be deleted.

## How it works
**How addresses get linked to people:**
- **On-ramps and off-ramps.** Exchanges and brokers that swap crypto for ordinary money must check customers' identity in most countries. Every coin that passes through them is tied to a name. See [[custodial-crypto]].
- **The Travel Rule.** Since 2019, the Financial Action Task Force's standards require crypto service providers to pass on details of who is sending and receiving transfers, much as banks do for wires. Countries set their own thresholds.
- **Clustering.** Analysts group addresses that are probably controlled by the same person. A common rule: when one transaction spends coins from several addresses, those addresses likely share an owner, because one person had to sign for all of them.
- **Change and reuse.** Spending usually sends leftover "change" to a new address of your own, which analysts try to spot. Reusing one address for many payments links them all directly.
- **Everyday leaks.** Posting an address publicly, buying something delivered to your home, or the timing and amounts of payments can all connect an address to a person.

**Chain analysis** firms combine these clues at scale and sell the results to exchanges, banks and law enforcement. Their labels are estimates, not proof. See [[data-sources]].

**Tools built for privacy:**
- **Mixers** pool many users' coins and pay them out to fresh addresses, to break the visible link between sender and receiver.
- **Privacy coins** such as Monero and Zcash use cryptography to hide amounts or the parties to a payment, by default or as an option.

Both are under legal pressure. In August 2022 the US Treasury sanctioned the Ethereum mixer Tornado Cash. In November 2024 a US appeals court ruled that its self-running smart contracts weren't property that could be sanctioned, and the Treasury removed the sanctions in March 2025. Several exchanges have stopped listing privacy coins.

## What goes wrong
- **Mistaking pseudonymity for anonymity.** Many people have been identified years later from a single linked address.
- **Permanent records.** A payment that is private today may be traced tomorrow, as analysis improves and old data is joined to new.
- **Tainted coins.** Coins linked to theft, sanctions or mixers can be frozen or refused by exchanges, even after passing through several honest hands.
- **Legal risk.** Privacy tools are lawful in some places and restricted in others, and the rules keep changing.
- **Security trade-off.** Publicly linking an address to your identity can tell others how much you hold, which is a physical security risk. See [[self-custody]].

> **Key rule:** treat every address as public and permanent. Privacy on a public ledger is something you keep or lose with every transaction, not a feature you get by default.

## Connects to
- [[keys-and-wallets]] — how addresses are made, and why a fresh one per payment helps.
- [[blockchains]] — the public record underneath.
- [[bitcoin]] — the ledger the Princeton course studies.
- [[cash-and-fiat]] — physical cash: private, but limited in size and reach.

## Check yourself

**Q:** Why is Bitcoin called pseudonymous rather than anonymous?

**A:** Because every transaction is public and permanent, and only names are left out. Once an address is linked to a person, for example through an exchange that checked their identity, their history on it can be read by anyone.

**Q:** One transaction spends coins from three different addresses. What do analysts usually assume, and why?

**A:** That one person controls all three, because spending from each address needs its own key, and one transaction is usually signed by one owner.
