## Phase 6 - Messaging and Event-Driven Systems

> HLD relevance: senior interviews often go deep on pipelines, replay, ordering, and correctness under asynchronous execution.

### 6.1 Why queues and logs exist
- decoupling
- buffering spikes
- async side effects
- replay and auditability
- competing consumers vs fan-out

### 6.2 Core messaging concepts
- producer -> queue/topic -> consumer
- point-to-point queue
- publish-subscribe
- acknowledgement and redelivery
- DLQ
- visibility timeout / message lease

### 6.3 Delivery guarantees
- at-most-once
- at-least-once
- exactly-once as a narrow systems claim
- idempotent producer
- idempotent consumer

### 6.4 Ordering
- queue ordering vs partition ordering
- key-based partitioning
- throughput vs ordering tradeoff
- reordering under retries and rebalancing

### 6.5 Kafka depth
- brokers, topics, partitions
- producer batching and compression
- consumer groups
- offsets
- leader/follower replication
- ISR
- retention and log compaction
- rebalancing and consumer lag

### 6.6 Broker selection
- Kafka for event streams and replay
- RabbitMQ for routed task queues
- SQS for managed queue simplicity
- know why, not just the names

### 6.7 Backpressure
- queue depth as a lagging symptom
- consumer lag
- scaling consumers
- producer throttling
- load shedding and prioritization

### 6.8 Event-driven architecture patterns
- event sourcing
- CQRS
- outbox pattern
- inbox pattern
- CDC and materialized read models

### 6.9 Stream processing
- windows
- watermarks
- stateful processing
- checkpointing
- batch correction for exactness

### 6.10 Batch, Lambda, and Kappa
- stream vs batch use cases
- Lambda architecture
- Kappa architecture
- replay and reprocessing tradeoffs

### 6.11 Schema evolution
- backward compatibility
- forward compatibility
- Avro + schema registry
- Protobuf for strong internal contracts

