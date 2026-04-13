
> [!info] The problem
> Async replication means secondaries lag behind the primary by milliseconds. For almost every redirect, this doesn't matter — the URL was created long ago and is fully synced. But there is one specific case where it does: the creator clicking their own link immediately after creating it.

---

## The scenario

```
T=0ms  → User creates bit.ly/x7k2p9
          Write goes to Shard-3 primary → acknowledged → short URL returned to user

T=50ms → User immediately clicks bit.ly/x7k2p9 to test it
          Redirect query goes to Shard-3 secondary
          Secondary hasn't synced yet → short_code not found → 404
```

The user just created a URL and immediately gets a 404 when they click it. This is a terrible experience — and it's specifically caused by async replication lag.

This is the **read-your-own-writes** problem. The solution is not to make replication synchronous everywhere — that would hurt availability. The solution is a targeted routing rule for this one specific case.

---

## Why full strong consistency is overkill

You could make all writes synchronous — only acknowledge the creation after both primary and secondaries confirm. This guarantees the secondary is always up to date.

But:
- Every write now waits for 2 secondary acknowledgments → higher write latency
- If a secondary is slow or unreachable → writes block → availability suffers
- 99.9% of reads are for URLs created minutes, hours, or days ago — fully synced anyway

Strong consistency across the board is the wrong trade-off. You're paying a system-wide cost to fix a problem that only affects one user for a few hundred milliseconds.

---

## The targeted fix — route the creator to the primary

For a short window after creation, route the creator's reads to the primary instead of secondaries.

```
T=0ms  → User creates bit.ly/x7k2p9 → write goes to primary
T=50ms → Same user clicks bit.ly/x7k2p9
          App server knows this user just created this URL
          → routes read to primary, not secondary
          → primary has the data → 200 OK, redirect works ✓

T=5min → Any other user clicks the same link
          → routes to secondary → fully synced by now → works ✓
```

The window is small — typically a few seconds is enough for async replication to catch up. After that window, the creator's reads go to secondaries like everyone else.

---

## How to implement it

Two options exist. They look similar but have a critical difference in efficiency.

---

### Option 1 — cookie-based sticky routing (the right approach)

When the creation response is returned, include a short-lived cookie in the response:

```
HTTP 200 OK
Set-Cookie: ryow_until=1713000030; Path=/; HttpOnly

{
  "data": { "short_url": "bit.ly/x7k2p9" }
}
```

`ryow_until` is just a Unix timestamp — `now + 30 seconds`. The cookie carries no shard info, no IPs, nothing sensitive.

On the next redirect request, the browser automatically sends this cookie back:

```
GET /x7k2p9
Cookie: ryow_until=1713000030
```

The app server's routing logic:

```
1. Extract short_code from path → x7k2p9
2. Check cookie: ryow_until present AND ryow_until > now?
   → YES → route to primary
   → NO  → route to secondary
3. hash(short_code) → consistent hashing → shard number
4. Look up shard's primary or secondary IP from etcd
5. Route query accordingly
```

**Where are the primary/secondary IPs stored?**

In etcd — the service registry. Every shard's topology lives there:

```
etcd:
  shard-1/primary    → 10.0.1.1
  shard-1/secondaries → [10.0.1.2, 10.0.1.3]
  shard-2/primary    → 10.0.1.4
  shard-2/secondaries → [10.0.1.5, 10.0.1.6]
  ...
```

App servers read this on startup and cache it locally. When a shard's primary changes due to failover, etcd updates the entry and notifies all app servers via a watch. The app server always knows the current primary without hardcoding IPs anywhere.

**Why this is efficient:**

The cookie decision happens entirely in the app server's memory — no extra network calls. The consistent hashing lookup is local computation. The etcd topology is cached locally. Zero extra round trips on the redirect path.

---

### Option 2 — write tracking in Redis (worse)

The app server writes a short-lived Redis key every time a URL is created:

```
Write x7k2p9 → SET ryow:x7k2p9 1 EX 30
Read x7k2p9  → GET ryow:x7k2p9
             → found → route to primary
             → not found → route to secondary
```

This solves the cross-app-server problem — any app server can check Redis for any short code. Unlike tracking in local memory, it works across a fleet.

**Why this is worse:**

Every single redirect — 100k/sec — now does an extra Redis lookup before the actual cache lookup. Most of those lookups return nothing. The URL was created days ago, the Redis key expired long ago, but you're still paying a Redis round trip to confirm that fact.

```
Option 1 → extra work per redirect: 0 network calls (cookie check is in-memory)
Option 2 → extra work per redirect: 1 Redis GET (100k/sec × 1 extra call = 100k extra Redis ops/sec)
```

You're paying 100k extra Redis operations per second to handle a problem that affects 1k users/sec for 30 seconds. The cost is completely disproportionate to the benefit.

---

### The verdict

**Option 1 wins.** Cookie carries the expiry timestamp, app server uses consistent hashing to find the shard, etcd provides the primary IP. No extra network calls on the redirect path. Clean, efficient, targeted.

---

## The tension with availability — why it's manageable

Routing to the primary for reads means the primary handles both writes and some reads. This adds load to the primary.

But:
- Only the creator is routed to the primary, and only for a short window
- 100k reads/sec — only a tiny fraction are from creators in the first 30 seconds after creation (1k writes/sec → 1k creators/sec who might click their link immediately)
- The primary handles 1k writes/sec already — a few extra reads for newly created URLs is negligible

The availability trade-off is real but manageable. RYOW is a scalpel, not a sledgehammer.

---

> [!tip] Interview framing
> "Async replication creates a window where the creator might click their own link and get a 404 — the secondary hasn't synced yet. Fix: sticky routing for the creator. For 10-30 seconds after creation, route that user's reads to the primary for that short code. Everyone else reads from secondaries. This is targeted — it doesn't make the system synchronous, doesn't hurt availability at scale. RYOW is a routing rule for one user for one URL for a few seconds."
