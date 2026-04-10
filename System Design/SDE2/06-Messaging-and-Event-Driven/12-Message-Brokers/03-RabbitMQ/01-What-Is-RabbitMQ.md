# What Is RabbitMQ

> [!info] RabbitMQ is a message broker that focuses on reliable task distribution and flexible message routing. Producers publish messages to an exchange, and RabbitMQ routes those messages to queues. Consumers read from queues.

---

## The problem it solves

Take an ad-click pipeline. A click event arrives and multiple downstream systems may need it:

```
1. Billing update
2. Fraud analysis
3. Analytics aggregation
```

If the click API calls all services directly, request latency grows and failures cascade. A slow fraud service can impact click ingestion. A temporary analytics outage can back up the API.

You need async handoff and routing between producers and consumers.

---

## RabbitMQ mental model

RabbitMQ introduces a routing layer between producer and queue:

```text
Producer -> Exchange -> Queue -> Consumer
```

Important detail:

- Producer does not publish directly to queue
- Producer publishes to exchange
- Exchange decides which queue(s) should receive the message
- Consumers pull from queues, not exchanges

---

## Why this design matters

Because routing logic sits in exchange/bindings, producers stay simpler.

If routing needs to change, teams can often update RabbitMQ bindings instead of changing producer application logic. This keeps producer code stable while message delivery patterns evolve.

---

## Ad-click example

```text
Ad Click API publishes:
{ click_id, ad_id, campaign_id, ts }
to exchange: click.events

Exchange routes to:
- billing.clicks.queue
- fraud.clicks.queue
- analytics.clicks.queue

Each worker fleet consumes independently.
```

This gives decoupling and independent scaling by workload.

---

> [!important] What it guarantees
> RabbitMQ gives asynchronous handoff and queue-based consumption with explicit routing control through exchanges.

> [!danger] What it doesn't guarantee
> RabbitMQ alone does not guarantee duplicate-free business effects. Consumers still need idempotent handling where duplicates are possible.

---

> [!tip] Interview framing
> "RabbitMQ is a routing-first broker. Producers publish to exchanges, exchanges route to queues using bindings, and workers consume queues independently. It is a strong fit when you need controlled routing plus task-queue semantics."

