# Interview Cheatsheet — Transaction Isolation Levels

> [!question] When does isolation come up in an interview?
> When you design any system where two users touch the same data. The interviewer will ask "how do you prevent inconsistent reads?" or "what isolation level do you use?" — this cheatsheet is your answer.

---

## The Four Problems — One Line Each

```
Dirty Read          → read uncommitted data that gets rolled back (phantom money)
Non-Repeatable Read → same row, different value within one transaction
Phantom Read        → new rows appear/disappear within one transaction
Lost Update         → one write overwrites another (race condition = money gone)
```

---

## The Levels — What Each Prevents

| Level | Prevents | Default for |
|---|---|---|
| READ COMMITTED | Dirty reads only | PostgreSQL, Oracle |
| REPEATABLE READ (snapshot) | Dirty + non-repeatable + phantoms | MySQL |
| SERIALIZABLE | All four | — (explicit choice) |

> [!important] Say "snapshot isolation" not just "REPEATABLE READ"
> It shows you know what databases actually implement. PostgreSQL's REPEATABLE READ = snapshot isolation — phantoms prevented too.

---

## Moment 1 — "What isolation level do you use?"

Always state your assumption first:

*"It depends on whether I have explicit locking in place. For a hotel booking with pessimistic locking (SELECT FOR UPDATE), REPEATABLE READ is sufficient — snapshot isolation prevents phantom reads and the explicit lock prevents lost updates. If I'm not using explicit locking, I'd go SERIALIZABLE and let the DB handle conflict detection automatically."*

---

## Moment 2 — "How do you prevent double booking?"

*"Two options — REPEATABLE READ with SELECT FOR UPDATE on the room row: the explicit lock prevents two transactions from booking simultaneously, and snapshot isolation ensures consistent reads throughout. Or SERIALIZABLE without explicit locking: the DB detects the conflicting access pattern and forces one transaction to retry. I'd use the first approach for better performance at scale, stating clearly that developers must remember to use FOR UPDATE on all critical paths."*

---

## Moment 3 — "Why use SERIALIZABLE if locking achieves the same thing?"

*"SERIALIZABLE is a safety net against developer error. REPEATABLE READ + SELECT FOR UPDATE is correct IF every developer remembers to add the lock on every critical query. One missed FOR UPDATE = race condition = money lost. SERIALIZABLE removes that human error risk — the DB enforces correctness automatically. For smaller teams or systems where correctness is non-negotiable, that safety net is worth the performance cost."*

---

## The Isolation + Locking Combination Guide

```
View counter / social feed:
  READ COMMITTED + no locking
  Slight inconsistency acceptable, performance matters

Audit report / multi-step reads:
  REPEATABLE READ (snapshot isolation) + no locking
  Consistent snapshot across all reads in transaction

Hotel booking / order processing:
  Option A: REPEATABLE READ + SELECT FOR UPDATE
  Option B: SERIALIZABLE (if not using explicit locking)
  State your assumption

Payment / bank transfer (high scale):
  REPEATABLE READ + SELECT FOR UPDATE
  Performance at scale, senior engineers handle locking

Payment / bank transfer (safety net):
  SERIALIZABLE
  DB guarantees correctness, no developer error possible

❌ Never: SERIALIZABLE + SELECT FOR UPDATE
  Redundant — paying twice for same guarantee
```

---

## Full Checklist

- [ ] Named the specific isolation level and justified the choice
- [ ] Stated whether explicit locking is in place (changes the answer)
- [ ] Said "snapshot isolation" when discussing REPEATABLE READ
- [ ] Explained what problems the chosen level prevents
- [ ] Mentioned the performance tradeoff of SERIALIZABLE
- [ ] For payments: explained why SERIALIZABLE exists even when locking achieves the same thing

---

## Quick Reference

```
Four problems:
  Dirty Read          → uncommitted data read
  Non-Repeatable Read → same row changes mid-transaction
  Phantom Read        → new rows appear mid-transaction
  Lost Update         → stale write overwrites another write

Four levels (weakest → strongest):
  READ UNCOMMITTED → prevents nothing (never use)
  READ COMMITTED   → prevents dirty reads (PostgreSQL default)
  REPEATABLE READ  → snapshot isolation in practice (prevents 3 of 4)
  SERIALIZABLE     → prevents all four (slowest)

Defaults:
  PostgreSQL → READ COMMITTED
  MySQL      → REPEATABLE READ (snapshot isolation)

Combination rules:
  Low stakes           → READ COMMITTED
  Consistent reads     → REPEATABLE READ
  Critical + locking   → REPEATABLE READ + SELECT FOR UPDATE
  Critical, no locking → SERIALIZABLE
  Never               → SERIALIZABLE + SELECT FOR UPDATE (redundant)
```
