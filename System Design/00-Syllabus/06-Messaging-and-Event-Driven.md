## Phase 6 — Messaging & Event-Driven Systems

> HLD relevance: Notification system, ad click aggregation, news feed, web crawler,
> chat, stock broker, job scheduler — all use async messaging.

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
  - When a worker picks up a message, the message becomes invisible to all other workers for a configurable window (e.g. 30 seconds)
  - If the worker successfully processes and acks the message, it is deleted from the queue
  - If the worker crashes or takes too long, the visibility timeout expires and the message reappears — another worker picks it up
  - This is the core mechanism that prevents duplicate execution in task queues (SQS, RabbitMQ, Celery)
  - The timeout must be set longer than the expected task execution time — if your task takes 45 seconds, set visibility timeout to 90 seconds
  - Workers can extend the visibility timeout mid-task if they need more time (heartbeat extension)
  - Directly applies to: Distributed Task Queue, Job Scheduling Platform case studies

### 6.3 Delivery Guarantees
- At-most-once — ack before processing, can lose on crash
- At-least-once — ack after processing, can duplicate on retry
- Exactly-once — idempotent consumer + transactional publish

### 6.4 Fan-out vs Competing Consumers
- Competing consumers — multiple workers on same queue, each message processed once (task distribution)
- Fan-out — same message delivered to all subscribers (notification broadcast, cache invalidation)
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
- Exactly-once — idempotent producer (no duplicate messages) + transactional API
- Kafka as event log — replay history, rebuild state from scratch, unlike traditional queues

### 6.5b Message Broker Comparison — Kafka vs RabbitMQ vs SQS
- **When to use Kafka**
  - High-throughput event streaming — millions of events/sec
  - You need message replay (reprocess from any offset)
  - Long retention — keep events for days/weeks
  - Ordering matters (per partition)
  - Event sourcing, CDC pipelines, log aggregation, stream processing
  - Use in: Ad Click Aggregation, News Feed, CDC, Stock Broker, any event-driven pipeline
- **When to use RabbitMQ**
  - Task queues — distribute work across workers, each task processed once
  - Complex routing needed (exchanges, bindings, headers-based routing)
  - Priority queues (Kafka has no native priority)
  - Lower latency per message than Kafka for small payloads
  - Use in: Notification System (email/SMS tasks), Distributed Task Queue, Job Scheduler
- **When to use SQS**
  - Already on AWS and want zero operational overhead (fully managed, no brokers to run)
  - Simple task distribution — no ordering guarantee needed (standard SQS)
  - FIFO SQS adds ordering and exactly-once delivery but at lower throughput (~300 msg/sec per group)
  - Visibility timeout built-in (same concept as competing consumers)
  - Use in: simple async processing, image resizing, email sending on AWS
- **Quick decision rule**
  - Event stream (high throughput, replay, ordering) → Kafka
  - Task queue (work distribution, complex routing, priority) → RabbitMQ
  - Simple task queue on AWS (zero ops, managed) → SQS

### 6.5c Backpressure
- **What it is** — when a consumer can't keep up with a producer, the system must signal the producer to slow down rather than let the queue grow unbounded or drop messages silently
- **Why queuing alone isn't enough** — a queue absorbs short bursts, but sustained overload just shifts the problem: queue depth grows, memory fills, latency explodes. You need a mechanism to push back.
- **How backpressure works in practice**
  - Consumer lag monitoring — track how far behind consumers are (Kafka consumer group lag)
  - Threshold breach → alert → scale consumers horizontally
  - If consumers can't scale fast enough → producer-side load shedding (drop low-priority requests, return 429)
  - TCP has built-in backpressure (receive window) — application-level queues do not, you must build it
