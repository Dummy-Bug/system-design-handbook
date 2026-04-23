
## Redis Cluster — Scaling Beyond One Node

Atomicity is solved with Lua scripts on a single Redis node. But a single Redis node cannot handle 400K QPS. This is where the architecture has to evolve.

---

## Why Single Redis Node Fails

Redis is single-threaded. Every command — including Lua scripts — executes one at a time, sequentially. No parallelism inside Redis.

A Lua script for Sliding Window Counter does:
```
Redis GET prev     : ~0.01ms
Redis GET curr     : ~0.01ms
Lua arithmetic     : ~0.01ms
Redis INCR         : ~0.01ms
Redis EXPIRE       : ~0.01ms
Network round trip : ~0.05ms
─────────────────────────────
Total per script   : ~0.1ms
```

Since Redis is single-threaded, it can only run one script at a time. Throughput is:

```
1 second = 1000ms
Each Lua script = ~0.1ms
Max scripts/sec = 1000ms / 0.1ms = 10,000 scripts/sec

For simple operations (GET, INCR without Lua):
  Max ops/sec = ~100,000/sec

For Lua scripts (4-5 ops + interpreter overhead):
  Max ops/sec = ~20,000-30,000/sec
```

We need 400K QPS. One Redis node handles 20-30K Lua scripts per second. The math:

```
400,000 / 25,000 = 16 nodes minimum
```

Add headroom for traffic spikes and node failures → **20-30 Redis nodes** in a cluster.

---

## Redis Cluster — Consistent Hashing

Adding 20 Redis nodes solves throughput. But now which node stores which user's counter?

If you route randomly, User A's requests go to different nodes each time — Node 3 sees 2 requests, Node 7 sees 3 requests, neither sees the full 5. The limit is completely broken.

The fix: **consistent hashing on user_id**. Every rate limiter server independently computes:

```
redis_node = consistent_hash(user_id) % num_nodes
```

Same user_id always produces the same hash → always routes to the same Redis node → one node owns all counters for that user → limit is enforced correctly.

```
User abc  → hash = 847392 → node 847392 % 20 = node 12
User xyz  → hash = 293847 → node 293847 % 20 = node 7

Every rate limiter server computes this independently.
No coordination needed between rate limiter servers.
Node 12 always gets User abc's requests — from every rate limiter server.
```

For unauthenticated requests, use `ip_address` as the hash key instead of `user_id`.

---

## Node Failure — Why Losing Counters Is Acceptable

Redis stores everything in RAM. When a node goes down, all counters on that node are gone. No disk persistence for rate limit counters — they are ephemeral by design.

When Node 12 goes down:

**Counter state is lost** — all users hashed to Node 12 lose their counter history. Their counts reset to zero on the next node they land on.

**Consistent hashing remaps** — only users on Node 12 are affected. The other 19 nodes continue normally. Roughly 1/20th = 5% of users are affected.

**Fail open** — rate limiter can't reach Node 12 → allows requests through for affected users. A brief unprotected window for 5% of users.

**Fresh start on recovery** — when Node 12 comes back up (or when consistent hashing remaps affected users to Node 13), those users start with a clean counter. They get a small window of extra requests.

Is this acceptable? Yes — for three reasons:

1. The blast radius is small — only 5% of users affected, not everyone.
2. The window is short — Redis nodes typically recover or remap in seconds.
3. The alternative is worse — replicating counter state across nodes adds latency to every single request just to handle a rare failure scenario. For rate limiters, losing counters briefly is far cheaper than adding replication overhead to 400K QPS.

> [!important] No replication needed for rate limit counters
> Unlike a database storing user records, losing a rate limit counter for 30 seconds is not a data integrity problem. The worst case is a user gets a few extra requests through. This is an acceptable tradeoff — do not add Redis replication for rate limit state.

---

## The Hot Key Problem

Consistent hashing solves the distributed counting problem. But it creates a new one.

A bot or attacker sends 400K requests per second — all from one IP address. Consistent hashing routes all of them to the same Redis node:

