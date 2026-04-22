
> [!info] Prefetch controls how many unacknowledged messages RabbitMQ can send to a consumer at once before waiting for ACKs. Without it, a single fast consumer can hoard the entire queue while slower workers sit idle — or a single slow consumer can hold a huge backlog nobody else can touch.

---

## The hoarding problem

You have 3 inventory workers pulling from the same queue. 1000 order events are waiting.

Without prefetch, RabbitMQ pushes messages as fast as the consumer can accept them. Worker A connects first and immediately buffers hundreds of messages in memory. Workers B and C connect a second later and find almost nothing left to pick up.

```
No prefetch limit:

Worker A: [msg_1 ... msg_847]  ← holding 847 messages
Worker B: [msg_848 ... msg_923]
Worker C: [msg_924 ... msg_1000]

Worker A is slow (each order takes 200ms to process)
Workers B and C finish their batch in 5 seconds
Workers B and C now sit idle while 800+ messages are stuck in Worker A's buffer
```

Those messages are unacked and in-flight — RabbitMQ won't send them to anyone else.

---

## Setting prefetch

```java
channel.basicQos(1);  // prefetch = 1
```

This is called before `basicConsume`. It tells RabbitMQ: don't send this consumer a new message until it ACKs the current one.

```java
// Full setup
channel.basicQos(1);
channel.basicConsume(queueName, false, (consumerTag, delivery) -> {
    processOrder(delivery.getBody());
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
}, consumerTag -> {});
```

---

## Prefetch = 1 — fair dispatch

Each worker holds at most one message at a time. Whoever finishes first gets the next one.

```
Queue: [order_1][order_2][order_3][order_4][order_5]

Worker A gets order_1 (takes 500ms — it's a large order)
Worker B gets order_2 (takes 100ms — small order)
Worker C gets order_3 (takes 100ms — small order)

Worker B finishes first → gets order_4
Worker C finishes next  → gets order_5
Worker A still processing order_1

Result: work distributed by actual throughput, not by who connected first
```

This is the right setting for jobs with variable processing time — order fulfilment, payment processing, video transcoding. Slow workers don't starve fast ones.

---

## High prefetch — throughput over fairness

With `prefetch = 50`, each worker grabs 50 messages at once. Fewer round trips to the broker, higher throughput.

```
Worker A: [order_1 ... order_50]
Worker B: [order_51 ... order_100]
Worker C: [order_101 ... order_150]
```

For small, fast, homogeneous jobs — like sending push notifications or writing log entries — this is fine. Each message takes milliseconds, workers process at similar speeds, the batching is worth it.

But for variable jobs, fairness breaks:

```
Worker A is slow, still holding order_15 through order_50
Worker B finished all 50, now idle
Worker C finished all 50, now idle

35 messages stuck in Worker A's buffer that B and C could finish in seconds
```

---

## The crash burst problem

High prefetch creates a second problem: when a worker crashes, all its unacked messages get redelivered at once.

```
prefetch = 100
Worker A crashes while holding 94 unacked messages

→ RabbitMQ redelivers all 94 to Workers B and C immediately
→ sudden spike in load on remaining workers
→ if they're already at capacity, queue backlog grows fast
```

With `prefetch = 1`, a crashed worker was holding exactly one message. The blast radius of a crash is one message, not a hundred.

---

## The trade-off

```
prefetch = 1
  → fair distribution by processing speed
  → crash loses at most 1 in-flight message per worker
  → more broker round trips (each ACK triggers next delivery)
  → lower throughput for fast, tiny jobs

prefetch = 10–50
  → better throughput for fast homogeneous jobs
  → some fairness lost when workers have uneven speed
  → crash redelivers up to N messages at once

prefetch = 0 (unlimited)
  → maximum throughput
  → complete hoarding, zero fairness
  → a single slow or crashed worker can hold the entire queue
```

No universal correct value. For order processing and payment flows: `prefetch = 1`. For notification dispatch or lightweight event fanout: `prefetch = 10–50`.

---

> [!important] Prefetch is per-consumer, not per-queue. Setting `basicQos(1)` means *this consumer* holds at most 1 unacked message. Other consumers on the same queue have their own prefetch limit.

> [!tip] **Interview framing:** "I set prefetch based on job variability. For long-running or uneven jobs — order processing, payment flows — I use prefetch=1 so work is distributed by actual throughput, not by who connected first. For fast homogeneous jobs I can raise it to reduce broker round trips. The hidden cost of high prefetch is the crash burst — a crashed worker redelivers all its in-flight messages at once."
