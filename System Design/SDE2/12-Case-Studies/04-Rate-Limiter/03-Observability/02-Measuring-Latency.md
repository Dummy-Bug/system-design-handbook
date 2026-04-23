
> [!info] You cannot store every latency measurement individually. Histograms let you keep the shape of the distribution while throwing away the raw numbers.

---

## Why Raw Storage Doesn't Work

At 400K decisions/sec peak:

```
400,000 decisions/sec
× 86,400 seconds/day
= 34,560,000,000 data points per day (34B)
```

At 8 bytes each, that's ~270GB of raw latency data per day. Storing it is expensive. Computing a percentile requires sorting 34 billion values — completely impractical in real time.

---

## Histograms — Keep the Shape, Discard the Raw Values

Each rate limiter instance maintains latency buckets in memory. Every incoming request increments exactly one counter based on how long the allow/block decision took.

```
Bucket          Counter
0-1ms:          310,000
1-3ms:           72,000
3-5ms:           12,000
5-10ms:           5,800
10-50ms:            180
50ms+:               20
─────────────────────────
Total:          400,000
```

Instead of 400,000 individual numbers, you store 6 integers. Incrementing a bucket counter is a single atomic operation — essentially free at any QPS.

---

## Computing p99 from a Histogram

p99 means: the latency value below which 99% of decisions fall. With 400,000 decisions, you need the bottom 396,000.

Walk the buckets, accumulating a running total until you cross 396,000:

```
0-1ms:    310,000  → running total: 310,000
1-3ms:     72,000  → running total: 382,000
3-5ms:     12,000  → running total: 394,000
5-10ms:     5,800  → running total: 399,800  ← 396,000 falls in here
```

p99 lands in the 5-10ms bucket. SLO says < 10ms. You're meeting it.

The tradeoff: you lose precision within the bucket. You know p99 is somewhere between 5ms and 10ms but not the exact millisecond. For SLO tracking this is fine — you care whether you're above or below the threshold, not the exact value.

---

## Merging Histograms Across the Fleet

Rate limiter runs across 10+ nodes. Each builds its own histogram independently. To get a fleet-wide p99, the metrics collector adds the bucket counts:

```
Node 1:   0-1ms: 32,000   1-3ms: 7,400   3-5ms: 1,200 ...
Node 2:   0-1ms: 31,500   1-3ms: 7,100   3-5ms: 1,180 ...
Node 3:   0-1ms: 30,800   1-3ms: 7,200   3-5ms: 1,220 ...
...
Fleet:    0-1ms: 310,000  1-3ms: 72,000  3-5ms: 12,000 ...
```

Histograms are mergeable by design — just add the counters. This is why they're the standard tool for distributed latency measurement.

---

## What to Measure Beyond Decision Latency

Latency alone doesn't tell the full story. Additional metrics worth tracking:

```
Redis latency p99         — p99 of Lua script execution specifically
                            if this climbs, decision latency follows

Local counter hit rate    — fraction of requests blocked by Layer 1
                            if this drops unexpectedly, Redis is taking more load

Redis connection errors   — count of failed Redis calls per second
                            rising errors → fail open rate is increasing

Block rate per endpoint   — fraction of requests blocked per endpoint
                            sudden spike on /login = credential stuffing attack

False positive rate       — sampled: requests blocked that shouldn't be
                            tracks over-counting from race conditions or bugs

Rule cache age            — time since last successful Rule DB poll
                            if > 5 minutes, rules may be dangerously stale
```

These are not SLIs but they are leading indicators. If Redis latency climbs from 0.5ms to 5ms, decision latency p99 will breach the SLO shortly after. Catching the leading indicator lets you act before the SLO is breached.

---

> [!tip] Interview framing
> "Each rate limiter instance maintains a histogram in memory — buckets for 0-1ms, 1-3ms, 3-5ms, 5-10ms, 10-50ms, 50ms+. p99 is computed by walking buckets until you hit 99% of total decisions. Histograms are mergeable so the metrics collector scrapes all nodes every 15 seconds, adds bucket counts, computes fleet-wide p99. Beyond decision latency, track Redis latency as a leading indicator and block rate per endpoint to detect attacks early."
