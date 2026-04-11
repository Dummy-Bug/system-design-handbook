
> [!info] RabbitMQ is a message broker built around the idea of **routing**. You don't publish a message directly to a queue — you publish it to an **exchange**, and the exchange decides which queue (or queues) should receive it based on routing rules you define. This routing layer is what sets RabbitMQ apart from simpler brokers like SQS.

---

## Why a routing layer matters

SQS is straightforward: one queue, producers write to it, consumers read from it. Perfect for simple task distribution.

But in real systems, the same event often needs to reach different sets of consumers depending on its content. An ad click during a fraud investigation campaign needs to go to the fraud queue AND the analytics queue, but NOT the billing queue (billing is paused for that campaign). How do you express that routing logic?

With plain SQS you'd need the producer to know about every queue and decide which ones to write to — coupling the producer to consumer topology. Every time you add a new consumer, you'd need to change the producer.

RabbitMQ solves this with the exchange layer.

---

## The RabbitMQ mental model

```
Producer → Exchange → Queue(s) → Consumer(s)
```

The producer only knows about the exchange. The exchange knows about the queues. The queues know about the consumers.

```
Ad Click API publishes to exchange "ad.events":
  { click_id: 1001, campaign_id: 77, type: "display" }

Exchange "ad.events" routes to:
→ analytics.queue  ← Analytics workers pick this up
→ billing.queue    ← Billing workers pick this up
→ fraud.queue      ← Fraud workers pick this up

Each worker fleet operates independently.
Analytics can be down for maintenance while Billing continues processing.
```

The producer published once. Three independent queues each got their own copy. The producer doesn't know how many consumers exist.

---

## The exchange is the routing brain

The exchange receives every published message and decides where to send it. The routing decision is controlled by two things:

**Exchange type** — the routing algorithm (direct, fanout, topic, headers). Covered in detail in the next file.

**Bindings** — the configuration connecting an exchange to a queue. You define these at setup time.

```
Exchange: ad.events (fanout type)
Bindings:
  → analytics.queue
  → billing.queue
  → fraud.queue

All three queues are bound to this exchange.
Every message published to ad.events goes to all three.
```

You change routing by changing bindings — not by changing producer code. Add a new analytics service? Create a new queue, bind it to the exchange, done. No producer changes needed.

---

## Producer → Exchange → Queue → Consumer — why four separate hops?

It might seem like extra complexity compared to "producer → queue → consumer". Here's why each hop exists:

**Producer → Exchange**: The producer declares intent ("this happened"), not destination. It doesn't know which queues care about this event.

**Exchange → Queue(s)**: The broker applies routing logic. The exchange can copy the message to one queue, multiple queues, or zero queues depending on the bindings.

**Queue → Consumer**: The queue holds the message durably until a consumer is ready. Standard ACK-based delivery. Consumer crashes? Message reappears.

The four-hop model gives you **separation of routing logic from delivery logic**. The exchange handles routing; the queue handles reliable delivery. They're different concerns solved by different parts of the system.

---

## What RabbitMQ is best at

RabbitMQ shines for use cases where:

**Task distribution with routing** — you have workers that should receive different subsets of events based on type, source, or content. RabbitMQ's exchange/binding model handles this natively without producer changes.

**Multiple independent worker pools** — different teams own different queues. The analytics team manages their queue, the billing team manages theirs. RabbitMQ's per-queue configuration (DLQ, retry policies, prefetch) lets each team tune their queue independently.

**Priority queues** — RabbitMQ has native support for per-message priority. Higher priority messages bubble up and get consumed first. Kafka has no native priority support.

**Low-to-medium throughput with complex routing** — tens of thousands of messages per second with rich routing rules. RabbitMQ handles this easily. For millions per second with simple routing, Kafka is better.

> [!important] RabbitMQ deletes messages after consumers ACK them — just like SQS. This means there is no replay. If you need to reprocess events from yesterday, they're gone. If replay is a requirement, use Kafka.

> [!tip] **Interview framing:** "I'd use RabbitMQ when I need flexible broker-side routing — the same event going to different queues based on type or routing key, without coupling the producer to consumer topology. For simple task distribution with no routing needs, SQS is simpler. For event streams that need replay, Kafka."
