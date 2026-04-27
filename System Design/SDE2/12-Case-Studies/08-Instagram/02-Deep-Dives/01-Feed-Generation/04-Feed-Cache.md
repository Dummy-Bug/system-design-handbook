# Instagram Feed Generation — The Feed Cache

Fan-out on write pre-builds every user's feed. But pre-built feeds need to live somewhere — somewhere fast enough to serve 1M reads per second with under 200ms latency.

The first instinct is a cache. But caches come in different shapes, and the wrong choice here creates a problem that shows up the moment users start scrolling.

---

## What goes in the cache

Each user's feed is stored under a single key:

```
Key    →  feed:{user_id}
Value  →  sorted set of post metadata, scored by timestamp
```

Post metadata is everything the client needs to render a feed item:

```
post_id, author_id, author_username, caption, media_url, like_count, timestamp
```

Notice what's not here — the actual photo or video bytes. Media stays in object storage (S3 or equivalent). The `media_url` is just a pointer — the client fetches the photo or video directly from the CDN using that URL. The cache never touches media bytes.

This matters for memory. A post's metadata is a few hundred bytes. A photo is 2MB. A video is 50MB. At 500M users, each with a feed of hundreds of posts, storing media in cache would require petabytes of RAM. Storing only metadata keeps each feed entry tiny and the cache size manageable.

---

## Memcached vs Redis

Both are fast in-memory stores. For a simple lookup — store a value, retrieve it by key — Memcached works fine and is arguably simpler to operate.

But the feed isn't a simple lookup. Users scroll. They request the next 10 posts after the last one they saw, then the 10 after that. That's a range query on a sorted list — fetch items between two timestamps, return exactly N results.

Memcached has no concept of sorted data. If you stored the feed as a serialised list in Memcached, fetching page 2 means pulling the entire list over the network and slicing it in application code. A user with 500 posts in their feed and wanting posts 200–210 forces a full 500-entry transfer just to use 10 entries.

Redis sorted sets make this a single command:

```
ZRANGEBYSCORE feed:user_456 (last_seen_timestamp -inf LIMIT 0 10 REV
```

One network call. Exactly the slice needed. Nothing wasted.

Redis wins not because it's faster than Memcached in raw throughput — they're comparable — but because its sorted set maps directly to what a paginated, time-ordered feed requires. Memcached forces you to implement that logic in the application layer, which is slower and more fragile.

---

> [!important] Cache vs DB
> The feed cache is the primary read path — the database is never hit for feed loads. The DB stores ground truth (all posts, all follow relationships), but reads go to cache. If a user's cache entry is cold — they haven't opened the app in days and their feed was evicted — the feed gets assembled from the DB on demand and written back to cache. After that, all reads are cache hits again.
