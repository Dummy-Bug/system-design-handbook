## Supplementary Topics

> These topics are not core phases but come up in interviews and case study deep dives.
> Study these after completing Phases 1–9. Don't start here.

### SDE-2 Depth Bar For This Phase
- Know these topics well enough to strengthen a design when relevant.
- Use them to sound production-aware: observability, reconciliation, feature flags, graceful degradation.
- Lambda/Kappa architecture, stream processing internals, and schema evolution are SDE-3 topics.

### Observability (Comes Up in Every Production System)

- **Logging** — structured logs (JSON, key-value pairs), log levels (DEBUG/INFO/WARN/ERROR)
  - Aggregation — ship logs to central store (Elasticsearch/Kibana or Splunk)
  - Use: debugging failures, audit trails
- **Metrics** — numeric measurements over time
  - Types: counter (total requests), gauge (current queue depth), histogram (latency distribution)
  - Stack: Prometheus (collect) + Grafana (visualize)
  - Key metrics — error rate, latency P99, QPS, queue depth, cache hit ratio
- **Distributed Tracing** — follow a request across multiple services
  - Each request gets a trace ID, each service adds a span
  - OpenTelemetry → Jaeger or Zipkin
- **Alerting** — fire alert when metric crosses threshold or SLO is at risk
  - Alert on error budget burn rate, not just raw error count
- **Correlation ID** — tag every request with an ID, log it everywhere, trace across services

### OLTP vs OLAP
- OLTP — many small fast queries, low latency, normalized (PostgreSQL, MySQL, DynamoDB)
- OLAP — few large slow queries, high throughput, denormalized (BigQuery, Redshift, Snowflake)
- Why it matters — don't run analytics queries on your OLTP database
- CDC pipeline: OLTP → Kafka → OLAP warehouse

### Feature Flags
- Deploy code disabled, enable for % of users without redeployment
- Use: gradual rollout, A/B testing, kill switch for bad feature
- Simple implementation — Redis key per flag, app checks on each request

### Reconciliation
- What it is — periodic batch job comparing internal records against an external source of truth
- Why needed — idempotency and retries handle most cases, but edge cases exist (network timeout after charge, before ack)
- Payment reconciliation — compare internal ledger against gateway settlement report nightly
- Ad click reconciliation — stream gives approximate real-time, batch gives exact numbers for billing
- Key design choices:
  - Run on read replica, never primary
  - Idempotent job — safe to re-run if crashes
  - Alert on discrepancies immediately

### Graceful Degradation Examples
- Chat — if message store is down, accept messages to queue, deliver when recovered
- News feed — if ranking service is down, serve unranked chronological feed
- Search — if ML ranking is down, fall back to TF-IDF relevance
- Video streaming — if transcoding is backlogged, serve lower resolution first
- Maps — if real-time traffic unavailable, route using historical traffic patterns
