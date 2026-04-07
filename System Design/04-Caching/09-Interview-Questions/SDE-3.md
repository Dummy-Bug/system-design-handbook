# Caching — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions with no single right answer. SDE-3 level is about trade-off reasoning, failure mode thinking, and end-to-end system design. Interviewers want to see how you think, not just what you know.

---

## Q1 — End-to-End Caching for a Personalised News Feed

> [!question] You're the tech lead for a system that serves personalised news feeds for 100 million users. Feed generation is expensive — takes 2 seconds to compute. Design the entire caching strategy end to end.

> [!success]- Answer
>
> **The layers — outside in:**
>
> **Layer 1 — CDN for static assets inside the feed:**
> The feed contains images and videos. Serving these from S3 directly for every request consumes massive bandwidth and is slow. CDN caches static assets at edge servers close to users.
>
> ```
> Use versioned URLs: thumbnail.v2.jpg
> → instant invalidation without purging thousands of edge servers
> → old version expires naturally
>
> Note: CDN caches ASSETS inside the feed, not the personalised feed payload itself
>       Personalised feeds are unique per user — CDN can't serve user:123's feed to user:456
> ```
>
> **CDN for generic/trending sections:**
> "Top Stories" and "Trending Now" are the same for all users in a region — perfect CDN candidate. Shared content, high read volume, 1–2 minute staleness acceptable.
>
> **Layer 2 — Redis for personalised feed per user:**
> Pre-compute and cache each user's personalised feed. Tier by activity to avoid wasting memory on cold users:
> ```
> Hot users (daily active)  → longer TTL + refresh-ahead → never see a miss
> Medium users              → standard TTL, cache-aside on request
> Cold users (rarely active) → let key expire, recompute on next login
>                              no point storing feed for users who visit monthly
> ```
>
> **Layer 3 — Fallback cache for fault tolerance:**
> If the personalisation service dies, don't show an error — fall back to a pre-computed generic feed from a separate cache.
> ```
> Personalisation service down:
>   → fallback cache → user gets slightly less personalised feed
>   → not a broken page ✓
>
> This is graceful degradation — the same pattern Netflix uses
> ```
>
> **Invalidation strategy:**
> ```
> Normal content:    TTL jitter → prevent avalanche
> Breaking news:     event-driven → publish to queue → feed service deletes affected keys
> CDN assets:        versioned URLs → old versions expire naturally
> ```
>
> **Full picture:**
> ```
> CDN          → static assets + generic trending (shared, high hit rate)
> Redis L1     → personalised feed per user, tiered by activity
> Redis L2     → fallback generic feed (graceful degradation)
> DB + S3      → source of truth, never touched on normal reads
> ```
>
> > [!tip] Interview framing
> > *"Three layers — CDN for static assets and generic trending content with versioned URLs. Redis for personalised feed payloads tiered by user activity — hot users get refresh-ahead, cold users lazy load. A separate fallback cache for graceful degradation if personalisation fails. TTL jitter for normal invalidation, event-driven for breaking news."*

---

## Q2 — Surviving a Redis Cluster Outage

> [!question] Your Redis cluster goes down completely for 30 seconds during peak traffic. Walk me through exactly what happens and how you design the system to survive it.

