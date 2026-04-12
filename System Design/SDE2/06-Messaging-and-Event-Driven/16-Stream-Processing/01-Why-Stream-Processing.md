A standard Kafka consumer processes one event at a time:

```
event → consumer → process → done
```

This works perfectly for simple operations: save to DB, send an email, update a counter.

But some problems require reasoning **across multiple events over time**:

- "Flag users who spent more than $1000 in the last 5 minutes"
- "Alert if the same card makes 5 transactions in 10 seconds"
- "Count orders per minute for a dashboard"

A single event doesn't have enough information to answer these questions. You need **aggregations over time windows**.

---

## What Stream Processing Gives You

Stream processing frameworks (Flink, Kafka Streams, Spark Streaming) make time-based aggregations a **first-class primitive**:

```java
stream
  .groupByKey(userId)
  .window(SlidingWindow(duration = 5.minutes, slide = 1.second))
  .sum(spend)
```

The framework handles:
- **Windowing** — defining and managing time buckets
- **State management** — storing partial aggregations across events
- **Fault tolerance** — checkpointing state so crashes don't lose progress
- **Distributed execution** — spreading work across many nodes
- **Late event handling** — what to do when events arrive out of order

---

## When You Need Stream Processing

| Use Case | Why Stream Processing |
|----------|----------------------|
| Fraud detection | Aggregate across events in a time window |
| Real-time dashboards | Count/sum events per minute/hour |
| Anomaly detection | Detect patterns across event sequences |
| Session analytics | Group events by user activity gaps |
| Rate limiting at scale | Distributed sliding window counters |

**Rule of thumb:** if your logic requires looking at **multiple events together over time**, you need stream processing.
