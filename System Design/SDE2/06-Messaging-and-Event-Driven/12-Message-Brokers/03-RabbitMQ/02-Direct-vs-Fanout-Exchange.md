# Direct vs Fanout Exchange

> [!info] In RabbitMQ, exchange type controls routing behavior. A direct exchange routes by exact routing-key match. A fanout exchange broadcasts to all bound queues.

---

## Why exchange type matters

Not every event needs the same delivery pattern.

- Sometimes only one workflow should receive a message.
- Sometimes every downstream system should receive a copy.

Exchange type encodes that choice.

---

## Direct exchange (selective routing)

A direct exchange uses exact routing-key match with bindings.

```text
Producer publishes:
routing_key = "billing"

Bindings:
"billing" -> billing.queue
"fraud"   -> fraud.queue

Result:
message goes only to billing.queue
```

Use this when you want targeted delivery.

---

## Fanout exchange (broadcast routing)

A fanout exchange ignores routing key and copies each message to all bound queues.

```text
Producer publishes message to fanout exchange

Bound queues:
- billing.queue
- fraud.queue
- analytics.queue

Result:
all bound queues receive a copy
```

Use this when every subscriber should react to the same event.

---

## Ad-click interpretation

If an event should trigger all downstream flows (billing + fraud + analytics), fanout gives broadcast behavior.  
If only one specific flow should receive a message based on type/key, direct gives selective delivery.

---

> [!important] What it guarantees
> Direct gives deterministic key-based routing. Fanout gives deterministic broadcast to all bound queues.

> [!danger] What it doesn't guarantee
> Exchange type does not remove the need for retries, dead-letter handling, and idempotent consumers.

---

> [!tip] Interview framing
> "In RabbitMQ, direct exchange is for exact-key targeted routing, while fanout is for broadcast. I choose based on whether one queue should process the event or all subscribed queues should get a copy."

