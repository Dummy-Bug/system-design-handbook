# Observability at Scale

## Logging
- Structured logs — JSON or key-value pairs, not free-text strings
- Log levels — DEBUG, INFO, WARN, ERROR — only ship WARN+ in production
- Log aggregation — ship to central store (Elasticsearch/Kibana, Splunk, CloudWatch)
- Correlation ID — tag every request with a unique ID, log it everywhere, trace across services
- Use cases — debugging failures, audit trails (stock broker, Gmail, Dropbox)

## Metrics
- Types:
  - Counter — total requests, total errors (monotonically increasing)
  - Gauge — current queue depth, active connections, cache size (can go up or down)
  - Histogram — request latency distribution (buckets, P50/P95/P99 derivable)
- Stack — Prometheus (collect and store) + Grafana (visualize)
- Key metrics per system:
  - Error rate, latency P99, QPS, queue depth, cache hit ratio
  - DB connection pool utilization, replication lag
  - Consumer lag (Kafka), DLQ depth

## **Metrics at Scale**
- **Cardinality explosion — high-cardinality labels (user_id, request_id) create millions of unique time series**
  - **Each unique label combination = a separate time series stored in Prometheus**
  - **1M users × 10 metrics = 10M time series. Prometheus falls over.**
  - **Fix — never use user_id as a Prometheus label. Use pre-aggregated counts instead.**
- **Downsampling — store raw metrics at 15s resolution for 24h, then aggregate to 1m for 30 days, 1h for 1 year**
  - **Reduces storage while preserving trend visibility over long windows**
- **Prometheus federation — hierarchical Prometheus setup**
  - **Per-datacenter Prometheus scrapes local services**
  - **Global Prometheus federates from all regional instances**
  - **Used at scale when single Prometheus can't scrape all targets**
- **Remote write — Prometheus writes metrics to long-term storage (Thanos, Cortex, VictoriaMetrics)**

## Distributed Tracing
- Each request gets a trace ID, each service adds a span with timing and metadata
- OpenTelemetry → Jaeger or Zipkin for storage and visualization
- Use — debugging latency in microservice chains (chat, news feed, Uber)
- **Sampling strategies:**
  - **Head-based sampling — decision made at the start of the trace (before outcome known)**
    - **Simple, low overhead, but may drop important traces (rare errors)**
    - **Fixed rate (1% of all requests) or rate-limited per route**
  - **Tail-based sampling — decision made after the trace completes (outcome known)**
    - **Can always keep slow traces, error traces regardless of base rate**
    - **Requires buffering all spans until trace completes — much higher memory cost**
    - **Better for debugging — you keep exactly the traces that matter**
  - **Practical approach — head-based 1% for normal traffic, always-on for errors and slow requests**

## Alerting
- Alert on error budget burn rate, not just raw error count
- Multi-window alerting — short window (5m) for fast burns, long window (1h) for slow burns
- Page on symptoms (user-facing error rate, latency) not causes (CPU usage, disk space)
- Alert fatigue — too many alerts → on-call ignores them. Keep alerts actionable and rare.

## **Chaos Engineering**
- **Core idea — intentionally inject failures in production (or staging) to verify your system handles them**
- **Why — you find out your resilience assumptions are wrong during a drill, not during an actual incident**
- **Netflix Chaos Monkey — randomly terminates EC2 instances in production. Teams must build services that survive.**
- **Chaos experiments:**
  - **Kill a random replica — does the system fail over correctly?**
  - **Inject latency on a downstream service — does circuit breaker open?**
  - **Fill a disk — does the system degrade gracefully?**
  - **Drop packets between two services — does the timeout fire correctly?**
- **Game Day — scheduled chaos exercise where the team runs scenarios and measures recovery time**
- **Blast radius — start small (one instance in one region), expand once confident**

## Reconciliation
- What it is — periodic batch job comparing internal records against external source to find discrepancies
- Why needed — even with idempotency and exactly-once, edge cases exist (network timeout after charge but before ack)
- Payment reconciliation — compare internal ledger against gateway settlement report nightly
- Ad click reconciliation — streaming approximation for real-time, batch reprocessing for accurate billing
- Design choices:
  - Run on read replica, never primary
  - Idempotent job — safe to re-run if crashes
  - Alert on discrepancies immediately

## Graceful Degradation
- Chat — if message store is down, accept to queue, deliver when recovered
- News feed — if ranking service down, serve unranked chronological feed
- Search — if ML ranking down, fall back to TF-IDF relevance
- Video streaming — if transcoding backlogged, serve lower resolution first
- Maps — if real-time traffic unavailable, route using historical patterns

## OLTP vs OLAP
- OLTP — operational DB, low-latency reads/writes (PostgreSQL, MySQL, DynamoDB)
- OLAP — analytical DB, large aggregations (Redshift, BigQuery, Snowflake, columnar storage)
- Never run analytics on production OLTP DB
- CDC or ETL pipeline copies OLTP → data warehouse

## Feature Flags
- Deploy code disabled, enable for % of users without redeployment
- Use — gradual rollout, A/B testing, kill switch for bad feature
- Simple implementation — Redis key per flag, app checks on each request
- Mention when — reducing deployment risk on any system
