## Supplementary Topics

> These topics are not core phases but come up in interviews and case study deep dives.
> Study these after completing Phases 1–9. Don't start here.

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

### Graceful Degradation Examples
Know one example per major case study type:
- Chat — if message store is down, accept messages to queue, deliver when recovered
- News feed — if ranking service is down, serve unranked chronological feed
- Search — if ML ranking is down, fall back to TF-IDF relevance
- Video streaming — if transcoding is backlogged, serve lower resolution first
- Maps — if real-time traffic unavailable, route using historical traffic patterns
