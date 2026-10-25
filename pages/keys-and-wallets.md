---
id: keys-and-wallets
title: Keys and Wallets
parent: blockchains
order: 2
summary: What you actually own is a secret key, not a coin. Wallets store keys; the coins stay on the ledger.
tags: digital assets, custody, keys
---
## What it is
Coins never leave the blockchain. What you hold is a **private key**: a secret number that lets you sign transactions moving coins recorded at your **address**. A **wallet** is software or a device that stores keys and signs transactions with them.

## Why it matters
Whoever has the key controls the coins. There is no bank to reverse a payment or reset a password. That is the freedom of a bearer asset, and its main risk.

## How it works
| Piece | What it is | Share it? |
|---|---|---|
| **Private key** | The secret that signs transactions | Never |
| **Seed phrase** | A list of words (often 12 or 24) that can rebuild all your keys | Never |
| **Public key / address** | Where others send you coins | Yes |

**Kinds of wallet:**
- **Hot wallet:** an app on a phone or computer connected to the internet. Convenient, more exposed to malware and phishing.
- **Hardware wallet:** a small device that keeps keys offline and signs inside the device.
- **Multisig wallet:** needs several keys to sign, so one lost or stolen key isn't fatal.
- **Custodial account:** an exchange holds the keys for you. That is a claim on the exchange, not a wallet you control. See [[custodial-crypto]].

## What goes wrong
- **Lost seed phrase:** the coins still exist on the ledger, but can never be moved.
- **Stolen seed phrase:** whoever has it can empty the wallet, with no recourse.
- **Phishing and fake apps** that ask you to type in a seed phrase.
- **Signing a malicious approval:** some token approvals let a program spend your tokens later. Approving the wrong one can drain a wallet without the seed ever leaking.

> **Key rule:** your seed phrase *is* your money. Anyone who asks for it is trying to take it.

## Connects to
- [[self-custody]] — holding your own keys, and how to do it safely.
- [[custodial-crypto]] — letting someone else hold them.

## Check yourself

**Q:** If a hardware wallet is lost or broken, are the coins gone?

**A:** No, as long as the seed phrase is safe. The coins are on the blockchain; the seed phrase can rebuild the keys on a new device. Lose both and the coins can never be moved.
