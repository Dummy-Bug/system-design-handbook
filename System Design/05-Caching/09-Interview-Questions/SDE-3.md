# Caching — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions with no single right answer. SDE-3 level is about trade-off reasoning, failure mode thinking, and end-to-end system design. Interviewers want to see how you think, not just what you know.

---

## Q1 — End-to-End Caching for Personalized News Feed

> [!question] You're the tech lead for a system that serves personalized news feeds for 100 million users. Feed generation is expensive — takes 2 seconds to compute. Design the entire caching strategy end to end.

> [!success] Answer
>
> **The layers:**
>
> **Layer 1 — CDN for static assets inside the feed:**
> The feed contains images and videos. Serving these from S3 directly for every request consumes massive bandwidth and is slow. CDN caches static assets (thumbnails, videos) at edge servers close to users. Use versioned URLs (`image.v2.jpg`) for instant invalidation without pushing to thousands of edge servers.
>
> Note: CDN caches *assets inside the feed*, not the personalized feed payload itself. Personalized feeds are unique per user — CDN can't serve user:123's feed to user:456.
>
> **CDN for generic/trending feed:**
> "Top Stories" and "Trending Now" sections are the same for all users in a region — perfect CDN candidate. Shared content, high read volume, 1–2 minute staleness acceptable.
>
> **Layer 2 — Redis for personalized feed per user:**
> Pre-compute and cache each user's personalized feed in Redis. Tier by activity:
> ```
> Hot users (daily active)    → longer TTL + refresh-ahead → never see a miss
> Medium users                → standard TTL, cache-aside on request
> Cold users (rarely active)  → let key expire, recompute on next login
> ```
>
> **Layer 3 — Fallback cache for fault tolerance:**
> If the personalization service dies, don't show an error — fall back to a pre-computed generic feed from a separate cache. User gets a slightly less personalized experience instead of a broken page. This is graceful degradation — the same pattern Netflix and Twitter use in production.
>
> **Invalidation strategy:**
> - Normal content: TTL jitter to prevent avalanche
> - Breaking news: event-driven invalidation — publish to a queue, feed service consumes and deletes affected keys
> - CDN assets: versioned URLs, old version expires naturally
>
> **Write strategy:**
> Cache-aside with the personalization service. On a miss, personalization service computes the feed, stores in Redis, returns to user.
>
> **Full picture:**
> ```
> CDN          → static assets + generic trending feed (shared, high hit rate)
> Redis L1     → personalized feed per user, tiered by activity
> Redis L2     → fallback generic feed (fault tolerance / graceful degradation)
> DB + S3      → source of truth, never touched on normal reads
> ```
>
> > [!tip] Interview framing
> > *"Three layers — CDN for static assets and generic trending content with versioned URLs. Redis for personalized feed payloads tiered by user activity — hot users get refresh-ahead, cold users lazy load. A separate fallback cache for graceful degradation if personalization fails. TTL jitter for normal invalidation, event-driven for breaking news."*

---

## Q2 — Surviving a Redis Cluster Outage

> [!question] Your Redis cluster goes down completely for 30 seconds during peak traffic. Walk me through exactly what happens and how you design the system to survive.

