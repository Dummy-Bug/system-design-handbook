## Phase 6 - Messaging and Event-Driven Systems

> HLD relevance: queues, logs, and event-driven workflows appear everywhere once systems get large enough.
> SDE-3 depth means you should be able to reason about ordering, replay, lag, backpressure, and exactly-once claims without hand-waving.

### SDE-3 depth bar for this phase
- Know the difference between a task queue, a broker, and an event log.
- Be able to explain end-to-end delivery guarantees, not just broker guarantees.
- Be able to discuss replay, retention, compaction, and consumer lag operationally.
- Tie patterns like outbox, CDC, CQRS, and batch correction back to real systems like payments, feeds, and analytics.

### 6.1 Why Message Queues Exist
- Decouple producers from consumers.
- Smooth traffic spikes.
- Move slow or unreliable side effects off the synchronous request path.
- Enable replay, auditability, and downstream fan-out.

### 6.2 Core Concepts
- Producer -> queue/topic -> consumer.
- Point-to-point queue vs publish-subscribe topic.
- Ack, nack, requeue, and redelivery.
- Visibility timeout / message lease.
- DLQ, delay queues, retry queues, and poison-message handling.

### 6.3 Delivery Guarantees
- At-most-once: possible loss, no duplicates.
- At-least-once: retries create duplicates, consumer must be idempotent.
- Exactly-once: usually a narrow claim about a specific boundary, not a whole distributed workflow.
- Senior-level depth: explain where dedup lives and what still can go wrong.

### 6.4 Fan-out vs Competing Consumers
- Competing consumers for work distribution.
- Fan-out for one event driving many downstream systems.
- Fan-out on write vs fan-out on read in feed systems.
- When each pattern shifts cost from write path to read path or vice versa.

### 6.5 Apache Kafka (Deep Dive)
- Brokers, topics, partitions, offsets.
- Producer batching, linger, compression, partitioner choice.
- Consumer groups and partition ownership.
- Leader / follower replication and ISR.
- Retention, segment files, and compaction.
- Rebalancing and the operational pain around it.
- Lag monitoring and what lag actually means.
- Senior-level depth: be able to explain why Kafka is an event log first and a queue second.

### 6.5b Message Broker Comparison - Kafka vs RabbitMQ vs SQS
- Kafka: replay, retention, high-throughput stream, partition ordering.
- RabbitMQ: rich routing and task-queue semantics.
- SQS: managed queue with low ops burden.
- Senior-level expectation: choose based on the actual workflow, not popularity.

### 6.5c Backpressure
- Queue depth is a symptom, not a solution.
- Consumer lag as a pressure signal.
- Scaling consumers vs throttling producers.
- Load shedding and priority dropping when downstream cannot recover fast enough.
- Tail-latency and data-loss tradeoffs under overload.

### 6.6 Event-Driven Architecture
- Event sourcing.
- CQRS.
- Outbox pattern.
- Inbox pattern.
- CDC-driven read-model updates.
- Materialized views and denormalized projections.
- Senior-level depth: explain how you keep read models correct enough and rebuildable.

### 6.7 Stream Processing
- Tumbling, sliding, and session windows.
- Watermarks and late-arriving events.
- Stateful processing and checkpointing.
- Exactly-once vs effectively-once semantics in practice.
- State store growth and recovery behavior.

### 6.8 Batch Processing (MapReduce / Spark)
- Why batch still matters even in "real-time" systems.
- Reconciliation, exact recomputation, historical backfill, and replay.
- Spark as the practical batch / large-scale transform tool.
- Senior-level depth: know when batch is the correctness layer and stream is the freshness layer.

### 6.9 Lambda and Kappa Architecture
- Lambda: batch layer + speed layer + serving layer.
- Kappa: stream-only plus replay.
- Operational cost of duplicated logic in Lambda.
- Retention and replay requirements that Kappa imposes.

### 6.10 Schema Evolution
- Backward compatibility vs forward compatibility.
- Avro + schema registry.
- Protobuf for strongly typed internal contracts.
- Version rollout problems when producers and consumers move independently.

### 6.11 What SDE-3 Should Be Comfortable Saying
- "I would use at-least-once plus idempotent consumer here because it is simpler and safe enough."
- "Exactly-once at the broker does not magically give exactly-once business behavior."
- "I need replay because I expect schema bugs, backfills, and read-model rebuilds."
- "If lag keeps growing, I need admission control or throttling, not just a bigger queue."
