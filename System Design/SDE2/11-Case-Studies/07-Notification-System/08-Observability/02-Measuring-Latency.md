# Measuring Latency — Notification System

> [!info] You cannot store billions of latency measurements. You don't need to.
> At 5M notifications/sec, storing raw delivery times would require petabytes per day. The trick is to throw away the raw numbers and keep only the shape of the distribution.

---

## What Latency Means for a Notification System

For a URL shortener, latency is simple — time from request to response on a single HTTP call. For a notification system, latency is the time from when the calling service submits the notification to when the external provider acknowledges delivery. This spans multiple hops:

```
Calling service submits → App Server → Kafka → Worker → APNs/Twilio/SendGrid → ack

Total latency = Kafka publish time + consumer lag + worker processing time + provider round trip
```

Each channel has its own latency profile. Push is measured in seconds, SMS in tens of seconds, email in minutes. You cannot aggregate them — a single "notification system p95" number is meaningless.

---

## Histograms — Keep the Shape, Throw Away the Raw Values

Each worker maintains a **histogram** — bucket counters for ranges of delivery latency. Every successful send increments exactly one bucket.

**Push worker histogram buckets:**
```
0-1s:      most notifications (fast APNs response)
1-3s:      slightly slow (APNs momentarily backed up)
3-5s:      approaching SLO threshold
5-10s:     SLO breach territory
10s+:      severe degradation
```

**SMS worker histogram buckets:**
```
0-5s:      fast Twilio response
5-15s:     normal range
15-30s:    approaching SLO threshold
30-60s:    SLO breach territory
60s+:      severe degradation
```

**Email worker histogram buckets:**
```
0-30s:     fast SendGrid response
30-60s:    normal range
60-120s:   approaching SLO threshold
120-300s:  SLO breach territory
300s+:     severe degradation
```

Each worker instance maintains its own histogram counters in memory — incrementing a counter is a single atomic operation, essentially free at 5M/sec.

---

## Computing p95 from a Histogram

p95 means: the latency value below which 95% of notifications were delivered. With 3.5M push notifications/sec across 18 workers, each worker handles ~195K sends/sec.

For one worker in one second:
```
Bucket     Counter    Running Total
0-1s:      180,000 →  180,000
1-3s:       12,000 →  192,000
3-5s:        2,500 →  194,500   ← 95% of 195,000 = 185,250 → falls in 1-3s bucket
5-10s:         400 →  194,900
10s+:           100 →  195,000
```

p95 lands in the 1-3s bucket — well under the 5s SLO. ✓

The tradeoff: you lose precision within the bucket. You know p95 is somewhere between 1s and 3s, not exactly where. For SLO tracking this is fine — you care whether you're above or below the threshold, not the exact millisecond.

---

## Merging Histograms Across the Fleet

18 push workers each maintain their own histogram. To get fleet-wide p95, add the bucket counts together:

```
Worker 1:  0-1s: 180,000  1-3s: 12,000  3-5s: 2,500 ...
Worker 2:  0-1s: 179,000  1-3s: 12,500  3-5s: 2,400 ...
...
Worker 18: 0-1s: 178,000  1-3s: 11,800  3-5s: 2,600 ...
---------------------------------------------------------
Fleet:     0-1s: 3.2M     1-3s: 216K    3-5s: 45K   ...
```

Histograms are mergeable by design — just add the counters. This is why histograms are the standard tool for distributed latency measurement.

---

## Kafka Consumer Lag — The Hidden Latency

Delivery latency is not just the external provider round trip. If a notification sits in the Kafka topic for 30 seconds before a worker picks it up, that's 30 seconds of latency the histogram doesn't capture.

**Kafka consumer lag** is a separate metric — how many messages behind the latest offset is each consumer group?

```
notifications-push consumer group lag: 0 messages    → workers keeping up ✓
notifications-push consumer group lag: 5M messages   → workers falling behind ✗
                                                         ~30 seconds of backlog at 3.5M/sec
```

Consumer lag is the earliest warning signal for capacity problems. Latency SLI breaches come after — consumer lag starts rising before users notice slow delivery.

---

## Who Does the Scraping

Each worker exposes its histogram counters on `/metrics`. A Prometheus instance (or Datadog agent) scrapes all workers every 15 seconds, merges the histograms per channel, and computes fleet-wide p95 per channel.

```
Every 15 seconds:
Prometheus → scrapes all 18 push workers   → merges → fleet push p95
Prometheus → scrapes all SMS workers       → merges → fleet SMS p95
Prometheus → scrapes all 84 email workers  → merges → fleet email p95
Prometheus → scrapes Kafka consumer lag    → per-topic lag metric
```

Four latency time-series, updated every 15 seconds, each independently alertable.

> [!tip] Interview framing
> "Latency is measured per channel — push, SMS, email have different SLOs and different delivery paths. Each worker maintains a histogram in memory, Prometheus scrapes and merges every 15 seconds. But delivery latency alone isn't enough — Kafka consumer lag is a separate metric that catches capacity problems before they show up in the latency histogram. Rising lag means the problem is coming. Rising p95 means it's already here."
