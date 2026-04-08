# What Each One Fundamentally Is

> [!info] SQS, RabbitMQ, and Kafka may all move messages between systems, but they solve different core problems. SQS is a task queue. RabbitMQ is a routing-first broker that ends in queues. Kafka is a retained append-only event log.

---

## Why this comparison matters

Many system design answers go wrong because people compare features before comparing mental models.

If you treat all three as "message queues," the design choice becomes fuzzy. The real decision starts one level deeper:

```text
Am I handing off a job?
Am I routing a message to the right workflows?
Am I writing an event into shared retained history?
```

That is the real fork in the road.

---

## SQS

SQS is fundamentally a task queue.

```text
Producer -> SQS queue -> worker
```

The producer is saying:

```text
here is a job, some worker should do it
```

This fits async work handoff very well:

- send email
- resize image
- process background billing task
- offload slow API work

---

## RabbitMQ

RabbitMQ is fundamentally a broker with a routing layer in front of queues.

```text
Producer -> Exchange -> Queue -> worker
```

The producer is saying:

```text
route this message to the right queue or queues
```

This is why RabbitMQ stands out when delivery patterns differ by workflow.

---

## Kafka

Kafka is fundamentally an append-only event log.

```text
Producer -> topic / partition log -> consumer groups read by offset
```

The producer is saying:

```text
this event happened, write it to the shared history
```

Consumers do not remove the event from history. They read it and move their offsets.

---

## The clean mental model

```text
SQS       -> do this job
RabbitMQ  -> route this message to the right work queues
Kafka     -> this event happened, append it to history
```

This is the foundation for every later comparison.

---

> [!important] What it guarantees
> Each system gives asynchronous decoupling between producers and consumers.

> [!danger] What it doesn't guarantee
> Similar vocabulary does not mean similar semantics. Using all three under the label "queue" hides the most important design differences.

---

> [!tip] Interview framing
> "I choose based on the core model first: SQS for task handoff, RabbitMQ for routing-first queue workflows, and Kafka for retained event streams with independent consumer groups."
