# Measuring Availability — Notification System

> [!info] Availability is not "are the workers running?" — it's "are notifications actually being delivered?"
> A worker pod can be running while APNs circuit breaker is open and zero push notifications are going out. Health checks miss this. Delivery success rate catches it.

---

## Two Availability SLIs

The notification system has two distinct availability concerns:

**1. Intake API availability** — can calling services successfully submit notification requests?

```
Intake availability = successful POST /notifications/send responses / total requests
```

A `201 Accepted` is a success. A `503 Service Unavailable` or timeout is a failure. This maps directly to the 99.99% availability SLO from the NFR.

**2. Delivery success rate per channel** — of notifications accepted into the pipeline, what fraction are actually delivered?

```
Push delivery success rate   = DELIVERED push notifications / total push attempts
SMS delivery success rate    = DELIVERED SMS notifications / total SMS attempts
Email delivery success rate  = DELIVERED email notifications / total email attempts
```

This is not in the NFR SLOs but is critical for production health. A 95% push delivery success rate means 5% of notifications silently fail — millions of missed notifications per day at scale.

---

## Intake Availability — Same Pattern as URL Shortener

Each app server tracks two counters:
- `intake_total` — incremented on every incoming request
- `intake_successful` — incremented when response is `201 Accepted`

A `503`, `429`, or timeout increments only `intake_total`. The metrics collector computes the ratio every 15 seconds.

```
What counts as a success:
POST /notifications/send → 201 Accepted    ✓ (notification accepted into pipeline)
POST /notifications/send → 400 Bad Request ✓ (system worked, caller sent bad data)
POST /notifications/send → 503 Unavailable ✗ (system broke, Kafka unreachable)
POST /notifications/send → timeout         ✗ (user got nothing)
```

400 is a success because the system worked correctly — it validated the request and returned the appropriate error. That is not a reliability failure. 503 is a failure because the system itself broke down.

---

## Delivery Success Rate — Notification-Specific

The worker tracks delivery outcomes per channel:

```
push_attempts_total    — incremented every time a push send is attempted
push_delivered_total   — incremented on APNs 200 OK
push_failed_total      — incremented after all retries exhausted

sms_attempts_total     — incremented every time an SMS send is attempted
sms_delivered_total    — incremented on Twilio 200 OK
sms_failed_total       — incremented after all retries exhausted
```

Delivery success rate:
```
push_success_rate  = push_delivered_total / push_attempts_total
sms_success_rate   = sms_delivered_total / sms_attempts_total
email_success_rate = email_delivered_total / email_attempts_total
```

A drop in push success rate is the first signal that APNs is degrading — before the circuit breaker trips, before the DLQ fills, before users complain.

---

## DLQ Depth — The Accumulation Signal

DLQ depth is the number of messages sitting in the dead letter queue waiting for retry:

```
notifications-push-dlq depth: 0        → healthy ✓
notifications-push-dlq depth: growing  → failures accumulating faster than retries drain ✗
```

DLQ depth growing while delivery success rate is falling = external provider is degraded, retries are not helping. Circuit breaker should trip if it hasn't already.

DLQ depth growing while delivery success rate is stable = retry worker is slow, not a provider problem. Scale the retry worker.

---

## External Provider Error Rate

Each worker tracks error responses from external providers:

```
apns_5xx_rate   — fraction of APNs calls returning 500+
apns_429_rate   — fraction of APNs calls being rate limited
twilio_5xx_rate
twilio_429_rate
sendgrid_5xx_rate
```

Provider error rates are the earliest warning signal — they rise before the circuit breaker trips and before delivery success rate visibly drops. Alerting on provider error rate gives the on-call engineer a head start.

> [!tip] Interview framing
> "Two availability SLIs for a notification system: intake API availability (same pattern as any API — successful requests / total) and per-channel delivery success rate (delivered / attempted). The delivery success rate is what actually matters — a system that accepts every request but delivers nothing is not available. DLQ depth and provider error rates are supporting operational metrics that give early warning before delivery success rate visibly degrades."
