# Caching — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning, failure mode awareness, and design decisions. Expected at SDE-2 level — not just definitions, but knowing when and why decisions matter.

---

## Q1 — Cache-Aside vs Write-Through

> [!question] You're designing a user profile service. 10M users, profiles are read 1000x more than they're written. Which caching strategy do you use — Cache-Aside or Write-Through? Why?

> [!success]- Answer
>
> **Why Write-Through wins here:**
>
> Cache-Aside is lazy — it only populates the cache on a miss. With 10M users, a fresh deployment means a completely cold cache. Every user's first request is a miss, all hitting DB simultaneously.
>
> ```
> Cache-Aside on cold start:
>   Write → DB only (cache not touched)
>   First read → cache miss → DB → populate cache → return
>   10M users × first read = 10M DB hits on cold start ✗
>   DB collapses under the spike
>
> Write-Through:
>   Write → DB + cache simultaneously
>   First read → cache hit → return ✓
>   Cache is always warm — no cold start problem
> ```
>
> **With a 1000:1 read-write ratio, reads need to be consistently fast.** Cold start misses blow that guarantee.
>
> **Consistency angle:**
> Write-Through keeps cache and DB always in sync. For user profiles, users expect to see their own updates immediately — no stale window after a write.
>
> **The trade-off acknowledged:**
> Every write is slower — must update both DB and cache synchronously. But with 1000:1 read-write ratio, write latency hit is acceptable. Reads are the bottleneck, not writes.
>
> > [!tip] Interview framing
> > *"Write-Through — with a 1000:1 read-write ratio, reads need to be consistently fast. Cache-Aside leaves us with cold start misses on every deploy. Write-Through ensures the cache is always warm. The slower write latency is an acceptable trade-off given how infrequently writes happen."*

---

## Q2 — Cache Avalanche

> [!question] Your service goes live. Traffic spikes at 9am every day when users log in. You notice the DB gets hammered exactly at 9am even though you have Redis caching. What's happening and how do you fix it?

> [!success]- Answer
>
> **What's happening — Cache Avalanche:**
>
> The clue is "exactly at 9am every day" — too consistent for a random cold start. This is cache avalanche: keys were bulk-loaded the previous day with identical TTLs. They all expire at the exact same second every morning.
>
> ```
> Previous day at 9am → bulk load 50,000 keys, all TTL = 24 hours
> Next day at 9am     → all 50,000 keys expire simultaneously
>                     → every request → cache miss → DB gets 50,000 queries at once
>                     → DB collapses under the spike
> ```
>
> **Why "increase TTL" doesn't fix it:**
> Longer TTL just delays the problem. Keys still expire together — just at a different time.
>
> **The fix — TTL Jitter:**
> ```
> Instead of: TTL = 86400s  (all expire same second)
> Use:        TTL = 86400s + random(0, 3600s)
>
> Keys now expire spread across a 1-hour window
> → DB sees ~14 misses/sec instead of 50,000 at once ✓
> ```
>
> One line of code. Completely solves it.
>
> **Additional fixes for hot keys:**
> - **Refresh-Ahead** on the most critical keys — refresh before TTL fires, users never see a miss
> - **Cache warming** — pre-load before 9am traffic hits
>
> > [!important] Avalanche = many keys expiring simultaneously. Stampede = one key expiring with thousands of concurrent requests hitting DB at once. Different problems, same root cause — both fixed with jitter on TTL.
>
> > [!tip] Interview framing
> > *"This is cache avalanche — bulk-loaded keys with identical TTLs all expiring at once. Fix: add TTL jitter on bulk loads to spread expirations across a time window. For the hottest keys, add refresh-ahead so they never expire during traffic hours."*

---

## Q3 — Cache Penetration

> [!question] A security researcher reports your API is getting thousands of requests per second for user IDs that don't exist — like `/user/99999999`. Your DB is struggling. What's the problem and how do you fix it?

