# Optimistic Locking

## What it is

> [!info] Optimistic locking assumes conflict WON'T happen. Don't lock anything — but verify nothing changed before writing. If it did change, someone else got there first — retry.

**When to use:** Low contention — conflicts are rare. User updating their own profile, editing a document, updating personal settings.

---

## How It Works — Version Numbers

Every row has a `version` column. Read it, remember it, check it before writing.

```
User A reads:  bio = "hello", version = 5
User A edits:  bio = "hello world"
User A writes: UPDATE WHERE version = 5 → set version = 6

→ 1 row updated → success ✓
→ 0 rows updated → someone else changed it → conflict → retry
```

**In SQL:**
```sql
-- Read
SELECT bio, version FROM users WHERE id = 123;
-- Returns: bio = "hello", version = 5

-- Write (atomic check + update)
UPDATE users
SET bio = 'hello world', version = 6
WHERE id = 123 AND version = 5;

-- Check rows affected:
-- 1 row → success
-- 0 rows → conflict, retry
```

The `WHERE version = 5` is the key — if anything changed that version between your read and write, the update finds 0 matching rows. Conflict detected.

---

## Version Number vs Timestamp

Both work for conflict detection:

| | Version Number | Timestamp |
|---|---|---|
| How | Increment integer on every write | Store last_updated datetime |
| Problem | None | Clock skew — two servers may have slightly different clocks, timestamp comparison unreliable |
| **Preferred** | ✅ Yes | Use only if version column not possible |

---

## What Happens on Conflict

```
User A reads version = 5
User B reads version = 5
User B writes → version becomes 6 (B wins)
User A writes WHERE version = 5 → 0 rows → conflict

User A options:
  1. Retry → re-read (now sees version = 6) → recompute → write WHERE version = 6
  2. Show error → "someone else updated this, please refresh"
  3. Merge changes → if possible (like Google Docs)
```

For most systems — retry is fine. For collaborative editing — merge.

---

## When Optimistic Locking Breaks Down

> [!danger] Optimistic locking assumes conflicts are RARE. If that assumption breaks — performance degrades badly.

```
100 users try to update same row simultaneously (high contention)
All read version = 5
All compute their change
All write WHERE version = 5
1 succeeds → version = 6
99 fail → all retry
99 read version = 6
1 succeeds → version = 7
98 fail → retry again
...
```

This is **livelock** — everyone retrying, system hammered, progress extremely slow.

> [!important] The decision rule
> ```
> High contention → Pessimistic (prevent conflicts upfront)
> Low contention  → Optimistic  (detect and retry cheaply)
> ```
> Choose based on expected contention of that specific resource — not dynamically at runtime.
