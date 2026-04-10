## Phase 8 — Infrastructure & Reliability Patterns

> HLD relevance: These patterns appear in the deep-dive sections of every case study.
> Rate limiter is its own case study. Geo-spatial for Uber. ID generation for URL shortener.

### SDE-2 Depth Bar For This Phase
- Know the common production patterns that make systems survivable: retries, circuit breakers, rate limiting, health checks, deployment strategy, migration strategy.
- Be able to talk about service boundaries, sidecars, BFF, geo setup, and storage patterns with real tradeoffs.
- Explain how systems degrade, recover, and roll out safely.
- This is where SDE-2 starts sounding production-ready instead of diagram-only.

### 7.1 Microservices vs Monolith
- Monolith — single deployable unit, simple to start, harder to scale teams
- Microservices — independently deployable, team autonomy, operational overhead
- Honest tradeoff — don't jump to microservices for a new system
- Data ownership — each service owns its data, no shared DB
- Inter-service communication — sync (REST/gRPC) vs async (Kafka/queue)
- When to split — bounded by domain, not by technical layer

### 7.1b Service Mesh & Sidecar Pattern
- **Problem** — in a microservices architecture, every service needs: mTLS, retries, circuit breaking, observability, traffic routing. Implementing this in every service's code is duplicated effort and inconsistent.
- **Sidecar proxy** — a lightweight proxy process deployed alongside every service instance (same pod in K8s). All inbound/outbound traffic flows through the sidecar.
  - The sidecar handles: TLS termination, retries, circuit breaking, load balancing, metrics collection, distributed tracing injection
  - The application code knows nothing about this — it just sends plain HTTP/gRPC to localhost
- **Service mesh** — the collection of all sidecars + a control plane that configures them
  - **Istio** — most well-known service mesh; uses Envoy as the sidecar proxy
  - **Linkerd** — lighter alternative, Rust-based proxy
  - Control plane pushes configuration (retry policies, routing rules, mTLS certs) to all sidecars
- **What it enables**
  - mTLS everywhere without application code changes — sidecar handles cert rotation
  - Traffic splitting — route 5% of traffic to canary version (canary deployment without app-level logic)
  - Observability for free — every sidecar emits latency, error rate, request count metrics
- **Trade-off** — adds latency per hop (extra network hop through sidecar), operational complexity, resource overhead per pod
- **When to mention** — any large microservices architecture where the interviewer asks "how do you handle service-to-service security?" or "how do you get observability across services?"
- **When NOT to mention** — small systems, monoliths, or when you only have 2-3 services. Overkill for simple architectures.

### 7.1c Backend-for-Frontend (BFF) Pattern
- Problem: mobile app needs a lightweight response (small payload, fewer fields), web dashboard needs a rich response (full detail, multiple entities joined). One API can't serve both well.
- BFF: a thin API layer per client type that aggregates and transforms backend service responses
  - Mobile BFF → calls 3 backend services, returns a compact combined response
  - Web BFF → calls the same 3 services but returns full detail with extra fields
- Why not just have the client make multiple calls? — mobile on 3G making 5 round trips is unacceptable; BFF reduces to 1 call from the client's perspective
- Trade-off: another service to maintain, can become a dumping ground for business logic (keep it thin — aggregation and transformation only)
- Alternative: GraphQL solves a similar problem by letting the client specify exactly which fields it needs
- When to mention: any case study with mobile + web clients (chat, news feed, ride-sharing)

### 7.2 Resilience Patterns

#### Circuit Breaker
- Problem: downstream service is slow, your threads pile up waiting, your service dies too
- States — Closed (normal), Open (reject fast, no downstream calls), Half-Open (probe recovery)
- Open the circuit when error rate crosses threshold
- Fallback — return cached response, default value, or graceful error
- Prevents cascading failures in microservice chains

#### Retry + Exponential Backoff + Jitter
- Retry on transient failures (5xx, timeout, connection refused)
- Do NOT retry on client errors (4xx) — retrying won't fix a bad request
- Exponential backoff — double wait each retry (1s, 2s, 4s, 8s...)
- Jitter — randomize backoff to prevent synchronized retry storms
- Max retry limit — don't retry forever
- Applies to: any service calling another service, Kafka producer retries

