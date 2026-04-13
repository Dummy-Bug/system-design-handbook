
> [!info] Flip the approach entirely
> The collision problem exists because you generate a key at request time and then check if it's taken. What if every key you handed out was guaranteed unique before the request even arrived? No check needed. No retry possible. Zero collisions by design.

---

## The core idea

Instead of generating a key when a creation request arrives, pre-generate keys in advance and store them in a pool. When a request arrives, just pick one from the pool.

```
Before any request arrives:
→ Keys pre-generated and verified as unused
→ Stored in pool, ready to hand out

When creation request arrives:
→ Pop one key from pool
→ Done — guaranteed unique, zero collision check, zero retry
```

The collision problem is eliminated entirely. Not reduced. Eliminated. The key is unique by the time it reaches the app server. There is no collision to check for.

---

## Why Redis, and why LPOP specifically

The pool needs to hand out keys atomically. If two app servers grab from the pool at the same moment, they must get different keys — not the same one.

This is exactly what Redis `LPOP` does. Redis is **single-threaded** — every command executes one at a time, in order. Even if 20 app servers call `LPOP` at the exact same millisecond, Redis processes them sequentially:

```
App server 1: LPOP → gets "x7k2p9" → removed from list
App server 2: LPOP → gets "k2m8q1" → removed from list
App server 3: LPOP → gets "p9n3r7" → removed from list
```

It is physically impossible for two `LPOP` calls to return the same value. Atomicity is guaranteed not by locks or transactions, but by Redis's single-threaded architecture. No locking mechanism needed. No `SELECT FOR UPDATE`. No coordination. Just `LPOP`.

`LPOP` is also O(1) — removes the head of a list in nanoseconds. Redis handles millions of these per second.

---

## The concurrency problem without Redis

To understand why Redis is the right tool here, consider what would happen with a regular database table as the pool:

```
App server 1: SELECT short_code FROM key_pool LIMIT 1
App server 2: SELECT short_code FROM key_pool LIMIT 1
→ Both read "x7k2p9" before either deletes it
→ Both try to use "x7k2p9" → duplicate
```

You'd need `SELECT FOR UPDATE SKIP LOCKED` to make it safe. That's row-level locking — expensive, complex, and adds latency. Redis `LPOP` is simpler, faster, and atomic by design.

---

## In-memory batch pre-fetch

At 1k creations/sec, app servers would call `LPOP` 1000 times per second. That's 1000 Redis operations per second just for key assignment — on top of all the cache reads already going to Redis.

The fix: each app server grabs a batch of keys upfront and keeps them in local memory.

```
App server starts up:
→ LPOP 100 keys from Redis pool
→ Store locally in memory as a queue

Creation request arrives:
→ Pop next key from local memory queue → zero network call
→ Queue empty → LPOP another 100 from Redis

Result: 1000 Redis calls/sec → ~10 Redis calls/sec (one batch refill every ~10 seconds)
```

100x reduction in Redis traffic for key assignment. The pool in Redis drains 100 keys at a time instead of one at a time.

---

## What happens when an app server crashes

Each app server holds up to 100 keys in local memory. If it crashes, those keys are lost — they were popped from Redis and never used.

This is not a problem. The keys are just random base62 strings. They have no intrinsic value. The pool has hundreds of millions of keys. Losing 60 or 100 of them is completely negligible.

```
Pool size:       100,000,000 keys
Lost on crash:   100 keys (worst case)
Impact:          0.0001% of pool → irrelevant
```

Compare this to the alternative — pushing unused keys back to Redis on crash. That would require a graceful shutdown handler, crash recovery logic, and coordination between app servers. All of that complexity to recover 100 keys out of 100 million. Not worth it.

---

> [!tip] Interview framing
> "Pre-generated key pool in Redis. App server calls LPOP — atomic by default because Redis is single-threaded, impossible for two servers to get the same key. App servers batch-fetch 100 keys at startup and refill when empty — reduces Redis traffic from 1k/sec to ~10/sec. Crashed server loses its batch — not a problem, losing 100 out of 100M keys is negligible."
