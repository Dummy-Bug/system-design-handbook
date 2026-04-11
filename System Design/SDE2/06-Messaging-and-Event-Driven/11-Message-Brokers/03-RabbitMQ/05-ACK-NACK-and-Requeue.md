# ACK, NACK, and Requeue

> [!info] In RabbitMQ, a message is not removed from the queue when it is delivered to a consumer. It is removed only after the consumer explicitly acknowledges it. If processing fails, the consumer can reject it and choose whether it should be retried.

---

## Why delivery is not enough

Suppose RabbitMQ hands a billing message to a worker:

```text
{ click_id: 123, campaign_id: 88, task: "update_billing" }
```

If RabbitMQ deleted the message immediately on delivery, then any consumer crash during processing would lose the work forever.

That is why delivery and deletion are two separate steps.

---

## ACK

`ACK` means: processing succeeded, the broker can safely delete the message.

```text
RabbitMQ -> deliver message
Consumer -> process successfully
Consumer -> ACK
RabbitMQ -> delete message
```

This is the happy path.

---

## NACK without requeue

`NACK` with `requeue=false` means: processing failed, and this message should not be placed back on the same queue for immediate retry.

```text
RabbitMQ -> deliver message
Consumer -> processing fails
Consumer -> NACK(requeue=false)
RabbitMQ -> discard or dead-letter message
```

This is useful for permanent failures such as invalid payloads or unsupported schema versions.

---

## NACK with requeue

`NACK` with `requeue=true` means: processing failed, but this looks temporary, so the message should go back to the queue.

```text
RabbitMQ -> deliver message
Consumer -> downstream DB times out
Consumer -> NACK(requeue=true)
RabbitMQ -> put message back on queue
```

This is useful for transient failures.

---

## The real trade-off

These three outcomes are how the consumer tells RabbitMQ what happened:

```text
ACK                 -> done
NACK(requeue=true)  -> retry later
NACK(requeue=false) -> stop retrying here
```

That makes consumer logic responsible for deciding whether the failure is temporary or permanent.

---

> [!important] What it guarantees
> RabbitMQ guarantees that a message is not considered complete until the consumer explicitly acknowledges it.

> [!danger] What it doesn't guarantee
> ACK/NACK does not by itself prevent duplicates. If the consumer crashes after doing the work but before ACK, the message may be redelivered.

---

> [!tip] Interview framing
> "In RabbitMQ, delivery and deletion are separate. The consumer ACKs on success, NACKs with requeue for transient failures, and NACKs without requeue for poison messages that should go to DLQ or be dropped."
