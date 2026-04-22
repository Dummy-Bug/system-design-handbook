
> [!info] The biggest behavioral difference between SQS/RabbitMQ and Kafka appears after a consumer reads a message. In SQS and RabbitMQ, the consumer is taking responsibility for a work item. In Kafka, the consumer is reading from retained history.

---

## SQS after read

In SQS:

```text
Producer -> queue -> worker reads
```

After the worker reads the message:

- it becomes temporarily invisible to other workers
- if processing succeeds, the worker deletes it
- if the worker crashes, the message becomes visible again

This is task-queue behavior.

The consumer is effectively saying:

```text
I am now responsible for finishing this job
```

---

## RabbitMQ after read

In RabbitMQ:

```text
Producer -> exchange -> queue -> consumer reads
```

After the consumer reads:

- the message stays unacknowledged
- if the consumer sends `ACK`, RabbitMQ deletes it
- if the consumer crashes before `ACK`, RabbitMQ redelivers it

**This is also work-queue behavior, but with richer routing before the queue.**

The consumer is again taking responsibility for a piece of work.

---

## Kafka after read

In Kafka:

```text
Producer -> topic / partition log -> consumer group reads by offset
```

After the consumer reads:

- the event stays in the Kafka log
- the consumer commits or moves its offset
- another consumer group can still read the same event
- replay is normal

The consumer is not removing the event from shared history.

---

## The clean contrast

```text
SQS / RabbitMQ -> read means taking responsibility for pending work

Kafka          -> read means moving through retained event history
```

That is one of the most important distinctions in the entire comparison.

---

> [!important] What it guarantees
> SQS and RabbitMQ optimize for work completion semantics. Kafka optimizes for retained shared event history.

> [!danger] What it doesn't guarantee
> Consumer read the message does not mean the same thing across these systems. Treating them as equivalent leads to wrong design choices.


> [!tip] Interview framing
> In SQS and RabbitMQ, consumption is about finishing a work item with retry on failure. In Kafka, consumption is about advancing an offset through a retained log that other groups can still read.
