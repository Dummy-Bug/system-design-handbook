# Messaging and Event-Driven Systems

## Why Message Queues Exist
- Decouple producers from consumers — they don't need to know about each other
- Buffer traffic spikes — queue absorbs burst, consumers drain at their pace
- Enable async processing — don't make users wait for slow operations
- Fan-out — one event triggers many consumers

## Core Concepts
- Producer → Queue/Topic → Consumer model
- Point-to-point queue — one message, one consumer (task queue)
- Publish-Subscribe topic — one message, many consumers (event broadcast)
- Message acknowledgement — consumer acks after processing, else requeue
- Dead Letter Queue (DLQ) — messages that fail repeatedly, for inspection
- Message ordering — FIFO per queue, per-partition in Kafka
- Delay queues — deliver message after N seconds
- Priority queues — higher priority messages processed first
- Visibility timeout — message becomes invisible to other workers when picked up
  - If worker acks → message deleted
  - If worker crashes or times out → message reappears for another worker
  - Set timeout longer than expected task execution time
  - Workers can extend timeout mid-task (heartbeat extension)

## Delivery Guarantees
- At-most-once — ack before processing, can lose on crash
- At-least-once — ack after processing, can duplicate on retry
- Exactly-once — idempotent consumer + transactional publish

## Fan-out vs Competing Consumers
- Competing consumers — multiple workers on same queue, each message processed once
- Fan-out — same message delivered to all subscribers
- Fan-out on write vs fan-out on read — directly relevant to news feed

## Apache Kafka
- Broker — Kafka server that stores and serves messages
- Topic — named stream of messages
- Partition — unit of parallelism, messages ordered within partition
- Offset — position of a message within a partition, consumer tracks this
- Consumer group — multiple consumers share partitions, each partition consumed by one member
- Producer — partitioner routes to partition (by key hash or round-robin), batching, compression
- Consumer — pull-based, consumer group rebalancing on join/leave, offset commit strategy
- Replication — each partition has leader + follower replicas, ISR (In-Sync Replicas)
- Retention — time-based (default 7 days) or size-based, messages persist after consumption
- Compacted topics — keep only latest value per key (state/changelog)
- **Kafka internals — append-only log on disk, segment files (active segment + closed segments)**
  - **Each partition = directory of segment files on disk**
  - **Segment file = index file (offset → position) + log file (actual messages)**
  - **Closed segments are immutable — only active segment accepts writes**
  - **Log retention — segments deleted when oldest segment exceeds retention time/size**
- **ISR guarantee — a message is committed only when all ISR replicas have written it**
  - **Producer acks=all — waits for all ISR replicas, strongest durability**
  - **Producer acks=1 — only leader acks, message can be lost if leader fails before replication**
  - **Producer acks=0 — fire and forget, maximum throughput, data loss possible**
- **Exactly-once in Kafka — idempotent producer (sequence numbers, no duplicates on retry) + transactional API (atomic write across multiple partitions)**

## Message Broker Comparison
- Kafka — high-throughput streaming, replay, long retention, ordering per partition, event sourcing
- RabbitMQ — task queues, complex routing (exchanges/bindings), priority queues, lower latency per message
- SQS — managed AWS, zero ops, visibility timeout built-in, FIFO SQS for ordering

## **Backpressure**
- **What it is — when a consumer can't keep up, the system must signal the producer to slow down**
- **Why queuing alone isn't enough — sustained overload grows queue depth unboundedly, memory fills, latency explodes**
- **How to handle in practice:**
  - **Monitor consumer lag (Kafka consumer group lag metric)**
  - **Lag exceeds threshold → trigger autoscaling of consumers**
  - **If consumers can't scale fast enough → producer-side load shedding (drop low-priority, return 429)**
- **Kafka specifics — Kafka does NOT push back on producers. Producer must observe consumer lag and decide to shed load.**
- **gRPC — has native flow control. Receiver can pause sender by not consuming bytes from network buffer.**
- **Interview pattern — "I'd monitor consumer lag on the Kafka topic. If lag exceeds X, trigger autoscale. If lag continues growing, enable load shedding at API gateway."**

## **Event Sourcing**
- **Core idea — store state as a sequence of immutable events, reconstruct current state by replaying**
- **Event store — append-only log of all events, never update or delete**
- **Projection — build a read model by replaying events (e.g., sum all deposit/withdrawal events → current balance)**
- **Snapshot optimization — checkpoint state every N events to avoid full replay from the beginning**
- **Why it's powerful — audit trail by design, replay to fix bugs, rebuild read models**
- **Trade-off — eventual consistency between write model and read projections, complex queries**
- **Use cases — banking ledger, stock broker order history, collaborative editing history**
- **Event sourcing vs CDC — event sourcing IS the primary model, CDC captures changes from a regular DB**

