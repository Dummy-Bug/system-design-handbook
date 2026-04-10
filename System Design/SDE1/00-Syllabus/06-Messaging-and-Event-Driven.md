## Phase 6 - Messaging and Event-Driven Systems

> HLD relevance: notification systems, task queues, email sending, media processing, and background workflows all rely on async messaging.
> At SDE-1 level, you should know why queues exist and how to use them safely.

### 6.1 Why message queues exist
- decouple producer from consumer
- absorb traffic spikes
- move slow work off the request path
- distribute background jobs to worker pools

### 6.2 Core concepts
- producer -> queue/topic -> consumer
- point-to-point queue
- publish-subscribe
- message acknowledgement
- retry and redelivery
- dead letter queue

### 6.3 Delivery guarantees
- at-most-once
- at-least-once
- why most real systems use at-least-once + idempotent consumer

### 6.4 Competing consumers vs fan-out
- competing consumers - one message processed once by one worker
- fan-out - one message copied to multiple downstream consumers
- examples - task queue vs notification broadcast

### 6.5 Task queues
- image resizing
- email sending
- report generation
- scheduled jobs
- visibility timeout / message lease intuition

### 6.6 Notification systems
- multi-channel delivery - push, email, SMS
- user preference filtering
- retries for external providers
- rate limiting per user

### 6.7 Broker choice - simplified
- Kafka - event stream, replay, high throughput
- RabbitMQ - task queue and routing
- SQS - managed AWS queue with low ops burden
- know the quick rule, not the internals yet

### 6.8 Event-driven patterns you should recognize
- events trigger downstream processing
- outbox pattern at a high level
- avoid doing slow side effects synchronously in the API path

