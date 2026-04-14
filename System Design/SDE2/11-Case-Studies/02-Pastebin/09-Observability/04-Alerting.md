
> [!info] Knowing your SLI is breached is useless if nobody finds out for an hour. Alerting closes the loop — when SLI diverges from SLO, a human gets paged immediately.

---

## The alert rules

```
IF viewData p99 read latency > 50ms
FOR more than 2 minutes
→ page on-call engineer

IF viewData availability < 99.99%
FOR more than 2 minutes
→ page on-call engineer

IF pasteData availability < 99.9%
FOR more than 2 minutes
→ page on-call engineer
```

Simple threshold rules. But the "for more than 2 minutes" part is important.

---

## Why you need a sustained breach window

Without the duration condition, a single spiky second triggers a page. At 3,000 reads/sec, occasional spikes happen — a GC pause on one instance, a brief Redis connection reset, a slow S3 response on one request. These self-resolve in seconds.

If you alert on every spike, you wake engineers at 3am for events that resolved before anyone could respond. This is **alert fatigue** — engineers start ignoring pages because most are false alarms. When the real incident happens, the page gets ignored too.

The 2-minute window filters out transient spikes while still catching real degradation fast enough to act on it.

```
S3 blip (20 seconds): condition met but not sustained → no page, self-resolved
Postgres failover window (10-30 seconds): same → no page
Actual S3 outage (5 minutes): condition met for > 2 minutes → page fires
```

---

## Leading indicator alerts — act before SLO breaches

SLO-based alerts tell you when you've already failed your users. Leading indicator alerts tell you something is degrading before the SLO is breached.

```
IF cache hit rate < 70%
FOR more than 5 minutes
→ warning alert (not a page, but visible on dashboard)
Reason: hit rate dropping means more S3 fetches → latency p99 will climb shortly

IF upload queue depth > 10,000 jobs
FOR more than 5 minutes
→ warning alert
Reason: worker lag means pastes stuck IN_PROGRESS for extended periods

IF circuit breaker state = OPEN
→ page immediately (no sustained window needed)
Reason: S3 is down, every cache miss returns 503 — this is always a real incident
```

The circuit breaker alert is the exception to the sustained window rule. If the circuit breaker opens, S3 is confirmed down — that is never a transient self-resolving spike. Page immediately.

---

## The full alerting loop

```
SLO:     p99 read latency < 50ms          ← the promise
SLI:     actual p99 measured every 15s    ← the reality
Alert:   fires when SLI > SLO for 2 min  ← the notification
Action:  on-call engineer investigates    ← the response
```

Every 15 seconds Prometheus computes fleet-wide p99. If it stays below 50ms, nothing happens. If it crosses 50ms and stays there for 2 minutes, PagerDuty pages the on-call engineer with the exact metric, the current value, and a link to the latency graph showing when it started.

---

## Tooling

**Prometheus + Grafana + Alertmanager** — self-hosted stack. Prometheus scrapes metrics, Grafana renders dashboards, Alertmanager routes pages to PagerDuty or Opsgenie. More control, more ops overhead.

**Datadog** — managed metrics, dashboards, and alerting in one platform. No infrastructure to run. Costs money at scale but eliminates the ops burden of running Prometheus.

For Pastebin at 100M MAU, either works. In an interview, commit to one and justify: "Datadog for managed simplicity" or "Prometheus if we want to avoid vendor lock-in."

---

> [!tip] Interview framing
> "Alert rule: if p99 exceeds 50ms for more than 2 minutes, page on-call. The 2-minute window prevents alert fatigue from transient spikes that self-resolve. Beyond SLO alerts, also alert on leading indicators: cache hit rate dropping below 70% warns that latency will climb, upload queue depth growing warns of worker lag. Circuit breaker opening is the exception — page immediately, no sustained window needed, S3 down is always real."
