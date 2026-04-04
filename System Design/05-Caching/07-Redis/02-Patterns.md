# Redis Patterns

---

## Distributed Lock

Multiple servers run the same background job — send email digests, process a payment, clean up expired sessions. Without coordination, every server picks up the same job simultaneously.

```
No lock:
  Server 1 picks up payment job → starts processing
  Server 2 picks up payment job → starts processing
  → payment charged twice
```

You need only one server to run the job at a time. That's a distributed lock.

**How Redis does it:**

```
SET lock:payment:123 "server1" NX PX 5000
```

```
NX       → only set if key does NOT exist
PX 5000  → auto-expire after 5000ms

→ key doesn't exist: set it, return OK   → you got the lock
→ key already exists: do nothing, nil    → someone else has it, skip
```

In practice:

```
Server 1: SET lock:payment:123 NX PX 5000 → OK   ✓ got the lock, process payment
Server 2: SET lock:payment:123 NX PX 5000 → nil  ✗ lock taken, skip
```

**Why the expiry?**

Server 1 gets the lock then crashes mid-job. Without expiry:

```
lock:payment:123 stays forever
→ no server can ever process this payment again
→ stuck forever
```

With `PX 5000` — lock auto-releases after 5 seconds even if the server that set it dies.

---

## Rate Limiter

Limit each user to 100 API requests per minute.

---

### Fixed Window — INCR + EXPIRE

```
User makes a request
→ INCR rate:user:123:2026-04-04-14:01   ← key includes current minute
→ if count == 1 → EXPIRE key 60s        ← start timer on first request
→ if count > 100 → reject
```

```
14:00:00 → count = 1,   EXPIRE 60s set
14:00:30 → count = 50   ✓
14:00:59 → count = 100  ✓
14:01:00 → count = 101  → rejected ✗
14:01:01 → new key, count resets to 1
```

Simple — one integer key per user per minute. Resets automatically when key expires.

**The boundary problem:**

```
14:00:50 → user fires 100 requests → all allowed ✓  (window 1)
14:01:10 → user fires 100 requests → all allowed ✓  (window 2)

200 requests in 20 seconds — even though limit is 100/min
```

The window only asks "how many in this bucket?" — not "how many in the last 60 seconds?". At the boundary, a user can double their limit by straddling two windows.

---

### Sliding Window — Sorted Set

Track the timestamp of every request. Always look at the last 60 seconds from right now.

```
now = current timestamp in ms

ZADD rate:user:123 now "req:unique-id"          ← add this request (score = timestamp)
ZREMRANGEBYSCORE rate:user:123 0 (now - 60000)  ← remove requests older than 60s
count = ZCARD rate:user:123                     ← how many in last 60s?
if count > 100 → reject
```

No boundary problem — window slides with every request:

```
T=14:00:50 → user fires 100 requests
T=14:01:10 → user tries another request

Sliding window: "how many between 14:00:10 and 14:01:10?"
→ those 100 requests from 14:00:50 are still inside
→ count = 100 → rejected ✗
```

**Trade-off:**

```
Fixed window    → 1 integer key per user per minute     → tiny memory
Sliding window  → 1 sorted set entry per request        → more memory, exact accuracy
```

> [!tip] For SDE-2: know both approaches and the trade-off. Fixed window is simpler but exploitable at boundaries. Sliding window is accurate but heavier. Redis commands are a bonus — the interviewer cares more about the trade-off.

---

## Redis Sentinel

One Redis primary goes down — all cache reads and writes fail — every request falls through to DB — DB collapses.

Sentinel is a monitoring process that watches your Redis primary and automatically promotes a replica when the primary dies.

```
Normal state:
  Sentinel watches Primary ──replicates──▶ Replica 1
                                        ──replicates──▶ Replica 2

Primary dies:
  Sentinels detect failure
  → majority vote among Sentinel nodes
  → Replica 1 promoted to primary
  → app told new primary address
  → Replica 2 now replicates from Replica 1
```

Your app doesn't talk to Redis directly — it asks Sentinel "who is the current primary?" and Sentinel points it to the right node.

**Why majority vote?**

If one Sentinel loses its network connection to the primary, it might think the primary is dead when it's actually fine. Requiring a majority prevents a single Sentinel from triggering a false failover.

**The unavoidable gap:**

```
Primary dies → Sentinels detect → vote → promote → app reconnects
→ ~10–30 seconds of Redis being unavailable
```

During that window every cache read fails and requests hit DB. This is an accepted trade-off — Sentinel minimises the window but doesn't eliminate it. Design your system to handle short DB burst traffic gracefully.

---

## Redis Cluster

Sentinel handles failover — what happens when a node dies.
Cluster handles sharding — what happens when data is too big for one node.

```
One Redis node → ~64GB RAM limit
1 billion users × 1KB profile = 1TB of data → doesn't fit
```

Redis Cluster splits data across multiple nodes automatically:

```
Node 1 → owns key slots 0     to 5460
Node 2 → owns key slots 5461  to 10922
Node 3 → owns key slots 10923 to 16383

SET user:123:profile → hashes to slot 5432 → goes to Node 1
SET user:456:profile → hashes to slot 7891 → goes to Node 2
```

Your app doesn't need to know which node holds which key — the cluster handles routing. Each node also has its own replicas for failover, so you get sharding and availability together.

```
Sentinel  → one primary + replicas, automatic failover on failure
Cluster   → many primaries, data sharded across them, each with replicas
```

> [!tip] For SDE-2: know Cluster exists and why (data too large for one node). You don't need the internals.
