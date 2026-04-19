# APNs Down — Fault Isolation

## How It Propagates

Push workers consume from the `notifications-push` Kafka topic and send to APNs. APNs starts returning 500s or timing out. Workers retry with exponential backoff — 1s, 2s, 4s — but APNs is fully down, all retries fail. Failed notifications get published to `notifications-push-dlq`. The DLQ starts accumulating messages at 3.5M/sec (the full push volume). Within minutes the DLQ has tens of millions of undelivered notifications.

**Impact on other channels: zero.** SMS and email workers have their own Kafka topics, their own worker pools, their own external providers. APNs being down does not affect Twilio or SendGrid. Channel isolation means one provider failure never bleeds into others.

---

## Detection

- APNs error rate spikes above threshold (e.g. >1% 5xx rate)
- Worker p99 latency spikes (timeouts instead of fast 50ms responses)
- DLQ consumer lag metric climbs rapidly
- Alert fires to on-call

---

## Containment — Circuit Breaker

Once the error rate crosses the circuit breaker threshold, the circuit opens. Workers stop sending to APNs entirely — no more wasted retry attempts. Failed notifications go straight to the DLQ without attempting the send.

```
Circuit breaker states:
CLOSED    → APNs healthy, normal sends
OPEN      → APNs down, skip send, go to DLQ directly
HALF-OPEN → every 30s, send 1 test request to check recovery
```

---

## Recovery — Gradual Ramp-Up

When APNs recovers, the circuit breaker enters HALF-OPEN and sends test requests. On success, traffic ramps up gradually — not all at once:

```
HALF-OPEN → 100 req/sec → success
          → 1K req/sec  → success
          → 10K req/sec → success
          → full throughput
```

This prevents a recovered APNs from being immediately overwhelmed by hours of DLQ backlog. The DLQ drain rate is controlled — always slower than APNs can handle, always faster than it is filling.

> [!danger] Never drain DLQ at full speed after recovery
> Hours of backlog dumped into APNs all at once is a second outage waiting to happen. Gradual ramp-up is mandatory — start at 1% of normal throughput and double every 30 seconds until stable.