> [!success]- Answer
>
> **What happens without protection:**
> ```
> Redis down → every cache read misses
>           → all requests fall through to DB
>           → DB receives 100% of traffic instead of the usual 5%
>           → DB collapses under the load
> ```
>
> **How to survive — three mechanisms working together:**
>
> **1. Redis Sentinel for fast failover:**
> Sentinel monitors the primary and automatically promotes a replica when it dies.
> ```
> Primary dies → Sentinels detect → majority vote → replica promoted → app reconnects
> Gap: ~10–30 seconds
>
> Reduces the outage window but doesn't eliminate it
> The 10–30 second gap still needs to be covered
> ```
>
> **2. L1 local in-process cache as buffer:**
> Each app server keeps a local in-process cache (Caffeine, Guava) with a short TTL (30–60 seconds).
> ```
> Redis down → L1 local cache absorbs hot reads
>              keys that were recently accessed: still served from local memory
>              DB never sees those requests ✓
>
>              Only cold keys (not in L1) fall through to DB
>              DB load: fraction of total, not 100%
> ```
>
> **3. Circuit breaker on Redis:**
> If Redis is down, stop trying Redis immediately. Don't let every request wait for a timeout before falling through.
> ```
> Without circuit breaker:
>   Request → try Redis (waits 500ms timeout) → miss → DB
>   Latency per request: +500ms during outage
>
> With circuit breaker:
>   Redis unhealthy detected → route directly to L1 or DB
>   No timeout overhead ✓
> ```
>
> **The recovery problem — cold start:**
> When Redis comes back after 30 seconds, cache is cold. Opening full traffic immediately causes another DB spike — this time from cache misses, not from Redis being down.
> ```
> Fix: cache warming on recovery
>      pre-load hot keys before routing traffic back through Redis
> ```
>
> **Persistence to minimise key loss:**
> AOF + RDB hybrid ensures Redis recovers with most keys restored from disk on restart.
>
> > [!important] The outage gap exists even with Sentinel. Design the system to handle the window gracefully — L1 cache + circuit breaker protect the DB during the gap. Cache warming prevents the cold start spike after recovery.
>
> > [!tip] Interview framing
> > *"Sentinel handles failover in ~30 seconds — during that window L1 local cache absorbs hot reads and a circuit breaker prevents cold requests waterfalling to DB. AOF + RDB hybrid minimises key loss on recovery. On Redis coming back, warm hot keys before opening full traffic to avoid the cold start spike."*

---

## Q3 — Flash Sale Inventory Without Overselling

> [!question] You're building a flash sale — 10 million users try to buy the same item at exactly 12pm. Inventory is 1,000 units. How do you use caching to handle this without overselling?

> [!success]- Answer
>
> **Why the DB can't handle this directly:**
> ```
> 10M concurrent requests:
>   UPDATE inventory SET count = count - 1 WHERE item_id = 123 AND count > 0
>
>   Even with row-level locking: DB serialises requests → massive queue → collapses
>   Each request waits for the lock → latency explodes → timeouts → retries → worse
> ```
>
> **Why pessimistic locking on Redis is also wrong:**
> Explicit locks serialise all 10M requests — every request waits in a queue. You've just rebuilt the same DB problem, but in Redis.
>
> **The right answer — Redis atomic DECR:**
> Store inventory as a Redis counter. Redis is single-threaded — DECR is atomic by design. No lock needed.
>
> ```
> SET inventory:item:123 1000
>
> On every purchase attempt:
>   result = DECR inventory:item:123
>   → returns new value
>   → if result >= 0: sale goes through ✓
>   → if result < 0:  INCR back, reject request ✗ (oversold, undo)
>
> Redis single-threaded = no two requests DECR simultaneously
> No race condition, no overselling ✓
> ```
>
> **Keeping Redis and DB in sync:**
> ```
> Every successful DECR → write to DB
>   Synchronous (write-through): DB always accurate, slightly slower
>   Batched every few seconds (write-back): faster, small window of discrepancy
>
> Redis = fast path for the sale
> DB    = source of truth for reconciliation
> ```
>
> **If Redis goes down mid-sale:**
> Fall back to DB with pessimistic locking. DB can't handle 10M requests but by this point most inventory may already be sold — the DB only sees the tail.
>
> **Post-sale reconciliation:**
> Never use cache as the sole source of truth for financial/inventory data. After the sale, compare Redis count with DB orders placed and flag any discrepancies.
>
> > [!important] Redis atomic operations eliminate the need for locks entirely here. Single-threaded execution = built-in serialisation without the overhead of explicit locking.
>
> > [!tip] Interview framing
> > *"Store inventory as a Redis counter. Atomic DECR — single-threaded Redis guarantees no race condition, no overselling, no lock needed. Successful DECRs write through to DB. Post-sale reconciliation catches any discrepancies. Redis goes down → fall back to DB with pessimistic locking."*

---

## Q4 — 95% Cache Hit Rate Is Not Enough

> [!question] A new engineer says "our cache hit rate is 95%, we're good." You disagree. Why?

