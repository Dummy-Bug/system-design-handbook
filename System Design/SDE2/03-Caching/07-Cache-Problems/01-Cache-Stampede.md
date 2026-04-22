# Cache Stampede (Thundering Herd)

> [!info] A hot key's TTL expires. Thousands of concurrent requests all get a cache miss simultaneously. All of them query the DB at once.

---

## How it happens

```
Homepage query cached with TTL = 60s
→ 50,000 requests/second hitting this key
→ T=60s: TTL expires
→ all 50,000 requests for that second get a cache miss
→ all 50,000 query the DB simultaneously
→ DB gets 50,000 queries instead of its usual 1
→ DB collapses under the load ✗
```

The problem isn't the cache miss itself. It's the **thundering herd** — thousands of identical DB queries happening in parallel because no one coordinated who should actually fetch the data.

---

## Fix 1 — Refresh-Ahead

Don't let the key expire in the first place. Detect that expiry is approaching and refresh proactively.

```
TTL = 60s, refresh threshold = 45s
T=45s → background job detects key has 15s remaining and is hot
       → fetches fresh data from DB → updates cache
T=60s → key would expire, but it's already fresh ✓
       → users never see a miss → DB never sees the spike ✓
```

Best for predictable hot keys. Requires knowing which keys are worth monitoring.

---

## Fix 2 — Mutex with Double-Checked Locking

When a key expires, only let one request fetch from DB. All others wait, then check the cache again.

```
T=60s: key expires → 50,000 requests get cache miss
→ all try to acquire a lock for this key
→ one request wins the lock
→ 49,999 wait

Winner:
  → fetches from DB
  → writes to cache
  → releases lock

Waiters (after lock released):
  → check cache again ← this is the double-check
  → cache hit ✓ → return immediately
  → DB gets exactly 1 query total ✓
```

**The double-check is critical:**
```python
def get(key):
    value = cache.get(key)
    if value: return value              # first check (no lock needed)

    lock.acquire(key)
    try:
        value = cache.get(key)          # second check (inside lock)
        if value: return value          # someone else already fetched it

        value = db.fetch(key)
        cache.set(key, value, ttl=60)
        return value
    finally:
        lock.release(key)
```

Without the second check inside the lock, waiters would fetch from DB too — serialised instead of eliminated. With it, DB gets exactly one query regardless of how many concurrent waiters.

---

## Fix 3 — Probabilistic Early Expiry

Each request near TTL expiry has a random chance of triggering a proactive refresh. No lock needed, no coordination.

```
TTL = 60s, key has 10s remaining
Each request flips a weighted coin:
  20% chance → this request refreshes the cache proactively
  80% chance → serve current value, do nothing

As TTL approaches zero, the probability increases
→ cache gets refreshed naturally before it expires
→ no thundering herd, no locks, no background jobs
```

Elegant and simple. The randomness ensures the refresh is distributed across requests rather than hitting all at once.

---

## Which fix to use

```
Refresh-Ahead             → predictable hot keys, background job available
Mutex + double-check      → unpredictable spikes, need coordination
Probabilistic expiry      → simple, works without any extra infrastructure
```

In practice, most production systems combine: Refresh-Ahead for known hot keys + mutex for everything else.
