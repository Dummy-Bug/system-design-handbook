
> [!info] The core idea
> Instead of one shared counter that requires locking, every server keeps its own counter and only ever increments its own. The total is the sum of all counters. When servers sync, they merge by taking the max of each position. Order of syncs doesn't matter — always converges to the same result.

---

## The structure

Every server gets its own slot in a vector — one slot per server in the system. Each server only ever increments its own slot. Never touches anyone else's.

```
Server 1 counter: [S1=0, S2=0, S3=0]
Server 2 counter: [S1=0, S2=0, S3=0]
Server 3 counter: [S1=0, S2=0, S3=0]
```

When likes come in:

```
Server 1 gets 3 likes → [S1=3, S2=0, S3=0]
Server 2 gets 5 likes → [S1=0, S2=5, S3=0]
Server 3 gets 2 likes → [S1=0, S2=0, S3=2]
```

No coordination. No locking. Each server works completely independently at full speed.

To get the total — just sum all slots:

```
Total = 3 + 5 + 2 = 10
```

---

## Syncing between servers — the merge rule

Servers periodically share their vectors with each other. When Server 1 receives Server 2's state, it merges by taking the **max of each position**:

```
Server 1 knows:        [S1=3, S2=0, S3=0]
Incoming from Server 2: [S1=0, S2=5, S3=0]

max(3,0)=3, max(0,5)=5, max(0,0)=0

Server 1 now knows: [S1=3, S2=5, S3=0]
```

> [!important] Same structure as vector clocks — different purpose
> Vector clocks track "how many events happened on each node" to detect causality. G-Counter tracks "how many increments each node received" to count. Same per-node vector structure, but purpose-built for counting.

---

## Why order of syncs doesn't matter

This is the "conflict-free" in CRDT. No matter what order syncs arrive, or even if the same sync arrives twice, the merge always produces the same final result.

```
Server 1 syncs with Server 2 first, then Server 3:
[3,0,0] → merge [0,5,0] → [3,5,0] → merge [0,0,2] → [3,5,2] → total = 10 ✓

Server 1 syncs with Server 3 first, then Server 2:
[3,0,0] → merge [0,0,2] → [3,0,2] → merge [0,5,0] → [3,5,2] → total = 10 ✓

Duplicate sync arrives:
[3,5,2] → merge [0,5,0] → max everywhere → [3,5,2] → total = 10 ✓
```

Always converges to the same state. This property is called **eventual consistency** — all nodes will eventually agree on the same value without any coordination.

---

## Throughput comparison

```
With locks:
  All 3 servers combined: 20 likes/sec (serialized by lock)

With G-Counter:
  Server 1: 1,000,000 likes/sec
  Server 2: 1,000,000 likes/sec
  Server 3: 1,000,000 likes/sec
  Total:    3,000,000 likes/sec ✓
```

Adding more servers increases throughput linearly. No contention, no SPOF, no coordination needed.

> [!danger] G-Counter is grow-only — you cannot decrement
> Because the merge rule is max(), any decrement would get overwritten the next time a sync arrives from a node that had the higher value. If you need both increment and decrement, you use a PN-Counter — two G-Counters, one for increments and one for decrements. Total = increments - decrements.
