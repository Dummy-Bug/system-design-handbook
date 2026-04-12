
> [!info] Kafka is built around retained history and replay. SQS and RabbitMQ hold pending work for processing, not long-term event history.

---

## Why this matters

Suppose you discover a bug in analytics logic yesterday and need to rebuild results from historical ad events.

This is where the three systems separate sharply.

---

## Kafka

Kafka keeps events in the log for the configured retention window even after consumers have processed them.

That means you can:

```text
fix consumer bug
reset offsets or start a new consumer group
re-read historical events
rebuild state
```

Replay is not a hack in Kafka. It is a normal design feature.

---

## SQS

SQS keeps messages only for bounded retention.

- if unread, they remain only until retention expires
- if processed and deleted, they are gone
- SQS is not designed as a long-term replayable history

So if you need historical rebuilds, you usually store the same events somewhere else as well.

---

## RabbitMQ

RabbitMQ queues are also designed around pending work, not retained history.

- once a message is acknowledged and removed, it is gone
- unread messages may sit in queue for some time
- but the system is not meant to be your long-term replay store

If replay matters, RabbitMQ usually needs another persistence path beside the broker.

---

## The clean rule

```text
Kafka          -> replay is native
SQS/RabbitMQ   -> replay usually needs a separate storage system
```

That is often the deciding factor in data-pipeline interviews.

---

> [!important] What it guarantees
> Kafka gives a retained log model where re-reading history is expected. SQS and RabbitMQ give bounded pending-work retention.

> [!danger] What it doesn't guarantee
> Unread messages sitting in SQS or RabbitMQ do not make them event-history systems. Pending work is not the same as replayable shared history.

---

> [!tip] Interview framing
> "If replay and historical rebuild are core requirements, Kafka is the natural fit. With SQS or RabbitMQ, I'd add a separate durable event store because the queue is for processing, not historical reconsumption."