#### Timeout + Deadline Propagation
- Always set timeouts — unbounded waits exhaust thread pools
- Connection timeout vs read timeout — set both
- Deadline propagation — pass remaining budget downstream ("you have 200ms total")
- Total budget across retries — don't let 3 retries × 5s = exceed 10s parent timeout

#### Bulkhead Pattern
- Isolate resources per downstream — separate thread pool per dependency
- One slow downstream can only exhaust its own pool, not the entire service

#### Health Check Patterns
- **Shallow health check** — `GET /health` returns 200 if the process is running. No dependency checks. Fast, used by load balancers to know if the instance is alive.
- **Deep health check** — `GET /health/ready` checks DB connectivity, Redis connectivity, disk space, downstream services. Returns 503 if any critical dependency is down.
- **Liveness vs Readiness** (Kubernetes terminology, but the concept is universal)
  - Liveness: "is this process alive?" — if no, restart it
  - Readiness: "can this process serve traffic?" — if no, stop sending traffic but don't restart (maybe DB is temporarily down)
- Load balancer uses shallow checks to route traffic. Monitoring uses deep checks to alert on dependency failures.
- Key interview point: "I'd expose a shallow /health for the load balancer to detect dead instances quickly, and a deep /health/ready that checks DB and Redis — if a dependency is down, the LB stops routing to that instance while it recovers."

### 7.3 Rate Limiting
> This is its own case study — know all 5 algorithms deeply

- Token Bucket — tokens refill at rate R, burst allowed up to capacity C
  - Most common, allows short bursts, smooth average rate
- Leaky Bucket — requests processed at constant rate, excess queued or dropped
  - Strict rate, no burst, smooth output
- Fixed Window Counter — count reqs in current window, reset at window boundary
  - Simple, but boundary condition allows 2x rate at window edge
- Sliding Window Log — store timestamp of every request, count within window
  - Accurate, memory-heavy (stores all timestamps)
- Sliding Window Counter — blend of current + previous window by overlap fraction
  - Balance of accuracy and memory efficiency

- Where to rate limit — API gateway (user/IP level), per-service (protect downstream)
- Distributed rate limiting — Redis INCR + EXPIRE, Lua script for atomic check-and-increment
- Rate limit headers — X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After
- Hard limit (drop) vs soft limit (queue or degrade)

### 7.4 Probabilistic Data Structures

#### Bloom Filter
- Answers "is X definitely NOT in the set?" with zero false negatives
- False positives possible — may say X is in set when it isn't
- How it works — bit array + k hash functions, set bits on insert, check all bits on query
- Space-efficient — millions of items in kilobytes
- Use cases
  - Web crawler — skip already-crawled URLs
  - Cache penetration — block DB queries for keys known not to exist
  - Username availability — fast "definitely available" check before DB lookup

#### HyperLogLog
- Approximate count of unique items in a stream
- Uses O(log log n) memory instead of O(n)
- Error rate ~1-2%, acceptable for analytics
- Redis commands — PFADD (add item), PFCOUNT (get estimate), PFMERGE (combine)
- Use cases — unique visitors per page, distinct search queries, DAU counting

#### Count-Min Sketch
- Approximate frequency of items in a stream
- 2D counter array + multiple hash functions
- Always overestimates, never underestimates
- Use cases — top-K heavy hitters, trending topics, frequency capping in ads
- Directly applies to: K-Heavy Hitters, Ad Click Aggregation case studies

#### Skip List
- Probabilistic sorted data structure — O(log n) for search, insert, delete
- Redis Sorted Set is backed by a skip list
- Useful to know when explaining how Redis leaderboards work internally

### 7.5 Geo-Spatial Indexing
> Directly applies to: Uber, Google Maps case studies

- Problem — find all drivers within 5km of a user in real time
- Geohash
  - Encode lat/lng as a base32 string — "9q8yy" represents a cell
  - Prefix = proximity — "9q8yy" and "9q8yz" are neighbors
  - Longer string = smaller cell = more precision
  - Edge case — cells on geohash boundary aren't necessarily adjacent string-wise
- Quadtree
  - Recursively split 2D space into 4 quadrants
  - Dense areas get more splits, sparse areas fewer
  - Good for dynamic data like driver locations
- S2 Geometry (Google) — spherical cells at multiple levels, used in Google Maps
- How Uber uses it — drivers update location every 4 seconds, geohash stored in Redis

