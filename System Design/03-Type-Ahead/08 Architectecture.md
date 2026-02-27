[[Architecture.png]]

# Flow A — TypeAhead (user typing / prefix suggestions)

Goal: return top-K suggestions for a prefix in <50ms p99 with extremely high QPS.

### User-visible example

User types: `par` → Expect top 10 suggestions such as `["paris hotels","paris weather","park near me", ...]`.

### Preconditions (client)

- Debounce input (example: 200–300ms).
    
- Only call if `3 <= prefix.length <= 20`.
    
- Cancel previous in-flight request when new keystroke arrives.
    
- Client caches last responses for immediate reuse.
    

### Full step-by-step (very detailed)

1. **Client** (debounced) issues HTTP GET to:
    
    `GET /api/v1/typeahead?partialSearchQuery=par`
    
    The request includes client headers, optional auth token, locale, and maybe personalization signals (userId, geo).
    
2. **API Gateway**
    
    - Authenticates token.
        
    - Applies per-IP and per-user rate limiting (token bucket).
        
    - Applies global QPS circuit protection (reject or degrade if overloaded).
        
    - Adds routing headers (version, region).
        
    - Checks CDN cache headers (if applicable) and forwards to Autocomplete Service.
        
3. **Edge / CDN (optional)**
    
    - If you cache top popular prefixes at CDN edge, CDN may return immediately.
        
    - Cache key = `typeahead:v{version}:prefix:{region}:{prefix}`.
        
4. **Autocomplete Service receives request**
    
    - It first checks local LRU cache (memory) keyed by prefix + personalization fingerprint.
        
    - If not found, it queries **Redis**.
        
5. **Redis Read**
    
    - Redis key pattern: `typeahead:prefix:{prefix_hash}` or `prefix:{prefix}` (choose hashed key to avoid very long keys).
        
    - Redis command to get top-K in descending frequency:
        
        `ZREVRANGE prefix:par 0 9 WITHSCORES`
        
        or (if you store string IDs and then resolve):
        
        `ZREVRANGE prefix:par 0 9 HMGET queries <id1> <id2> ...`
        
    - Redis returns the top 10 items sorted by score (frequency).
        
6. **Post-process & ranking**
    
    - Autocomplete service optionally applies personalization ranking (re-rank by user weight) or filters (safe search, locale).
        
    - If personalization is used, apply a small re-scoring factor (local in service) instead of retrieving an entirely different set.
        
7. **Response formation**
    
    - Return JSON: `{ success: true, data: [ ...top10... ] }`.
        
    - Add HTTP headers: `Cache-Control`, `ETag`, rate-limit info.
        
    - Optionally add a `staleness` header indicating snapshot age (e.g., `X-Index-Version: v20260117-1200`).
        
8. **Client receives & displays suggestions instantly.**
    

### Latency expectations

- Local cache hit: <1ms.
    
- Redis read (same region): <1ms.
    
- Network + processing: target p50 ~ 10–20ms, p99 <50ms.
    

### Important implementation notes

- **Top-K precomputed per prefix** — there is no DFS or on-demand traversal at read time.
    
- **Keys are immutable snapshots**. You serve from a versioned snapshot so reads are lock-free.
    
- **Personalization** should be a light re-rank on top of top-K to avoid extra Redis calls.
    
- **Edge caching** for hot prefixes reduces origin load massively.
    

---

# Flow B — Search (user clicks a suggestion / submits full query)

Goal: record the successful query (for ranking signal) and serve full search results. Writes are asynchronous and approximate. Do not block reads.

### User-visible example

User clicks `paris city cost of living` or presses Enter. They expect paginated search results and the system must _record_ the click/submission for ranking.

### Full step-by-step (very detailed)

1. **Client** issues search request:
    
    `POST /api/v1/search Body: { query: "paris city cost of living", userId: "..." }`
    
    This is the full search submission. API may also be triggered by clicking a suggestion.
    
2. **API Gateway**
    
    - Auth, rate-limit, metrics.
        
    - Request routed to Search Results Service.
        
