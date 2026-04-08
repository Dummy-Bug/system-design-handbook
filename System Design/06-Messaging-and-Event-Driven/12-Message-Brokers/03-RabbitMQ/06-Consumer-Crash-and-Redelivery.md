# Consumer Crash and Redelivery

> [!info] If a RabbitMQ consumer crashes before acknowledging a message, RabbitMQ treats the message as unfinished work and makes it available for redelivery.

---

## The failure case

Take a billing worker processing an ad click:

```text
1. RabbitMQ delivers message to consumer
2. Consumer updates billing state
3. Consumer crashes before ACK
```

From the consumer's point of view, the work may already have happened.  
From RabbitMQ's point of view, the work never finished because it never received the ACK.

That mismatch is where redelivery comes from.

---

## What RabbitMQ does

When the consumer connection or channel closes unexpectedly, unacknowledged messages are returned for another consumer to process.

```text
RabbitMQ -> deliver M1 to Worker A
Worker A -> crashes before ACK
RabbitMQ -> sees channel close
RabbitMQ -> makes M1 available again
Worker B -> receives M1
```

This is how RabbitMQ avoids losing unfinished work.

---

## Why duplicates are unavoidable

Now consider the timing:

```text
Worker A updates database successfully
Worker A crashes before ACK
RabbitMQ redelivers message
Worker B updates database again
```

The same business effect may happen twice.

RabbitMQ is choosing safety against loss over protection from duplicate execution. That is the standard at-least-once trade-off.

---

## What the application must do

The broker cannot know whether the business effect already happened. Only the application can know that.

So consumers need idempotency:

```text
if message_id already processed:
    skip business action
    ACK
else:
    do business action
    mark processed
    ACK
```

---

> [!important] What it guarantees
> Crash before ACK does not silently lose the message. RabbitMQ will redeliver it.

> [!danger] What it doesn't guarantee
> Redelivery does not mean the business operation is safe to run twice. Idempotency is still required.

---

> [!tip] Interview framing
> "If a RabbitMQ consumer crashes before ACK, the broker redelivers the message. That protects against loss but creates duplicate risk, so I assume at-least-once delivery and make the consumer idempotent."
