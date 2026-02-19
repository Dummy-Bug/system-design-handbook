
### Latency Requirements

|Metric|Target|
|---|---|
|p50 latency|< 20ms|
|p99 latency|< 50ms|

Autocomplete must feel instant.

* Latency for Increment API does not matter as it is Async operation.

---

### Availability Target

- 99.99% uptime.

- Must continue serving during:
    - Cache node failure. 
    - Partial network outage.
    - Index rebuild. 

---

### Consistency vs Availability Tradeoff

---

## What happens if availability is prioritized?

Design behavior:

```
Serve from cache + snapshot
Write updates asynchronously
```

Results:

- Suggestions always load.
- Ranking may be slightly stale.
- System continues during failures.

User experience:

Fast. Smooth. Forgiving.

---

## What happens if consistency is prioritized?

Design behavior:

```
Synchronous writes
Strongly consistent reads
Quorum or leader coordination
```

Results:

- Higher latency.
- Throughput bottlenecks.
- Service stalls on partial failures.

User experience:

Slow. Fragile. Janky.

---

## User-Centered Reality

---

### What users actually want

> Helpful suggestions instantly.

---

### What users do NOT care about

- Perfect ordering.
- Real-time popularity updates.
- Sub-second freshness.

Autocomplete is probabilistic by nature.

---

## Risk Analysis

---

### If consistency is wrong

Worst case:

- Suggestions slightly misordered.
- Trending query appears minutes late.

Impact:

Low.

---

### If availability is wrong

Worst case:

- Suggestions fail to load.
- Typing feels broken.
- Product feels slow.

Impact:

High.
