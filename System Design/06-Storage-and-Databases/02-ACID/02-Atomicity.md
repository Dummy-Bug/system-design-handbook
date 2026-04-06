# Atomicity

> [!info] Atomicity — all operations in a transaction succeed together, or none of them happen. No partial state ever persists.

---

## The guarantee

A transaction is an indivisible unit. From the database's perspective, a transaction either happened completely or never happened at all. There is no observable in-between.

```
Transfer $100 (Alice → Bob):

Without atomicity:
  Step 1: Deduct $100 from Alice  ✓
  CRASH
  Step 2: Add $100 to Bob         ✗  (never ran)
  → corrupt state: Alice debited, Bob untouched, $100 missing

With atomicity:
  Step 1: Deduct $100 from Alice  ✓
  CRASH
  → rollback triggered automatically
  → Alice's $100 restored to original value
  → as if the transaction never started ✓
```

---

## How the database achieves it — the WAL

The database uses a **Write-Ahead Log (WAL)** to make rollback possible. Before applying any change to actual data, it writes a log entry describing what it's about to do and what the previous value was.

```
Transaction starts:
  WAL entry: "going to deduct $100 from Alice (current: $500)"
  → deduct $100 → Alice now $400

  WAL entry: "going to add $100 to Bob (current: $300)"
  CRASH  ← before this step runs

On recovery:
  → DB reads WAL
  → sees incomplete transaction (deduct logged, credit not committed)
  → uses WAL entry to reverse: Alice restored to $500
  → clean state ✓
```

The WAL is always written first, always to disk, before any changes to actual data. That's what "write-ahead" means — the log precedes the action.

---

## Rollback vs crash recovery

Atomicity works in two scenarios:

**Explicit rollback** — your application code decides to abort:
```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 'alice';
-- discover Alice has insufficient funds
ROLLBACK;  -- Alice's balance restored, no partial state
```

**Crash recovery** — the server dies mid-transaction:
```
DB restarts → replays WAL → finds uncommitted transaction → rolls it back
→ clean state, as if the transaction never ran
```

Both end in the same place: no partial state persists.

---

## What atomicity does NOT protect against

Atomicity protects against partial completion within a single database. It does not help you when:

```
DB write succeeds → app tries to publish to Kafka → Kafka publish fails
→ DB has the data, Kafka doesn't → inconsistency between two systems
```

This is the dual-write problem — atomicity only spans a single transaction boundary on a single database. For cross-system atomicity, you need the **Outbox Pattern** (covered in CDC section).
