# Cache Writing & Reading Strategies — Overview

> [!abstract] When does data enter the cache? When does it get written back to the DB? Five patterns — each with a different answer to these two questions. Choosing the wrong one means either stale data, slow writes, or data loss.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Read-Strategies.md | Cache-Aside and Read-Through — how reads populate the cache |
| 02-Write-Strategies.md | Write-Through, Write-Back, Write-Around — how writes interact with the cache |
| 03-Interview-Cheatsheet.md | Which strategy to mention and when |

---

## The quick decision map

```
Read-heavy, app controls cache?        → Cache-Aside (most common)
Read-heavy, want cleaner app code?     → Read-Through
Write-heavy, consistency matters?      → Write-Through
Write-heavy, speed matters most?       → Write-Back (accept data loss risk)
Write-once data, rarely read back?     → Write-Around
```
