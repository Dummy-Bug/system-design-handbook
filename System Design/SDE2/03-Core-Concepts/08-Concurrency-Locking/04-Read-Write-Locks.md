# Read-Write Locks

## The Problem with Regular Locks

Regular pessimistic locks treat reads and writes the same — only one thread at a time, full stop.

```
User A reading article  → locks row
User B wants to read    → waiting...
User C wants to read    → waiting...
```

Readers blocking readers makes no sense — reads don't modify data, two simultaneous reads can never conflict.

---

## What Read-Write Locks Do

> [!info] Read-Write locks distinguish between reads and writes — multiple readers can proceed simultaneously, writers get exclusive access.

```
Rule:
  Multiple readers simultaneously  → allowed ✓
  One writer at a time             → allowed ✓
  Reader + Writer simultaneously   → NOT allowed ✗
```

---

## How It Works

```
User A reading article  → acquires READ lock
User B reading article  → acquires READ lock  ✓ (readers don't block readers)
User C reading article  → acquires READ lock  ✓
1M users reading        → all concurrent, no waiting ✓

Editor wants to update  → tries WRITE lock
                        → readers holding read locks → editor waits
All readers finish      → editor acquires WRITE lock (exclusive)
Editor updates article  → releases write lock
New readers come in     → READ locks again
```

---

## Where It's Useful

| System | Reads | Writes | Benefit |
|---|---|---|---|
| News website | Millions/day | Few per day | All readers concurrent, brief write pause |
| Config service | Every request reads config | Rare updates | Zero read contention |
| Leaderboard | Everyone reads rankings | Periodic recalculation | Reads never block each other |
| Bank balance | Multiple services read | Payment writes | Services read concurrently |

> [!warning] Not suitable for systems where wrong reads are catastrophic
> If User A reads a bank balance mid-write and sees a half-updated value — that's a dirty read. For those cases, use MVCC instead — it gives readers a consistent snapshot without blocking writers at all.

---

## Read-Write Lock vs MVCC

| | Read-Write Lock | MVCC |
|---|---|---|
| Readers block each other | No | No |
| Readers block writers | Yes (writer waits) | No |
| Writers block readers | Yes (readers wait) | No |
| Use case | Systems where brief write pause is acceptable | Modern databases — nobody blocks anybody |

> [!tip] Interview framing
> *"For read-heavy systems I'd use read-write locks — multiple readers proceed concurrently, writer gets brief exclusive access. For database-level concurrency I'd rely on MVCC which goes further — readers and writers never block each other at all via snapshot isolation."*
