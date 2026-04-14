
> [!info] Message queues and streams have very different throughput profiles — know the numbers before you recommend one
> Kafka handles millions of messages per second. RabbitMQ handles hundreds of thousands. The gap matters when you're estimating whether one broker is enough.

---

## Kafka

```
Throughput per broker:          100,000 – 1,000,000 messages/sec
Throughput per partition:       ~10 MB/s write, ~50 MB/s read

Produce latency (ack=1):        5 – 15 ms
Produce latency (ack=all):      10 – 30 ms   (waits for all replicas)

End-to-end latency:             10 – 50 ms   (produce → consumer reads)

Consumer throughput:            100,000 – 500,000 messages/sec per consumer group

Retention:                      days to weeks (configurable, disk-backed)

Replication factor:             3 (standard)
Max message size (default):     1 MB (configurable)
```

**What partition count determines:**
- Parallelism — consumers in a group = partitions (one consumer per partition max)
- Throughput — more partitions = more parallel writes
- Rule of thumb: partitions = max consumers you'll ever need

```
Example: 500k messages/sec needed
→ 1 broker handles 1M/sec easily → 1 broker is fine for throughput
→ But you want 3 for replication (fault tolerance)
→ Partition count: if 10 consumer instances needed → 10+ partitions
```

**Kafka is a log, not a queue:**
Messages are not deleted after consumption — they're retained for the configured period. Multiple consumer groups can independently read the same topic. This is why Kafka is used for fan-out: one producer, N independent consumers each processing the full stream.

**ack modes and their trade-off:**
```
ack=0   → fire and forget, lowest latency, data loss possible
ack=1   → leader confirms, fast (5-15ms), replica lag gap possible
ack=all → all replicas confirm, slowest (10-30ms), strongest durability
```

For most systems: ack=1 is the right default. ack=all for financial data, payments.

---

## RabbitMQ

```
Throughput:          20,000 – 100,000 messages/sec (single queue)
Latency:             1 – 10 ms
Persistence:         optional (durable queues, message persistence adds latency)
Message retention:   until consumed (then deleted) — not a log
```

**RabbitMQ vs Kafka:**

```
RabbitMQ:
→ Traditional message queue — message consumed once, then gone
→ Complex routing (exchanges, bindings, topic patterns)
→ Good for task queues — N producers, M workers, each message processed once
→ Throughput: 100k/sec max per node
→ Use for: job queues, RPC, routing-heavy workflows

Kafka:
→ Distributed log — messages retained, multiple consumers can replay
→ Simple routing (topic + partition)
→ Good for event streaming — audit logs, analytics, fan-out
→ Throughput: 1M/sec per broker
→ Use for: event streaming, analytics pipelines, fan-out to multiple systems
```

**The deciding question:**
- Does each message need to be processed by exactly one worker? → RabbitMQ
- Does the same event need to reach multiple independent systems? → Kafka
- Do you need to replay past events? → Kafka (log retention)
- Do you need complex routing rules? → RabbitMQ (exchanges)

---

## SQS (AWS managed queue)

```
Standard queue throughput:  nearly unlimited (AWS manages it)
FIFO queue throughput:      3,000 messages/sec (with batching), 300/sec without
Latency:                    ~1 ms – a few ms
Retention:                  up to 14 days
Message size:               max 256 KB
Visibility timeout:         message hidden during processing, reappears if not deleted
```

SQS is a managed RabbitMQ-equivalent. You don't operate it. For systems where you don't want to run Kafka yourself, SQS + SNS (for fan-out) is the AWS-native answer.

---

## Quick reference — when to use what

| System | Throughput | Retention | Fan-out | When to use |
|---|---|---|---|---|
| Kafka | 1M/sec/broker | Days–weeks | Yes (multiple consumers) | Event streaming, analytics, audit logs |
| RabbitMQ | 100k/sec | Until consumed | Limited | Task queues, job workers |
| SQS | Unlimited (standard) | Up to 14 days | Via SNS | AWS-native, managed, no ops |

---

> [!tip] Interview framing
> "Kafka handles 100k–1M messages/sec per broker, end-to-end latency 10–50ms. RabbitMQ handles 100k/sec — traditional queue, message consumed once then deleted. Kafka is a log — multiple consumer groups can replay the same stream independently, which makes it the right choice for fan-out to multiple downstream systems. For task queues where each job is processed once, RabbitMQ or SQS."
