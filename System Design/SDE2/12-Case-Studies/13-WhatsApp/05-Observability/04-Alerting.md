
> [!info] Knowing your SLI is breached is useless if nobody finds out for an hour. Alerting closes the loop — when SLI diverges from SLO, a human gets paged immediately.

---

## The alert rules

```
IF delivery latency p99 > 500ms
FOR more than 2 minutes
→ page on-call engineer

IF delivery availability < 99.99%
FOR more than 2 minutes
→ page on-call engineer

IF connection availability < 99.9%
FOR more than 2 minutes
→ page on-call engineer
```

Simple threshold rules. But the "for more than 2 minutes" part is critical.

---

## Why you need a sustained breach window

Without the duration condition, a single spiky second triggers a page. At 100K messages/second, occasional spikes happen — a GC pause on one app server, a brief Redis connection reset, a DynamoDB partition rebalancing. These self-resolve in seconds.

If you alert on every spike, you wake engineers at 3am for events that resolved before anyone could respond. This is **alert fatigue** — engineers start ignoring pages because most are false alarms. When the real incident happens, the page gets ignored too.

The 2-minute window filters out transient spikes while still catching real degradation fast enough to act.

```
DynamoDB brief hiccup (15 seconds):  condition met but not sustained → no page, self-resolved
Redis failover (30 seconds):         same → no page
Actual DynamoDB outage (10 minutes): condition met for > 2 minutes → page fires
```

---

## Leading indicator alerts — act before SLO breaches

SLO-based alerts tell you when you've already failed your users. Leading indicator alerts tell you something is degrading before the SLO is breached.

```
IF Kafka consumer lag (registry) > 100,000 events
FOR more than 3 minutes
→ warning alert
Reason: lag growing means users appear offline longer → delivery delays incoming

IF pending_deliveries table depth > 1M rows
FOR more than 5 minutes
→ warning alert
Reason: delivery worker falling behind → messages queuing up → latency will climb

IF Redis inbox shard p99 read latency > 10ms
FOR more than 2 minutes
→ warning alert
Reason: inbox loads slowing down → user experience degrading

IF DynamoDB circuit breaker state = OPEN
→ page immediately (no sustained window needed)
Reason: circuit OPEN means writes are failing — this is always a real incident

IF connection server reconnect rate > 10x baseline
→ page immediately
Reason: mass reconnect event in progress — connection server likely down
```

The circuit breaker alert and reconnect spike are exceptions to the sustained window rule. Both indicate confirmed failures — not transient spikes.

---

## The full alerting loop

```
SLO:     p99 delivery latency < 500ms          ← the promise
SLI:     actual p99 measured every 15s         ← the reality
Alert:   fires when SLI > SLO for 2 min        ← the notification
Action:  on-call engineer investigates         ← the response
```

Every 15 seconds Prometheus computes fleet-wide p99. If it stays below 500ms, nothing happens. If it crosses 500ms and stays there for 2 minutes, PagerDuty pages the on-call engineer with the exact metric, the current value, and a link to the latency graph showing when it started.

---

## Tooling

**Prometheus + Grafana + Alertmanager** — self-hosted stack. Prometheus scrapes metrics, Grafana renders dashboards, Alertmanager routes pages to PagerDuty. More control, more ops overhead.

**Datadog** — managed metrics, dashboards, and alerting in one platform. No infrastructure to run. Costs more at scale but eliminates the ops burden of running Prometheus.

At WhatsApp scale, either works. In an interview, commit to one and justify.

> [!tip] Interview framing
> "Alert rule: if p99 delivery latency exceeds 500ms for more than 2 minutes, page on-call. 2-minute window prevents alert fatigue from transient spikes. Leading indicators: Kafka consumer lag, pending_deliveries depth, Redis read latency — these warn before the SLO breaches. Circuit breaker opening and mass reconnect spikes are immediate pages — no sustained window needed, both are confirmed incidents."
