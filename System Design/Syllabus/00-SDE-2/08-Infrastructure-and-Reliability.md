## Phase 8 — Infrastructure & Reliability Patterns

> HLD relevance: These patterns appear in the deep-dive sections of every case study.

### SDE-2 Depth Bar For This Phase
- Know the common production patterns that make systems survivable: retries, circuit breakers, rate limiting, health checks, deployment strategy.
- Be able to talk about service boundaries, BFF, geo setup, and storage patterns with real tradeoffs.
- Explain how systems degrade, recover, and roll out safely.
- Service mesh, data migration at scale, and HLS/DASH are SDE-3 topics — stop short of those here.

### 7.1 Microservices vs Monolith
- Monolith — single deployable unit, simple to start, harder to scale teams
- Microservices — independently deployable, team autonomy, operational overhead
- Honest tradeoff — don't jump to microservices for a new system
- Data ownership — each service owns its data, no shared DB
- Inter-service communication — sync (REST/gRPC) vs async (Kafka/queue)
- When to split — bounded by domain, not by technical layer

### 7.2 BFF (Backend-for-Frontend) Pattern
- Problem: mobile needs lightweight response, web needs rich response. One API can't serve both well.
- BFF: a thin API layer per client type that aggregates and transforms backend responses
- Why not multiple client calls — mobile on 3G making 5 round trips is unacceptable
- Trade-off: another service to maintain, keep it thin (aggregation only, no business logic)
- Alternative: GraphQL lets the client specify exactly which fields it needs

### 7.3 Resilience Patterns

#### Circuit Breaker
- Problem: downstream is slow, your threads pile up, your service dies too
- States — Closed (normal), Open (reject fast), Half-Open (probe recovery)
- Open circuit when error rate crosses threshold
- Fallback — return cached response, default value, or graceful error
- Prevents cascading failures in microservice chains

#### Retry + Exponential Backoff + Jitter
- Retry on transient failures (5xx, timeout, connection refused)
- Do NOT retry on client errors (4xx)
- Exponential backoff — double wait each retry (1s, 2s, 4s, 8s...)
- Jitter — randomize backoff to prevent synchronized retry storms
- Max retry limit — don't retry forever

#### Timeout + Deadline Propagation
- Always set timeouts — unbounded waits exhaust thread pools
- Connection timeout vs read timeout — set both
- Deadline propagation — pass remaining budget downstream ("you have 200ms total")

#### Bulkhead Pattern
- Isolate resources per downstream — separate thread pool per dependency
- One slow downstream can only exhaust its own pool

#### Health Check Patterns
- Shallow health check — GET /health returns 200 if process is running. For load balancers.
- Deep health check — GET /health/ready checks DB, Redis, downstream. Returns 503 if any critical dependency is down.
- Liveness vs readiness (Kubernetes) — liveness: restart if dead, readiness: stop traffic if not ready

### 7.4 Rate Limiting
- Token Bucket — tokens refill at rate R, burst allowed up to capacity C
- Leaky Bucket — requests processed at constant rate, excess queued or dropped
- Fixed Window Counter — count in current window, reset at boundary. 2× rate at window edge.
- Sliding Window Log — store timestamp of every request. Accurate, memory-heavy.
- Sliding Window Counter — blend of current + previous window. Balance of accuracy and memory.
- Distributed rate limiting — Redis INCR + EXPIRE, Lua script for atomic check-and-increment
- Rate limit headers — X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After

### 7.5 Probabilistic Data Structures

#### Bloom Filter
- Answers "is X definitely NOT in the set?" — zero false negatives, false positives possible
- How it works — bit array + k hash functions, set bits on insert, check all bits on query
- Use cases — web crawler (skip crawled URLs), cache penetration, username availability

#### HyperLogLog
- Approximate count of unique items in a stream
- O(log log n) memory, error rate ~1-2%
- Redis commands — PFADD, PFCOUNT, PFMERGE
- Use cases — unique visitors, distinct queries, DAU counting

#### Count-Min Sketch
- Approximate frequency of items in a stream
- 2D counter array + multiple hash functions, always overestimates
- Use cases — top-K heavy hitters, trending topics, frequency capping

#### Skip List
- Probabilistic sorted data structure — O(log n) for search, insert, delete
- Redis Sorted Set is backed by a skip list internally

### 7.6 Geo-Spatial Indexing
- Problem — "find all drivers within 5km" — standard B+Tree cannot answer this
- Geohash — encode lat/lng as base32 string, prefix = proximity, query 8 surrounding cells
- Quadtree — recursively split 2D space into 4 quadrants, good for dynamic driver locations
- S2 Geometry (awareness) — Google's spherical cells, used in Google Maps and Uber
- How Uber uses it — drivers update location every 4 seconds, geohash stored in Redis

### 7.7 ID Generation
- Auto-increment — simple, centralized, reveals record count, not distributed-safe
- UUID v4 — random 128-bit, globally unique, not sortable, index-unfriendly
- Snowflake ID (Twitter/Discord) — 64-bit: [41-bit timestamp ms][10-bit machine ID][12-bit sequence]
  - Sortable by creation time, no coordination needed, clock skew must be handled
- Shard-encoded ID — embed shard key in ID, routing derivable without lookup

### 7.8 Security Essentials
- JWT — stateless token, verify without DB hit
- Session token — server stores session, cookie holds session ID
- OAuth 2.0 — delegated access (login with Google), Authorization Code flow
- API keys — long-lived, for service-to-service
- RBAC — roles have permissions, users have roles
- ACL — per-resource permission list
- TLS everywhere, AES-256 at rest

### 7.9 Multi-Region & Global Architecture
- Why multi-region — reduce latency for global users, survive region outage
- Active-passive — one region handles traffic, other is warm standby
- Active-active — both regions serve traffic, need conflict resolution for writes
- Data replication across regions — sync (strong consistency) vs async (low latency, lag)
- GeoDNS — route users to nearest region based on their IP
- Read local, write global — serve reads from nearest region, route writes to home region
- Conflict resolution — LWW for simple cases, application merge for complex cases

### 7.10 Storage Patterns at Scale
- Storage tiers — hot (SSD/Redis), warm (object store), cold (Glacier)
- Chunked upload — split large file into 4–8 MB chunks, upload in parallel, server reassembles
  - Resumable — on failure, restart from last successful chunk
  - Deduplication — hash each chunk, skip upload if chunk already exists (Dropbox)
- Content-addressable storage — SHA256 of content = storage key, automatic dedup

### 7.11 Deployment Strategies
- Rolling deploy — replace instances one at a time, old and new briefly coexist
  - API must be backward compatible during rollout
- Blue-green — two identical environments, switch traffic at load balancer. Instant rollback.
- Canary — route small % of traffic to new version, watch error rate, expand or rollback
- Feature flags — deploy code disabled, enable for % of users without redeployment
- Key point — always pair deployment strategy with DB migration strategy
