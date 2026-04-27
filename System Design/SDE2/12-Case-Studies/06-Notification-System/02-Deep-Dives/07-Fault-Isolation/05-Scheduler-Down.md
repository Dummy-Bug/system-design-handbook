# Scheduler Down — Fault Isolation

## How It Propagates

The scheduler service polls the Scheduler DB every second for due notifications and publishes them to Kafka. If the scheduler crashes, polling stops. Scheduled notifications continue accumulating in the Scheduler DB — writing is unaffected since the app server still writes to it. But nothing is reading from it and dispatching to Kafka.

Users with scheduled notifications miss their delivery time. A birthday notification scheduled for 9:00am sits in the Scheduler DB undelivered while the scheduler is down.

**Impact on immediate notifications: zero.** Immediate notifications bypass the Scheduler DB entirely — they go straight from the app server to Kafka. Only scheduled notifications are affected.

---

## Detection

- Scheduler service heartbeat missing (scheduler emits a heartbeat to a monitoring endpoint every 5 seconds)
- Scheduler DB row count growing with no corresponding Kafka publish rate
- Scheduled notification delivery lag metric climbing
- Alert fires to on-call

---

## Containment — Redis Distributed Lock and Standby Instances

The scheduler runs as multiple instances, but only one dispatches at a time — controlled by a **Redis distributed lock**:

```
Redis SET scheduler_lock <instance_id> NX EX 5
→ only the instance that wins the lock runs the poll-and-dispatch loop
→ lock TTL: 5 seconds
→ if leader crashes, lock expires in 5 seconds
→ standby instance wins the lock and takes over
```

Maximum downtime: **5 seconds** — the TTL of the Redis lock. After that, a standby instance takes over automatically with no manual intervention.

---

## Recovery — Catch-Up Dispatch

When the new scheduler instance takes over, it queries the Scheduler DB for all notifications where `scheduled_at <= now` that were never dispatched — these are the notifications that missed their window while the leader was down.

The new scheduler publishes all of them to Kafka immediately. Workers process them through the normal pipeline — preference check, deduplication, send to external provider.

```
Scheduler was down for 10 minutes:
  → 10 minutes of scheduled notifications sitting in Scheduler DB
  → New scheduler queries: SELECT * WHERE scheduled_at <= now
  → Publishes all missed notifications to Kafka
  → Workers drain them within seconds
```

---

## Scheduled Notifications Are Late, Not Lost

If the scheduler is down for 10 minutes, notifications scheduled during that window are delivered ~10 minutes late. They are never lost — the Scheduler DB is the durable store. As long as the Scheduler DB is up, notifications survive a scheduler crash.

The lateness is bounded by the outage duration + the 5-second lock TTL. For most scheduled notification types (birthdays, reminders, marketing) a 10-minute delay is imperceptible. For time-sensitive scheduled notifications (OTPs with a specific send time), the jitter rules already applied at intake mean exact timing was never guaranteed anyway.

> [!important] The Scheduler DB is the durability guarantee
> The scheduler service is stateless — it reads from the DB and publishes to Kafka. Crashing and restarting loses no data because all state lives in the Scheduler DB. A stateless service with durable backing store can always recover cleanly.

---

## What If the Scheduler DB Is Also Down?

If both the scheduler service and the Scheduler DB are down simultaneously, scheduled notifications cannot be dispatched or even written. New scheduled notification requests from the app server fail at write time.

This is treated as a catastrophic dual failure — the app server returns `503` for scheduled notification requests, and calling services are responsible for retrying. Immediate notifications are unaffected.

---

## Summary

| Failure | Impact | Recovery time |
|---|---|---|
| Scheduler service crashes | Scheduled notifications delayed | 5 seconds (Redis lock TTL) |
| Scheduler service + Redis down | Scheduled notifications delayed until Redis recovers | Minutes |
| Scheduler DB down | Scheduled notifications lost if not yet written | Catastrophic — treat as P0 |

> [!info] Immediate notifications are never affected by scheduler failures
> The scheduler only handles notifications with a future `scheduled_at`. Immediate notifications go directly from app server to Kafka — the scheduler is not in their path at all.
