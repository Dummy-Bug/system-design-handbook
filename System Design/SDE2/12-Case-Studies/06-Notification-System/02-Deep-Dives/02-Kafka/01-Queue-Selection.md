> [!important] Why One Worker Handling All Channels Is a Problem
> Push, SMS, and email have fundamentally different delivery characteristics. Push delivers in milliseconds, is free, and handles high volume. SMS goes through telecom carriers with strict rate limits (Twilio caps at a few hundred messages/sec per account) and costs money per message. Email goes through SMTP servers and can take minutes.
>
> If you have one worker processing a mixed batch, it hits the SMS rate limit and starts throttling. Now every push notification in the same batch — which should deliver in milliseconds — is stuck waiting behind a queue of slow SMS jobs. The slowest channel poisons the fastest one.
>
> The fix is per-channel workers: each channel gets its own consumer group, its own Kafka topic, its own scaling policy, and its own rate limiting logic. Push workers scale horizontally for throughput. SMS workers throttle to respect carrier limits. Email workers batch for efficiency. They never interfere with each other.

---

## The Problem

The app server receives notification requests at **5M/sec at peak**. It needs to hand these off to workers without blocking the caller, without losing jobs on crash, and without the workers being overwhelmed. This is a classic queue problem.

But the scale makes it non-trivial. A celebrity posts on Instagram — 10M followers each need a push notification. That single event produces 10M jobs in seconds. The queue needs to absorb this spike without falling over, and workers need to drain it at their own pace.

---

## Why Not SQS?

Amazon SQS is a managed message queue — simple, reliable, and operationally easy. But it has two problems at this scale:

**Throughput ceiling.** SQS standard queues support ~3,000 messages/sec per queue by default. Even with FIFO queues and batching, you hit scaling limits that require partitioning across many queues manually. At 5M/sec, you're managing hundreds of SQS queues and routing logic yourself — you've built a poor man's Kafka.

**No replay.** SQS does support individual message acks — each message has its own receipt handle, so if a worker processes 500 out of 1000 and crashes, the unacked 500 become visible again and get redelivered. That part is fine.

The problem is a different scenario: you deploy a bug that silently sends wrong notifications for 2 hours. By the time you notice, SQS has already deleted every message from that window — consumed and gone. You cannot go back. You cannot rewind and re-process those 2 hours with the fixed code. The data no longer exists in the queue.

With Kafka, messages are retained on disk for a configurable window (say, 7 days). You rewind the consumer offset to 2 hours ago and replay the entire window cleanly. SQS gives you zero ability to do this.

SQS is fine for low-volume, fire-and-forget queuing. It is not built for 5M/sec fan-out with replay requirements.

---

## Why Not RabbitMQ?

RabbitMQ is a traditional message broker — it supports complex routing, exchanges, bindings, and acknowledgement semantics. It's more powerful than SQS for routing logic, but has a different fundamental problem:

**Per-message state kills linear scaling.** RabbitMQ tracks delivery state per message on the broker — which consumer received it, was it acked, does it need redelivery. A single node handles ~50K–100K messages/sec. At 5M/sec you'd need ~100 nodes minimum.

But 100 nodes doesn't give you 5M/sec — and here's why. When you cluster RabbitMQ, nodes need to coordinate that per-message state with each other. Consumer on node 2 acks a message that arrived on node 1 — node 1 needs to hear about that ack. At 5M/sec, every node is constantly gossiping delivery state with every other node. The cross-node coordination becomes the bottleneck, not the machines themselves. Adding more nodes makes it worse, not better.

Kafka avoids this entirely because it is **leader-based**. Each partition has one leader broker that handles all reads and writes for that partition. Followers just replicate silently — they never coordinate on delivery. The consumer tracks its own offset and commits it as a single lightweight batch operation. No per-message state on the broker, no cross-node negotiation. Add a broker, add proportional throughput. Linear scaling.

**No log — no replay.** Like SQS, RabbitMQ deletes messages after acknowledgement. Once consumed, they're gone. No replay, no rewind, no audit trail.

RabbitMQ is the right tool for complex routing at moderate throughput (think: task queues, RPC patterns). At 5M/sec with replay requirements, it falls apart.

> [!danger] "Just add more machines" doesn't work here
> At 100 nodes, every node gossips delivery state with 99 others. At 200 nodes, every node gossips with 199 others. Coordination traffic grows with cluster size — you spend more CPU and network on cross-node chatter than on actual message processing. This is an architectural problem, not a capacity problem. No amount of machines fixes a design that requires per-message state coordination across the cluster.

> [!important] Why Cassandra's gossip doesn't have this problem
> Cassandra is also leaderless and also uses gossip — but it gossips about **cluster state** (node health, ring topology, who owns which token range). This gossip is infrequent (every second or so) and the payload is tiny. It doesn't grow with write throughput — 10M writes/sec or 1M writes/sec, the gossip traffic is the same size. RabbitMQ gossips about **per-message delivery state**, which grows directly with throughput. The rule: gossip about cluster state scales fine. Gossip about data state kills you.

---

## Why Kafka?

Kafka is not a queue in the traditional sense — it is a **distributed commit log**. Messages are written to an append-only log, partitioned across brokers, and consumers read at their own pace using an offset. The broker never tracks delivery state per consumer — each consumer group maintains its own offset.

Three reasons Kafka wins for this system:

**1. Throughput.** A single Kafka broker sustains **500K–1M messages/sec** using sequential disk writes — the fastest I/O pattern available. At 5M/sec you need just 10 brokers. Horizontal scaling is linear because brokers are independent — add a broker, add proportional throughput, no coordination tax.

```
5,000,000 / 500,000 = 10 brokers to handle peak
```

**2. Fan-out via consumer groups.** Multiple independent consumer groups can read the same topic simultaneously, each with their own offset. The push worker, SMS worker, email worker, and analytics pipeline all consume the same notifications topic independently — no duplication, no coordination. In SQS you'd need separate queues per consumer. In RabbitMQ you'd need exchange bindings. In Kafka it's free.

**3. Replay.** Messages are retained on disk for a configurable window (7 days by default). Deploy a bug that sends wrong notifications for 2 hours? Rewind the consumer offset to 2 hours ago and re-process the entire window with the fixed code. SQS and RabbitMQ deleted those messages the moment they were consumed — there's nothing to rewind to.

> [!info] The Core Difference
> SQS and RabbitMQ are queues — consume a message and it's gone. Kafka is a log — messages persist, consumers read at their own pace, multiple consumers can read the same data independently.

> [!danger] Common Trap
> Choosing SQS because it's "simpler to operate." At 5M/sec with fan-out and replay requirements, SQS forces you to build the complexity yourself across hundreds of queues. Kafka's operational overhead is front-loaded but the model fits the problem natively.

---

## Summary

| | SQS | RabbitMQ | Kafka |
|---|---|---|---|
| Throughput per node | ~3K/sec | ~50–100K/sec | ~500K–1M/sec |
| Replay | No | No | Yes (offset rewind) |
| Fan-out | Manual (multiple queues) | Exchange bindings | Consumer groups |
| Broker state | Per message | Per message | Per consumer group offset |
| Operational complexity | Low | Medium | High |
| Right for this system | No | No | Yes |

Kafka wins because the problem is high-throughput, fan-out, and replay — exactly the three things Kafka is built for and SQS/RabbitMQ are not.
