## Supplementary Topics

> These are not the first things to study, but they come up often in strong senior loops and deep dives.

### SDE-3 depth bar for this phase
- Know how these topics connect to real systems, not just their definitions.
- Use them to strengthen a design only when they are actually relevant.

### Observability
- structured logging
- metrics and RED / USE style intuition
- distributed tracing
- correlation IDs
- SLO and error-budget alerting
- per-subsystem dashboards for queue lag, replica lag, cache hit ratio, and p99 latency

### OLTP vs OLAP
- transactional systems vs analytical systems
- serving path vs warehouse path
- CDC from OLTP to OLAP
- why exact reporting often belongs off the serving path

### Lambda vs Kappa Architecture
- speed layer vs batch layer
- replay-based stream-only architecture
- operational duplication vs replay requirements

### Data Warehouse Basics
- columnar storage
- partitioning
- rollups and aggregation tables
- reporting cost vs freshness tradeoff

### Feature Flags
- canary and gradual rollout support
- kill switch for unstable features
- policy-driven release instead of redeploy-driven release

### Reconciliation
- payment reconciliation
- billing correctness
- exact recomputation after approximate streaming
- when reconciliation is your final correctness safety net

### Graceful Degradation
- feed without ranking
- search without ML ranker
- queueing writes when downstream is degraded
- serving stale-but-safe data when fresh data is unavailable

### Multi-Tenant and Compliance Concerns
- tenant isolation
- audit logs
- retention and deletion workflows
- data residency
- permission checks in retrieval and serving paths

### Control Plane vs Data Plane
- request serving path vs management / configuration path
- why the control plane can be slower but must be safe
- why the data plane must stay simple and resilient
