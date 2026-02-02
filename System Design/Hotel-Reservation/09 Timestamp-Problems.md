# Core Problem With Timestamp Locking

It relies on **time** as a correctness signal.

Time is a weak consistency primitive.

Version numbers are deterministic. Time is not.

---

## Problem 1: Timestamp Precision Loss

Most databases store timestamps with limited precision:

- MySQL `DATETIME` → seconds or microseconds depending on config
    
- PostgreSQL `timestamp` → microsecond precision
    
- Application clocks → often milliseconds
    

Now consider this:

Two updates happen within the same timestamp resolution window.

Example:

- Update A at `12:00:01.123`
    
- Update B at `12:00:01.123`
    

Both write the **same timestamp value**.

Result:

- Conflict is NOT detected
    
- Second update overwrites first
    
- Data corruption occurs silently
    

This is not theoretical. It happens under high load.

---

## Problem 2: Clock Synchronization Issues

In distributed systems:

- App servers run on different machines
    
- Clocks drift
    
- NTP sync is not perfect
    

Scenario:

Server A timestamp: `10:00:00.500`  
Server B timestamp: `10:00:00.200`

Server B writes later but has an earlier timestamp.

Now your locking logic breaks:

- Older update may overwrite newer data
    
- Ordering becomes incorrect
    

Version numbers do not have this problem.

---

## Problem 3: Time Zone and Conversion Bugs

Developers regularly mess this up:

- UTC vs local time
    
- Serialization format mismatch
    
- Precision truncation when converting Java `Instant` to SQL `TIMESTAMP`
    
- ORM mapping issues
    

All can cause:

- False update failures
    
- Or worse, missed conflicts
    

Version integers avoid all of this.

---

## Problem 4: Harder to Reason About

With version:

```
version = 5 → version = 6
```

Clear.

With timestamp:

```
2026-01-21 10:00:00.124567
```

Hard to debug.

Hard to compare manually.

Hard to test.

---

## Problem 5: Update Ordering Ambiguity

Timestamp does not guarantee **monotonic increase**.

Example:

Transaction A starts earlier but commits later.

Transaction B starts later but commits earlier.

Depending on implementation:

- Commit order ≠ timestamp order
    
- Breaks optimistic locking semantics
    

Version increments always reflect commit order.

---

## Problem 6: Database Index Inefficiency

Using timestamp in WHERE clause:

```sql
WHERE last_updated_at = ?
```

Is slower than:

```sql
WHERE version = ?
```

Why:

- Integer comparison is faster
    
- Smaller index size
    
- Better cache locality
    

At scale this matters.

---

# When Timestamp Locking Is Acceptable

Rare cases:

- Low concurrency systems
    
- Audit-focused tables
    
- Append-heavy workloads
    
- Soft conflict tolerance
    

Not for financial, inventory, or booking systems.

---

# Industry Practice

Almost every serious system uses:

- Integer version column
    
- Or row hash
    
- Or database native MVCC versioning
    

Examples:

- JPA `@Version` uses integer by default
    
- Hibernate uses version column
    
- CockroachDB uses internal revision numbers
    
- PostgreSQL uses system column `xmin`
    

Not timestamps.

---

# Brutal Summary

Timestamp locking:

- Looks simple
    
- Fails under pressure
    
- Breaks in distributed setups
    
- Causes silent data bugs
    

Version locking:

- Deterministic
    
- Safe
    
- Faster
    
- Easier to debug
    
- Production proven
    

---

# Correct Recommendation

If you are building real systems:

Use:

```
version INT NOT NULL
```

Never rely on time for concurrency control.