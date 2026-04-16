
> [!info] Cold start and thundering herd — what happens when the cache is empty
> On startup or after a Redis restart, the cache is empty. Every request falls through to DynamoDB. The question is whether this is a crisis — and how request coalescing limits the damage.

---

## The cold start scenario

Redis restarts. Every cached profile is gone. The next inbox load for every user is a cache miss.

The instinct is to panic: "all my users are hammering DynamoDB simultaneously." But let's do the actual math before deciding if this is a real problem.

---

## The math

**Assumptions:**
- 100M DAU
- Peak hour: 20% of DAU open the app = 20M users
- Spread across 1 hour = 20M / 3600 ≈ **5,500 users/second** opening the inbox
- Each inbox load → 20 profile reads = **110,000 profile reads/second**
- Not all 20 contacts are unique across users — assume 20% uniqueness = **22,000 unique profile reads/second** hitting DynamoDB

```
100M DAU × 20% peak = 20M users in peak hour
20M / 3600s          = 5,500 users/second
5,500 × 20 profiles  = 110,000 reads/second
× 20% unique         = 22,000 unique reads/second on DynamoDB
```

DynamoDB is designed to handle millions of reads per second. 22,000 RPS is trivial.

Within the first few minutes of the peak hour, the most frequently accessed profiles are cached. DynamoDB load drops toward zero as the cache warms up naturally.

> [!important] Cold start is survivable
> At reasonable peak assumptions, the DynamoDB burst from a cold start is well within capacity. The cache warms up within minutes, and load drops sharply. This is not a crisis — it's a brief warm-up period.

---

## The thundering herd — a different problem

Cold start is about total load. The thundering herd is about load on a **single key**.

Charlie is in 10,000 people's inboxes. At 9am, 10,000 users open WhatsApp at the same moment. The cache is cold. All 10,000 requests ask for `user:charlie` simultaneously — all get a miss — all race to DynamoDB.

Without protection, DynamoDB receives 10,000 reads for the exact same row in the same second. With coalescing, it receives 1.

**Request coalescing (mutex on cache miss):**

```
10,000 requests for user:charlie — all miss
→ Thread 1 acquires lock on key user:charlie
→ Threads 2-9999 see the lock — they wait
→ Thread 1 fetches Charlie's profile from DynamoDB
→ Thread 1 writes to Redis, releases lock
→ Threads 2-9999 all read from Redis
→ Result: 1 DB read, not 10,000
```

The lock is in-process, per app server. It's not a distributed lock — just a local mutex per key. At the app server level, only one goroutine/thread fetches the same key at the same time. Others wait on that result.

---

## Pre-warming for planned restarts

For unplanned Redis failures, the cold start math shows the system survives. For **planned** restarts (maintenance, Redis version upgrade, cluster migration), you can do better.

Before routing traffic to the new Redis instance, pre-populate it with the most frequently accessed profiles:

```
Planned Redis restart:
→ spin up new Redis cluster
→ fetch top 10M profiles from DynamoDB (by access frequency)
→ populate new Redis
→ route traffic to new cluster
→ cache hit rate starts high, DynamoDB barely notices
```

This requires tracking access frequency (a simple counter per key, or just using LFU eviction policy on Redis to know what was hot). At WhatsApp scale, the top 10M profiles cover the vast majority of inbox reads.

> [!tip] Interview framing
> "Cold start is survivable — 22K unique profile reads/second is well within DynamoDB's capacity, and the cache warms up within minutes. For the thundering herd on popular keys, request coalescing on the app server limits each unique key to one DB read at a time. For planned restarts, we pre-warm the cache before routing traffic."

---

> [!info] Full thundering herd deep dive
> The thundering herd problem — multiple components, backpressure, load shedding — is covered in full in the Peak Traffic deep dive.
