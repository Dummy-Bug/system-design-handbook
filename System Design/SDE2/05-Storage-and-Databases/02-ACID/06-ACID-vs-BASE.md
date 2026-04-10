# ACID vs BASE

> [!question] ACID gives you strong guarantees — but every guarantee has a cost. At massive scale, some systems can't afford those costs. What do you trade away, and what do you get in return?

---

## The cost of each ACID property

ACID is not free. Each property adds overhead to every write:

```
Atomicity  → rollback log maintained for every transaction
             on crash: WAL must be replayed to undo partial work

Consistency → constraint checks run on every INSERT and UPDATE
              foreign key lookups, uniqueness scans, check evaluations

Isolation  → snapshot management (MVCC versions of rows kept)
             or locking (readers/writers block each other)
             reduced concurrency under high load

Durability → fsync() on every commit — physical disk write before returning
             slowest operation in the chain
```

At 1,000 writes/second: manageable.
At 1,000,000 writes/second: fsync latency, lock contention, and constraint checks become bottlenecks.

---

## BASE — the alternative

High-scale NoSQL systems (Cassandra, DynamoDB, MongoDB) often relax ACID guarantees in exchange for performance and availability. The trade-off is described as **BASE**:

```
BA — Basically Available
     System remains operational even during partial failures
     (some nodes down → others still serve requests)

S  — Soft State
     Data may be temporarily inconsistent across nodes
     (replicas may have slightly different values)

E  — Eventually Consistent
     Given enough time with no new writes, all replicas converge
     to the same value
```

BASE is not a database feature you configure — it's a description of the guarantees you get (and don't get) from systems that prioritise availability over consistency.

---

## What you give up with BASE

```
ACID guarantee        What BASE systems may allow
─────────────────────────────────────────────────
Atomicity             Partial writes visible during failure windows
Consistency           Replicas temporarily disagree on a row's value
Isolation             Concurrent writes can result in lost updates
Durability            Async replication means recent writes can be lost
                      if a node fails before replicating
```

---

## The consistency window

The key concept in BASE is the **consistency window** — the period during which replicas may disagree.

```
User updates profile picture:
  → write goes to Node A
  → Node A replicates to Node B async (50ms later)

During those 50ms:
  → User reads from Node A → sees new photo ✓
  → User reads from Node B → sees old photo ✗ (stale)

After 50ms:
  → Node B catches up → both nodes agree → consistent ✓
```

For many use cases, a 50ms inconsistency window is completely acceptable:

```
Instagram profile picture    → 50ms stale: nobody notices
Twitter follower count       → slightly stale: acceptable
Amazon shopping cart         → briefly stale: acceptable

Bank account balance         → stale: unacceptable
Stock trade execution        → stale: unacceptable
Hotel room availability      → stale: leads to double booking ✗
```

---

## Choosing between ACID and BASE

```
Use ACID when:
  ✓ Financial data — balance errors are real-world losses
  ✓ Inventory — overselling is a customer support disaster
  ✓ Bookings — double booking destroys trust
  ✓ Any system where partial failure = data corruption

Use BASE (relaxed consistency) when:
  ✓ Social feeds, likes, follower counts — slightly stale is invisible
  ✓ Analytics, metrics — approximate counts are fine
  ✓ User preferences — milliseconds of lag don't matter
  ✓ Caches — stale by design
  ✓ High write throughput where ACID overhead is the bottleneck
```

> [!tip] Interview framing
> "I'd use a fully ACID-compliant database for the payment and booking tables — correctness is non-negotiable there. For the activity feed and analytics, I'd use an eventually consistent store — the write volume is too high to afford fsync on every event, and brief staleness is invisible to users."

The ability to consciously choose which parts of your system need ACID and which can tolerate BASE — and justify why — is exactly what a strong hire demonstrates.
