# Infrastructure and Reliability

## Microservices vs Monolith
- Monolith — single deployable unit, simple to start, harder to scale teams
- Microservices — independently deployable, team autonomy, operational overhead
- Data ownership — each service owns its data, no shared DB
- Inter-service communication — sync (REST/gRPC) vs async (Kafka/queue)
- When to split — by domain boundary, not by technical layer

## **Service Mesh and Sidecar Pattern**
- **Problem — every microservice needs mTLS, retries, circuit breaking, observability. Implementing this in every service is duplicated effort.**
- **Sidecar proxy — lightweight proxy deployed alongside every service instance (same pod in K8s)**
  - **All inbound/outbound traffic flows through the sidecar**
  - **Sidecar handles — TLS termination, retries, circuit breaking, load balancing, metrics collection, distributed tracing injection**
  - **Application code talks plain HTTP/gRPC to localhost, knows nothing about this**
- **Service mesh — all sidecars + a control plane that configures them**
  - **Istio — most well-known, uses Envoy as sidecar proxy**
  - **Linkerd — lighter alternative, Rust-based proxy**
  - **Control plane pushes retry policies, routing rules, mTLS certs to all sidecars**
- **What service mesh enables:**
  - **mTLS everywhere without app code changes — sidecar handles cert rotation**
  - **Traffic splitting — route 5% to canary version without app-level logic**
  - **Observability for free — every sidecar emits latency, error rate, request count**
- **Trade-off — adds latency per hop, operational complexity, resource overhead per pod**
- **When to mention — large microservices architecture, "how do you handle service-to-service security?"**
- **When NOT to mention — small systems, monoliths, 2-3 services. Overkill.**

## BFF (Backend-for-Frontend)
- Problem — mobile needs lightweight response, web needs rich response. One API can't serve both well.
- BFF — thin API layer per client type that aggregates and transforms backend responses
- Why not multiple client calls — mobile on 3G making 5 round trips is unacceptable
- Trade-off — another service to maintain, keep it thin (aggregation only, no business logic)
- Alternative — GraphQL lets client specify exactly which fields it needs

## Resilience Patterns

### Circuit Breaker
- Problem — downstream is slow, your threads pile up waiting, your service dies too
- States — Closed (normal), Open (reject fast, no downstream calls), Half-Open (probe recovery)
- Open circuit when error rate crosses threshold
- Fallback — return cached response, default value, or graceful error
- Prevents cascading failures in microservice chains

### Retry + Exponential Backoff + Jitter
- Retry on transient failures (5xx, timeout, connection refused)
- Do NOT retry on client errors (4xx) — retrying won't fix a bad request
- Exponential backoff — double wait each retry (1s, 2s, 4s, 8s...)
- Jitter — randomize backoff to prevent synchronized retry storms
- Max retry limit — don't retry forever

### Timeout and Deadline Propagation
- Always set timeouts — unbounded waits exhaust thread pools
- Connection timeout vs read timeout — set both
- Deadline propagation — pass remaining budget downstream ("you have 200ms total")
- Total budget across retries — 3 retries × 5s must not exceed parent timeout

### Bulkhead Pattern
- Isolate resources per downstream — separate thread pool per dependency
- One slow downstream exhausts only its own pool, not the entire service

### Health Checks
- Shallow health check — GET /health returns 200 if process is running. For load balancers.
- Deep health check — GET /health/ready checks DB, Redis, disk. Returns 503 if dependency down.
- Liveness vs readiness (Kubernetes) — liveness: restart if dead, readiness: stop traffic if not ready

## Rate Limiting
- Token Bucket — tokens refill at rate R, burst allowed up to capacity C
- Leaky Bucket — constant processing rate, excess queued or dropped
- Fixed Window Counter — count in current window, reset at boundary. Allows 2× at edge.
- Sliding Window Log — store all timestamps, count within window. Accurate, memory-heavy.
- Sliding Window Counter — blend of current + previous window. Balance of accuracy and memory.
- Distributed rate limiting — Redis INCR + EXPIRE, Lua script for atomic check-and-increment
- Where to rate limit — API gateway (user/IP), per-service (protect downstream)

## Probabilistic Data Structures

### Bloom Filter
- Answers "is X definitely NOT in the set?" — zero false negatives, false positives possible
- **How it works — bit array of size m + k hash functions. On insert: set k bits. On query: check all k bits.**
- **False positive rate — depends on m (array size), k (hash functions), n (items inserted). Tunable.**
- **Space-efficient — millions of items in kilobytes**
- Use cases — web crawler (skip crawled URLs), cache penetration (block queries for non-existent keys), username availability

### HyperLogLog
- Approximate count of unique items in a stream
- **Uses O(log log n) memory — 12 KB for any cardinality up to 2^64**
- **How it works — hash each item, observe max leading zeros in binary representation, use as cardinality estimate**
- Error rate ~1-2%, acceptable for analytics
- Redis commands — PFADD, PFCOUNT, PFMERGE
- Use cases — unique visitors, distinct search queries, DAU counting

### Count-Min Sketch
- Approximate frequency of items in a stream
- **How it works — 2D counter array (d rows × w columns) + d independent hash functions. Increment d cells on insert. Query = minimum across d rows.**
- **Always overestimates (never underestimates) — minimum across rows reduces but doesn't eliminate hash collisions**
- **Space — O(d × w) regardless of number of distinct items**
- Use cases — top-K heavy hitters, trending topics, frequency capping in ads

