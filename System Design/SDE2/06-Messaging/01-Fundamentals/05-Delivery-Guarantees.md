
> [!info] A delivery guarantee defines what the queue promises about whether and how many times a message will be delivered to a consumer. There are three levels — at-most-once, at-least-once, and exactly-once. Understanding the trade-offs between them is a core system design skill.

## Why this matters

You learned that if a consumer crashes before ACKing, the message gets redelivered. That means the same notification could fire twice for the same photo post. The user gets two push notifications. That's bad.

But what's the alternative? Don't redeliver at all? Then the notification never gets sent if the service crashes. That's also bad.

This tension is exactly what delivery guarantees are about — and there's no free lunch.

---

## At-Most-Once

**The promise:** the message will be delivered zero or one times. Never more than once. But it might not arrive at all.

**How it works:** the producer fires the message and doesn't wait for an ACK. No retries. If the consumer crashes, the message is lost.

```
Producer sends message → doesn't wait for ACK → moves on
Consumer crashes before processing → message is gone forever
```

**When to use it:** when losing a message is acceptable. Metrics, logs, analytics events — if one click event out of a million gets dropped, nobody cares. The cost of redelivery (duplicate data, extra processing) outweighs the cost of occasionally losing a message.

> [!tip] At-most-once is not "careless" — it's a deliberate choice for use cases where loss is cheaper than duplication.

---

## At-Least-Once

**The promise:** the message will definitely be delivered. But it might be delivered more than once.

**How it works:** the queue retries until it gets an ACK from the consumer. If the consumer crashes mid-processing before ACKing, the visibility timeout expires and the message gets redelivered to another consumer.

```
Consumer picks up message → starts processing → crashes before ACKing
Visibility timeout expires → message reappears
Another consumer picks it up → processes it → ACKs → deleted
```

The message got processed twice. The notification fires twice. The thumbnail gets generated twice.

**The risk:** duplicate processing. For notifications this means the user gets the same push notification twice. For payments this means the user gets charged twice. For thumbnail generation it's just wasted CPU.

**When to use it:** almost everywhere. It's the default for most production systems — Kafka, SQS, RabbitMQ all default to at-least-once. The duplicate problem is handled at the consumer level

---

## Exactly-Once

**The promise:** the message will be delivered exactly once. No loss, no duplicates.

**Why it's hard:** consider this sequence of events:

```
Consumer processes the message successfully
Consumer sends ACK back to queue
Queue crashes before receiving the ACK
Queue restarts → thinks message was never ACKed → redelivers it
Consumer processes it again → duplicate
```

The ACK and the processing happen in two separate systems. There is no way to make both atomic at the network level — the network can always fail between them. This is a fundamental distributed systems problem.

**How queues try to achieve it:** Kafka has a transactional producer API that uses a two-phase commit-like mechanism internally. It's expensive — lower throughput, higher latency, more complexity.

**The honest truth:** true exactly-once at the queue level is rarely worth the cost. The industry standard is something better.

---

## The Pragmatic Standard — At-Least-Once + Idempotent Consumer

Instead of making the queue guarantee exactly-once (hard, expensive), make the **consumer** handle duplicates safely. This is a consumer-side fix, not a queue-level fix.

An **idempotent consumer** is one where processing the same message twice produces the same result as processing it once.

```
First delivery of photo_posted_123:
→ Notification Service checks DB: "have I sent this notification already?"

→ No → sends notifications → writes { event_id: "photo_posted_123", status: "sent" } to DB

Second delivery of photo_posted_123 (due to crash/retry):
→ Notification Service checks DB: "have I sent this notification already?"
→ Yes → skips it → ACKs the queue → done
```

The duplicate delivery is harmless. The user never receives two notifications.

> [!important] This is the consumer-side fix — the queue still delivers at-least-once. The consumer is responsible for detecting and ignoring duplicates. The queue doesn't need to do anything special.

**How to implement idempotency:**
- Store a `processed_events` table with the event ID
- Before processing, check if the event ID already exists
- If yes, skip and ACK. If no, process and insert the event ID — ideally in the same DB transaction as the actual work.

---

## Summary

| Guarantee | Loss possible? | Duplicate possible? | Cost | Use when |
|---|---|---|---|---|
| At-most-once | Yes | No | Cheapest | Metrics, logs, analytics |
| At-least-once | No | Yes | Medium | Most production systems |
| Exactly-once | No | No | Expensive | Financial transactions (use sparingly) |

> [!tip] **Interview answer:** "I'd use at-least-once delivery with an idempotent consumer. True exactly-once at the queue level is expensive and complex. Making the consumer idempotent gives us the same safety guarantee at a fraction of the cost — and it's where the fix logically belongs anyway, since the consumer is the one that knows what 'already processed' means for its specific operation."
