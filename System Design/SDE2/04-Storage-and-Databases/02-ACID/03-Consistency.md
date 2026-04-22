# Consistency

> [!info] Consistency — the database always moves from one valid state to another valid state. Your defined rules are never violated.

---

## The guarantee

You define what "valid" means for your data — through constraints, foreign keys, check rules, and type definitions. The database enforces these on every write. If a write would violate any rule, the entire transaction is rejected.

```
Alice balance: $50
Transfer attempt: $100

Without consistency:
  Deduct $100 → Alice balance = -$50
  → database allows negative balance
  → invalid state persists ✗

With consistency:
  Deduct $100 → balance would be -$50
  → violates CHECK constraint: balance >= 0
  → transaction rejected
  → database stays at Alice = $50, valid state ✓
```

---

## How you define consistency — constraints

Consistency is only as strong as the rules you write. The database enforces whatever you tell it to enforce.

```sql
-- No negative balances
ALTER TABLE accounts ADD CONSTRAINT positive_balance CHECK (balance >= 0);

-- Every email must be unique (no duplicate accounts)
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);

-- Every order must reference a real user
ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id);

-- Status can only be one of defined values
ALTER TABLE bookings ADD CONSTRAINT valid_status 
  CHECK (status IN ('pending', 'confirmed', 'cancelled'));
```

Each constraint is a rule the database checks automatically on every INSERT and UPDATE. You write it once; the database enforces it forever.

---

## What consistency protects against

```
Accidental negative balances     → CHECK (balance >= 0)
Duplicate account emails         → UNIQUE constraint
Orphaned records (order for      → FOREIGN KEY constraint
non-existent user)
Invalid status transitions       → CHECK (status IN (...))
Wrong data type stored           → column type definition
```

---

## An important nuance — C in ACID vs C in CAP

These are two different things that share the same letter. This confuses many candidates.

**C in ACID (this file)** — constraint enforcement within a single database. "No write will leave the database in a state that violates your defined rules."

**C in CAP theorem** — linearizability across distributed nodes. "All nodes see the same data at the same time."

They are completely unrelated concepts. In an interview, always clarify which C you mean when both topics are in play.

> [!danger] Common trap
> "I'll use a consistent database" can mean two completely different things depending on context. If you're talking about constraints and rules → ACID consistency. If you're talking about distributed systems and whether nodes agree → CAP consistency. Don't conflate them.

---

## What consistency does NOT protect against

Consistency enforces your rules — but only the rules you defined. It doesn't protect against:

```
Business logic bugs   → constraint says balance >= 0
                        but you forgot to add the constraint → no protection

Application errors    → your code deducts the wrong amount
                        → constraint is satisfied, data is still wrong

Concurrent anomalies  → two transactions simultaneously read balance = $100
                        both try to deduct $100 → both pass the check
                        → balance goes to -$100 (race condition)
                        → this is an Isolation problem, not a Consistency problem
```

The last point is critical. Preventing concurrent anomalies is the job of **Isolation**, not Consistency.
