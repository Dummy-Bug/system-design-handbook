
> [!info] In RabbitMQ, immediate requeue can create hot retry loops. A better retry design uses dedicated retry queues with TTL and dead-letter routing, and sends permanently failing messages to a DLQ.

---

## Why blind requeue is dangerous

Suppose this message is permanently bad:

```text
{ click_id: 123, ad_id: null }
```

If the consumer keeps doing this:

```text
NACK(requeue=true)
```

then the same poison message comes back immediately:

```text
Worker A fails -> requeue
Worker B fails -> requeue
Worker C fails -> requeue
```

The system burns CPU but makes no progress.

---

## Temporary failure vs permanent failure

Not every failure should be treated the same way.

Transient failure:

- downstream database timeout
- temporary `503`
- network hiccup
- consumer restart mid-processing

Permanent failure:

- invalid payload
- unsupported schema
- missing required business field

Transient failures deserve retry. Permanent failures should be isolated.

---

## Better retry pattern

Instead of immediate requeue, send the message to a retry queue with TTL.

```text
main queue
-> consumer fails
-> publish/send to retry queue
-> retry queue waits 30s
-> TTL expires
-> dead-letter routing sends message back to main queue
```

This gives downstream systems time to recover and avoids instant retry storms.

---

## DLQ

After a bounded number of attempts, the message should stop retrying and move to DLQ.

```text
main queue
-> retry queue
-> main queue
-> retry queue
-> still failing after max attempts
-> DLQ
```

DLQ is where operators inspect poison messages, fix bugs, and decide whether replay is safe.

---

> [!important] What it guarantees
> Retry queues smooth temporary failures, and DLQ prevents poison messages from clogging the main flow forever.

> [!danger] What it doesn't guarantee
> DLQ does not repair bad data. Without operational handling, the failure is only moved, not solved.

---

> [!tip] Interview framing
> "I avoid `NACK(requeue=true)` loops for every failure. For transient issues I use retry queues with TTL and dead-letter routing back to the main queue. After a bounded number of attempts, I send the message to DLQ."
