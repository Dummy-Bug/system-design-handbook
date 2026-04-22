## Phase 6 — Messaging & Event-Driven Systems

> HLD relevance: Notification system, news feed, web crawler,
> chat, job scheduler — all use async messaging.

### SDE-2 Depth Bar For This Phase
- Know why queues, topics, and logs exist and when to choose each.
- Be able to explain delivery guarantees, ordering, fan-out, and replay.
- Go deep on Kafka at the design level: partitions, offsets, consumer groups, replication, retention.
- Understand the outbox pattern well enough to use it in real designs.

### 6.1 Why Message Queues Exist
- Decouple producers from consumers — they don't need to know about each other
- Buffer traffic spikes — queue absorbs burst, consumers drain at their pace
- Enable async processing — don't make users wait for slow operations
- Fan-out — one event triggers many consumers

### 6.2 Core Concepts
- Producer → Queue/Topic → Consumer model
- Point-to-point queue — one message, one consumer (task queue)
- Publish-Subscribe topic — one message, many consumers (event broadcast)
- Message acknowledgment — consumer acks after processing, else requeue
- Dead Letter Queue (DLQ) — messages that fail repeatedly go here for inspection
- Message ordering — FIFO per queue, per-partition in Kafka
- Delay queues — deliver message after N seconds (retry scheduling, reminders)
- Priority queues — higher priority messages processed first
- Visibility timeout (message lease)
  - When a worker picks up a message, it becomes invisible to other workers for a configurable window
  - If worker acks → message deleted. If worker crashes → message reappears for another worker.
  - Set timeout longer than expected task execution time
  - Workers can extend visibility timeout mid-task (heartbeat extension)

### 6.3 Delivery Guarantees
- At-most-once — ack before processing, can lose on crash
- At-least-once — ack after processing, can duplicate on retry
- Exactly-once — idempotent consumer + transactional publish

### 6.4 Fan-out vs Competing Consumers
- Competing consumers — multiple workers on same queue, each message processed once
- Fan-out — same message delivered to all subscribers
- Fan-out on write vs fan-out on read — directly relevant to news feed case study

### 6.5 Apache Kafka (Deep Dive)
- Core concepts
  - Broker — Kafka server that stores and serves messages
  - Topic — named stream of messages
  - Partition — unit of parallelism, messages ordered within partition
  - Offset — position of a message within a partition, consumer tracks this
  - Consumer group — multiple consumers share partitions, each partition consumed by one member
- Producers
  - Partitioner — routes message to partition (by key hash or round-robin)
  - Batching and compression — throughput optimization
- Consumers
  - Pull-based — consumer controls its pace
  - Consumer group rebalancing — partitions reassigned when consumers join/leave
  - Offset commit — at-least-once (commit after) vs at-most-once (commit before)
- Replication — each partition has leader + follower replicas, ISR (In-Sync Replicas)
- Retention — time-based (default 7 days) or size-based, messages persist after consumption
- Compacted topics — keep only latest value per key (good for state/changelog)
- Kafka as event log — replay history, rebuild state from scratch, unlike traditional queues

### 6.6 Message Broker Comparison — Kafka vs RabbitMQ vs SQS
- When to use Kafka
  - High-throughput event streaming — millions of events/sec
  - You need message replay (reprocess from any offset)
  - Long retention, ordering matters (per partition)
  - Event sourcing, CDC pipelines, log aggregation
- When to use RabbitMQ
  - Task queues — distribute work, each task processed once
  - Complex routing needed (exchanges, bindings)
  - Priority queues (Kafka has no native priority)
- When to use SQS
  - Already on AWS, want zero operational overhead
  - Simple task distribution, no ordering guarantee needed
  - FIFO SQS adds ordering and deduplication at lower throughput
- Quick decision rule
  - Event stream (high throughput, replay, ordering) → Kafka
  - Task queue (work distribution, complex routing, priority) → RabbitMQ
  - Simple task queue on AWS (zero ops) → SQS

### 6.7 Outbox Pattern
- Problem — you write to DB and then publish to Kafka. DB succeeds, Kafka fails → inconsistency.
- Solution — write event to an outbox table in the SAME DB transaction as the business change
- A CDC worker or polling process reads outbox table and publishes to Kafka
- Guarantees — DB write and event publish are atomic (same transaction)
- Inbox pattern — consumer stores message ID before processing, skips duplicates