> [!success]- Answer
>
> **95% hit rate is a vanity metric without context.**
>
> **Problem 1 — Which 5% is missing?**
> Hit rate tells you the overall average. It hides which endpoints are missing. If the 5% misses are concentrated on payment or checkout flows:
> ```
> 10M requests/day × 5% miss = 500,000 DB hits/day
>
> If those 500,000 are all on /checkout:
>   → DB struggling on the most critical path
>   → Exactly where you can least afford it
>
> vs. if those 500,000 are on low-traffic admin pages:
>   → Completely acceptable
>
> Same 95% hit rate. Completely different impact.
> ```
>
> **Problem 2 — Scale makes small percentages huge:**
> ```
> At 10M requests/day: 5% = 500,000 misses
> Those are 500,000 users experiencing slow responses
>
> The percentage looks small
> The impact is not
> ```
>
> **Problem 3 — Are the 95% hits on valuable data?**
> If someone cached everything including one-time-use data, OTPs, and single-use tokens — the hit rate looks great but RAM is wasted on keys that will never be read again. High hit rate doesn't mean the cache is well-designed.
>
> **What to look at instead:**
> ```
> Hit rate per endpoint — not overall average
> P99 latency per endpoint before and after cache
> Actual DB load reduction
>
> For payment flows:  target P99.9 hit rate
> For feed content:   P95 hit rate is acceptable
> ```
>
> > [!tip] Interview framing
> > *"95% overall hit rate hides which 5% is missing. If misses are concentrated on payment flows, that's catastrophic at scale. I'd look at hit rate per endpoint, P99 latency, and actual DB load reduction. For critical paths like payments I'd target P99.9 hit rate — at our scale even 0.1% misses represents thousands of users."*

---

## Q5 — Adding Caching From Scratch

> [!question] You join a company as a senior engineer. The system has no caching at all and the DB is struggling. Walk me through your step-by-step process.

> [!success]- Answer
>
> **Step 1 — Understand the system:**
> What does it do, what are the read/write patterns, what data flows where. Don't add caching to something you don't understand.
>
> **Step 2 — Confirm caching is the right solution:**
> ```
> Maybe the DB just needs an index
> Maybe a slow query needs optimisation
> Cache on top of a broken query just hides the problem
>
> Fix root cause first → then cache on top of a fast query to make it faster
> ```
>
> **Step 3 — Baseline first, always:**
> ```
> Before touching anything, measure current state:
>   DB query latency per endpoint   → baseline
>   P99 response time               → baseline
>   DB CPU / connection count       → baseline
>
> Without a baseline you can't prove caching helped
> This must happen before building, not after
> ```
>
> **Step 4 — Identify what to cache:**
> ```
> Cache:        high read frequency, staleness acceptable, expensive to fetch
> Don't cache:  real-time data, sensitive data (balances), one-time-use data
> ```
>
> **Step 5 — Staleness tolerance per data type:**
> Different data has different freshness requirements.
> ```
> User profiles     → 5 min stale is fine
> Feed content      → 30 sec stale is fine
> Inventory         → stale is dangerous → cache carefully or don't cache
> ```
>
> **Step 6 — TTL, eviction, write strategy, layer:**
> ```
> TTL per type     → based on staleness tolerance, add jitter on bulk loads
> Eviction         → LRU as default
> Write strategy   → cache-aside for read-heavy, write-through where consistency matters
> Layer            → CDN for static, Redis for app data, L1 for ultra-hot keys
> ```
>
> **Step 7 — Cache warming:**
> Lazy loading (cache-aside) for most data. Cache warming for hot keys before go-live — avoid cold start on deploy.
>
> **Step 8 — Ship, measure, iterate:**
> Compare metrics against baseline. Did P99 improve? Did DB load drop? Is hit rate where expected? Tune TTLs and eviction based on real traffic, not guesses.
>
> > [!important] Steps 1–3 happen before writing a single line of code. Understanding the problem and defining success metrics upfront is what separates senior engineers from everyone else.
>
> > [!tip] Interview framing
> > *"First confirm caching is the right solution — maybe the DB just needs an index. Then baseline current metrics so you can prove the impact. Identify what to cache, define staleness tolerance per data type, choose TTL and eviction, pick write strategy and layer, plan cache warming. Ship, measure against baseline, iterate."*
