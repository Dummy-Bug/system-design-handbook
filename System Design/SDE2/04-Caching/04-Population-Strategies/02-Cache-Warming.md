# Cache Warming

> [!info] Pre-populate the cache at startup or before a traffic spike so the cache is never cold when real traffic hits.

---

## The problem it solves

Every time your cache is empty — fresh deployment, Redis restart, new region launch — every request is a cold miss:

```
New cache deployed (0 keys in cache)
→ first 10,000 requests all miss
→ all hit DB
→ DB sees full production traffic instead of the usual 5%
→ DB collapses under the load ✗
```

This is the **cold start problem**. Same symptom as cache stampede (DB hammered), but a completely different cause — it's not one key expiring, it's nothing in cache at all.

---

## How cache warming works

Before opening traffic to the new cache instance, pre-populate it with the data that's most likely to be requested.

```
Before launch:
  Step 1 → replay yesterday's access logs → identify top-N most-requested keys
  Step 2 → fetch those keys from DB
  Step 3 → write them all into the new cache
  Step 4 → open traffic to the warmed cache

First request → cache hit ✓ (key was pre-loaded)
DB → sees only cache misses for cold keys, not the entire traffic volume
```

---

## Common warming approaches

```
Startup warming      → load top-N keys from DB when service boots
                       block traffic until warming completes (or accept brief cold period)

Scheduled warming    → cron job pre-loads cache before peak traffic window
                       e.g. load tomorrow's trending products at midnight
                       before the morning rush hits

Replay warming       → replay recent read traffic against the new cache instance
                       most accurate — loads exactly what was hot yesterday
                       used by large-scale systems (Netflix, Google)

Shadow warming       → run the new cache instance in shadow mode alongside the old one
                       new instance receives copies of all reads but doesn't serve them
                       cache fills up with real traffic naturally before cutover
```

**Real-world example:** Netflix pre-warms caches with the top trending shows before a new region goes live. They don't wait for organic traffic to fill the cache — the first request in a new region should be a hit, not a miss that hammers a cold DB.

---

## What's good

```
No cold start penalty        → cache is useful from the very first request
Predictable performance      → no slow ramp-up period after deploys
Controlled DB load           → warming is one batch read, not many concurrent misses
```

---

## What's bad

```
Warms data that may not be requested  → memory used before demand is confirmed
Increases startup time                → boot is slower if warming is synchronous
Warming can be stale                  → yesterday's hot keys may not be today's
```

> [!tip] Interview framing
> "On deploy I'd warm the cache by replaying the previous hour's access logs against the new instance before switching traffic. This ensures the cache is pre-populated with the exact keys that were hot, so the first real request hits a warm cache rather than hammering the DB."