> [!success] Answer
>
> **What happens during the 30 second gap:**
> Every cache read misses → all requests fall through to DB → DB receives 100% of traffic instead of the usual 5% → DB collapses under the load.
>
> **How to survive — three mechanisms:**
>
> **1. Sentinel for fast failover:**
> Redis Sentinel monitors the primary and automatically promotes a replica when primary dies. Failover completes in ~10–30 seconds. Reduces the outage window but doesn't eliminate it.
>
> ```
> Primary dies → Sentinels detect → majority vote → replica promoted → app reconnects
> Gap: ~10–30 seconds
> ```
>
> **2. L1 local in-process cache as buffer:**
> Each app server keeps a local in-process cache (Caffeine, Guava) with short TTL (30–60 seconds). During the Redis outage, hot keys that were recently accessed are still served from local memory. The DB never sees those requests.
>
> ```
> Redis down → L1 local cache absorbs hot reads
> Only cold keys (not in L1) fall through to DB
> DB load: fraction of total, not 100%
> ```
>
> **3. Circuit breaker:**
> If Redis is down, stop trying Redis immediately. Don't let every request wait for a Redis timeout before falling through. Circuit breaker detects Redis is unhealthy and routes directly to L1 or DB without the timeout overhead.
>
> **The recovery problem — cold start:**
> When Redis comes back after 30 seconds, cache is cold. Opening full traffic immediately causes another DB spike — this time from cache misses, not from Redis being down.
>
> Fix: cache warming on recovery — pre-load hot keys before routing traffic back through Redis.
>
> **Persistence to minimise data loss:**
> AOF + RDB hybrid ensures Redis recovers with minimal key loss. Most keys restored from disk on restart.
>
> > [!important] The outage gap exists even with Sentinel. Design the system to handle it gracefully — L1 cache + circuit breaker protect the DB during the window. Cache warming prevents cold start after recovery.
>
> > [!tip] Interview framing
> > *"Sentinel handles failover in ~30 seconds — during that window L1 local cache absorbs hot reads and a circuit breaker prevents cold requests waterfalling to DB. AOF + RDB hybrid minimises key loss on recovery. On Redis coming back, warm hot keys before opening full traffic to avoid cold start spike."*

---

## Q3 — Flash Sale Inventory Without Overselling

> [!question] You're building a flash sale — 10 million users try to buy the same item at exactly 12pm. Inventory is 1000 units. How do you use caching to handle this without overselling?

> [!success] Answer
>
> **Why a DB won't work directly:**
> 10 million concurrent requests hitting DB with `UPDATE inventory SET count = count - 1 WHERE count > 0` — even with row-level locking, the DB collapses under that volume.
>
> **Why pessimistic locking on Redis is wrong:**
> Pessimistic lock serialises all 10M requests — every request waits for the lock. Massive queue, terrible latency, still slow.
>
> **The right answer — Redis atomic DECR:**
> Store inventory as a Redis counter:
> ```
> SET inventory:item:123 1000
> ```
>
> On every purchase attempt:
> ```
> DECR inventory:item:123
> → returns new value
> → if value >= 0: sale goes through ✓
> → if value < 0: INCR back, reject request ✗
> ```
>
> Redis is single-threaded. DECR is atomic. No two requests can decrement simultaneously. No overselling. No lock needed.
>
> **Keeping Redis and DB in sync:**
> Every successful DECR also writes to DB — either synchronously (write-through) or batched every few seconds (write-back). Redis is the fast path, DB is source of truth.
>
> **If Redis goes down mid-sale:**
> Fall back to DB with pessimistic locking as last resort. DB can't handle 10M requests but by this point most inventory may already be sold.
>
> **Post-sale reconciliation:**
> Never use cache as sole source of truth for financial/inventory data. After the sale, run a reconciliation job — compare Redis count with DB orders placed and flag any discrepancies.
>
> > [!important] Redis atomic operations eliminate the need for locks entirely for this use case. Single-threaded execution = built-in serialisation without the overhead of explicit locking.
>
> > [!tip] Interview framing
> > *"Store inventory as a Redis counter. Atomic DECR — single-threaded Redis guarantees no race condition, no overselling, no lock needed. Successful DECRs write through to DB. Post-sale reconciliation job catches any discrepancies. Redis goes down → fall back to DB with pessimistic locking."*

---

## Q4 — 95% Cache Hit Rate Is Not Enough

> [!question] A new engineer says "our cache hit rate is 95%, we're good". You disagree. Why?

