## Phase 8 - Infrastructure and Reliability Patterns

> HLD relevance: senior engineers are expected to think beyond the steady state.
> This phase is about what makes large systems operable, safe to evolve, and survivable under failure.

### 8.1 Monolith vs microservices
- monolith as the simpler starting point
- when microservices are justified
- service boundaries and data ownership
- sync vs async inter-service communication

### 8.2 Service mesh and sidecars
- why teams push retries, mTLS, and observability into sidecars
- sidecar pattern
- service mesh awareness
- when service mesh is useful and when it is overkill

### 8.3 Backend-for-Frontend
- client-specific aggregation layer
- mobile vs web payload needs
- BFF vs GraphQL as ways to reduce client over-fetching

### 8.4 Resilience patterns
- circuit breaker
- retry with backoff and jitter
- timeout and deadline propagation
- bulkhead
- graceful degradation

### 8.5 Rate limiting and traffic protection
- token bucket
- leaky bucket
- fixed window
- sliding window log
- sliding window counter
- hard vs soft limits

### 8.6 Probabilistic data structures
- Bloom filter
- HyperLogLog
- Count-Min Sketch
- where each is useful in production systems

### 8.7 Geo-spatial systems
- geohash
- quadtree
- S2 awareness
- moving data and write-heavy geo indexes

### 8.8 ID generation
- auto-increment
- UUID
- Snowflake
- shard-encoded IDs
- clock skew consequences

### 8.9 Multi-region architecture
- active-passive
- active-active
- home region vs nearest region
- async replication across regions
- geo routing and failover
- data residency and compliance

### 8.10 Storage patterns at scale
- chunked upload
- resumable upload
- content-addressable storage
- delta sync
- compression and storage tiers

### 8.11 Data migration at scale
- backfill
- CDC during migration
- shadow traffic / dark reads
- phased cutover
- rollback plan

### 8.12 Deployment strategies
- rolling
- blue-green
- canary
- feature-flag-assisted rollout

