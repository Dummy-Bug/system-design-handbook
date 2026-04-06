# Cache Avalanche

> [!info] Thousands of cache keys expire at exactly the same time. Mass cache miss across the entire keyspace. The DB gets hammered simultaneously by every miss.

---

## How it happens

Cache Avalanche is Cache Stampede at scale — not one key expiring, but thousands or millions.

```
E-commerce site, Black Friday prep:
  Midnight: bulk-load 50,000 product pages into cache, all TTL = 5 minutes

12:05am: all 50,000 keys expire simultaneously
→ every product page request → cache miss
→ 50,000 DB queries at once
→ DB collapses ✗
```

The cause is always the same: keys created in a batch with identical TTL values — they were born together, so they die together.

```
Other common triggers:
  Cache restart → all keys lost → manually re-warm with identical TTLs → all expire together
  Scheduled refresh job → refreshes all keys at the same time → same TTL → expire together
  Deployment → new cache instance → warm all keys simultaneously → all expire together
```

---

## How it differs from Stampede

```
Cache Stampede → ONE key expires → burst of misses for that key → recovers quickly
Cache Avalanche → MANY keys expire simultaneously → sustained mass miss → DB collapse
```

Avalanche is more severe and more sustained. A stampede resolves once one request repopulates the key. An avalanche requires the DB to handle thousands of simultaneous queries across the entire key set.

---

## Fix — TTL Jitter

Add randomness to the TTL on bulk loads so expirations are spread out over a time window:

```
Without jitter:
  All 50,000 keys → TTL = 300s → expire at exactly the same second

With jitter:
  Each key → TTL = 300s + random(0, 60s)
  Key A → TTL = 312s
  Key B → TTL = 347s
  Key C → TTL = 301s
  Key D → TTL = 358s
  ...

Result: expirations spread across a 60-second window
  → ~833 misses/second instead of 50,000 at once ✓
  → DB sees a gentle, manageable trickle of cache misses
```

One line of code. Completely solves the problem.

```python
# Without jitter — dangerous
cache.set(key, value, ttl=300)

# With jitter — safe
import random
cache.set(key, value, ttl=300 + random.randint(0, 60))
```

---

## Other fixes

**Refresh-Ahead on the entire batch** — instead of letting keys expire, proactively refresh them before expiry. More complex, but prevents misses entirely.

**Staggered bulk-loading** — when loading a large batch, insert keys in groups with different TTL offsets:
```
Keys 1-10,000:    TTL = 300s
Keys 10,001-20,000: TTL = 310s
Keys 20,001-30,000: TTL = 320s
→ expirations naturally staggered across 30-second windows
```

> [!tip] Interview framing
> "I'd add jitter to TTL values on bulk loads — instead of all keys expiring at the same time, each gets a random offset of ±30 seconds. This spreads expiry across a time window so the DB sees a trickle of misses rather than a simultaneous flood."
