# Implementing State Machines In A Database

## The Status Column

> [!info] The simplest implementation — a `status` column that holds the current state of the entity.

```sql
rides table
-----------
id  | status      | updated_at
1   | REQUESTED   | 2026-04-03 10:00
```

To transition state, you UPDATE this column. But naively doing this is wrong:

```sql
-- WRONG — no guard
UPDATE rides SET status = 'MATCHED' WHERE id = 1
```

This runs regardless of what the current status is. If the ride is already COMPLETED, you just set it back to MATCHED. That's a bug.

---

## The WHERE Guard

> [!info] The guard is a condition on the current state in the WHERE clause. If the current state isn't what you expect, the update affects 0 rows.

```sql
UPDATE rides
SET status = 'MATCHED'
WHERE id = 1
AND status = 'REQUESTED'    ← the guard
```

Your application checks the affected row count:

```
1 row affected → transition was valid, current state was REQUESTED ✓
0 rows affected → transition was illegal, current state was something else ✗ → throw error
```

This single line enforces the entire state machine at the database level.

---

## State IS The Version Number

> [!important] This is optimistic locking — the state column is the version number.

Regular optimistic locking:
```sql
UPDATE rides SET status = 'MATCHED'
WHERE id = 1
AND version = 3       ← generic version, tells you something changed
```

State machine approach:
```sql
UPDATE rides SET status = 'MATCHED'
WHERE id = 1
AND status = 'REQUESTED'    ← tells you exactly what state this transition expects
```

The state machine version is **more powerful** — a version number only tells you something changed, but the state tells you whether the right change is happening at the right time.

```
version = 3         → something changed — but what? could be anything
status = REQUESTED  → this entity is specifically in the state
                       this transition requires
```

---

## Concurrency Solved For Free

> [!important] Two servers trying to transition the same entity simultaneously — the database handles it without any explicit locks.

```
Server A and Server B both try to match ride #1 at the same time:

Server A: UPDATE rides SET status = 'MATCHED' WHERE id = 1 AND status = 'REQUESTED'
Server B: UPDATE rides SET status = 'MATCHED' WHERE id = 1 AND status = 'REQUESTED'

Database serializes them:
  Server A executes first → 1 row affected → status is now MATCHED ✓
  Server B executes next  → 0 rows affected → status is already MATCHED, guard fails ✗
```

Server B gets 0 rows affected, detects the conflict, and handles it (retry, error, or ignore).

No explicit locks. No SELECT FOR UPDATE. The atomic nature of a single UPDATE statement does the work.

---

## Enum vs Varchar

```
ENUM   → database enforces valid values at the schema level
         adding a new state requires a schema migration
         slightly faster queries

VARCHAR → application enforces valid values
          adding a new state = just use the new string
          more flexible, slightly looser
```

> [!tip] For SDE-2 interviews, either is fine. Say ENUM if you want to show schema awareness. Say VARCHAR if you want to emphasise flexibility. Just justify your choice.
