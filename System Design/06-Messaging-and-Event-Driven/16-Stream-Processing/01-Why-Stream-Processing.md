# Why Stream Processing

## The Problem With Plain Kafka Consumption

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

## Why Not Just Use Redis?

Redis feels like a natural fit — sorted sets, TTLs, fast lookups. But let's stress test it.

**Requirement:** sum of spend per user in the last 5 minutes, updated every second.

What you'd need to implement in Redis:

```
1. ZADD user:123:spends <timestamp> <amount>   # on every transaction
2. ZRANGEBYSCORE user:123:spends <now-5min> <now>  # fetch events in window
3. sum all amounts in application code          # aggregate yourself
4. ZREMRANGEBYSCORE user:123:spends 0 <now-5min>   # clean up old entries
```

You're writing all of this yourself. Now multiply by:
- 10 different aggregation types (sum, count, avg, max, p99)
- 5 different window sizes
- Millions of users

You've now built a **custom stream processing engine on top of Redis** — with no fault tolerance for mid-computation state, no distributed execution, and no framework support.

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
