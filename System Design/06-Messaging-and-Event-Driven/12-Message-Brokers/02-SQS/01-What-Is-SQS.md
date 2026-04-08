# What Is SQS

> [!info] Amazon SQS (Simple Queue Service) is a fully managed message queue on AWS. A producer sends messages to a queue, and consumers pull those messages later for asynchronous processing.

---

## The problem SQS solves

Imagine an ad platform during a big sports final. Traffic jumps from `20,000 clicks/sec` to `150,000 clicks/sec` in minutes.

Each click needs more work than just returning `200 OK`:

```
1. Bill the advertiser
2. Update campaign analytics
3. Run fraud checks
4. Update pacing and budget systems
```

If the API does all this synchronously in the click path, latency spikes and failures cascade across services.

---

## The SQS model

SQS lets the click API accept the event quickly, then hand off heavy work to background workers.

```
User clicks ad
→ Click API sends message to SQS:
  { click_id, ad_id, campaign_id, ts }
→ Click API returns 200 quickly

Background:
→ Billing worker pulls message and processes
→ Analytics worker processes downstream data
→ Fraud worker evaluates click quality
```

This keeps user-facing latency low while still processing click events reliably.

---

## Why teams pick SQS

With self-hosted brokers, teams must run and maintain infrastructure: upgrades, storage tuning, failover, capacity planning, and on-call operations.

With SQS:

- AWS runs the queue infrastructure
- You call `SendMessage`, `ReceiveMessage`, `DeleteMessage`
- You scale workers independently from producers

This is the core reason SQS appears in many production designs: low operational overhead for async pipelines.

---

## What SQS guarantees vs what it doesn't

> [!important] What it guarantees
> Durable queueing, decoupling between producers and consumers, and retry-friendly asynchronous processing.

> [!danger] What it doesn't guarantee
> SQS alone does not guarantee exactly-once business effects. Consumers must handle duplicates safely.

---

> [!tip] Interview framing
> "I'd use SQS to decouple the click ingestion API from slower downstream processing. The API path stays fast under spikes, while worker fleets drain the queue asynchronously. Since SQS is managed, we get queue reliability without operating broker infrastructure."

