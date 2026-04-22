# SLI-SLO Connection — Notification System

> [!info] SLO is the target. SLI is the measurement. You need both.
> Writing "push p95 < 5 seconds" in your NFR is easy. Knowing whether you're actually hitting it in production requires something else entirely.

---

## The Gap Between Design and Reality

When you design the notification system, you make assumptions. APNs responds in 50ms. Redis cache hit rate is 95%. Kafka consumer lag stays under 1 second. You run the numbers and conclude: push p95 should be well under 5 seconds.

But those are estimates. Production is not a whiteboard.

Maybe APNs is throttling silently during a celebrity event — your actual response time is 2 seconds, not 50ms. Maybe Redis is under memory pressure and LRU is evicting preference keys — workers are falling back to PostgreSQL on 30% of requests instead of 5%. Maybe a Kafka partition is hot and one consumer is lagging 30 seconds behind.

None of this shows up in your estimates. It only shows up when you measure.

---

## What SLI Actually Means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   push p95 < 5 seconds
SLI (reality):  actual measured p95 = 3.2 seconds  ← this is what you observe
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## The SLOs from the NFR and Their SLIs

From the NFR, three latency SLOs and one availability SLO:

```
SLO 1:  push p95 < 5 seconds
SLI 1:  actual p95 delivery latency for push channel — from Kafka publish to APNs ack

SLO 2:  SMS p95 < 30 seconds
SLI 2:  actual p95 delivery latency for SMS channel — from Kafka publish to Twilio ack

SLO 3:  email p95 < 2 minutes
SLI 3:  actual p95 delivery latency for email channel — from Kafka publish to SendGrid ack

SLO 4:  intake API 99.99% availability
SLI 4:  successful intake requests / total intake requests
```

Each channel has its own SLI because each has a different SLO and a different delivery path. Aggregating them into one metric would hide channel-specific degradation — push being healthy doesn't tell you SMS is broken.

---

## Why "Is the Worker Running?" Is Not Enough

The instinct is to check if worker processes are alive. If the push worker pod is running, push is healthy.

This is a health check, and it is useful — Kubernetes uses it to restart crashed pods. But it is not an SLI.

A worker pod can be running while:
- APNs circuit breaker is open — no push notifications being delivered
- Kafka consumer lag is 5 minutes — notifications arrive 5 minutes late
- DLQ depth is growing — failed notifications are accumulating unnoticed

From Kubernetes's perspective: all pods healthy. From the user's perspective: notifications are broken.

SLI measures what users actually experience — did their notification arrive, and how long did it take?

---

## Notification-Specific SLIs Beyond the NFR

The NFR SLOs are the core commitments. But a notification system has additional operational SLIs that matter for production health:

**Kafka consumer lag** — how far behind are workers from the latest message in each topic? Growing lag means workers can't keep up with intake rate.

**DLQ depth** — how many notifications are sitting in the dead letter queue? Growing DLQ depth means failures are accumulating faster than the retry worker can drain them.

**Delivery success rate per channel** — what fraction of attempted sends actually succeed? A 95% success rate on push means 5% of notifications silently fail.

**External provider error rate** — what fraction of APNs/Twilio/SendGrid calls return errors? Rising error rate is an early warning before the circuit breaker trips.

These four operational SLIs are what an on-call engineer checks first when paged at 3am.

> [!tip] Interview framing
> "SLO is the promise, SLI is the measurement. For a notification system, the core SLIs are per-channel p95 delivery latency and intake API availability — matching the NFR SLOs. But in production you also need operational SLIs: Kafka consumer lag, DLQ depth, delivery success rate per channel, and external provider error rates. These are the metrics that tell you a problem is developing before users start complaining."