### 7.6 ID Generation
> Directly applies to: URL Shortener, Unique ID Generator case studies

- Auto-increment — simple, centralized, reveals record count, not distributed-safe
- UUID v4 — random 128-bit, globally unique, not sortable, index-unfriendly (random inserts = B+ tree splits)
- Snowflake ID (Twitter/Discord)
  - 64-bit integer: [41-bit timestamp ms] [10-bit machine ID] [12-bit sequence]
  - Sortable by creation time — great for DB indexes
  - No coordination needed — each machine generates independently
  - Clock skew problem — handle by waiting or refusing to generate
- Shard-encoded ID — embed shard key in ID so routing is derivable without lookup
- Instagram ID — timestamp + shard ID + sequence per shard, fits in 64 bits

### 7.7 Security Essentials for System Design
- Authentication — who are you?
  - JWT — stateless token, header.payload.signature, verify without DB hit
  - Session token — server stores session, cookie holds session ID
  - OAuth 2.0 — delegated access (login with Google), Authorization Code flow
  - API keys — long-lived, for service-to-service
- Authorization — what can you do?
  - RBAC (Role-Based Access Control) — assign roles to users, roles have permissions
  - ACL (Access Control List) — per-resource permission list
- Encryption
  - In transit — TLS everywhere, even internal services
  - At rest — AES-256 for sensitive data on disk
- Know when to mention each — chat needs auth per WebSocket connection, Dropbox needs per-file ACL

### 7.8 Multi-Region & Global Architecture
- Why multi-region — reduce latency for global users, survive region outage
- Active-passive — one region handles traffic, other is warm standby
  - RTO depends on failover detection + DNS propagation time
- Active-active — both regions serve traffic
  - Need conflict resolution for writes to same data from different regions
- Data replication across regions — sync (strong consistency, high latency) vs async (low latency, lag)
- GeoDNS — route users to nearest region based on their IP
- Read local, write global — serve reads from nearest region, route writes to home region
- Conflict resolution — LWW for simple cases, CRDT for counters, application merge for complex cases
- Data residency — some data must stay in specific regions (GDPR for EU users)

### 7.9 Storage Patterns at Scale
- Storage tiers — hot (SSD/Redis), warm (object store), cold (Glacier/tape)
- Chunked upload — split large file into 4-8MB chunks, upload in parallel, server reassembles
  - Resumable — on failure, restart from last successful chunk
  - Deduplication — hash each chunk, skip upload if chunk already exists (Dropbox)
- Content-addressable storage — SHA256 of content = storage key, automatic dedup
- Compression — compress before storing (gzip text, H.265 video) — significant cost reduction
- **Delta sync** — on file change, only upload the chunks that changed, not the whole file
  - Client computes SHA256 of each chunk of the new version; compares against stored chunk hashes
  - Only chunks whose hash differs are uploaded — a 1-byte change in a 1 GB file uploads only 4–8 MB (one chunk), not 1 GB
  - Server receives the new chunk list and assembles the new file version from existing + new chunks
  - This is the main Dropbox deep-dive question — understand the full client → server flow
  - Client sync architecture: local file watcher (inotify on Linux, FSEvents on Mac) detects change → diff chunk hashes → upload delta → update metadata DB with new chunk list
  - Conflict resolution: two clients edit the same file offline → server gets two different chunk lists → create a conflict copy (Dropbox approach) or apply CRDT merge (Google Docs approach)
- Directly applies to: Dropbox, Google Drive, YouTube, Gmail case studies

### 7.9b Data Migration at Scale
> Comes up when interviewers ask: "how do you migrate from the old system to this new one?"

- **Why it's hard** — you can't stop a production system to migrate. Users are reading and writing the entire time. A bad migration corrupts data or causes downtime.
- **Dual-write pattern**
  - Write to both old and new system simultaneously during migration
  - Read from old system (source of truth) until migration verified
  - Problem: if one write fails and the other succeeds, data diverges → need reconciliation
  - Better alternative: use CDC from old DB to populate new DB (avoids dual-write consistency risk)
- **Backfill strategy**
  - Migrate historical data in batches — scan old DB in chunks (cursor-based, not OFFSET), write to new DB
  - Rate-limit the backfill to avoid overwhelming either database
  - Track progress with a checkpoint (last migrated ID) — safe to restart on failure
  - Run backfill on a read replica of the old DB to avoid impacting production reads
