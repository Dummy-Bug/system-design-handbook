
> [!info] You cannot store every latency measurement individually. Histograms let you keep the shape of the distribution while throwing away the raw numbers.

---

## Why raw storage doesn't work

At 3,000 read requests/sec peak:

```
3,000 requests/sec
× 86,400 seconds/day
= 259,200,000 data points per day (259M)
```

At 8 bytes each, that's ~2GB of raw latency data per day just for reads. Manageable on its own — but this is per service, and you'd need to sort 259M values to compute a percentile. You need a better approach.

---

## Histograms — keep the shape, discard the raw values

Each viewData instance maintains a set of latency buckets in memory. Every incoming request increments exactly one counter based on how long it took to respond.

```
Bucket       Counter
0-5ms:       2,100
5-10ms:       580
10-20ms:      210
20-50ms:       85
50-100ms:      18
100ms+:         7
-----------------------
Total:        3,000
```

Instead of 3,000 individual numbers, you store 6 integers. Incrementing a bucket counter is a single atomic operation — essentially free.

---

## Computing p99 from a histogram

p99 means: the latency value below which 99% of requests fall. With 3,000 requests, you need the bottom 2,970.

Walk the buckets, accumulating a running total until you cross 2,970:

```
0-5ms:    2,100  →  running total: 2,100
5-10ms:     580  →  running total: 2,680
10-20ms:    210  →  running total: 2,890
20-50ms:     85  →  running total: 2,975  ← 2,970 falls in here
```

p99 lands in the 20-50ms bucket. SLO says < 50ms. You're meeting it.

The tradeoff: you lose precision within the bucket. You know p99 is somewhere between 20ms and 50ms but not the exact millisecond. For SLO tracking this is fine — you care whether you're above or below the threshold, not the exact value.

---

## Merging histograms across the fleet

viewData runs multiple instances. Each builds its own histogram independently. To get a fleet-wide p99, the metrics collector adds the bucket counts:

```
Instance 1:   0-5ms: 720   5-10ms: 195   10-20ms: 72 ...
Instance 2:   0-5ms: 698   5-10ms: 187   10-20ms: 68 ...
Instance 3:   0-5ms: 682   5-10ms: 198   10-20ms: 70 ...
-----------------------------------------------------------
Fleet total:  0-5ms: 2,100  5-10ms: 580  10-20ms: 210 ...
```

Histograms are mergeable by design — just add the counters. This is why they're the standard tool for distributed latency measurement. Raw values are not mergeable without storing everything. Bucket counts are trivially addable.

---

## What to measure beyond read latency

Latency alone doesn't tell the full story. Additional metrics worth tracking:

```
Cache hit rate        — if this drops, latency climbs (more S3 fetches)
S3 fetch latency      — p99 of S3 calls specifically (signals S3 degradation)
DB query latency      — p99 of Postgres queries on cache miss
Upload queue depth    — how many async S3 uploads are waiting (signals worker lag)
Upload failure rate   — fraction of upload jobs that hit FAILED status
Circuit breaker state — CLOSED / OPEN / HALF-OPEN (signals S3 health)
```

These are not SLIs but they are leading indicators. If cache hit rate drops from 85% to 60%, latency p99 will climb shortly after. Catching the leading indicator lets you act before the SLO is breached.

---

> [!tip] Interview framing
> "Each viewData instance maintains a histogram in memory — bucket counters for 0-5ms, 5-10ms, 10-20ms, 20-50ms, 50-100ms, 100ms+. p99 is computed by walking buckets until you hit 99% of total requests. Histograms are mergeable so the metrics collector scrapes all instances every 15 seconds, adds bucket counts, computes fleet-wide p99. Beyond read latency, also track cache hit rate as a leading indicator — if it drops, latency follows."
