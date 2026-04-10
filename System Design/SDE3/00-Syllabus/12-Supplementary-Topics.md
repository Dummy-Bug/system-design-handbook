## Supplementary Topics

> These are not the first topics to study, but they regularly appear in senior interviews and deep dives.

### Observability
- structured logs
- metrics
- tracing
- error budget alerts
- subsystem-specific dashboards

### OLTP vs OLAP
- transactional stores vs analytical stores
- CDC from OLTP to warehouse
- why you should not run heavy analytics on your primary serving DB

### Lambda vs Kappa
- batch plus speed layer vs stream-only architecture
- where replay complexity is worth it

### Data warehouse basics
- columnar storage
- partitions
- rollups and reporting pipelines

### Feature flags
- gradual rollout
- canary support
- kill switch

### Reconciliation
- payment reconciliation
- billing correctness
- exact batch recompute after approximate stream processing

### Graceful degradation
- feed without ranking
- search without ML ranking
- queueing writes when downstream is degraded
- historical traffic fallback in maps

### Multi-tenant and compliance concerns
- tenant isolation
- data residency
- audit logs
- retention and deletion workflows

### Control plane vs data plane
- configuration and coordination separated from request serving path
- why this distinction matters in large systems

