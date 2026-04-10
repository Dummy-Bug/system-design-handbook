# When To Choose What

> [!info] The right choice depends on the shape of the problem. SQS is best when the problem is async job handoff. RabbitMQ is best when the problem is flexible routing into queue workflows. Kafka is best when the problem is retained event streams with independent consumers and replay.

---

## Choose SQS when

Choose SQS when the problem is:

```text
do this work later
```

Typical cases:

- email jobs
- image processing
- background billing tasks
- async API offloading

SQS is especially attractive when you are already on AWS and want queue behavior without operating broker infrastructure.

---

## Choose RabbitMQ when

Choose RabbitMQ when the problem is:

```text
route this message to the right workflow queues
```

Typical cases:

- one event needs to reach different internal workflows in different ways
- routing rules are important
- selective fanout matters
- task-queue semantics still matter after routing

RabbitMQ becomes attractive when queue semantics and broker-side routing are both first-class requirements.

---

## Choose Kafka when

Choose Kafka when the problem is:

```text
write this event to a shared retained stream
```

Typical cases:

- clickstream ingestion
- analytics pipelines
- CDC
- event sourcing
- state rebuild from historical events

Kafka becomes attractive when replay, high throughput, and multiple independent consumer groups are central requirements.

---

## The shortest decision rule

```text
SQS       -> managed task queue
RabbitMQ  -> routing-first broker
Kafka     -> retained event stream
```

That is the answer you should be able to say out loud in an interview before going into details.

---

> [!important] What it guarantees
> Each tool has a natural sweet spot. Choosing by problem shape leads to simpler designs.

> [!danger] What it doesn't guarantee
> None of these tools is a universal "best message system." Using Kafka for simple job queues or using plain SQS for rich routing usually adds unnecessary pain.

---

> [!tip] Interview framing
> "I'd choose SQS for simple managed async work, RabbitMQ when broker-side routing is important, and Kafka when I need replayable high-throughput event streams with multiple independent consumer groups."
