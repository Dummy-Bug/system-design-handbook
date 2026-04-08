# Idempotency and Dead Letter Queue (DLQ)

> [!info] SQS delivers messages at least once, so duplicates are possible. Consumers must be idempotent. Messages that keep failing should be moved to a Dead Letter Queue for inspection.

---

## Why idempotency is mandatory

Consider ad-click billing:

```
1. Worker processes click_id=abc123
2. Billing update succeeds
3. Worker crashes before DeleteMessage reaches SQS
4. SQS redelivers abc123
```

If billing logic is not idempotent, advertiser may be charged twice for one click.

---

## Idempotent consumer pattern

Use a stable business key like `click_id`.

```
if click_id already processed:
    skip business update
    delete message
else:
    apply billing update
    mark click_id processed
    delete message
```

This turns duplicate delivery into harmless reprocessing.

At large scale (`100M+` clicks/day), even a tiny duplicate rate creates large billing inaccuracies if idempotency is missing.

---

## Poison messages and DLQ

Some messages fail every time:

- malformed payload
- missing required fields
- unknown campaign/ad IDs
- incompatible schema/version

Retrying these forever wastes compute and blocks queue health.

SQS DLQ pattern:

```
main queue -> process fail -> retry
after maxReceiveCount reached
-> move message to DLQ
```

Main queue stays healthy, while bad messages are isolated for debugging.

---

## Operating model for DLQ

DLQ is not trash storage. It is an investigation queue.

Typical handling:

1. Inspect failure reason
2. Fix parser/schema/business bug
3. Decide whether to replay messages safely

---

> [!important] What it guarantees
> Idempotency guarantees repeated delivery does not create repeated business effects. DLQ guarantees repeatedly failing messages are isolated from normal traffic.

> [!danger] What it doesn't guarantee
> DLQ does not automatically fix bad messages. Without runbooks and replay policy, failures just move from one queue to another.

---

> [!tip] Interview framing
> "For SQS, I assume at-least-once delivery and design consumers idempotent using click_id as the dedup key. I also configure DLQ with maxReceiveCount so poison messages stop cycling and can be triaged separately."

