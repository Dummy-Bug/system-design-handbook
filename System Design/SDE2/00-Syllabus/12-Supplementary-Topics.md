## Supplementary Topics

> These topics are not core phases but come up in interviews and case study deep dives.
> Study these after completing Phases 1–9. Don't start here.

### SDE-2 Depth Bar For This Phase
- Know these topics well enough to strengthen a design when relevant.
- Do not start here, but do not ignore them once the core path is done.
- Use them to sound production-aware: observability, reconciliation, OLTP vs OLAP, feature flags, graceful degradation.

### Observability (Comes Up in Every Production System)
When an interviewer asks "how would you monitor this system?" — use these.

- **Logging** — structured logs (JSON, key-value pairs), log levels (DEBUG/INFO/WARN/ERROR)
  - Aggregation — ship logs to central store (Elasticsearch/Kibana or Splunk)
  - Use: debugging failures, audit trails (stock broker, Gmail, Dropbox)
- **Metrics** — numeric measurements over time
  - Types: counter (total requests), gauge (current queue depth), histogram (request latency distribution)
  - Stack: Prometheus (collect) + Grafana (visualize)
  - Key metrics to track per system — error rate, latency p99, QPS, queue depth, cache hit ratio
- **Distributed Tracing** — follow a request across multiple services
  - Each request gets a trace ID, each service adds a span
  - OpenTelemetry → Jaeger or Zipkin
  - Use: debugging latency in microservice chains (chat, news feed, Uber)
- **Alerting** — fire alert when metric crosses threshold or SLO is at risk
  - Alert on error budget burn rate, not just raw error count
- **Correlation ID** — tag every request with an ID, log it everywhere, trace across services

### OLTP vs OLAP
- OLTP (Online Transaction Processing) — many small fast queries, low latency, normalized
  - Examples: hotel reservation, stock broker, chat
  - Use: PostgreSQL, MySQL, DynamoDB
- OLAP (Online Analytical Processing) — few large slow queries, high throughput, denormalized
  - Examples: ad click reporting, business intelligence dashboards
  - Use: BigQuery, Redshift, Snowflake — columnar storage, parallel query execution
- Why it matters — don't run analytics queries on your OLTP database, separate them
- CDC pipeline: OLTP → Kafka → OLAP warehouse (directly applies to Ad Click Aggregation)

### Lambda vs Kappa Architecture
- Lambda architecture
  - Batch layer — reprocess all historical data periodically, accurate
  - Speed layer — process real-time stream, approximate
  - Serving layer — merge batch and speed results for queries
  - Problem: two code paths to maintain, complexity
- Kappa architecture
  - Stream-only — one code path
  - Reprocess history by replaying Kafka topic from offset 0
  - Simpler, but requires Kafka to retain long enough for full replay
- When each applies — ad aggregation, top-K, analytics systems

### Data Warehouse Basics
- Columnar storage — store all values of one column together, great for analytical scans
- Partitioning in warehouse — partition by date, queries scan only relevant partitions
- BigQuery, Redshift, Snowflake — know what they are, not how to operate them
- Mention in: Ad Click Aggregation, any reporting system case study

### Feature Flags
- Deploy code disabled, enable for % of users without redeployment
- Use: gradual rollout, A/B testing, kill switch for bad feature
- Simple implementation — Redis key per flag, app checks on each request
- Mention in: any system where you want to reduce deployment risk

### Reconciliation
> Comes up in Payment System, Banking Ledger, Ad Click Aggregation

- **What it is** — a periodic batch job that compares your internal records against an external source of truth to find and fix discrepancies
- **Why it's needed** — even with idempotency keys and exactly-once guarantees, distributed systems have edge cases: network timeouts after charge but before ack, clock skew causing duplicate event IDs, bugs in event deduplication logic. Reconciliation is the safety net.
- **Payment reconciliation example**
  - Every night, fetch all transactions recorded in your ledger for the day
  - Fetch the same day's transactions from the payment gateway (Stripe, Adyen) via their settlement report API
  - Compare the two lists: any transaction in your DB but not in the gateway report = failed charge you marked as successful → trigger reversal or manual review; any in gateway but not in your DB = missed event → insert and trigger fulfillment
- **Ad click reconciliation example**
  - Streaming aggregation (Count-Min Sketch) gives approximate counts in real time
  - Nightly batch job reprocesses the raw click log from Kafka/S3 for exact counts
  - Billing uses the batch-accurate numbers; real-time is for dashboards only
- **How to mention in an interview** — "I'd add a nightly reconciliation job that compares our internal ledger against the payment gateway's settlement file to catch any discrepancies from network failures or deduplication bugs. This is a standard safety net in any financial system."
- **Key design choices**
  - Run reconciliation on a read replica or offline copy — never on the primary DB under load
  - Idempotent reconciliation job — safe to re-run if it crashes halfway
  - Alert on reconciliation failures immediately — a discrepancy that isn't caught within 24 hours becomes much harder to reverse

### Graceful Degradation Examples
Know one example per major case study type:
- Chat — if message store is down, accept messages to queue, deliver when recovered
- News feed — if ranking service is down, serve unranked chronological feed
- Search — if ML ranking is down, fall back to TF-IDF relevance
- Video streaming — if transcoding is backlogged, serve lower resolution first
- Maps — if real-time traffic unavailable, route using historical traffic patterns
