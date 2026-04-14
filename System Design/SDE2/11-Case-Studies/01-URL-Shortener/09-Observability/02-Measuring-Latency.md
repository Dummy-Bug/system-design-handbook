
> [!info] You cannot store 86 billion latency measurements. You don't need to.
> 1M requests/sec × 86,400 seconds/day = 86.4 trillion data points per day. The trick is to throw away the raw numbers and keep only the shape of the distribution.

---

## The naive approach and why it fails

The obvious way to measure p99 latency: record the response time of every request, sort all of them at the end, find the 99th percentile value.

At 1M requests/second, you have:

```
1,000,000 requests/sec
× 86,400 seconds/day
= 86,400,000,000,000 data points per day  (86.4 trillion)
```

Storing 86.4 trillion latency values (even at 4 bytes each) would require 345 terabytes per day. And sorting 86.4 trillion values to compute a percentile is computationally impossible in real time.

You need a completely different approach.

---

## Histograms — keep the shape, throw away the raw values

Instead of storing individual latency values, you define a set of **buckets** — ranges of latency — and keep a counter for each bucket. Every request increments exactly one counter based on how long it took.

```
Bucket          Counter
0-5ms:          812,000
5-10ms:         143,000
10-20ms:        31,000
20-50ms:        12,000
50-100ms:       1,800
100ms+:         200
-----------------------
Total:          1,000,000
```

This is a histogram. Instead of storing 1,000,000 individual numbers, you store 6 integers. The counters live in memory on the app server — incrementing a counter is a single atomic operation, essentially free.

---

## Computing p99 from a histogram

p99 means: the latency value below which 99% of requests fall. With 1,000,000 total requests, you need the bottom 990,000.

Walk the buckets in order, accumulating a running total until you cross 990,000:

```
0-5ms bucket:    812,000  →  running total: 812,000
5-10ms bucket:   143,000  →  running total: 955,000
10-20ms bucket:  31,000   →  running total: 986,000
20-50ms bucket:  12,000   →  running total: 998,000  ← 990,000 falls in here
```

p99 lands in the 20-50ms bucket. Your SLO says < 50ms. You're meeting it. ✓

The tradeoff: you lose precision within the bucket. You know p99 is somewhere between 20ms and 50ms, but not exactly where. For SLO tracking this is fine — you care about whether you're above or below the threshold, not the exact millisecond.

---

## Merging histograms across the fleet

You have 20 redirect servers. Each one builds its own histogram independently. To get a fleet-wide p99, you add the bucket counts together:

```
Server 1:    0-5ms: 40,600   5-10ms: 7,150   10-20ms: 1,550 ...
Server 2:    0-5ms: 41,200   5-10ms: 7,300   10-20ms: 1,580 ...
...
Server 20:   0-5ms: 39,800   5-10ms: 6,950   10-20ms: 1,490 ...
-------------------------------------------------------------------
Fleet total: 0-5ms: 812,000  5-10ms: 143,000  10-20ms: 31,000 ...
```

Histograms are mergeable by design — just add the counters. This is why histograms are the standard tool for distributed latency measurement. Raw values are not mergeable without storing everything. Histogram bucket counts are trivially mergeable.

---

## Who does the scraping

Each app server exposes its histogram counters on a simple HTTP endpoint — `/metrics`. A dedicated metrics collector (Prometheus if self-hosted, or a managed service like Datadog) scrapes all 20 servers every 15 seconds, merges the histograms, and stores the result.

```
Every 15 seconds:
Prometheus → GET /metrics from server 1  → histogram snapshot
Prometheus → GET /metrics from server 2  → histogram snapshot
...
Prometheus → GET /metrics from server 20 → histogram snapshot
→ merge all 20 histograms
→ compute fleet p99
→ store time-series result
```

You now have fleet-wide p99 updated every 15 seconds. If you plot this over time you get a latency graph. If you set a threshold at 50ms, you can alert when it's crossed.

---

> [!tip] Interview framing
> "You can't store raw latency for 1M req/sec — that's 86 trillion data points per day. Instead, each app server maintains a histogram: bucket counters for 0-5ms, 5-10ms, 10-20ms, 20-50ms, 50-100ms, 100ms+. p99 is computed by walking buckets until you hit 99% of total requests. Histograms are mergeable — the metrics collector scrapes all 20 servers every 15 seconds, adds bucket counts, computes fleet-wide p99. Prometheus for self-hosted, Datadog for managed."
