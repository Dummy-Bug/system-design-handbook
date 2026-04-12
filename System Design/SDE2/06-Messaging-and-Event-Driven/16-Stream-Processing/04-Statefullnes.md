
## What "Stateful" Means

Some computations need memory across events.

**Stateless:** each event is processed independently.
```
event → transform → output
```

**Stateful:** you need to remember things from previous events.
```
event → check against past events → update state → output
```

Example: "Flag if same card makes 5 transactions in 10 seconds."

A single transaction event tells you nothing. You need to remember how many transactions this card has made recently. That's **state**.

---

## Processor Nodes vs Kafka Brokers

These are completely separate machines:

```
Kafka Brokers         Processor Nodes (Flink / Kafka Streams)
──────────────        ──────────────────────────────────────
Store events          Consume and compute
Broker 1, 2, 3        Node 1, 2, 3
Serve partitions      Read from partitions
```

Processor nodes are your application instances — not Kafka. They consume from Kafka, run your logic, and maintain state.

---

## Key-Based Partitioning: The Prerequisite

Kafka assigns events to partitions using:

```
partition = hash(key) % num_partitions
```

If you set `key = card_id`:
```
hash("card-456") % 4 = 2  → always Partition 2
hash("card-789") % 4 = 0  → always Partition 0
```

Every event from card-456 **always** lands on Partition 2, regardless of when it arrives.

Since each partition is assigned to one processor node:
```
Partition 2 → Node 2

card-456, tx1 → Partition 2 → Node 2
card-456, tx2 → Partition 2 → Node 2
card-456, tx3 → Partition 2 → Node 2
```

Node 2 sees **all** events for card-456. So it can maintain a correct local counter.

---

## Local State: No Network Hop

Instead of calling Redis or a DB on every event, the processor keeps state **in its own memory**:

```
Node 2 local state:
  card-456 → 3 transactions in last 10s
  card-789 → 1 transaction in last 10s
```

No network call. No latency. Just a local hashmap.

At millions of events per second, this is the difference between feasible and impossible.

---

## The Round Robin Bug

If you produce events **without a key**, Kafka uses round robin:

```
card-456, tx1 → Partition 0 → Node 1  (sees 1 tx)
card-456, tx2 → Partition 2 → Node 3  (sees 1 tx)
card-456, tx3 → Partition 1 → Node 2  (sees 1 tx)
```

Each node thinks card-456 has made only 1 transaction. Fraud detection never fires.

**This is a common production bug.** Someone removes the key to "distribute load more evenly" and stateful logic silently breaks.

```java
// WRONG — round robin, stateful processing broken
producer.send(topic="transactions", value=event)

// CORRECT — key-based routing, same card always same node
producer.send(topic="transactions", key=card_id, value=event)
```

**Rule:** stateful stream processing requires key-based partitioning. It is not optional.
