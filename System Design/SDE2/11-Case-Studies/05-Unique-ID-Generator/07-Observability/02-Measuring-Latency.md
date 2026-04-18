# Measuring Latency

## What to measure

Latency = time from when the node receives the request to when it returns the ID. This is pure in-memory work — no disk, no network to another service. Should be sub-millisecond in normal operation.

Track as a histogram, not an average. Averages hide tail latency.

```
Buckets: 0.1ms, 0.5ms, 1ms, 2ms, 5ms, 10ms, 50ms
SLO boundary: p99 < 5ms
```

---

## Per-node histograms

Run separate histograms per node. If one node's p99 is 20ms while others are 0.5ms, that node has a problem — bad hardware clock, NTP issues, or resource contention. A single aggregated histogram would hide this.

```
Node 1: p99 = 0.4ms  ✅
Node 2: p99 = 0.3ms  ✅
Node 3: p99 = 18ms   ❌ ← investigate this node
```

---

## Clock skew contribution to latency

When the clock moves backwards, the node waits — this wait time shows up as latency on those specific requests. A sudden spike in p99 latency on one node, combined with clock skew wait events, points directly to NTP correction as the cause.

Track clock skew wait duration as a separate metric so you can correlate with latency spikes.

---

## At our scale

At 1M IDs/second sustained across ~3 nodes, each node handles ~333K requests/second. The histogram collects 333K data points per second per node. Use reservoir sampling or HDR histograms to keep memory usage bounded while maintaining accuracy at the tail.
