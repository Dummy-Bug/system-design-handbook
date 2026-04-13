
> [!info] The core idea
> One shared counter with locks solves correctness but destroys throughput. A lock round trip across data centers serializes every increment — turning 3,000,000 likes/sec into 20 likes/sec. Locks also reintroduce a single point of failure. You need a solution that is both correct and coordination-free.

---

## The problem — counting likes at scale

Say you're building a like counter for a viral post. Simple enough — one server, one counter in the database. Every like increments it.

```
Like comes in → Server reads counter (10) → increments → writes back (11)
```

Works fine at small scale. But a viral post gets 3 million likes per second. One server hits its throughput limit. You need to scale horizontally — add more servers.

---

## Horizontal scaling breaks the counter

Now you have 3 servers sharing one counter in the database. Two likes arrive at the same time on different servers:

```
Server 1 reads counter: 10 → increments → writes 11
Server 2 reads counter: 10 → increments → writes 11

Final value: 11  ← should be 12, one like is lost
```

Both servers read 10, both write 11. Two likes came in but the counter only went up by 1. This is the classic **lost update** problem — concurrent writes overwriting each other.

---

## Attempt to fix — distributed locks

The fix seems obvious — add a lock. Before any server increments, it must acquire the lock. No two servers can increment at the same time.

```
Server 1 acquires lock → reads 10 → writes 11 → releases lock
Server 2 waits → acquires lock → reads 11 → writes 12 → releases lock

Final value: 12 ✓ correct
```

Correctness is restored. But now look at what this does to throughput.

---

## The throughput disaster locks create

A lock round trip across data centers takes about **50ms**. While one server holds the lock, every other server sits idle waiting.

```
0ms   → Server 1 acquires lock, increments, releases
50ms  → Server 2 acquires lock, increments, releases
100ms → Server 3 acquires lock, increments, releases
150ms → Server 1 acquires lock again...
```

In 1000ms, only 20 increments happen total across all 3 servers combined:

```
1000ms / 50ms = 20 likes/sec total
```

Compare that to what you had without locks:

```
Without locks (but with lost updates):
  Server 1: 1,000,000 likes/sec
  Server 2: 1,000,000 likes/sec
  Server 3: 1,000,000 likes/sec
  Total:    3,000,000 likes/sec

With locks (correct but serialized):
  All 3 servers combined: 20 likes/sec
```

> [!danger] 150,000x throughput drop
> You went from 3,000,000 likes/sec to 20 likes/sec just by adding a lock. Adding more servers makes it worse — more servers means more contention on the same lock, longer wait queues, lower throughput. The lock becomes the bottleneck that scales inversely with the number of servers.

And if the lock server goes down — everything stops. You've reintroduced a single point of failure.
