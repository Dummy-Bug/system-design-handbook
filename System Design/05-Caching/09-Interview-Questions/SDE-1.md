# Caching — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of what a cache is, how it works, and when to use it. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is a Cache?

> [!question] What is a cache? Give me a one-line definition and a real-world example.

> [!success]- Answer
>
> **Definition:**
> A cache is a fast, temporary storage layer that holds copies of data so future requests can be served faster without hitting the original source.
>
> The key idea — avoid repeating expensive work by storing the result closer to where it's needed. The expense could be a slow DB query, a network call to a third-party API, or an expensive computation.
>
> **Real-world analogy:**
> Placing your daily reading book on your desk instead of walking to the bookshelf in another room every time. The book is the same — but the access time is drastically reduced. You don't move the bookshelf, you just keep a copy closer.
>
> **In production:**
> ```
> Third-party API response  → cache it → avoid calling API on every request
>                              saves latency, avoids rate limits
>
> DB query result           → cache it → 10,000 users reading same profile
>                              don't trigger 10,000 DB queries
>
> Computed feed             → cache it → don't re-rank 500 posts on every load
> ```
>
> > [!tip] Interview framing
> > *"A cache is a fast temporary storage layer that holds copies of expensive-to-fetch data closer to the requester — avoiding repeated DB queries, API calls, or computations."*

---

## Q2 — Cache Hit and Cache Miss

> [!question] What is a cache hit and a cache miss? Walk me through the full flow for both.

> [!success]- Answer
>
> **Cache Hit:**
> Request comes in → data found in cache → returned immediately. DB never touched.
>
> **Cache Miss:**
> Request comes in → data not in cache → fetch from DB → **store result in cache** → return to client.
>
> ```
> Hit:  Request → Cache → Return ✓  (fast, ~1ms)
>
> Miss: Request → Cache (empty) → DB → Store in Cache → Return
>                next request  → Cache → Return ✓  (fast now)
> ```
>
> **The critical step candidates forget: store in cache after a miss.**
> If you miss and don't store, every future request for the same data is also a miss — the cache never helps.
>
> > [!important] The miss flow has two jobs — fetch the data AND populate the cache. Skip the second step and your cache is useless.
>
> > [!tip] Interview framing
> > *"On a hit, data is returned directly from cache. On a miss, we fetch from DB, store the result in cache so the next request is a hit, then return the data."*

---

## Q3 — What Is TTL and Why Do We Set One?

> [!question] What is TTL? Why do we set one? What happens if you don't?

> [!success]- Answer
>
> **What TTL is:**
> TTL (Time To Live) is a timer on a cache key. When the timer fires, the key is deleted automatically — regardless of whether the data has changed or not. It's purely time-based.
>
> **Why we set one:**
> The cache doesn't automatically know when the DB changes. If a user updates their profile, the cache still has the old value. TTL ensures the key eventually expires so the next request fetches fresh data from DB.
>
> It's a safety net — even if you forget to manually invalidate a key, it won't live forever.
>
> **What happens without TTL:**
> ```
> User updates profile at T=10s
> No TTL set → cache key lives forever
> → cache serves old profile indefinitely
> → user sees their own stale data forever
> → memory fills up with keys never needed again
> ```
>
> **Choosing TTL values:**
> ```
> News feed like count   → stale 30s is fine    → TTL = 30s
> User profile           → stale 5min is fine   → TTL = 300s
> Bank balance           → stale 1s is not fine → don't cache, or TTL = 1s
> ```
>
> > [!important] TTL is a timer, not an invalidation strategy. It doesn't react to DB changes — it only reacts to time. The data can become stale the moment after it's cached and TTL won't know.
>
> > [!tip] Interview framing
> > *"TTL is a safety net — it guarantees no key lives forever. Without it, stale data is served indefinitely and memory fills up with keys never needed again. Always set a TTL even if you use other invalidation strategies."*

---

## Q4 — Cache Eviction vs TTL

> [!question] What is cache eviction? How is it different from TTL? Give an example where eviction fires but TTL hasn't expired.

> [!success]- Answer
>
> **The difference:**
>
> | | Trigger | Mechanism |
> |---|---|---|
> | TTL | Time — key expires after N seconds | Time-based, independent of memory |
> | Eviction | Memory — cache is full, need space | Memory-based, independent of time |
>
> They are completely independent. Both can apply to the same key — whichever fires first wins.
>
> **Example where eviction fires before TTL:**
> ```
> Key "user:123:profile" set with TTL = 5 minutes
>
> At T=3min → cache fills up with other hot data
> → LRU eviction fires → "user:123:profile" hasn't been accessed recently
> → evicted at T=3min, 2 minutes before TTL would have fired
> ```
>
> **Most common eviction policy — LRU (Least Recently Used):**
> The key you haven't accessed the longest gets evicted first. Redis uses LRU by default. The intuition: if you haven't needed it recently, you probably won't need it soon.
>
> > [!important] TTL = time-based expiry. Eviction = memory-pressure-based removal. Two separate mechanisms, both can apply to the same key.
>
> > [!tip] Interview framing
> > *"TTL expires keys by time regardless of memory. Eviction removes keys by memory pressure regardless of time. They're independent — on a full cache, LRU eviction can remove a key that still has 4 minutes of TTL left."*

---

## Q5 — When NOT to Cache

> [!question] A senior engineer says "just add a cache" to fix slow performance. What questions do you ask before doing that?

> [!success]- Answer
>
> **The most important question first — should we even cache?**
>
> Before picking tools or strategies, validate that caching is actually the right solution:
>
> ```
> Is this a caching problem at all?
>   → Maybe the DB query just needs an index
>   → Cache on top of a broken query just hides the problem
>
> Is the data read frequently?
>   → If read once and never again, caching wastes memory
>
> Is staleness acceptable?
>   → Stock prices, live inventory → don't cache
>   → User profiles, feed content → fine to cache
>
> Is the fetch actually expensive?
>   → If DB query takes 1ms, caching adds complexity for no real gain
> ```
>
> **If yes to all — then ask implementation questions:**
> ```
> Which layer?        CDN, Redis, local in-process?
> What data structure? String vs Hash vs Sorted Set?
> What TTL?           Per data type?
> What eviction?      LRU, LFU, TTL-only?
> What write strategy? Cache-aside, write-through, write-back?
> ```
>
> > [!danger] Cache added on top of a slow query is a band-aid. Fix the root cause first — add an index, optimise the query. Then add caching on top of a fast query to make it faster.
>
> > [!tip] Interview framing
> > *"Before adding a cache I'd ask — is the data read frequently enough to justify it, is staleness acceptable, and is the fetch actually expensive? If yes to all three, then decide layer, data structure, TTL, and eviction policy. Otherwise fix the root cause first."*