## **CQRS (Command Query Responsibility Segregation)**
- **Separate write model (commands) from read model (queries)**
- **Write model — normalized for consistency, append-only event log or standard DB**
- **Read model — denormalized for speed, optimized per query pattern**
- **How they stay in sync — event handler updates read model when write model changes**
- **Why useful — write and read have different scaling requirements and shapes**
- **Trade-off — eventual consistency between write and read models, more moving parts**
- **Use cases — news feed (write to event log, maintain per-user denormalized feed), banking**
- **CQRS ≠ Event Sourcing — they often go together but are independent patterns**

## **Outbox Pattern**
- **Problem (dual write) — you write to DB and then try to publish to Kafka. DB write succeeds, Kafka publish fails. Data inconsistency.**
- **Solution — write event to an outbox table in the SAME DB transaction as the business change**
- **CDC or a polling worker reads the outbox table and publishes to Kafka**
- **Guarantees — DB write and event publish are atomic (same transaction)**
- **Inbox pattern — consumer stores message ID before processing. If already seen, skip. Idempotent consumption.**

## **Stream Processing**
- **Why stream processing — real-time aggregations over time windows, not possible with plain Kafka consumer**
- **Windowing — aggregate events over a time window:**
  - **Tumbling window — fixed non-overlapping windows (hourly click counts)**
  - **Sliding window — overlapping (clicks in last 60 minutes, updated every minute)**
  - **Session window — based on user activity gaps (session ends after N minutes of inactivity)**
- **Watermarks — handle late-arriving events**
  - **Problem: event time ≠ processing time. A click that happened at 10:59 may arrive at 11:01.**
  - **Watermark = threshold of how long to wait before closing a window**
  - **Trade-off: wait longer → more complete results, higher latency**
- **Stateful stream processing — maintain running counts, joins across streams**
- **Checkpointing — snapshot state + offset to S3/HDFS. On crash, replay Kafka from last checkpoint.**
- **Tools — Kafka Streams (embedded in app), Apache Flink (separate cluster, stronger guarantees)**
- **Applies to: ad click aggregation, top-K heavy hitters, real-time analytics**

## **Batch Processing**
- **MapReduce — Google's original (2004 paper)**
  - **Map phase — each node processes local data chunk, emits (key, value) pairs**
  - **Shuffle phase — framework groups all values by key across nodes**
  - **Reduce phase — aggregate values per key (count, sum, merge)**
  - **Hadoop = open-source MapReduce + HDFS**
  - **Limitation — every step reads/writes to disk, slow for iterative algorithms**
- **Apache Spark — faster MapReduce**
  - **In-memory processing — intermediate results stay in RAM between steps**
  - **DAG (Directed Acyclic Graph) execution — optimizes multi-step pipelines**
  - **10–100x faster than Hadoop MapReduce for iterative workloads**
  - **Use cases — batch ETL, ML training, log analysis, recommendation batch jobs**
- **When batch processing appears — reconciliation, reprocessing, analytics rollups**

## **Lambda and Kappa Architecture**
- **Lambda architecture:**
  - **Batch layer — reprocess all historical data periodically, accurate but delayed**
  - **Speed layer — process live events for low latency, approximate**
  - **Serving layer — merge batch and speed results for queries**
  - **Problem — two codebases doing the same logic, must be kept in sync**
- **Kappa architecture:**
  - **Stream-only — one codebase handles both live and historical**
  - **Historical reprocessing — replay Kafka topic from offset 0 through a new consumer group**
  - **Simpler operationally, requires long Kafka retention or cold storage (S3) as source of truth**
- **When to use which:**
  - **Lambda — batch accuracy non-negotiable (billing, compliance) and you can afford two pipelines**
  - **Kappa — operational simplicity preferred and stream processor can handle replay at scale**

## **Schema Evolution**
- **Why it matters — producers and consumers update independently, old messages still in Kafka**
- **Backward compatibility — new consumer can read old messages (add optional fields only)**
- **Forward compatibility — old consumer can read new messages (ignore unknown fields)**
- **Avro + Schema Registry — schema stored centrally by ID, consumer looks up schema by ID embedded in message**
- **Protobuf — field numbers not names. Safe to add new fields (consumers ignore unknown). Never reuse field numbers.**
- **When this matters — Kafka topics with long retention, any system where producer and consumer deploy independently**
