## Supplementary Topics

> These are useful, but they should not block the main SDE-1 path.
> Study them after the core phases.

### Observability basics
- logs
- metrics
- distributed tracing at a high level
- correlation IDs
- what to monitor - latency, error rate, QPS, queue depth, cache hit ratio

### OLTP vs OLAP
- OLTP for transactional systems
- OLAP for analytics and reporting
- do not run large analytics queries on your primary transactional DB

### Feature flags
- gradual rollout
- kill switch
- safer deploys

### Reconciliation
- compare your internal state with an external source of truth
- common in payment and billing systems
- safety net for distributed failures

### Graceful degradation examples
- chat - queue messages if store is down
- feed - serve chronological feed if ranking fails
- search - fall back to simple ranking if ML layer is down
- video - serve lower quality if transcoding lags

### Optional probabilistic data structures
- Bloom filter
- HyperLogLog
- Count-Min Sketch
- know where they are useful, but do not over-invest early

