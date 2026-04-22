# Message Queues

## Why Async Processing
- Synchronous vs asynchronous — what the difference feels like to the user
- The problem with doing everything in the request path (slow operations, cascading failures)
- Traffic spike absorption — queue absorbs burst, consumers drain at their own pace
- Decoupling producers and consumers — they don't need to know about each other

## Message Queue Basics
- Producer, queue, consumer — the mental model
- Point-to-point queue — one message, one consumer (task distribution)
- Publish-subscribe topic — one message, many consumers (event broadcast, fan-out)
- Message acknowledgement — consumer acks after processing, not before
- At-most-once vs at-least-once delivery — the tradeoff between losing messages vs duplicating them
- What happens if a consumer crashes mid-processing — message reappears for another consumer

## Visibility Timeout
- When a worker picks up a message, it becomes invisible to all other workers for a configurable window
- If the worker acks → message deleted from queue
- If the worker crashes or takes too long → timeout expires, message reappears, another worker picks it up
- Set timeout longer than expected task execution time — if task takes 45 sec, set timeout to 90 sec
- Workers can extend timeout mid-task if they need more time

## Dead Letter Queues
- What a DLQ is — a separate queue for messages that keep failing
- Why messages end up there — max retries exceeded, malformed messages (poison pills)
- Why you need one — never silently drop failed messages, they need human inspection
- DLQ = safety net, not a normal processing path

## Retry and Backoff
- Retry on transient failures — network blip, temporary DB overload
- Don't retry forever — set a max retry limit, then move to DLQ
- Exponential backoff — wait longer between each retry (1s, 2s, 4s, 8s)
- Jitter — randomize backoff to prevent all failed consumers retrying at the same moment

## Common Use Cases
- Sending emails and notifications (don't do it in the request path)
- Image/video processing after upload (async, can take seconds to minutes)
- Order processing pipelines (decouple checkout from fulfillment)
- Decoupling microservices (service A publishes event, B/C/D react independently)

## Tools Overview (Awareness Only)
- Redis as a simple queue — LPUSH to enqueue, BRPOP to consume. No persistence guarantees.
- SQS — managed AWS queue, at-least-once, visibility timeout built-in, simple to operate
- RabbitMQ — more routing flexibility, supports priority queues, exchanges and bindings
- Kafka — not a queue, it's an append-only log. Consumers track their own offset. Save for SDE-2.