- **Shadow traffic / dark reads**
  - After backfill, route a copy of live read traffic to the new system (but don't serve the response to users)
  - Compare responses between old and new system — log discrepancies
  - Once discrepancy rate drops to zero → switch reads to new system
- **The full migration playbook (4 phases)**
  1. **Backfill** — copy historical data from old → new
  2. **CDC / dual-write** — stream ongoing writes to new system in real time
  3. **Shadow reads** — validate new system returns correct results
  4. **Cutover** — switch reads to new system, stop writes to old system, decommission old
- **Rollback plan** — keep old system running and writable for N days after cutover. If something breaks, reverse the read path back to old.
- **Schema migration specifically**
  - Never run `ALTER TABLE` with a lock on a large production table — it blocks all writes
  - Use online schema migration tools (gh-ost for MySQL, pg_repack for PostgreSQL) that copy data to a new table in the background
  - Expand-and-contract pattern: add new column → backfill → deploy code that writes both → deploy code that reads new → drop old column
- **When to mention** — any case study where you're replacing a database (SQL → NoSQL migration), splitting a monolith DB, or the interviewer asks "what if requirements change and you need to re-shard?"

### 7.9c Deployment Strategies
> Moved from 7.9b — renumbered after Data Migration insertion
- **Rolling deploy** — replace instances one at a time; old and new versions briefly run simultaneously
  - Zero downtime, but mixed-version window means your API must be backward compatible during rollout
  - Rollback = slow (must re-roll every instance back)
- **Blue-green** — two identical environments (blue = live, green = new version); switch traffic at load balancer
  - Instant rollback — just point LB back to blue
  - Cost: double the infrastructure during the switch window
  - DB migration must be backward compatible — both blue and green point to the same DB
- **Canary** — route a small % of traffic (1–5%) to the new version; watch error rate and latency; expand or rollback
  - Best for risk reduction on high-traffic systems — real traffic validates the new version before full rollout
  - Requires traffic splitting at load balancer or API gateway level
  - Used by Google, Netflix, Amazon as standard practice
- **Feature flags** — deploy code disabled, enable for % of users without redeployment (covered in Supplementary)
- Key interview point: always pair deployment strategy with DB migration strategy — schema changes must be backward compatible across versions during rollout

### 7.10 Adaptive Bitrate Streaming (HLS / DASH)
> Directly applies to: YouTube, Netflix, any video streaming case study

- **Problem** — users have different and changing network speeds; serving a fixed-quality video causes buffering on slow connections or wastes bandwidth on fast ones
- **HLS (HTTP Live Streaming)** — Apple's standard, widely supported
  - Video is pre-transcoded into multiple quality tiers: 360p, 480p, 720p, 1080p, 4K
  - Each tier is split into small segments, typically 2–10 seconds each (`.ts` files or `.m4s` in fMP4)
  - A **manifest file** (`.m3u8`) lists all available tiers and segment URLs — the client fetches this first
  - The player starts downloading segments; if download speed is fast, it upgrades to a higher tier; if slow, it drops down
  - Segments are served from CDN edge nodes — no origin server hit for playback
- **DASH (Dynamic Adaptive Streaming over HTTP)** — MPEG standard, used by YouTube
  - Same concept as HLS; uses `.mpd` manifest instead of `.m3u8`
  - Codec-agnostic (supports H.264, H.265, AV1)
- **How it fits in the architecture**
  1. Video uploaded → stored as raw blob in S3
  2. Transcoding workers (triggered via Kafka) encode raw video into multiple resolutions + formats
  3. Transcoded segments stored in S3 under structured paths by resolution
  4. Manifest file generated and stored in S3 / served via CDN
  5. Client player fetches manifest → selects tier → downloads segments via CDN
- **Buffer management** — player maintains a playback buffer of ~30 seconds; switches quality to keep buffer full
- **Key deep-dive question**: "What happens when a user pauses and resumes?" — segments already fetched stay in buffer; player re-fetches manifest to get fresh segment URLs if CDN URLs expire
- Tradeoff: HLS/DASH segments are stored for every resolution — 5 resolutions × 3 formats = 15x raw video storage cost