### Skip List
- Probabilistic sorted data structure — O(log n) for search, insert, delete
- **How it works — multiple levels of linked lists. Top level has few nodes (express lane), bottom has all nodes.**
- **Each node promoted to higher level with probability 1/2**
- Redis Sorted Set is backed by a skip list internally

## Geospatial Indexing
- Geohash — encode lat/lng as base32 string, prefix = proximity, query 8 surrounding cells too
- **S2 Geometry — spherical cells using Hilbert space-filling curve (covered in Storage section)**
- Quadtree — recursively split 2D space into 4 quadrants, good for dynamic driver locations
- How Uber uses it — drivers update every 4 seconds, geohash stored in Redis

## ID Generation
- Auto-increment — simple, centralized, reveals record count, not distributed-safe
- UUID v4 — random 128-bit, globally unique, not sortable, index-unfriendly
- Snowflake (Twitter/Discord) — 64-bit: [41-bit timestamp ms][10-bit machine ID][12-bit sequence]
  - Sortable by time, no coordination needed, clock skew requires waiting or refusing to generate
- Shard-encoded ID — embed shard key in ID, routing derivable without lookup

## Security Essentials
- JWT — stateless token, header.payload.signature, verify without DB hit
- Session token — server stores session, cookie holds session ID
- OAuth 2.0 — delegated access (login with Google), Authorization Code flow
- API keys — long-lived, for service-to-service
- RBAC — roles have permissions, users have roles
- ACL — per-resource permission list
- TLS everywhere, AES-256 at rest

## **Multi-Region and Global Architecture**
- Why multi-region — reduce latency for global users, survive region outage
- Active-passive — one region handles traffic, other is warm standby. RTO depends on failover + DNS propagation.
- Active-active — both regions serve traffic. Requires conflict resolution for writes.
- Data replication across regions — sync (strong consistency, high latency) vs async (low latency, lag)
- GeoDNS — route users to nearest region based on their IP
- Read local, write global — serve reads from nearest region, route writes to home region
- **Conflict resolution strategies:**
  - **Last Write Wins (LWW) — use timestamp, simple, risk of data loss**
  - **CRDT — converge automatically, no data loss, limited to specific data types**
  - **Application merge — custom logic per entity type, most flexible, most complex**
- **Data residency — GDPR requires EU user data to stay in EU. Design must enforce at data layer, not just routing.**
- **Anycast — same IP announced from multiple regions, BGP routes to nearest**

## **Storage Patterns at Scale**
- Storage tiers — hot (SSD/Redis), warm (S3), cold (Glacier)
- Chunked upload — split large file into 4–8 MB chunks, upload in parallel, server reassembles
- Resumable upload — on failure, restart from last successful chunk
- Content-addressable storage — SHA256 of content = key, automatic deduplication
- **Delta sync (Dropbox deep dive):**
  - **Client computes SHA256 of each chunk of new version**
  - **Compares against stored chunk hashes**
  - **Only chunks whose hash differs are uploaded**
  - **A 1-byte change in a 1 GB file uploads only 4–8 MB (one chunk), not 1 GB**
  - **Server assembles new version from existing + new chunks**
  - **Conflict resolution — two clients edit same file offline → create conflict copy (Dropbox) or CRDT merge (Google Docs)**

## **Data Migration at Scale**
- Covered in detail in Storage and Databases section
- Full playbook — Backfill → CDC/dual-write → Shadow reads → Cutover → Rollback

## Deployment Strategies
- Rolling deploy — replace instances one at a time, old and new versions briefly coexist
- Blue-green — two identical environments, switch traffic at load balancer. Instant rollback.
- Canary — route small % of traffic to new version, expand or rollback based on metrics
- **Canary with DB migration — expand-and-contract pattern ensures both old and new code work during rollout**
- Feature flags — deploy code disabled, enable for % of users without redeployment

## **Adaptive Bitrate Streaming (HLS / DASH)**
- **Problem — users have different and changing network speeds. Fixed quality → buffering on slow connections.**
- **HLS (HTTP Live Streaming) — Apple's standard:**
  - **Video pre-transcoded into multiple tiers (360p, 720p, 1080p, 4K)**
  - **Each tier split into segments (2–10 seconds, .ts or .m4s files)**
  - **Manifest file (.m3u8) lists all tiers and segment URLs — client fetches this first**
  - **Player downloads segments, upgrades/downgrades quality based on download speed**
  - **Segments served from CDN — no origin hit for playback**
- **DASH (Dynamic Adaptive Streaming over HTTP) — MPEG standard, used by YouTube**
  - **Same concept as HLS, uses .mpd manifest instead of .m3u8**
  - **Codec-agnostic (H.264, H.265, AV1)**
- **Architecture flow:**
  - **Upload → S3 (raw) → transcoding workers (Kafka-triggered) → S3 (segments per resolution) → manifest generated → CDN**
- **Buffer management — player maintains ~30s playback buffer, switches quality to keep buffer full**
- **Storage cost — 5 resolutions × 3 formats = 15× raw video storage**
