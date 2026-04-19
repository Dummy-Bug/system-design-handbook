# Kafka Down — Fault Isolation

## How It Propagates

The app server receives notification requests from calling services and publishes them to Kafka. If Kafka is unavailable, the app server cannot publish — no notifications enter the pipeline at all. Workers are idle, the DLQ is empty, external providers receive nothing. Every incoming request from every calling service fails at the intake point.

This is the most severe failure scenario in the system. Every other failure (APNs down, Cassandra down, Redis down) degrades one part of the pipeline. Kafka down stops everything.

---

## Making Kafka Resilient — Replication Factor 3

Kafka is deployed with **replication factor 3** — each partition has 3 replicas distributed across different brokers. A single broker failure triggers leader election: one of the replicas is promoted to leader within seconds. No data loss, no manual intervention.

**Multi-AZ deployment** spreads brokers across availability zones. An entire AZ going down still leaves 2 AZs with replicas — the cluster stays healthy.

```
3 brokers across 3 AZs:
  Broker 1 (AZ-A) — partition leader
  Broker 2 (AZ-B) — replica
  Broker 3 (AZ-C) — replica

AZ-A goes down → Broker 2 or 3 elected as new leader in ~10-30 seconds
```

This handles the vast majority of Kafka failure scenarios. A full cluster failure (all 3 AZs simultaneously down) is extremely rare and treated as a catastrophic event.

---

## Leader Election Window — 10-30 Seconds

Even with replication, leader election takes 10-30 seconds. During this window, the app server cannot publish to Kafka. Calling services are blocked — their requests time out and they get errors.

If the app server just waits, calling services timeout and start retrying. When Kafka recovers, all the retries arrive simultaneously — a thundering herd that could overwhelm Kafka at the worst possible moment.

The app server needs a way to absorb requests during this brief window without blocking callers.

---

## Why In-Memory Buffer Fails

The naive fix is an in-memory buffer on the app server — hold requests in memory, retry publishing to Kafka every few seconds. Calling services get `202 Accepted` immediately.

The problem: if the app server crashes while holding the buffer, all buffered notifications are lost permanently. No durability guarantee.

At 5M/sec intake, even a 30-second buffer holds:
```
5M/sec × 30s = 150M notifications in memory
```

150M notifications in memory is not feasible — the app server runs out of RAM and crashes, making things worse.

---

## Load Shedding — Only Critical Notifications Buffered

The fix is to not buffer everything — **shed load aggressively during a Kafka outage**. The app server accepts only critical high-priority notifications into the buffer and immediately rejects everything else with `503`:

- **Accepted:** OTPs, fraud alerts, password resets, account security alerts
- **Rejected with 503:** marketing, social (likes, comments), reminders, digests

Critical notifications are ~1% of total traffic:
```
5M/sec × 1% = 50K/sec critical notifications
50K/sec × 30s = 1.5M notifications to buffer
```

1.5M is manageable. Calling services for non-critical channels see a `503` and retry later — acceptable since those notifications are not time-sensitive.

---

## Redis as Temporary Buffer

1.5M notifications at 50K/sec needs a fast, durable store — not in-memory on the app server. **Redis** is the right choice:

- Sub-millisecond writes — handles 50K/sec easily
- Persisted to disk (Redis AOF mode) — survives app server crash
- Separate from Kafka — Redis being up when Kafka is down is the common case

```
Kafka leader election in progress:
  App server → Redis buffer (critical notifications only)
  Calling services → 202 Accepted (don't know Kafka is down)

Kafka recovers:
  App server reads from Redis buffer → publishes to Kafka
  Redis buffer drained → back to normal
```

---

## Full Kafka Failure — Reject with 503

If Kafka is fully down (all brokers, all AZs — a catastrophic event), the Redis buffer fills up within minutes at 50K/sec. Once the buffer is full, the app server rejects all requests including critical ones with `503`.

Calling services are responsible for retrying with their own backoff. This is the correct behaviour — your notification system cannot absorb an indefinite Kafka outage. The calling service must own retry responsibility for catastrophic failures.

---

## Detection and Recovery

**Detection:**
- Kafka produce error rate spikes to 100%
- App server request success rate drops
- Worker Kafka consumer lag stops growing (workers idle — nothing to consume)
- Alert fires immediately — Kafka down is P0

**Recovery:**
- Kafka leader election completes → app server resumes publishing
- Redis buffer drained to Kafka in order
- Normal pipeline resumes
- No manual intervention for single broker failure

> [!danger] Kafka is the single most critical component
> Every other failure degrades one channel or one operation. Kafka down stops all notifications system-wide. Invest heavily in Kafka reliability: replication factor 3, multi-AZ, aggressive monitoring, and on-call escalation for any Kafka alert.
