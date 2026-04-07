# Population Strategies — Interview Cheatsheet

---

## When to mention each

```
"What happens when your cache key expires on a hot key?"
→ Refresh-Ahead — proactively refresh before expiry, zero miss for users

"What happens when you deploy a new cache instance?"
"What happens when Redis restarts?"
→ Cache Warming — pre-populate before opening traffic

"How do you handle cache stampede?"
→ Mention Refresh-Ahead as one fix (alongside mutex and probabilistic expiry)
```

---

## One-line definitions

> [!info] Refresh-Ahead
> Detect that a hot key is about to expire, fetch fresh data from DB proactively, update cache before TTL runs out. Users never see a miss.

> [!info] Cache Warming
> Before opening traffic to a new or restarted cache, pre-populate it with the most-requested keys. No cold start penalty.

---

## The critical distinction

| | Refresh-Ahead | Cache Warming |
|---|---|---|
| Problem | Key exists but about to expire | Cache is empty, nothing exists |
| When it runs | Continuously, triggered by TTL threshold | Once, at startup or before traffic shift |
| What it prevents | Stampede on popular key expiry | Cold start DB collapse |
| Limitation | Doesn't help empty cache | Doesn't prevent expiry stampedes |
