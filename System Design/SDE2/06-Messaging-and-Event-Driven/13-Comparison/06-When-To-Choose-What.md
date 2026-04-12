
> [!info] The decision between SQS, RabbitMQ, and Kafka comes down to one question asked before any feature comparison:
>  what is the nature of the thing being sent? 
>  - Is it a job to be done once? 
>  - An event to be broadcast to specific services?
>  - A fact to be kept in history and replayed? The answer determines the broker. Everything else is tuning.

---

## Start with the shape of the problem, not the feature list

Every system design resource will give you a feature comparison table. Kafka has partitions. RabbitMQ has exchanges. SQS has visibility timeout. But picking a broker by features leads to over-engineering — you end up adding Kafka to a system that just needs email workers, or using SQS for a pipeline that needs event replay.

The right question to start with is not "what features do I need?" — it's "what is the nature of the thing I'm sending?"

---

## Job vs Event — the most important distinction

Before anything else, you need to know whether you're dealing with a **job** or an **event**. These are fundamentally different things, and conflating them leads to the wrong broker every time.

A **job** is a command. It says: *"Someone needs to do this work."*

```
User uploads a video → "resize this video to 720p"
User places an order → "send a confirmation email to user@gmail.com"
```

A job belongs to one worker. Once that worker does the work, the message is useless — delete it. Nobody else needs to know that a video was resized. It was a unit of work, assigned, executed, gone.

An **event** is a fact. It says: *"This thing happened."*

```
User clicked Nike's ad → "nike_ad_click at 14:03:22"
```

That fact doesn't belong to anyone. Multiple completely independent systems care about it for completely different reasons:

```
Billing     → charge Nike $1.00
Fraud       → check if this was a bot
Analytics   → update click-through rate dashboard
ML model    → retrain ad ranking with new signal
```

Nobody "owns" this fact. It happened, it's recorded, and any system — including ones that don't exist yet — should be able to read it.

The clearest test is: **after one system reads it, should it be deleted?**

```
Job:   "resize this video"
         → video worker reads it
         → video resized
         → delete ✓ — no one else needs this

Event: "Nike ad was clicked"
         → billing reads it    → still there
         → fraud reads it      → still there
         → analytics reads it  → still there
         → delete? Never — other systems still need it
                               — replay is the whole point
```

Jobs are instructions to one consumer. Events are facts broadcast to the world. This single distinction determines your broker.

---

## The decision ladder

```
1. Is this a job? (work to be done once, then gone)
   → Task queue → SQS or RabbitMQ

2. Does the job need routing? (different consumers get different messages)
   → Routing-first broker → RabbitMQ

3. Is this an event? (a fact that happened, multiple systems need to know)
   → Event stream → Kafka

4. Do I need replay? (new consumers, historical analysis, failure recovery)
   → Only Kafka has this
```

---

## Choose SQS when

You need to distribute background jobs to workers, you're already on AWS, and you don't want to run any broker infrastructure.

SQS is the right choice when the problem is this simple: "the API is too slow, let's move this work to background workers." Image resizing, email sending, payment processing, report generation — anything where the job should happen exactly once and you don't need to know what happened last Tuesday.

```
Use cases:
→ Async offloading: "generate this PDF in the background, don't block the user"
→ Rate limiting: "send max 100 emails/sec, queue the rest"
→ Retry handling: "if payment processing fails, retry up to 5 times"
→ Any AWS stack where you want zero infrastructure overhead
```

The deal-breaker: if you need ordering across messages from multiple producers, or routing to different consumer pools, or replay, SQS alone won't do it.

---

## Choose RabbitMQ when

You need flexible routing — the same event should reach different consumers based on its content — and queue-based task semantics still apply after routing.

RabbitMQ sits in the sweet spot where you need more than SQS (routing, per-queue config, priority) but don't need Kafka's retention and replay.

```
Use cases:
→ One event, multiple worker pools: "ad click should go to billing AND fraud AND analytics"
→ Event type routing: "user.signup goes to welcome-email-queue, user.signup + enterprise tag goes to enterprise-onboarding-queue"
→ Priority processing: "critical alerts processed before routine notifications"
→ Per-consumer retry policies: fraud detection gets 10 retries, analytics gets 3
→ Any system where routing rules need to change without touching producers
```

The deal-breaker: RabbitMQ has no replay. If a new service joins the system, it can only receive events from that point forward. If you need historical data, you'd need a separate data store.

---

## Choose Kafka when

Multiple independent consumer groups need the same events, you need replay capability, and the volume is high enough that per-message infrastructure overhead matters.

Kafka is the right choice when the event is a fact that should persist in a shared history — not a job that should be done once and erased.

```
Use cases:
→ Event streaming pipelines: ad clicks, user activity, IoT sensor data
→ Multiple consumers, one source: billing + fraud + analytics all need the same click data
→ New services onboarding: new ML model needs 30 days of history to train — replay from offset 0
→ Event sourcing: Kafka as the event log that other services project into read models
→ CDC (Change Data Capture): DB changes streamed as events to downstream systems
→ Log aggregation: all service logs in one topic, multiple consumers (alerting, storage, search)
→ Stream processing: real-time aggregations (fraud detection, dashboards, rate limiting)
```

The deal-breaker: Kafka is operationally heavier than SQS (you manage brokers, ZooKeeper/KRaft, partitions). And its model is wrong for simple one-shot job distribution — messages don't disappear after consumption, so "done" is less clear.

---

## The real-world hybrid pattern

Most production systems at scale use multiple brokers for different layers of the same system:

```
E-commerce order processing:
→ Kafka: order_placed events (event stream, all services consume independently)
→ RabbitMQ: email/SMS notifications (task queue with routing by notification type)
→ SQS: image resizing workers (simple background jobs, AWS ecosystem)
```

This isn't over-engineering — it's using the right tool for the right layer. The event stream (Kafka) feeds the notification system (RabbitMQ) which feeds the worker pool (SQS). Each layer uses the model that fits.

---

## Quick decision table

| Scenario | Answer | Why |
|---|---|---|
| Background jobs on AWS | SQS | Zero ops, simple delivery |
| Background jobs with routing rules | RabbitMQ | Exchange-based routing without producer changes |
| High-throughput event stream | Kafka | Partitioned log, scales to millions/sec |
| Multiple services read same events | Kafka | Consumer groups, independent offsets |
| New service needs historical data | Kafka | Replay from any offset |
| Priority queue needed | RabbitMQ | Native per-message priority |
| Task queue with no AWS | RabbitMQ | More control, routing, priority vs Kafka |
| Simple AWS task queue | SQS | Managed, cheap, good enough |

> [!tip] **Interview framing:** "Before I pick a broker, I ask: is this a job to be done once, or an event that should persist in shared history? For jobs — SQS if we're on AWS, RabbitMQ if we need routing or priority. For events — Kafka, especially if multiple consumers need the same data or I need replay for new services or failure recovery."
