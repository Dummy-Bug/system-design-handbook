## Phase 8 - Infrastructure and Reliability Patterns

> HLD relevance: this is where architecture becomes operable.
> SDE-3 depth means you should be able to discuss not just the steady-state design, but rollout, migration, failure containment, and regional survival.

### SDE-3 depth bar for this phase
- Be able to explain why an infra pattern exists, what pain it removes, and what new cost it introduces.
- Discuss safe evolution: migration, deployment, rollback, and shadow validation.
- Show operational awareness: health checks, load shedding, rate limiting, geo failover, auditability.
- Tie patterns back to concrete systems like feeds, schedulers, maps, storage, and payments.

### 8.1 Microservices vs Monolith
- Monolith as the lowest-ops starting point.
- Microservices for team boundaries, deploy independence, and scaling isolation.
- Data ownership and avoiding a shared-database pseudo-monolith.
- Sync vs async service communication.
- Senior-level expectation: be honest about when microservices are overkill.

### 8.1b Service Mesh and Sidecar Pattern
- Why teams move mTLS, retries, and tracing out of app code.
- Sidecar proxy as the per-instance traffic layer.
- Service mesh as sidecars plus centralized control plane.
- Benefits: traffic splitting, consistent policy, cross-service telemetry.
- Costs: latency, resource overhead, debugging complexity.

### 8.1c Backend-for-Frontend (BFF) Pattern
- Mobile and web often need different payload shape and aggregation.
- BFF reduces client round trips and keeps client-specific shaping out of core services.
- Compare BFF vs GraphQL.
- Risk: BFF turning into a business-logic dumping ground.

### 8.2 Resilience Patterns
- Circuit breaker states and fallback behavior.
- Retry with exponential backoff and jitter.
- Timeout taxonomy and deadline propagation.
- Bulkhead isolation by dependency.
- Health checks: shallow vs deep, liveness vs readiness.
- Senior-level expectation: explain how you stop one bad dependency from sinking the whole fleet.

### 8.3 Rate Limiting
- Token bucket, leaky bucket, fixed window, sliding log, sliding counter.
- Global vs per-tenant vs per-user vs per-IP limits.
- Hard drop vs soft degradation vs queued admission.
- Distributed rate limiting with Redis / edge gateway enforcement.
- Exposing Retry-After and quota headers.

### 8.4 Probabilistic Data Structures
- Bloom filter for negative membership checks and cache-penetration defense.
- HyperLogLog for approximate unique counts.
- Count-Min Sketch for approximate heavy hitters.
- Senior-level expectation: know the error model and why approximation is acceptable.

### 8.5 Geo-Spatial Indexing
- Geohash, quadtree, S2 awareness.
- Nearby lookup vs update-heavy moving-object workload.
- Cell-boundary edge cases.
- Senior-level depth: distinguish static map-tile systems from live driver-location systems.

### 8.6 ID Generation
- Auto-increment and its centralization cost.
- UUID and index fragmentation tradeoff.
- Snowflake: timestamp + worker + sequence.
- Shard-encoded IDs and routing benefit.
- Clock skew handling in time-based ID systems.

### 8.7 Security Essentials for System Design
- Authentication, authorization, RBAC, ACL.
- Service-to-service identity.
- Encryption in transit and at rest.
- Secret rotation awareness.
- Audit logging for sensitive operations.
- Tenant-isolation awareness in multi-tenant systems.

### 8.8 Multi-Region and Global Architecture
- Active-passive vs active-active.
- Home-region model vs nearest-region serving.
- Sync vs async cross-region replication.
- Geo routing and failover.
- Data residency and compliance constraints.
- Senior-level expectation: talk about failback, not just failover.

### 8.9 Storage Patterns at Scale
- Chunked upload and resumable upload.
- Content-addressable storage and deduplication.
- Delta sync for large mutable files.
- Storage tiers and lifecycle transitions.
- Compression and egress economics.

### 8.9b Data Migration at Scale
- Backfill historical data safely.
- CDC or outbox to keep new system current during migration.
- Shadow reads / dark traffic to validate parity.
- Phased cutover and rollback plan.
- Expand / migrate / contract for schema evolution.
- Senior-level expectation: never hand-wave migration as "copy the data."

### 8.9c Deployment Strategies
- Rolling deploy.
- Blue-green.
- Canary.
- Feature-flag-assisted release.
- Safe rollback, not just safe rollout.

### 8.10 Adaptive Bitrate Streaming (HLS / DASH)
- Segment-based video delivery.
- Playlist / manifest-driven bitrate selection.
- Client adaptation to network conditions.
- Why CDN and transcode pipeline design matter more than one API call.

### 8.11 What SDE-3 Should Be Comfortable Saying
- "I would use canary because I need real traffic validation before global rollout."
- "Migration is its own project: backfill, CDC, shadow read, cutover, rollback."
- "Multi-region active-active sounds attractive, but conflict resolution cost may not be worth it for this workload."
- "This sidecar / service-mesh layer buys consistency of policy but adds operational and debugging overhead."
