
> [!info] Exchange type controls how the exchange makes its routing decision. A **direct exchange** routes by exact routing key match — only the queue whose binding key matches exactly gets the message. A **fanout exchange** ignores the routing key entirely and copies the message to every bound queue.

---

## Direct exchange — exact match routing

A direct exchange is the simplest routing model. When a message arrives, the exchange looks at its routing key and finds all bindings where the binding key is an **exact match**. No wildcards, no patterns — character for character.

```
Producer publishes:
  routing_key: "payment.failed"

Bindings:
  "payment.failed"  →  billing.queue
  "payment.success" →  billing.queue
  "order.placed"    →  inventory.queue

Result:
  billing.queue   ✓  (exact match)
  inventory.queue ✗  (no match)
```

This is useful when you have distinct event types that should go to specific queues. A payment service publishing `payment.failed` and `payment.success` — each goes to billing, but `order.placed` never reaches billing at all.

The direct exchange is precise and intentional. No message ends up somewhere it shouldn't.

---

## Fanout exchange — broadcast to everyone

A fanout exchange doesn't look at the routing key at all. The moment a message arrives, it copies it to **every queue that is bound to the exchange**, regardless of what the routing key says.

```
Producer publishes to fanout exchange "system.alerts":
  routing_key: "disk.full"  ← ignored completely

Bound queues:
  ops-pagerduty.queue
  ops-slack.queue
  ops-email.queue

Result:
  ops-pagerduty.queue ✓
  ops-slack.queue     ✓
  ops-email.queue     ✓

All three get a copy. Always. No matter what routing key the producer used.
```

Use fanout when every bound queue must react to every message without exception.

---

## When to use which

```
Direct exchange:
  → you have distinct event types
  → each type should reach specific queue(s)
  → some queues should NOT see certain events
  → example: payment.failed → billing only, not inventory

Fanout exchange:
  → one event, every downstream system reacts
  → routing key is irrelevant — all queues get the same copy
  → example: order placed → inventory + email + recommendations all need it
```

The key question is: **does every bound queue need every message?**

Yes → fanout. No → direct (or topic, which is direct with wildcards — covered next).

---

> [!important] Fanout ignores routing keys completely. If you publish to a fanout exchange with routing_key "order.placed" and routing_key "order.cancelled" — every bound queue gets both, every time. If some queues should skip certain events, fanout is the wrong exchange type.

> [!tip] **Interview framing:** "I'd use a direct exchange when I need exact targeted routing — payment events go to billing, order events go to inventory, nothing crosses. I'd use a fanout exchange when every downstream system needs the same event — it's the RabbitMQ equivalent of SNS, publish once and all bound queues get a copy."
