
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

**Option 1 — sticky session after creation**

When the creation response is returned, set a short-lived flag for that user (in a cookie, a session store, or a header). For the next 10-30 seconds, the app server checks this flag and routes reads for that user to the primary shard.

```
Create URL → set cookie: ryow_until = now + 30 seconds
Read URL   → if ryow_until > now AND same user → route to primary
           → else → route to secondary
```

**Option 2 — read from primary for the first N seconds after write**

The app server tracks recent writes in memory (or a small cache). If a short code was written within the last 30 seconds, route its reads to the primary.

```
Write x7k2p9 → record in local cache: x7k2p9 → written_at = now
Read x7k2p9  → check cache → written_at = 5 seconds ago → route to primary
Read x7k2p9  → check cache → written_at = 2 minutes ago → route to secondary
```

Both approaches work. The key point is that this is a **targeted routing rule** — it affects one user for one URL for a short window. It does not make the system synchronous. Availability is barely impacted.

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
