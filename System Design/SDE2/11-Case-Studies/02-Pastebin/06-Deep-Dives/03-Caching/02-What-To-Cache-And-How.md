
> [!info] Lazy loading — cache on demand, not in advance. The cache fills itself as real traffic hits it.

---

## What to cache

Cache the full paste content, keyed by short code.

```
Key:   shortCode          (e.g. "aB3kZ9")
Value: paste content      (the full text, up to 10KB)
TTL:   expires_at - now   (auto-expires exactly when the paste does)
```

This is all a read needs. The client sends a short code, the server returns content. No other fields need to be in cache — metadata like `creator_id` and `created_at` is never returned to the reader.

---

## Lazy loading — cache on read, not on write

The temptation when a paste is created is to immediately write it into Redis. This is called **eager loading** or **write-through caching**. It sounds efficient but has a problem: most pastes are never read again, or are only read once. Writing every paste into Redis on creation wastes memory on content nobody will request.

The better approach is **lazy loading** — only cache a paste when someone actually reads it.

```
Read request arrives for shortCode X:

  1. Check Redis for key X
     → Cache hit:  return content immediately (~1ms)
     → Cache miss: continue to step 2

  2. Query Postgres for metadata (is it expired? deleted?)
     → Not found or expired: return 404

  3. Fetch content from S3

  4. Write content into Redis with TTL = expires_at - now

  5. Return content to client
```

After the first read, every subsequent read for the same short code hits Redis and never touches Postgres or S3. This is exactly the right behaviour for Pastebin — hot pastes (shared links, incident logs, popular forum snippets) get read repeatedly, and those are the ones that end up in cache.

---

## Why not pre-warm the cache?

A cron job that looks at the most-read pastes and pre-loads them into Redis sounds reasonable. The problem is timing — you only know a paste is hot *after* it's been read. Yesterday's hot pastes may not be today's hot pastes. Pre-warming with stale data wastes cache space and still misses the first wave of reads on newly viral content.

Lazy loading solves this automatically. The moment a paste becomes hot, the first read populates the cache. Every subsequent read is served from Redis. No cron job, no pre-warming logic, no stale data.

---

## Eviction policy — LRU

Redis has a fixed memory budget. When it fills up, it needs to evict entries. The right policy here is **LRU (Least Recently Used)** — evict the paste that hasn't been read the longest.

This matches the access pattern perfectly. Pastes shared recently are being actively read. Pastes from two weeks ago that nobody has clicked are the right candidates for eviction. LRU naturally keeps the hot content in cache and removes the cold content.

---

> [!tip] Interview framing
> "Lazy load — cache on read, not on write. On cache miss, fetch from Postgres + S3, populate Redis, return to client. TTL set to expires_at - now so cache entries auto-expire with the paste. Eviction policy is LRU — keeps recently read pastes in cache, evicts cold ones. No pre-warming needed — lazy loading fills the cache with exactly what's hot."
