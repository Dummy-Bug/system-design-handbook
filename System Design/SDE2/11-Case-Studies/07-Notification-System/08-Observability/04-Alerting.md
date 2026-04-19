# Alerting — Notification System

> [!info] Knowing your SLI is breached is useless if nobody finds out for an hour.
> Alerting closes the loop — when SLI diverges from SLO, a human gets paged immediately.

---

## The Alert Rules

**Latency alerts — per channel:**
```
IF push_p95_delivery_latency > 5s    FOR > 2 minutes → page on-call (P1)
IF sms_p95_delivery_latency > 30s    FOR > 2 minutes → page on-call (P1)
IF email_p95_delivery_latency > 2min FOR > 5 minutes → page on-call (P2)
```

Email gets a longer window (5 minutes) because it has a 2-minute SLO — brief spikes within the SLO don't need a page.

**Intake availability alert:**
```
IF intake_availability < 99.99% FOR > 2 minutes → page on-call (P0)
```

Intake availability dropping means calling services cannot submit notifications at all — the most severe failure.

**Delivery success rate alerts:**
```
IF push_success_rate < 95%  FOR > 2 minutes → page on-call (P1)
IF sms_success_rate < 95%   FOR > 2 minutes → page on-call (P1)
IF email_success_rate < 95% FOR > 5 minutes → page on-call (P2)
```

**Operational alerts — early warning:**
```
IF notifications-push-dlq depth > 100K messages  → page on-call (P2)
IF notifications-sms-dlq depth  > 10K messages   → page on-call (P2)
IF kafka_consumer_lag (push)    > 1M messages     → page on-call (P2)
IF apns_5xx_rate > 1%           FOR > 1 minute   → page on-call (P2)
IF twilio_5xx_rate > 1%         FOR > 1 minute   → page on-call (P2)
```

---

## Why You Need a Sustained Breach Window

Without the duration condition, a single spiky second triggers a page. At 5M notifications/sec, you will have occasional spiky seconds — a Kylie Jenner post hits, GC pauses fire simultaneously across workers, APNs has a 10-second hiccup. Then everything recovers.

If you alert on every spike, you wake engineers at 3am for events that self-resolved before anyone could respond. This is **alert fatigue** — engineers start ignoring pages because most are false alarms. When a real incident happens, the page gets ignored too.

The sustained window filters transient spikes while still catching real degradation fast enough to act on it.

```
APNs hiccup for 30 seconds → alert condition met, not sustained → no page
APNs degraded for 3 minutes → condition met for > 2 minutes → page fires
```

---

## Priority Levels

**P0 — intake API down:**
No notifications can enter the system. Every calling service is affected. All hands on deck immediately.

**P1 — channel delivery degraded:**
A channel is missing its SLO or delivery success rate is low. Users are missing notifications. Page the on-call engineer, start investigation within 5 minutes.

**P2 — early warning signals:**
DLQ growing, consumer lag rising, provider error rate ticking up. Not yet a user-facing problem but heading there. Page the on-call engineer, investigate before it becomes P1.

---

## What the On-Call Engineer Sees

When a P1 alert fires for push latency, the engineer gets:

- Alert name: `push_p95_delivery_latency_breach`
- Current value: `p95 = 8.3 seconds` (SLO: 5s)
- Duration: `breached for 4 minutes`
- Link to Grafana dashboard showing:
  - Push p95 latency over time (spike visible)
  - APNs error rate (spiking simultaneously → provider issue)
  - DLQ depth (growing → retries piling up)
  - Kafka consumer lag (stable → workers keeping up, not a capacity issue)

In 30 seconds the engineer knows: APNs is degraded, circuit breaker may have tripped, DLQ is filling. They check the circuit breaker state and start the recovery procedure.

> [!tip] Interview framing
> "Alert rules have two parts: the threshold and the duration. Push p95 > 5s for more than 2 minutes pages on-call. The duration window prevents alert fatigue from transient spikes. Priority levels matter: P0 for intake down (all notifications affected), P1 for channel degradation (SLO breach), P2 for early warning signals (DLQ growing, provider error rate rising). The operational alerts are what let you catch problems before they become SLO breaches."
