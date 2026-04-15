
> [!info] Kafka has good retention — but it's the wrong data structure for this problem
> Kafka keeps messages durably for configurable periods. At first glance it looks like a good fit for holding undelivered messages. But the access pattern kills it.

---

## What Kafka is good at

Kafka is a distributed log. Messages are written to a topic and consumers read from an offset. It's durable, high-throughput, and retains messages for days or weeks.

```
Topic: undelivered-messages
  Partition 0: [msg1, msg2, msg3, msg4, ...]
  Partition 1: [msg5, msg6, msg7, ...]
```

---

## The access pattern mismatch

When Bob reconnects, the server needs to answer:

```
"Give me all undelivered messages for Bob"
```

This is a **key-value lookup** — key is Bob's user_id, value is the list of pending messages.

Kafka does not support this. Kafka is a sequential log with offset-based reads. To find Bob's messages, you'd need to:

```
Option A: Give Bob his own Kafka partition
  → Scales to 500M users = 500M partitions
  → Kafka was not designed for millions of partitions
  → Each partition has overhead: file handles, memory, replication
  → Falls apart completely at this scale

Option B: Put all users in shared partitions, filter by user_id
  → On reconnect, scan the entire partition to find Bob's messages
  → Every reconnect = full partition scan
  → O(N) where N is all undelivered messages across all users
  → Completely unacceptable latency
```

---

## The fundamental mismatch

Kafka is optimised for **sequential consumption by a known consumer group**. It is not optimised for **random key-based lookups by user_id**.

What you need is:

```
GET pending_messages WHERE user_id = bob
```

That is a key-value or relational query. Kafka cannot do that efficiently. You lose the key-val lookup the moment you move to Kafka.

> [!important] Tool fit matters
> Kafka is the right tool for fan-out, stream processing, and event pipelines. It is the wrong tool for per-user mailboxes that need random access by user_id. Using the wrong tool here means either rebuilding an index on top of Kafka (complexity) or accepting O(N) scans (performance). Neither is acceptable.

The right store is one that supports fast key-based lookup, is durable by default, and scales horizontally — which points directly to DynamoDB.
