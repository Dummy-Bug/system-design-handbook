# Cache Problems — Overview

> [!abstract] Four failure modes that all look the same on the outside — the DB gets hammered — but have completely different causes and require different fixes. Diagnosing which one you have determines which solution to reach for.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Cache-Stampede.md | One hot key expires — thousands of requests hit DB simultaneously |
| 02-Cold-Start.md | Cache is empty — every request misses, DB sees full traffic |
| 03-Cache-Penetration.md | Keys that don't exist bypass cache forever |
| 04-Cache-Avalanche.md | Thousands of keys expire at the same time |
| 05-Interview-Cheatsheet.md | Diagnose fast, fix correctly |

---

## The diagnostic question

```
DB is being hammered. Which problem is it?

Is the cache empty?                           → Cold Start
Does one specific popular key keep expiring?  → Cache Stampede
Are requests for non-existent keys flooding?  → Cache Penetration
Did many keys expire at the same time?        → Cache Avalanche
```