```
hash("1.2.3.4") → always Node 7
400,000 requests/sec → all hitting Node 7
Node 7 can handle 25,000 scripts/sec
Node 7 is overwhelmed → crashes
```

Node 7 goes down. Consistent hashing remaps the attacker's IP to Node 8. Same thing happens. Node 8 goes down. And so on — the attacker can cascade through your entire Redis cluster, node by node, taking each one down.

This is the rate limiter's irony: **the user you are trying to limit can take down the component doing the limiting.**

Standard hot key fixes (key salting, replication across nodes) don't work here — if you split the counter across nodes, you lose the accurate global count. You can't know if the user exceeded the limit if the count is spread across 5 nodes.

The fix has to happen before the request reaches Redis.

---

## Two-Layer Fix — Local Counter + Redis

The insight: stop the flood at the rate limiter server itself, before it hits Redis.

Each rate limiter server maintains a small **in-process local counter** per user. This counter lives in the server's own memory — no network call, nanosecond access.

**Setting the local limit:**

Traffic is evenly distributed across 20 rate limiter nodes. Each node sees roughly 1/20th of any user's traffic. So on average each node sees:

```
global_limit / num_nodes = 5 / 20 = 0.25 requests per node per minute
```

Round up → **local limit = 1 request per node per minute**.

Under normal traffic, a legitimate user makes at most 1 request to any given rate limiter node per minute. If a rate limiter node sees more than 1 request from the same user, something abnormal is happening.

**How the two layers work together:**

```
Request arrives at rate limiter Node 1 for User abc:

Layer 1 — Local counter check (in-process, no network):
  local_count = get_local_counter(user_id)
  if local_count >= local_limit (1):
    → BLOCK immediately — Redis never called

Layer 2 — Redis check (only if local counter allows):
  if local_count < local_limit:
    → call Redis Lua script → get global decision
    → update local counter
    → return allow/block
```

**Normal user scenario:**
```
User abc makes 5 requests spread across 20 nodes:
  Node 1 sees 1 request → local count = 1 → checks Redis → allow
  Node 2 sees 1 request → local count = 1 → checks Redis → allow
  Node 3 sees 1 request → local count = 1 → checks Redis → allow
  Node 4 sees 1 request → local count = 1 → checks Redis → allow
  Node 5 sees 1 request → local count = 1 → checks Redis → Redis count = 5 → block

Redis sees 5 calls total. Accurate global count. Limit enforced correctly.
```

**Attacker scenario (400K req/sec all to Node 1):**
```
Request 1 → local count = 1 → checks Redis → allow
Request 2 → local count = 2 → local limit exceeded → BLOCK (no Redis call)
Request 3 → local count = 3 → BLOCK
...
Request 400,000 → BLOCK

Redis sees 1 call. Node 1 handles 400K decisions per second in memory.
Redis is completely protected.
```

The local counter is a **pre-filter**. It doesn't need to be perfectly accurate globally — it just needs to absorb the flood before it reaches Redis. A small amount of under-counting at the local level is acceptable (remember: AP system, under-counting is fine).

> [!important] Local counter TTL
> Local counters must expire with the window — same as Redis counters. Use the same window_id calculation to key local counters. When the window flips, the local counter resets automatically.

---

## Summary

```
Single Redis node     : handles ~20-30K Lua scripts/sec
                        insufficient for 400K QPS

Redis cluster         : 20-30 nodes
                        consistent hashing on user_id routes same user
                        to same node — accurate global counter

Node failure          : fail open for affected users (~5%)
                        fresh start on recovery
                        no replication needed — losing counters acceptable

Hot key problem       : attacker's 400K QPS overwhelms one Redis node
                        standard key salting breaks global counter accuracy

Two-layer fix         :
  Layer 1 (local)     : in-process counter per user per rate limiter node
                        local_limit = global_limit / num_nodes
                        blocks flood before hitting Redis
  Layer 2 (Redis)     : global accurate counter
                        only called when local limit not yet exceeded
                        protected from hot key storms
```
