> [!abstract] Isolation levels are the formal specification of how much one transaction can see of another's in-progress work. Too little isolation — race conditions and dirty reads. Too much — performance collapses. This folder covers the four problems, the four levels, and how to choose the right combination for any system.

---

## The Four Standard Levels

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Lost Update |
|---|---|---|---|---|
| READ UNCOMMITTED | ❌ possible | ❌ possible | ❌ possible | ❌ possible |
| READ COMMITTED | ✅ prevented | ❌ possible | ❌ possible | ❌ possible |
| REPEATABLE READ | ✅ prevented | ✅ prevented | ❌ possible | ❌ possible |
| SERIALIZABLE | ✅ prevented | ✅ prevented | ✅ prevented | ✅ prevented |

> [!tip] READ UNCOMMITTED is never used in practice — it prevents nothing meaningful.

---

## READ COMMITTED

> The default for PostgreSQL.

**What it guarantees:** You only ever read committed data. No dirty reads.

**What it allows:** Non-repeatable reads, phantom reads, lost updates.

```sql
-- This is fine under READ COMMITTED:
BEGIN;
SELECT balance FROM accounts WHERE id = 123;  -- 1000
-- another transaction commits balance = 1500
SELECT balance FROM accounts WHERE id = 123;  -- 1500 (different result — allowed)
COMMIT;
```

**Use when:** High-volume, low-stakes operations where slight inconsistency is acceptable. View counters, social feeds, analytics.

---

## REPEATABLE READ

> The default for MySQL. But not what you think.

**Textbook definition:** Prevents dirty reads + non-repeatable reads. Phantom reads still possible.

**Reality — Snapshot Isolation:**
Most modern databases (PostgreSQL, Oracle, SQL Server) implement **snapshot isolation** when you set REPEATABLE READ — which also prevents phantom reads.

```
Textbook REPEATABLE READ → prevents 2 of 4 problems
Snapshot Isolation        → prevents 3 of 4 problems
```

PostgreSQL's REPEATABLE READ = Snapshot Isolation. You get phantom read protection for free.

**How snapshot isolation works:**
```
Transaction starts → database takes a snapshot of current state
Every read within the transaction → sees data from that snapshot
Other transactions commit new data → your snapshot doesn't change
Phantom rows can't appear → your snapshot is frozen
```

**Use when:** Multi-step operations needing consistency — hotel bookings, order processing, audit reports.

---

## SERIALIZABLE

> Full isolation. Transactions behave as if they ran one after another, never concurrently.

**What it guarantees:** All four problems prevented. No dirty reads, no non-repeatable reads, no phantoms, no lost updates.

**How it works:** Database detects conflicting access patterns and forces transactions to wait or retry — not just snapshot isolation but actual conflict detection.

**The cost:** Significant performance overhead. More locking, more waiting, lower throughput.

**Use when:** Financial transactions, payment processing — anywhere correctness is non-negotiable and the cost of a bug exceeds the cost of slower performance.

---

## The Gap — Why Snapshot Isolation Exists

Standard levels jump from REPEATABLE READ (2 problems prevented) to SERIALIZABLE (all 4). There's a gap:

```
READ COMMITTED    → prevents: dirty reads only
REPEATABLE READ   → prevents: dirty reads + non-repeatable reads (textbook)
                  → prevents: dirty reads + non-repeatable + phantoms (actual — snapshot isolation)
SERIALIZABLE      → prevents: all four
```

Snapshot isolation fills the gap — it's what real databases use because it's cheaper than SERIALIZABLE but safer than textbook REPEATABLE READ.

---

## Default Isolation Levels

| Database | Default | What it actually gives you |
|---|---|---|
| PostgreSQL | READ COMMITTED | Only dirty read prevention |
| MySQL | REPEATABLE READ | Snapshot isolation (phantom reads prevented too) |
| Oracle | READ COMMITTED | Only dirty read prevention |
| SQL Server | READ COMMITTED | Only dirty read prevention |

> [!warning] PostgreSQL's default (READ COMMITTED) leaves non-repeatable reads, phantom reads, and lost updates possible. For anything beyond simple reads — explicitly set a higher isolation level.
