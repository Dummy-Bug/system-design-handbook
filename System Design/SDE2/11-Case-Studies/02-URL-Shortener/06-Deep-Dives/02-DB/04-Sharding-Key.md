
> [!info] The most important sharding decision
> The sharding key determines which shard a row lives on. A bad sharding key causes hotspots — one shard gets all the traffic while others sit idle. A good sharding key distributes load evenly and aligns with your access patterns.

---

## The access patterns drive the key choice

Two queries:

```
Redirect (read)  → given short_code, return long_url
Creation (write) → given long_url, generate short_code and insert
```

For the redirect query, you always have the short code — it's right there in the URL the user clicked. If you shard by short code, you can route directly to the correct shard without any lookup.

For the creation query, the app server generates the short code before inserting. So by the time the INSERT hits the database, the short code already exists. You can shard the write the same way as the read.

**One sharding key for both reads and writes: short_code.**

---

## Why not shard by long_url?

The long URL is what the user provides on creation. The instinct might be: shard by long URL so you can check if the same long URL was already shortened before.

But we scoped this out in FR — the system does not deduplicate. Two users submitting the same long URL get two different short codes. There is no need to look up by long URL at all.

Sharding by long URL would mean:
- Redirect queries arrive with a short code → you don't know which shard to go to → you'd need a lookup table → extra hop on every redirect

That's the worst possible outcome for a read-heavy system. The 100k reads/sec redirect flow would pay an extra network round trip on every request.

---

## Why short_code is the right key

```
Redirect arrives with short_code → hash(short_code) → shard number → direct query
Creation generates short_code    → hash(short_code) → shard number → direct insert
```

No extra lookups. No cross-shard queries. Every operation knows exactly which shard to hit from the short code alone.

Short code is also globally unique — no two rows share a short code. This means no shard will ever have to handle two rows with the same key. The data distributes cleanly.

---

## Hot shard risk

One concern with any sharding key: hotspots. If a celebrity tweets a link and one short code gets 10M clicks in an hour, does that overwhelm one shard?

The answer here is no — because caching absorbs the spike. A viral short code is cached in Redis. The shard never sees the 10M clicks. It only sees the 20% of traffic that misses the cache, spread across all short codes — not concentrated on one.

Caching and sharding work together. Caching prevents hot shards. Sharding handles storage growth.

---

> [!tip] Interview framing
> "Shard by short_code. Redirect queries always arrive with the short code — direct routing to the correct shard, no extra hops. Creation generates the short code before inserting — same routing logic. No deduplication in scope so no need to look up by long URL. Hot shard risk is mitigated by caching — viral URLs are served from Redis, the shard never sees the spike."
