# Dead Letter Queue (DLQ)

> [!info] A Dead Letter Queue is where messages go when they have failed too many times and the queue gives up retrying. It's a safe holding area for bad messages — they don't block the main queue, and engineers can inspect them manually.

---

## The problem

At-least-once delivery means the queue retries until it gets an ACK. But what if the consumer keeps crashing on the same message every single time? The queue would retry forever — spamming the consumer, wasting resources, and never making progress.

```
Message delivered → consumer crashes → redelivered
               → consumer crashes → redelivered
               → consumer crashes → redelivered
               ... forever
```

You need a way to say: "after N failures, stop retrying and put this message somewhere safe for investigation."

---

## How it works

The **queue** tracks the failure count — not the consumer. The consumer doesn't report failure. It just never sends an ACK. Silence = failure from the queue's perspective.

Every time the visibility timeout expires without an ACK, the queue increments a retry counter on that message.

```
Message picked up → no ACK within 30s → attempt_count: 1
Redelivered      → no ACK within 30s → attempt_count: 2
Redelivered      → no ACK within 30s → attempt_count: 3
Redelivered      → no ACK within 30s → attempt_count: 4
Redelivered      → no ACK within 30s → attempt_count: 5
attempt_count hits 5 → queue automatically moves message to DLQ
```

The main queue is now clean. The bad message isn't blocking or retrying anymore. An engineer can inspect it in the DLQ at their own pace.

---

## DLQ in a Pub/Sub setup

In pub/sub, each subscriber has its own internal queue — so each internal queue tracks its own failure count and has its own DLQ independently.

```
photo_posted_123 copied to:
→ Notification Queue  → fails 5 times → moved to Notification DLQ
→ Feed Queue          → processed fine, ACKed ✓
→ Moderation Queue    → fails 5 times → moved to Moderation DLQ
```

Each subscriber fails and recovers independently. Feed Service being fine doesn't help or hurt Notification Service's DLQ.

---

## Why does a message keep failing?

Two most common reasons:

**1. Poison pill message** — the message itself is malformed or corrupt. Bad JSON, missing required field, unexpected data type. The consumer crashes every time it tries to parse it. No amount of retrying will fix it — the data is just wrong.

**2. Consumer bug** — a code bug that crashes on one specific input. Every other message processes fine, but this particular message hits an edge case in the consumer's code every single time.

Both can only be fixed by a human — either fixing the bad data and replaying the message, or fixing the bug, deploying a fix, and then replaying the DLQ messages.

> [!important] The DLQ's job is not to retry — it's to **isolate** bad messages so they don't poison the main queue, and give engineers a safe place to inspect them without time pressure.

> [!tip] **Interview framing:** "I'd configure a DLQ with a max retry count of 5. Any message that fails repeatedly gets moved there automatically. We'd have an alert on DLQ depth — if messages start piling up, an engineer gets paged to investigate. This keeps the main queue healthy and gives us visibility into systemic failures."
