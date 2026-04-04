# Cache Population Strategies

> [!info] Population strategies control **how data gets proactively loaded into the cache** — before a user even asks for it. Unlike read/write strategies, these are not reactive. They run ahead of demand.
---

## Refresh-Ahead

> [!info] Proactively refresh a cache key before its TTL expires. Users never see a miss on hot keys.

```
Key TTL = 60 seconds
At T=45s → background job detects key is about to expire
         → fetches fresh data from DB
         → updates cache before expiry
At T=60s → key would have expired, but it's already fresh
         → users keep hitting cache hits, no miss, no stampede
```

Without refresh-ahead:
```
T=60s → key expires → 50,000 simultaneous requests all miss
      → all hit DB at once → DB spike → stampede
```

**What's good:**
```
Zero cache misses on hot keys      → seamless user experience
Prevents stampede on TTL expiry    → DB never sees the expiry spike
```

**What's bad:**
```
May refresh data nobody requests again    → wasted DB reads
Requires background refresh mechanism    → more operational complexity
```

**Use when:** hot keys with predictable access patterns — trending posts, homepage content, leaderboard top 10.

> [!tip] The refresh threshold is usually 70–80% of TTL. If TTL = 60s, refresh at T=45s. Too early wastes reads. Too late risks a miss window.

---

## Cache Warming

> [!info] Pre-populate the cache at startup or before a traffic spike — so the cache is never cold when real traffic hits.

```
Without warming:
  Server restarts → cache is empty → first N requests all miss
  → DB gets hammered until cache fills up → slow startup period

With warming:
  Before restart completes → background job loads top 1000 keys
  → cache is pre-filled → first request is already a hit
```

**Common approaches:**

```
Startup warming     → load top-N keys from DB on service boot
Scheduled warming   → cron job pre-loads cache before peak hours
                      e.g. load tomorrow's trending content at midnight
Replay warming      → replay recent read traffic against new cache instance
```

**Real-world example:** Netflix pre-warms caches with the top trending shows before a new region goes live. They don't wait for organic traffic to fill the cache.

**What's good:**
```
No cold start penalty       → cache is useful from first request
Predictable performance     → no slow ramp-up after deploys
```

**What's bad:**
```
Warms data that may not be requested    → memory used before demand is confirmed
Increases startup time                  → boot is slower if warming is synchronous
```

**Use when:** services that restart frequently, new deployments, geographic expansions, or predictable traffic spikes (Black Friday, live events).

---

## The Full Picture

| Strategy | When it runs | Problem it solves | Limitation |
|---|---|---|---|
| Refresh-Ahead | Before TTL expires (proactive) | Prevents expiry misses on hot keys | Key must already exist in cache |
| Cache Warming | At startup / before traffic spike | Prevents cold cache on deploy | Warms data that may not be requested |

> [!important] These two patterns solve **different problems**:
> - **Cache Warming** — solves the cold cache problem. Cache is empty, nothing to serve yet.
> - **Refresh-Ahead** — solves the TTL expiry miss problem. Cache already has the key, but it's about to expire.
>
> Refresh-Ahead does **not** help a cold cache — there is nothing to refresh if the key was never loaded in the first place. You need warming for that.
