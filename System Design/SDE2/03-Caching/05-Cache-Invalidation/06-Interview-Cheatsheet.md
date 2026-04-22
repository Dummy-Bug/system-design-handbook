# Cache Invalidation — Interview Cheatsheet

---

## The default combination

> [!tip] Most production systems combine: TTL as safety net + event-driven for critical data + stale-while-revalidate for feeds. No single strategy fits everything.

---

## Strategy selector

| Data type | Strategy | Reason |
|---|---|---|
| Any data | TTL (safety net) | Always set — ensures stale data can't live forever |
| User's own profile | Event-driven or Write-Through | Must be fresh after user writes |
| News feed, leaderboard | Stale-While-Revalidate | One stale response is acceptable |
| Hot key approaching expiry | Refresh-Ahead | Prevent stampede on predictable expiry |
| CDN static assets | Cache Versioning | Versioned URL = no invalidation needed |
| Payment, inventory | Event-driven + short TTL | Zero tolerance for stale data |

---

## One-line definitions

> [!info] TTL-Based
> Key auto-deletes after a timer. Simple, always use as a safety net. Stale window = up to TTL duration.

> [!info] Event-Driven
> Delete (or update) cache key the instant DB is written. Zero stale window. Needs infrastructure to trigger.

> [!info] Write-Through
> On every write, update cache AND DB synchronously. No miss after write. Slower writes.

> [!info] Cache Versioning
> Embed version in cache key. Old keys expire naturally. Best for CDN assets, costs two lookups for DB-backed data.

> [!info] Stale-While-Revalidate
> Serve stale on expiry, refresh in background. One stale response per expiry cycle. Great for feeds.

---

## Interview framing

> "I'd layer the strategies. TTL on every key as a safety net — 5 minutes for profiles, 30 seconds for feed counts. For the user's own profile update, I'd use event-driven invalidation so they see their change immediately. For the news feed, stale-while-revalidate — one slightly stale feed load is invisible to users, but waiting 50ms on a DB query isn't."