> [!success]- Answer
>
> **What's happening — Cache Penetration:**
>
> Normal cache misses resolve themselves — fetch from DB, store in cache, next request hits cache. Penetration never resolves:
>
> ```
> GET /user/99999999 → cache miss → DB returns null → nothing to cache
> Next request       → cache miss again → DB again → null again → forever
>
> 1,000 requests/sec × non-existent IDs = 1,000 DB queries/sec
> all returning null, none ever cached → DB dies
> ```
>
> **Fix 1 — Rate Limiter (first line of defence):**
> Block abusive traffic at the API gateway before it reaches cache or DB. If an IP is hitting non-existent IDs 1,000 times/sec, rate limit them immediately.
>
> **Fix 2 — Bloom Filter:**
> A bloom filter sits in front of the cache. On every user creation, add their ID to the filter. On every request, check the filter first:
> ```
> Request for user:99999999
> → bloom filter: "has this ID ever existed?" → NO
> → return 404 immediately, cache and DB never touched ✓
>
> No false negatives — if it says no, it's definitely no
> ```
>
> **Fix 3 — Cache the Null:**
> ```
> DB returns null → cache.set("user:99999999", NULL, TTL=60s)
> Next 1,000 requests → cache hit → return null → DB sees zero queries ✓
>
> Short TTL so if the user is created later, the null expires and real data gets cached
> ```
>
> **Defence in depth — all three together:**
> ```
> Layer 1 — Rate Limiter   → block abusive traffic at entry
> Layer 2 — Bloom Filter   → filter non-existent IDs before cache
> Layer 3 — Cache Null     → catch remaining misses for known-missing keys
> Layer 4 — DB             → last resort, rarely hit
> ```
>
> > [!tip] Interview framing
> > *"This is cache penetration — non-existent keys bypass cache forever. First line of defence: rate limiter at the API gateway. Second: bloom filter in front of cache — non-existent IDs never reach cache or DB. Third: cache null values with short TTL for any that slip through."*

---

## Q4 — Leaderboard Design

> [!question] You have a leaderboard for a game with 50 million players. Scores update every few seconds. The top 10 players are fetched millions of times per second. How do you design the caching layer?

> [!success]- Answer
>
> **Why a DB won't work directly:**
> ```
> 50M players, scores updating every few seconds
>
> SELECT * FROM scores ORDER BY score DESC LIMIT 10
> → full sort on every read → collapses at scale
>
> Each score write → triggers re-sort for the top 10 query
> → disk write + sort on millions of rows → DB dies
> ```
>
> **Layer 1 — Redis Sorted Set for score storage:**
> Every score update → `ZADD leaderboard <score> <userId>` directly in Redis. Redis keeps members sorted by score automatically at O(log N).
>
> ```
> ZADD leaderboard 9800 "charlie"  ← O(log N), auto-sorted
> ZRANGE leaderboard 0 9 REV       ← top 10, already sorted, O(log N + 10)
>
> DB updated asynchronously as source of truth
> Leaderboard reads never touch DB ✓
> ```
>
> **Layer 2 — Cache the top 10 result itself:**
> Top 10 is fetched millions of times per second. Even Redis at ~0.1ms — that's unnecessary load. Cache the `ZRANGE` result as a simple String key with TTL = 1–2 seconds:
>
> ```
> SET leaderboard:top10 <serialized result> TTL=2s
>
> Millions of reads → hit this one key → ~0.1ms each
> Every 2 seconds  → one ZRANGE call refreshes it
> ```
>
> **Staleness:**
> 1–2 seconds of staleness is acceptable for a leaderboard. Players can't tell if their rank is 1 second old. This trade-off absorbs massive read traffic cheaply.
>
> > [!tip] Interview framing
> > *"Sorted Set in Redis for score storage and ranking — ZADD on every update, always sorted. Cache the top 10 result as a String key with TTL=1-2s to absorb millions of reads without hitting the Sorted Set each time. DB updated async as source of truth, never touched on reads."*

---

## Q5 — Scaling Beyond One Redis Node

> [!question] You have 500GB of data to cache but a single Redis node maxes out at 64GB. How do you scale?

> [!success]- Answer
>
> **The answer — shard across multiple nodes:**
> Distribute data across multiple Redis nodes so each node holds a fraction of the total keyspace.
>
> **Why naive hashing breaks:**
> ```
> 8 nodes: hash("user:123") % 8 = node 5  ✓
>
> Add one node:
>   hash("user:123") % 9 = node 3  ✗ different node
>
>   ~90% of ALL keys remap to different nodes
>   → mass cache miss → every request hits DB simultaneously → DB collapses
> ```
>
> **The right answer — Consistent Hashing:**
> Place nodes on a hash ring. Each key maps to the nearest node clockwise. Adding a node only affects the keys between it and its neighbour — roughly 1/N of the keyspace remaps, everything else is untouched.
>
> ```
> Before: A ──── B ──── C ──── A (ring)
>
> Add D:  A ──── B ── D ── C ──── A
>                  ↑
>               only the B→D slice remaps ✓
>               A's keys, C's keys: completely untouched
> ```
>
> **Add replication per shard:**
> Each shard has a replica — if a node dies, the replica promotes and that slice stays available. You get both horizontal scale and high availability.
>
> **Redis Cluster does this automatically:**
> Splits keyspace into 16,384 slots, distributes across nodes, handles routing transparently. The app doesn't need to know which node holds which key.
>
> > [!tip] Interview framing
> > *"Shard across multiple Redis nodes using consistent hashing — adding/removing nodes only remaps ~1/N of keys instead of causing a mass miss. Each shard has a replica for availability. Redis Cluster handles this automatically — 16,384 key slots distributed across nodes."*
