
> [!info] The thundering herd — when everyone opens WhatsApp at the same time
> New Year's midnight. 500M users open WhatsApp simultaneously. Every one of them hits the inbox API, which reads their sorted set from Redis. This is the thundering herd problem — a sudden, coordinated spike that overwhelms a single node.

---

## The inbox Redis under spike

In normal operation, the inbox sorted set fits comfortably on Redis. The math:

```
500M users × (16 bytes conv_id + 8 bytes timestamp) = ~12.5GB
```

Storage is not the problem. The problem is read and write throughput at midnight.

**Read load:**

500M users open the app at midnight. Each inbox load reads the top K conversations from Redis. That's 500M reads hitting Redis in a very short window — not spread across an hour, because it's midnight and humans are predictably synchronised.

**Write load:**

Those same 500M users each send roughly 5 "Happy New Year" messages within the first minute. Each sent message updates the sorted set for the recipient's inbox.

```
500M users × 5 messages = 2.5B writes
2.5B / 60 seconds       = ~40M writes/second peak
```

Even conservatively, this is orders of magnitude beyond what a single Redis primary can handle. A single Redis node handles roughly 100K ops/second.

---

## The fix — shard by user_id

The solution is to split the inbox data across multiple Redis primaries. Each primary owns a slice of users, determined by a simple hash:

```
primary_index = user_id % N
```

Where N is the number of primary nodes.

**How many primaries do you need?**

```
Peak write load: ~1M writes/second (rounding up conservatively)
Single primary:  100K ops/second
Primaries needed: 1M / 100K = 10 primaries
```

With 10 primaries, each owns 1/10th of users. A write for user_id 4523897 always goes to `4523897 % 10 = 7` — primary 7. Consistent, deterministic, no coordination needed.

---

## Read replicas for read scaling

Writes go to primaries. But reads can be served by replicas.

Each primary has N read replicas. The app server can read from any replica — spreading 500M inbox reads across the full replica fleet.

```
10 primaries × 3 replicas each = 30 nodes total
500M reads / 30 nodes          = ~16M reads/node
```

Over a 60-second window that's manageable per node.

**Replication lag:** Redis replication is asynchronous, so replicas can be a few milliseconds behind the primary. On New Year's midnight, serving an inbox that's 50ms stale is completely acceptable. The user sees their conversations — none of that data is changing fast enough for the lag to matter.

---

## TTL extension for predictable events

The inbox sorted set TTL in normal operation is set to match typical usage patterns. But New Year's midnight is a known event — people who haven't opened WhatsApp in days will open it tonight.

Extend TTL to 26 hours on December 31st so that yesterday's inbox data is still warm when the spike hits. The cost is slightly more Redis memory for one day. The benefit is that the cold-start problem (all misses falling through to DynamoDB) doesn't compound on top of the thundering herd.

> [!tip] Interview framing
> "For the inbox Redis, I'd shard by user_id across 10 primaries to handle the write spike, add read replicas per primary to spread reads, and extend TTL to 26 hours ahead of known high-traffic events so the cache is warm when the spike arrives."