3. **Search Results Service**
    
    - Produces the user-facing search results. (This is the paginated, heavyweight result from your search index / DB / ES.)
        
    - Responds immediately to the client with search results (label `b` on diagram).
        
    - Enqueues a _write event_ to the **Queue**. The write event contains:
        
        `{ eventType: "SEARCH_SUBMIT", query: "paris city cost of living", userId, timestamp, requestId }`
        
    - Important: responding to client is synchronous and low-latency; the update of typeahead ranking is asynchronous.
        
4. **Queue (Kafka/SQS)**
    
    - Durably stores events.
        
    - Partitioning key should be `query` hash or `prefix` so that related updates land in same partition for aggregation.
        
    - Configure retention and monitor lag.
        
5. **Processing / Aggregator Pipeline**
    
    - Consumer(s) read events from the queue.
        
    - The consumer does cheap local aggregation (in-memory map or Redis local cache):
        
        `localCounts[query] += 1`
        
    - This aggregator batches updates and applies two reduction strategies (you proposed earlier):
        
        - **Batching threshold**: only flush to Redis when localCounts[query] >= BATCH_THRESHOLD (e.g., 100).
            
        - **Sampling**: randomly only process 1% of events to further reduce write volume (useful when traffic huge).
            
    - When flush condition is met, the pipeline computes **prefix updates** and writes to Redis in a single atomic operation per prefix (prefer Lua script).
        
6. **How aggregator writes to Redis (detailed)**
    
    - For the query `"paris city cost of living"` compute prefixes to update:
        
        `p, pa, par, pari, paris, paris , paris , ... up to 20 chars or word-level prefixes depending on design`
        
        (Most systems use character prefixes up to configured length).
        
    - For each prefix key `prefix:par`, you perform:
        
        1. `ZINCRBY prefix:par <delta> "paris city cost of living"` to increase score.
            
        2. Trim the ZSET to top-M (e.g., M=500) using:
            
            `ZREMRANGEBYRANK prefix:par 0 -501`
            
            or use a Lua script that does `ZINCRBY` + `ZREMRANGEBYRANK` atomically.
            
    - You also update a global query counter for analytics:
        
        `HINCRBY query:counts "paris city cost of living" <delta>`
        
        or a global ZSET `ZINCRBY global:queries <delta> "paris city cost of living"`.
        
7. **Snapshot & rebuild fallback**
    
    - In addition to incremental updates, you periodically run a full offline rebuild job from nightly analytics (to correct sampling/batching approximation).
        
    - Publish new snapshot version and atomically swap keys or change the pointer the Autocomplete Service reads.
        

### Why batching & sampling

- Raw write volume is enormous. If you updated Redis for every single submit you’d overload the cluster.
    
- Batching reduces writes by a factor equal to the threshold.
    
- Sampling reduces writes probabilistically while preserving relative ordering.
    
- Combining both gives large write reduction while maintaining useful ranking signals.
    

### Redis atomicity & correctness

- Use Lua scripts to make `ZINCRBY` + `ZREMRANGEBYRANK` atomic to avoid race conditions.
    
- Use consistent key naming and versioning to perform atomic swaps on rebuild.
    

---

# Redis key design and commands (practical)

- **Prefix ZSET key**: `typeahead:v{version}:prefix:{prefix}`  
    Use versioned keys for atomic snapshot swaps.
    
- **Query count hash**: `typeahead:counts` (HASH) or `typeahead:global` (ZSET)
    
- **Redis read**:
    
    `ZREVRANGE typeahead:v42:prefix:par 0 9 WITHSCORES`
    
- **Redis incremental write** (Lua pseudo):
    
    `local key = KEYS[1] -- prefix key local member = ARGV[1] -- query local delta = tonumber(ARGV[2]) redis.call('ZINCRBY', key, delta, member) redis.call('ZREMRANGEBYRANK', key, 0, -501) -- keep top 500 return 1`
    
- **Global counter**:
    
    `HINCRBY typeahead:counts "paris city cost of living" <delta>`
    

---

# Putting it all together — short sequence diagrams

### TypeAhead (read)

`Client --(debounced GET prefix)--> API Gateway --> Autocomplete Service --> Redis ZSET (ZREVRANGE) --> Autocomplete Service --> API Gateway --> Client`

### Search Submit (write)

`Client (click) --> API Gateway --> Search Results Service (responds) --> Enqueue event --> Q`