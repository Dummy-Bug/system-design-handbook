# Cache Invalidation — Overview

> [!abstract] "There are only two hard things in computer science: cache invalidation and naming things." The reason it's hard: the cache doesn't automatically know when the DB changes. You have to tell it — or wait for time to expire it. Every strategy is a different trade-off between freshness, complexity, and performance.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-TTL-Based.md | Let time expire stale keys — simple, always use as safety net |
| 02-Event-Driven.md | Invalidate the moment the DB changes — no stale window |
| 03-Write-Through.md | Update the cache on every write instead of deleting it |
| 04-Cache-Versioning.md | Change the key itself — old keys expire naturally |
| 05-Stale-While-Revalidate.md | Serve stale immediately, refresh in background |
| 06-Interview-Cheatsheet.md | Which strategy to mention and when |

---

## The spectrum

```
TTL-based              → simplest, stale window up to TTL duration
Event-driven           → instant, needs infrastructure
Write-through          → no miss after write, slower writes
Cache versioning       → no invalidation needed, two cache lookups per read
Stale-while-revalidate → one stale response, then fresh
```