> [!success] Answer
>
> **95% hit rate is a vanity metric without context.**
>
> **Problem 1 — Which 5% is missing?**
> Hit rate tells you the overall average. It hides which endpoints are missing. If the 5% misses are concentrated on payment or checkout flows:
> ```
> 10M requests/day × 5% miss = 500,000 DB hits/day
> If those are all on /checkout → 500,000 users hitting DB on most critical path
> → DB struggling exactly where you can least afford it
> ```
>
> **Problem 2 — Scale makes small percentages huge:**
> At 10M requests/day, 5% = 500,000 misses. That's not a small number — that's 500,000 users experiencing slow responses. The percentage looks small; the impact is large.
>
> **Problem 3 — Are the 95% hits on valuable data?**
> If someone cached everything — including one-time-use data, OTPs, single-use tokens — the hit rate looks great but RAM is wasted on keys that will never be read again. High hit rate doesn't mean the cache is well-designed.
>
> **What to look at instead:**
> - Hit rate **broken down by endpoint** — not overall
> - **P99 latency** per endpoint before and after cache
> - **DB load** — is it actually reduced?
> - For payment flows: target P99.9 hit rate
> - For feeds: P95 hit rate is acceptable
>
> > [!tip] Interview framing
> > *"95% overall hit rate hides which 5% is missing. If misses are concentrated on payment flows, that's catastrophic at scale. I'd look at hit rate per endpoint, P99 latency, and actual DB load reduction. For critical paths like payments I'd target P99.9 hit rate — at our scale even 0.1% misses represents thousands of users."*

---

## Q5 — Adding Caching From Scratch

> [!question] You join a company as a senior engineer. The system has no caching at all and the DB is struggling. Walk me through your step-by-step process for adding caching.

> [!success] Answer
>
> **Step-by-step:**
>
> **1. Understand the system**
> What does it do, what are the read/write patterns, what data flows where. Don't add caching to something you don't understand.
>
> **2. Confirm caching is the right solution**
> Maybe the DB just needs an index. Maybe a slow query needs optimisation. Cache on top of a broken query just hides the problem. Fix root cause first.
>
> **3. Define success metrics and baseline**
> Before touching anything, measure current state:
> ```
> DB query latency per endpoint   → baseline
> P99 response time               → baseline
> DB CPU / connection count       → baseline
> ```
> Without a baseline you can't prove caching helped or know where to tune. This must happen before building, not after.
>
> **4. Identify what to cache**
> Not everything should be cached:
> ```
> Cache:      high read frequency, staleness acceptable, expensive to fetch
> Don't cache: real-time data, sensitive data, one-time-use data
> ```
>
> **5. Decide staleness tolerance per data type**
> Different data has different freshness requirements. User profiles → 5 min stale is fine. Inventory → stale is dangerous.
>
> **6. Choose TTL and eviction policy**
> TTL per data type based on staleness tolerance. LRU eviction as default. Add jitter on bulk loads to prevent avalanche.
>
> **7. Choose write strategy**
> Cache-aside for read-heavy data. Write-through where consistency matters. Write-back only if write speed is critical and some loss is acceptable.
>
> **8. Decide the layer**
> CDN for static and shared content. Redis for shared application data. Local in-process for ultra-hot keys. L1 + L2 for the highest traffic systems.
>
> **9. Plan cache population strategy**
> Lazy loading (cache-aside) for most data. Cache warming for hot keys before go-live to avoid cold start.
>
> **10. Ship, measure, iterate**
> Compare metrics against baseline. Is hit rate where expected? Did P99 improve? Did DB load drop? Tune TTLs and eviction based on real traffic.
>
> > [!important] Steps 1–3 happen before writing a single line of code. Understanding the problem and defining success metrics upfront is what separates senior engineers from junior ones.
>
> > [!tip] Interview framing
> > *"First confirm caching is the right solution — maybe the DB just needs an index. Then baseline current metrics so you can prove the impact. Identify what to cache, define staleness tolerance, choose TTL and eviction, pick write strategy and layer, plan cache warming. Ship, measure against baseline, iterate."*
