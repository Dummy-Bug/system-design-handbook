## Supplementary Topics

> These topics are not core phases but come up in interviews and case study deep dives.
> Study these after completing Phases 1–9. Don't start here.

### SDE-2 Depth Bar For This Phase
- Know these topics well enough to strengthen a design when relevant.
- Use them to sound production-aware: observability, reconciliation, feature flags, graceful degradation.
- Lambda/Kappa architecture, stream processing internals, and schema evolution are SDE-3 topics.

### Observability (Comes Up in Every Production System)

Interviewers at FAANGM directly ask: "How do you know this system is healthy?" or "How do you know if your SLO is at risk?" You need to answer this in layers — not just "use Prometheus."

**The four pillars:**

- **Logging** — structured logs (JSON, key-value pairs), log levels (DEBUG/INFO/WARN/ERROR)
  - Aggregation — ship logs to central store (Elasticsearch/Kibana or Splunk)
  - Use: debugging failures, audit trails, forensic investigation after an incident
  - Always include a correlation ID in every log line

- **Metrics** — numeric measurements over time
  - Types: counter (total requests), gauge (current queue depth), histogram (latency distribution)
  - Stack: Prometheus (collect) + Grafana (visualize)
  - Key metrics to always mention: error rate, latency P99, QPS, queue depth, cache hit ratio, DB connection pool utilisation

- **Distributed Tracing** — follow a single request as it travels across multiple services
  - Each request gets a trace ID at the entry point (API gateway or load balancer)
  - Each service adds a span — a timed segment of work with its own metadata
  - Spans form a tree: one root span (the original request) + child spans per service hop
  - OpenTelemetry is the standard instrumentation library → export to Jaeger or Zipkin
  - Use case: a request is slow but all individual services look fine. Tracing shows the gap is in the network call between service B and C.

- **Alerting** — fire alert when a metric crosses a threshold or an SLO is at risk
  - Alert on error budget burn rate, not just raw error count
  - A spike to 5% errors for 2 minutes is less critical than 0.5% errors sustained for 6 hours — burn rate captures this, raw error rate doesn't
  - Correlation ID — tag every request with a unique ID at entry, log it in every service, trace failures across the entire call chain without a distributed tracer

**SLIs, SLOs, and Error Budgets — the most important interview answer**

Interviewers ask this directly. Know the three terms cold:

- **SLI (Service Level Indicator)** — the actual measurement. "Our P99 latency is 120ms." "Our error rate is 0.1%."
- **SLO (Service Level Objective)** — the internal target. "P99 latency must stay below 200ms." "Error rate must stay below 0.5%."
- **SLA (Service Level Agreement)** — the external contract with a customer, with financial penalties. Always stricter internally than your SLO.
- **Error budget** — the gap between 100% and your SLO. If SLO is 99.9% availability, your error budget is 0.1% — about 43 minutes of downtime per month.
  - Budget is burning fast → freeze non-critical deploys, focus on reliability
  - Budget is healthy → deploy freely, invest in new features
  - This is how Google teams decide deploy velocity — not gut feel

**What to say in an interview:**
> "For observability I'd instrument three things. Metrics via Prometheus — I'd track error rate, P99 latency, and queue depth, alerting on burn rate not raw thresholds. Distributed tracing via OpenTelemetry so we can follow a request across services when something is slow. And structured logs with a correlation ID on every request so we can tie metrics, traces, and logs together during an incident. The SLO for this system I'd set at 99.9% availability — that gives us a 43-minute error budget per month to work within."

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
