# Wildcards and Full Flow

> [!info] In a RabbitMQ topic exchange, the routing key is split into dot-separated segments. `*` matches exactly one segment. `#` matches zero or more segments.

---

## The two wildcard rules

Take this routing key:

```text
click.us.mobile
```

Now look at these bindings:

```text
click.us.*      -> matches
click.*.mobile  -> matches
click.#         -> matches
click.eu.*      -> does not match
billing.#       -> does not match
```

The rules are simple:

- `*` means exactly one word
- `#` means any remaining words, including none

So:

```text
click.us.*      matches click.us.mobile
click.*.mobile  matches click.us.mobile
click.#         matches click.us.mobile
click.us        does not match click.us.mobile
```

---

## Why this matters

Pattern routing lets one producer publish a single message while different consumers subscribe to different slices of traffic.

In an ad-click system:

- US analytics team wants all US clicks
- mobile team wants all mobile clicks
- global reporting team wants every click

The producer should not know about all these consumers. It should just publish a structured routing key.

---

## Full flow from producer to consumer

Start with the producer:

```text
Producer publishes:
exchange = click.events
routing_key = click.us.mobile
body = { click_id: 123, ad_id: 88 }
```

RabbitMQ receives the message at the topic exchange and checks every binding attached to that exchange.

```text
Bindings:
click.us.*      -> us-clicks.queue
click.*.mobile  -> mobile-clicks.queue
click.#         -> all-clicks.queue
click.eu.*      -> eu-clicks.queue
```

Matching result:

```text
click.us.*      -> match
click.*.mobile  -> match
click.#         -> match
click.eu.*      -> no match
```

RabbitMQ then copies the message into each matching queue:

```text
Producer
-> Topic Exchange (click.events)
-> us-clicks.queue
-> mobile-clicks.queue
-> all-clicks.queue
```

Finally, consumers pull from their own queues:

```text
US Click Worker         reads us-clicks.queue
Mobile Analytics Worker reads mobile-clicks.queue
Global Reporting Worker reads all-clicks.queue
```

The exchange never talks to consumers directly. Its job is only routing. Consumers always read from queues.

---

> [!important] What it guarantees
> Topic exchange plus wildcard bindings guarantees that any queue with a matching binding receives a copy of the message.

> [!danger] What it doesn't guarantee
> Wildcard routing does not fix poor routing-key design. If teams use inconsistent key formats, bindings become fragile and hard to maintain.

---

> [!tip] Interview framing
> "In a topic exchange, the producer publishes one structured routing key like `click.us.mobile`. RabbitMQ matches that key against bindings where `*` means one segment and `#` means zero or more segments, then copies the message into every matching queue. Consumers only read from queues, never from the exchange."
