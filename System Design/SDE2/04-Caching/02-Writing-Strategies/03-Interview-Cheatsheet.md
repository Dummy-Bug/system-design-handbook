# Cache Writing Strategies — Interview Cheatsheet

---

## The default combination

> [!tip] Most production systems use Cache-Aside for reads + Write-Through or Write-Around for writes. Say this as your default, then adjust per data type.

---

## Strategy selector

| Data type | Read strategy | Write strategy | Reason |
|---|---|---|---|
| User profiles, settings | Cache-Aside | Write-Through | Read-heavy, must be consistent after write |
| Social feed, like counts | Cache-Aside | Write-Back | Write-heavy, slight staleness acceptable |
| Logs, audit trails | Cache-Aside | Write-Around | Write-once, rarely read back |
| Config / feature flags | Read-Through | Write-Through | Consistency critical, cleaner abstraction |

---

## One-line definitions

> [!info] Cache-Aside
> App checks cache, fetches DB on miss, populates cache manually. Most common. App has full control.

> [!info] Read-Through
> Cache handles its own misses — fetches from DB and populates itself. Cleaner app code, more complex cache config.

> [!info] Write-Through
> Write to cache and DB synchronously. Always consistent. Slower writes.

> [!info] Write-Back
> Write to cache immediately, flush to DB asynchronously. Fastest writes. Risk of data loss on cache crash.

> [!info] Write-Around
> Write directly to DB, skip cache. Cache populated only on first read. Prevents cache pollution with write-once data.

---

## Interview framing

> "For reads I'd use cache-aside — the app checks Redis first and falls back to Postgres on a miss. For writes to user profiles I'd use write-through so the cache is never stale after a write. For activity feed events I'd use write-around — they're written once and rarely read individually, so caching them on write wastes memory."