- **Kafka-specific** — Kafka does not push back on producers; the producer side must observe consumer lag metrics and decide to shed load or pause
- **gRPC** — has native flow control; the receiver can pause the sender by not consuming bytes from the network buffer
- **Key interview point** — "I'd monitor consumer lag on the Kafka topic. If lag exceeds X, I'd trigger an autoscaling event to add consumer instances. If lag continues to grow despite scaling, I'd enable load shedding at the API gateway — drop non-critical writes and return 503 with Retry-After."
- Directly applies to: Ad Click Aggregation, Notification System, any write-heavy streaming pipeline

### 6.6 Event-Driven Architecture
- Event sourcing — store state as sequence of immutable events, reconstruct by replay
  - Projection — build a read model by replaying events
  - Event store — append-only log of all events
  - Use case: audit trail (stock broker), collaborative editing history
- CQRS (Command Query Responsibility Segregation)
  - Separate write model (commands) from read model (queries)
  - Write model normalized for consistency, read model denormalized for speed
  - Use case: news feed (write to event log, maintain denormalized feed per user)
- Outbox Pattern — write DB record + event in single transaction
  - CDC or polling picks up event from outbox table
  - Solves dual-write problem (DB write succeeds, Kafka publish fails)
- Inbox Pattern — consumer stores message ID before processing, skips duplicates

### 6.7 Stream Processing
- Stream processing vs batch — process events as they arrive vs processing large chunks
- Windowing — aggregate events over a time window
  - Tumbling window — fixed non-overlapping (hourly click counts)
  - Sliding window — overlapping (clicks in last 60 minutes, updated per minute)
  - Session window — based on user activity gaps
- Watermarks — handle late-arriving events, define how long to wait before closing window
- Stateful stream processing — maintain running counts, joins across streams
- Lambda architecture — batch layer (accurate, delayed) + speed layer (approximate, real-time)
- Kappa architecture — stream-only, reprocess by replaying Kafka topic
- Applies to: ad click aggregation, top-K heavy hitters, real-time analytics

### 6.7b Batch Processing (MapReduce / Spark)
- **MapReduce — the original**
  - Google invented it (2004 paper) — mentioning it in a Google interview is a positive signal
  - Map phase: each node processes its local data chunk, emits (key, value) pairs
  - Shuffle phase: framework groups all values by key across nodes
  - Reduce phase: aggregate values per key (count, sum, merge)
  - Example: word count across 1TB of web pages — Map emits (word, 1), Reduce sums counts per word
  - Hadoop = open-source implementation of MapReduce + HDFS (distributed file system)
  - Limitation: every step reads/writes to disk — slow for iterative algorithms
- **Spark — faster MapReduce**
  - In-memory processing — intermediate results stay in RAM, not written to disk between steps
  - DAG (Directed Acyclic Graph) execution — optimizes multi-step pipelines instead of rigid map-reduce phases
  - 10–100x faster than Hadoop MapReduce for iterative workloads
  - Used for: batch ETL, ML training, log analysis, recommendation batch jobs
- **When batch processing appears in interviews**
  - Reconciliation: nightly batch compares your data against external source (Payment System, Ad Clicks)
  - Reprocessing: replay Kafka topic through batch job to rebuild a corrupted index or fix a bug in aggregation
  - Analytics: aggregate raw events into daily/hourly rollup tables for dashboards
  - Lambda architecture: batch layer (accurate, slow) + speed layer (approximate, fast)
- **Key interview point** — "For the real-time dashboard I'd use Kafka + stream processing. For the billing report I'd use a nightly batch job — reprocess the raw event log from S3 for exact counts. The stream gives approximate real-time; the batch gives exact numbers for invoicing."

### 6.8 Schema Evolution
- Why it matters — producers and consumers update independently, schema must be compatible
- Backward compatibility — new consumer can read old messages
- Forward compatibility — old consumer can read new messages
- Avro + Schema Registry — schema stored centrally, consumers look up schema by ID
- Protobuf — strongly typed, field numbers not names, safe to add/remove fields
- Use this when designing Kafka-based systems with long retention
