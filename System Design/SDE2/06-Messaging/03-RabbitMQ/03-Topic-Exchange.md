
> [!info] A topic exchange routes messages by **pattern matching** on the routing key. Unlike a direct exchange which requires an exact key match, a topic exchange lets queues subscribe to groups of related messages using wildcard patterns.

---

## Why direct exchange isn't enough

A direct exchange works fine when you have a small, fixed set of event types:

```
"order.placed"    →  inventory.queue
"payment.failed"  →  billing.queue
```

But real systems have events that span multiple dimensions — type, region, severity, source. And different consumers care about different slices of those dimensions.

Imagine your e-commerce platform grows internationally. Order events now look like:

```
order.placed.india
order.placed.us
order.cancelled.india
order.cancelled.us
payment.failed.india
payment.failed.us
```

Now you have:
- A global inventory team that needs ALL order events regardless of region
- A regional India ops team that needs ALL India events regardless of type
- A billing team that needs only payment events globally

With a direct exchange you'd need exact bindings for every combination — `order.placed.india`, `order.placed.us`, `order.cancelled.india`... and every time you add a new region, you add new bindings everywhere. It falls apart fast.

Topic exchange solves this with wildcards.

---

## Wildcards — * and #

Binding patterns in a topic exchange can use two wildcards:

```
*  →  matches exactly one word (one dot-separated segment)
#  →  matches zero or more words
```

```
"order.*"    matches:  order.placed       ✓
                       order.cancelled    ✓
                       order.placed.india ✗  ← two words after dot, * only covers one

"order.#"    matches:  order.placed       ✓
                       order.cancelled    ✓
                       order.placed.india ✓  ← # covers everything after
                       order.placed.india.express ✓
```

`*` is precise — exactly one segment. `#` is greedy — everything from that point on.

---

## How it routes

Producer publishes with routing key `order.placed.india`:

```
Bindings:
  "order.#"          →  inventory.queue        ← global inventory
  "#.india"          →  india-ops.queue        ← everything India
  "payment.#"        →  billing.queue          ← payment events only
  "order.placed.*"   →  recommendations.queue  ← placed events only, any region

Matching:
  "order.#"        → order.placed.india  ✓  → inventory.queue gets it
  "#.india"        → order.placed.india  ✓  → india-ops.queue gets it
  "payment.#"      → order.placed.india  ✗  → billing.queue skipped
  "order.placed.*" → order.placed.india  ✓  → recommendations.queue gets it
```

One message, three queues receive it, one skips it — all based on pattern matching, zero producer changes.

Now a new region launches — `order.placed.eu`. No binding changes needed for inventory (matches `order.#`) or recommendations (matches `order.placed.*`). You only add a new binding if you want a new EU-specific queue.

---

## When to use topic exchange

Topic exchange is the right choice when your routing key naturally has multiple dimensions:

```
event_type.region         →  order.placed.india
severity.service          →  error.payments
event_type.user_tier      →  order.placed.premium
```

Different consumers subscribe to different slices of those dimensions without the producer knowing anything about who is listening.

```
Direct exchange  →  small fixed set of exact event types, no dimensions
Fanout exchange  →  everyone gets everything, no routing needed
Topic exchange   →  structured routing keys with multiple dimensions, consumers subscribe to slices
```

> [!important] Routing key design matters a lot with topic exchange. Once producers start publishing `order.placed.india`, you can't easily change that structure without updating all bindings. Design your routing key schema upfront — treat it like an API contract between producers and consumers.

> [!tip] **Interview framing:** "I'd use a topic exchange when routing has multiple natural dimensions — like event type and region. The producer emits a structured routing key like `order.placed.india`. The global inventory team binds to `order.#`, the India ops team binds to `#.india`, billing binds to `payment.#`. Each team subscribes to exactly the slice they care about, and adding a new region requires zero producer changes."
