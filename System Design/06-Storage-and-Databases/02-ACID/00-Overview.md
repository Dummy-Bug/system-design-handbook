# ACID Properties — Overview

> [!abstract] ACID is the set of four guarantees that make a database safe to use for anything that matters — money, bookings, orders, inventory. Every serious relational database is ACID-compliant. Understanding what each property actually does (and what it costs) is what separates candidates who can recite the acronym from candidates who can design correct systems.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-The-Problem.md | Why ACID exists — the banking transfer failure scenario |
| 02-Atomicity.md | All or nothing — no partial transactions, ever |
| 03-Consistency.md | Valid state to valid state — constraints always enforced |
| 04-Isolation.md | Concurrent transactions don't interfere with each other |
| 05-Durability.md | Committed data survives crashes, power loss, anything |
| 06-ACID-vs-BASE.md | The cost of ACID, when you can relax it, and what BASE means |
| 07-Interview-Cheatsheet.md | When and how to use ACID in a design round |

---

## The one-line mental model

```
Atomicity  → all or nothing
Consistency → your rules are always enforced
Isolation  → concurrent transactions don't see each other's half-done work
Durability → "success" means it's on disk, forever
```
