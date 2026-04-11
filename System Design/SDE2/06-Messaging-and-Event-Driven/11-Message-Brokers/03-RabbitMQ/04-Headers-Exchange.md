
> [!info] A headers exchange ignores the routing key entirely. Instead, the producer attaches **key-value pairs** in the message headers, and queues bind with header conditions. RabbitMQ routes based on whether the message headers match those conditions — either ALL must match (`x-match: all`) or ANY one must match (`x-match: any`).

---

## The problem with one-string routing keys

Topic exchange routes on a single string — `order.placed.india`. This works until your routing dimensions grow. Add a new dimension like `priority` and your routing key becomes `order.placed.india.high`. Now every existing binding that matched `order.placed.*` breaks — it expected three segments, now there are four.

Headers exchange solves this by replacing the single routing key string with named attributes:

```
Instead of:  routing_key = "order.placed.india.high"

Use:         headers = {
               type:     "order.placed",
               region:   "india",
               priority: "high"
             }
```

Add a new dimension anytime. Existing queue bindings that don't reference that dimension keep working unchanged.

---

## x-match — AND vs OR

Every queue binding in a headers exchange carries an `x-match` rule:

```
x-match: all  →  message must satisfy ALL header conditions in the binding  (AND)

x-match: any  →  message must satisfy ANY ONE condition in the binding      (OR)
```

---

## The same three problems, solved with headers

### Problem 1 — Direct exchange scenario (exact targeted routing)

Original: billing queue should only get `payment.failed` and `payment.success`. Nothing else.

With headers:

```
Producer publishes:
  headers: {
    type:    "payment.failed",
    service: "checkout"
  }
```

```
billing.queue (binding 1)
  x-match: all
  conditions: type="payment.failed"
  result:     ✓  type matches

billing.queue (binding 2)
  x-match: all
  conditions: type="payment.success"
  result:     ✗  type="payment.failed" ≠ "payment.success"

inventory.queue
  x-match: all
  conditions: type="order.placed"
  result:     ✗  type="payment.failed" ≠ "order.placed"
```

Same targeted delivery as direct exchange — but now you can add a `service` dimension without restructuring anything.

---

### Problem 2 — Fanout exchange scenario (broadcast to all)

Original: a `system.alerts` event must reach ops-pagerduty, ops-slack, and ops-email — every queue, no exceptions.

With headers:

```
Producer publishes:
  headers: {
    category: "alert",
    severity: "critical"
  }
```

```
ops-pagerduty.queue
  x-match: all
  conditions: category="alert" AND severity="critical"
  result:     ✓  both match

ops-slack.queue
  x-match: all
  conditions: category="alert"
  result:     ✓  category matches

ops-email.queue
  x-match: all
  conditions: category="alert"
  result:     ✓  category matches
```

All three get it. But pagerduty only wakes up when `severity="critical"` — change severity to `"info"` and pagerduty is skipped while slack and email still receive it. Fanout exchange cannot do this — it's all or nothing. Headers exchange gives you broadcast with optional filtering layered on top.

---

### Problem 3 — Topic exchange scenario (multi-dimensional routing)

Original:
`order.placed.india` routed to global inventory (`order.#`), 
india-ops (`#.india`), recommendations (`order.placed.*`).

With headers:

```
Producer publishes:
  headers: {
    type:   "order.placed",
    region: "india"
  }
```

```
inventory.queue
  x-match: any
  conditions: type="order.placed" OR type="order.cancelled"
  result:     ✓  type="order.placed" matches

india-ops.queue
  x-match: all
  conditions: region="india"
  result:     ✓  region="india" matches

recommendations.queue
  x-match: all
  conditions: type="order.placed"
  result:     ✓  type="order.placed" matches

billing.queue
  x-match: any
  conditions: type="payment.failed" OR type="order.placed"
  result:     ✓  type="order.placed" matches — type="payment.refund" would be skipped
```

Now add a new `priority: "express"` dimension tomorrow:

```
express-ops.queue → x-match: all, 
priority: "express", region: "india"
```

Zero changes to existing bindings. Topic exchange would require restructuring the routing key string from `order.placed.india` to `order.placed.india.express`.

---

## When to use headers exchange

```
Direct exchange   →  small fixed set of exact event types, simple and readable
Fanout exchange   →  truly broadcast, every queue gets every message, no conditions
Topic exchange    →  structured multi-dimensional routing key, dimensions are stable
Headers exchange  →  dimensions grow over time, AND/OR logic across multiple attributes
```

> [!important] Headers exchange is the most flexible but also the hardest to reason about at a glance. A routing key like `order.placed.india` is self-documenting. A set of headers spread across producer and binding config is not. Use it when topic exchange genuinely can't express the routing logic — not as a default.

> [!tip] **Interview framing:** "I'd reach for headers exchange when my routing dimensions are unstable — new attributes get added over time and I don't want to restructure routing keys every time. It also lets me express AND/OR logic across multiple attributes, which topic exchange can't do. For stable dimensions, topic exchange is simpler and more readable."
