# Durable Queues, Persistent Messages, and Publisher Confirms

> [!info] In RabbitMQ, queue durability, message persistence, and publisher confirms solve three different failure risks. Durable queues protect the queue definition. Persistent messages protect queued contents. Publisher confirms protect the producer from assuming a message was accepted when it was not.

---

## Why one setting is not enough

Suppose an ad-click producer publishes a billing message and RabbitMQ crashes.

There are three separate questions:

```text
1. Does the queue still exist after restart?
2. Does the message still exist after restart?
3. Does the producer know whether RabbitMQ really accepted the message?
```

These are different problems, so RabbitMQ uses different mechanisms.

---

## Durable queue

A durable queue survives broker restart as a queue definition.

```text
RabbitMQ restarts
-> queue metadata still exists
```

If the queue is not durable, the queue itself may disappear.

But durable queue alone does not guarantee the messages in it survived.

---

## Persistent message

A persistent message is written so it can survive broker restart.

```text
Producer publishes persistent message
RabbitMQ stores it durably
Broker restarts
-> message can still be present
```

But persistent message alone is not enough if the queue itself disappears.

That is why durable queue and persistent message are usually used together.

---

## Publisher confirms

Now consider producer-side uncertainty:

```text
Producer sends message
RabbitMQ receives it
Broker crashes before the producer gets reliable confirmation
Producer assumes success
Message is actually lost
```

Publisher confirms solve this by making the producer wait for broker acknowledgment that the message was accepted.

```text
Producer publishes
-> waits for publisher confirm
-> only then treats message as safely accepted
```

Without publisher confirms, the producer can believe a write succeeded when it did not.

---

## The complete model

```text
Durable queue      -> queue survives restart
Persistent message -> message survives restart
Publisher confirm  -> producer knows broker accepted the write
```

You usually need all three for serious reliability.

---

> [!important] What it guarantees
> These mechanisms together protect queue existence, message durability, and producer-side certainty about successful publish.

> [!danger] What it doesn't guarantee
> Even with all three, RabbitMQ still does not guarantee exactly-once business processing. Consumer crashes after side effects can still create duplicates.

---

> [!tip] Interview framing
> "For reliable RabbitMQ publishing, I use durable queues, persistent messages, and publisher confirms. They solve different failure modes: queue survival, message survival, and producer certainty that the broker accepted the write."
