
> [!info] RabbitMQ has three separate mechanisms for reliability — and they protect three different things:
> - **Durable queue** — queue definition survives broker restart
> - **Persistent message** — message contents survive broker restart
> - **Publisher confirms** — producer knows the broker actually received the message

---

## Why one setting is not enough

Your order service publishes an `order.placed` event. The RabbitMQ broker crashes two seconds later.

Three separate questions:

```
1. Does the queue still exist after restart?       → durable queue
   
2. Do the messages in it still exist after restart? → persistent message
   
3. Did the broker even receive the message before crashing? → publisher confirms
```

Each is a separate failure mode. Each needs its own fix.

---

## Durable queue — queue survives restart

By default, a queue is transient — it exists in memory only. Broker restart wipes it.

```java
// Transient queue — disappears on restart
channel.queueDeclare("order.queue", false, false, false, null);
//                                   ↑ durable = false

// Durable queue — survives restart
channel.queueDeclare("order.queue", true, false, false, null);
//                                   ↑ durable = true
```

With `durable = true`, RabbitMQ writes the queue definition to disk. After restart, the queue reappears automatically — consumers can reconnect and keep consuming.

Without it:

```
RabbitMQ restarts
→ order.queue is gone
→ inventory workers reconnect, queue no longer exists
→ new order events have nowhere to go — silently dropped
```

> [!important] Durable queue only saves the queue definition — not the messages inside it. A durable queue can restart empty if the messages weren't also made persistent.

---

## Persistent message — contents survive restart

Even with a durable queue, messages are stored in memory by default. Broker crash → messages lost.

```java
// Default (non-persistent) — stored in memory only
channel.basicPublish(
    "order.events",
    "order.placed",
    null,                                           // no properties
    messageBody
);

// Persistent — written to disk
channel.basicPublish(
    "order.events",
    "order.placed",
    MessageProperties.PERSISTENT_TEXT_PLAIN,        // deliveryMode = 2
    messageBody
);
```

`PERSISTENT_TEXT_PLAIN` sets `deliveryMode = 2` on the message. RabbitMQ writes it to disk before confirming receipt.

```
Without persistent:
  order_123 queued in memory
  RabbitMQ crashes
  → order_123 gone, never processed

With persistent + durable queue:
  order_123 written to disk
  RabbitMQ restarts
  → order_123 still in queue, inventory worker picks it up
```

> [!important] Persistent messages have a performance cost — every publish involves a disk write. For high-throughput, low-value events (metrics, logs) this may not be worth it. For orders and payments, it is.

---

## Publisher confirms — producer knows the broker accepted it

There's a timing gap between the producer sending a message and the broker safely storing it. If the broker crashes in that window, the producer has no idea the message was lost.

```
Producer publishes order_123
→ message in broker's network buffer (not yet on disk)
→ broker crashes
→ producer assumes success (no error was returned)
→ order_123 is gone, never processed, producer never retries
```

Publisher confirms close this gap. **The broker sends an ACK back to the producer only after the message is safely written** (to disk if persistent, to queue if not).

```java
// Enable publisher confirms on the channel
channel.confirmSelect();

// Publish
channel.basicPublish(
    "order.events",
    "order.placed",
    MessageProperties.PERSISTENT_TEXT_PLAIN,
    messageBody
);

// Wait for broker confirmation
channel.waitForConfirmsOrDie(5000);  // throws if not confirmed within 5s
```

`waitForConfirmsOrDie` blocks until the broker ACKs. If it times out or gets a NACK, it throws — and you know to retry.

For higher throughput, use async confirms instead:

```java
channel.addConfirmListener(
    (sequenceNumber, multiple) -> {
        // broker ACKed — message safely stored
    },
    (sequenceNumber, multiple) -> {
        // broker NACKed — retry this message
    }
);
```

---

## The complete picture

```
Failure: broker restarts
Fix:     durable queue + persistent message

Failure: broker crashes before receiving the message
Fix:     publisher confirms

Failure: consumer crashes after processing but before ACK
Fix:     manual ACK (covered in file 05)
```

You need all three for end-to-end reliability:

```java
// Durable queue
channel.queueDeclare("order.queue", true, false, false, null);

// Publisher confirms
channel.confirmSelect();

// Persistent publish
channel.basicPublish(
    "order.events", "order.placed",
    MessageProperties.PERSISTENT_TEXT_PLAIN,
    messageBody
);
channel.waitForConfirmsOrDie(5000);
```

---

> [!danger] Persistent messages + publisher confirms protect the publish path. They say nothing about what happens after the consumer receives the message. Consumer crashes after processing but before ACK still causes redelivery and duplicates — that's an idempotency problem, not a durability problem.

> [!tip] **Interview framing:** "For reliable RabbitMQ publishing I use three things together: durable queues so the queue survives broker restart, persistent messages so the contents survive restart, and publisher confirms so the producer knows the broker actually received and stored the message. Each protects a different failure window."
