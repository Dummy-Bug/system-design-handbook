# Cache Population Strategies — Overview

> [!abstract] Population strategies load data into the cache *before* a user asks for it — proactively, not reactively. They solve two different problems: a cache that's about to expire (Refresh-Ahead), and a cache that's completely empty (Cache Warming).

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Refresh-Ahead.md | Proactively refresh hot keys before TTL expires |
| 02-Cache-Warming.md | Pre-populate cache before launch or restart |
| 03-Interview-Cheatsheet.md | When to mention each |

---

> [!important] These two solve different problems
> **Cache Warming** — cache is empty. Nothing to serve yet. Load it before traffic hits.
> **Refresh-Ahead** — cache has the key, but it's about to expire. Refresh it before users see a miss.
> Refresh-Ahead does not help a cold cache — there's nothing to refresh if the key was never loaded.
