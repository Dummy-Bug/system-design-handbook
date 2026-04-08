# Prefetch and Fairness

> [!info] Prefetch controls how many unacknowledged messages RabbitMQ can send to a consumer at once. It is a throughput-versus-fairness tuning knob.

---

## Why this exists

Suppose you have 3 consumers and a queue full of jobs. If RabbitMQ sent unlimited messages to the first consumer that asked, that consumer could hold a huge batch in memory while other consumers sit idle.

Prefetch limits how much work one consumer can reserve.

---

## Prefetch = 1

With `prefetch = 1`, each consumer gets only one unacknowledged message at a time.

```text
Worker A gets M1
Worker B gets M2
Worker C gets M3

Whoever finishes first gets the next message
```

This produces fairer distribution, especially when job duration varies.

It is common for heavy jobs like video processing, large exports, or expensive billing flows.

---

## High prefetch

With `prefetch = 100`, one consumer can reserve many messages at once.

```text
Worker A gets 100 messages
Worker B gets 100 messages
Worker C starts later and gets none yet
```

This reduces round trips to the broker and improves throughput, but it also creates message hoarding.

---

## Why fairness breaks

Imagine Worker A is slow and Worker B is fast:

```text
Worker A still holds 80 unprocessed messages
Worker B has already finished its batch
Worker C is idle
```

Those 80 messages are stuck in Worker A's in-flight set even though other workers could process them faster.

So the queue is not balanced by actual processing speed anymore.

---

## The trade-off

```text
Low prefetch  -> fairer, safer, more broker chatter
High prefetch -> higher throughput, fewer round trips, less fairness
```

There is no universal correct value. It depends on task size, task variability, and acceptable redelivery burst if a consumer crashes.

---

> [!important] What it guarantees
> Prefetch bounds how many unacknowledged messages one consumer can hold.

> [!danger] What it doesn't guarantee
> Prefetch does not guarantee perfect fairness. It only limits hoarding. Poorly chosen values can still create skewed utilization.

---

> [!tip] Interview framing
> "I use low prefetch for long-running or uneven jobs so work is distributed fairly. For tiny homogeneous jobs I can increase prefetch to reduce broker round trips and improve throughput."
