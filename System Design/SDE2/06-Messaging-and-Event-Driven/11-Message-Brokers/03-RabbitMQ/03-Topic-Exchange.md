# Topic Exchange

> [!info] A topic exchange routes messages by pattern matching on the routing key. It is more flexible than a direct exchange because queues can subscribe to groups of related messages instead of one exact key.

---

## Why direct exchange is not enough

A direct exchange works well when routing decisions are simple:

```text
"billing" -> billing.queue
"fraud" -> fraud.queue
```

But real systems often need more expressive routing.

Take an ad-click platform operating across regions and devices. Messages may look like this:

```text
click.us.mobile
click.us.desktop
click.eu.mobile
click.in.mobile
```

Now imagine three different consumers:

- one team wants all US clicks
- one team wants all mobile clicks
- one team wants every click event globally

With a direct exchange, producers would need to know every exact combination in advance. That becomes rigid fast.

---

## How topic exchange works

A topic exchange matches routing keys against binding patterns.

Producer:

```text
routing_key = "click.us.mobile"
```

Bindings:

```text
click.us.*      -> us-clicks.queue
click.*.mobile  -> mobile-clicks.queue
click.#         -> all-clicks.queue
billing.#       -> billing.queue
```

Result:

```text
us-clicks.queue      gets the message
mobile-clicks.queue  gets the message
all-clicks.queue     gets the message
billing.queue        does not get the message
```

One published message can match multiple patterns, so multiple queues can receive copies.

---

## What makes it useful

Topic exchange is useful when routing dimensions naturally form categories:

- event type
- region
- device type
- tenant
- status

Instead of hardcoding every route in producer logic, the producer emits a structured routing key and RabbitMQ handles the routing.

---

> [!important] What it guarantees
> A topic exchange guarantees pattern-based routing based on binding rules. If a routing key matches multiple bindings, each matching queue gets a copy.

> [!danger] What it doesn't guarantee
> Topic exchange does not guarantee that routing keys are well-designed. If naming is inconsistent, bindings become confusing and routing logic gets hard to reason about.

---

> [!tip] Interview framing
> "I'd use a topic exchange when routing depends on multiple dimensions like event type, region, and device. That lets producers emit one structured routing key such as `click.us.mobile`, while consumers subscribe with patterns like `click.us.*` or `click.#`."
