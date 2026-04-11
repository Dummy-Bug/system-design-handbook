
> [!info] RabbitMQ's practical delivery model is at-least-once. Messages are protected from silent loss through acknowledgments and redelivery, but duplicate processing is still possible. Idempotent consumers are what make the business result safe.

---

## Why RabbitMQ is not exactly-once

Take a payment-like flow:

```text
1. RabbitMQ delivers message
2. Consumer charges customer
3. Consumer crashes before ACK
4. RabbitMQ redelivers
5. Another consumer may charge again
```

The broker and the business side effect live in different systems. RabbitMQ cannot make them one atomic operation.

That is why true exactly-once is not really a broker guarantee here.

---

## The practical model: at-least-once

RabbitMQ chooses this trade-off:

```text
better to redeliver than to lose the message
```

So the safe assumption is:

```text
message may be delivered again
```

That is the correct mental model for interview answers and production design.

---

## Idempotency is the real fix

If duplicate delivery is possible, the consumer must make repeated execution harmless.

For an ad-click billing worker:

```text
if click_id already processed:
    skip billing update
    ACK
else:
    apply billing update
    record click_id as processed
    ACK
```

This turns broker-level at-least-once into effectively-once business behavior.

---

## End-to-end safety model

```text
Producer side  -> publisher confirms
Broker side    -> durable queue + persistent message
Consumer side  -> ACK after processing + idempotency
Overall        -> at-least-once delivery with duplicate-safe business logic
```

That is the real production answer.

---

> [!important] What it guarantees
> RabbitMQ can reliably redeliver unfinished work and reduce message loss.

> [!danger] What it doesn't guarantee
> RabbitMQ does not guarantee that a business operation happened only once. That must be enforced in the application.

---

> [!tip] Interview framing
> "I assume RabbitMQ gives me at-least-once delivery. I use idempotency keys or processed-message tracking so duplicate delivery does not produce duplicate business effects."
