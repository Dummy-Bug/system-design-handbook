
> [!info] You cannot store every latency measurement individually. Histograms let you keep the shape of the distribution while throwing away the raw numbers.

---

## Why raw storage doesn't work

At peak, WhatsApp processes roughly 100K messages/second across the fleet:

```
100,000 messages/sec
× 86,400 seconds/day
= 8.64 billion data points per day
```

At 8 bytes each, that's ~69GB of raw latency data per day. Storing it is expensive. More critically, computing a percentile requires sorting all 8.64 billion values — that's not a real-time operation.

You need a better approach.

---

## Histograms — keep the shape, discard the raw values

Each app server maintains a set of delivery latency buckets in memory. Every message that completes delivery increments exactly one counter based on how long it took.

```
Bucket          Counter
0-50ms:         61,000
50-100ms:       22,000
100-200ms:       9,500
200-500ms:       5,800
500ms-1s:        1,400
1s+:               300
--------------------------
Total:         100,000
```

Instead of 100,000 individual numbers, you store 6 integers. Incrementing a bucket is a single atomic operation — essentially free.

---

## Computing p99 from a histogram

p99 means: the latency value below which 99% of messages fall. With 100,000 messages, you need the bottom 99,000.

Walk the buckets, accumulating a running total until you cross 99,000:

```
0-50ms:    61,000 → running total: 61,000
50-100ms:  22,000 → running total: 83,000
100-200ms:  9,500 → running total: 92,500
200-500ms:  5,800 → running total: 98,300
500ms-1s:   1,400 → running total: 99,700  ← 99,000 falls in here
```

p99 lands in the 500ms-1s bucket. SLO says < 500ms. **You're breaching it.** This would fire an alert.

The trade-off: you lose precision within the bucket. You know p99 is somewhere between 500ms and 1s, not the exact millisecond. For SLO tracking this is fine — you care whether you're above or below the threshold, not the exact value.

---

## Merging histograms across the fleet

WhatsApp runs thousands of app servers. Each builds its own histogram independently. To get a fleet-wide p99, the metrics collector adds bucket counts:

```
Server 1:   0-50ms: 610   50-100ms: 220   100-200ms: 95 ...
Server 2:   0-50ms: 598   50-100ms: 215   100-200ms: 91 ...
Server 3:   0-50ms: 602   50-100ms: 218   100-200ms: 93 ...
...
Fleet total: 0-50ms: 61,000  50-100ms: 22,000 ...
```

Histograms are mergeable by design — just add the counters. This is why they're the standard tool for distributed latency measurement.

---

## Leading indicators for delivery latency

Latency alone doesn't tell the full story. Leading indicators warn you before the SLO breaches:

```
Kafka consumer lag (registry updates)  — growing lag → users appear offline longer → delivery delays
DynamoDB write latency p99             — spikes here cascade into delivery latency
Pending_deliveries table depth         — growing backlog → delivery worker falling behind
Redis inbox read latency               — spike here slows every inbox load
Connection server queue depth          — backed up → messages waiting to be forwarded
```

These aren't SLIs, but a spike in any of them predicts a delivery latency SLO breach within minutes.

> [!tip] Interview framing
> "Each app server maintains a latency histogram — bucket counters for 0-50ms, 50-100ms, 100-200ms, 200-500ms, 500ms-1s, 1s+. Prometheus scrapes all servers every 15 seconds and adds bucket counts to compute fleet-wide p99. Beyond the SLI, also track Kafka consumer lag and pending_deliveries depth as leading indicators — both predict delivery latency degradation before the SLO breaches."
