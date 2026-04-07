# Cache Problems — Interview Cheatsheet

---

## Diagnose first, then fix

> [!important] All four problems look identical from outside — the DB gets hammered. The fix depends entirely on the cause. Diagnose before prescribing.

```
"The DB is being hammered unexpectedly. What's happening?"

Cache is completely empty?                         → Cold Start
One popular key's TTL just expired?                → Cache Stampede
Requests for IDs that don't exist in the DB?       → Cache Penetration
Many keys expiring at the same time?               → Cache Avalanche
```

---

## The four problems at a glance

| Problem | Cause | Fix |
|---|---|---|
| **Stampede** | One hot key expires, thousands hit DB at once | Refresh-Ahead, mutex + double-check, probabilistic expiry |
| **Cold Start** | Cache empty — new deploy, restart, new region | Warm cache before opening traffic |
| **Penetration** | Non-existent keys bypass cache, DB returns null forever | Cache null values (short TTL), Bloom filter |
| **Avalanche** | Thousands of keys expire simultaneously — same TTL on bulk load | TTL jitter on bulk loads |

---

## One-line fixes

> [!info] Stampede fix
> Refresh-Ahead for known hot keys. Mutex with double-checked locking for everything else.

> [!info] Cold Start fix
> Replay yesterday's access logs to pre-populate cache before switching traffic.

> [!info] Penetration fix
> Bloom filter at the entry point — non-existent keys never reach cache or DB.

> [!info] Avalanche fix
> `ttl = base_ttl + random(0, jitter)` on every bulk load. One line of code.

---

## Interview framing

> "I'd protect against four cache failure modes. Stampede: Refresh-Ahead on hot keys, mutex with double-check for the rest. Cold start: warm the cache before switching traffic on deploys. Penetration: Bloom filter so non-existent keys never reach the DB. Avalanche: TTL jitter on bulk loads so expirations are staggered across a time window."

Saying all four unprompted — with causes and fixes — is a strong hire signal.
