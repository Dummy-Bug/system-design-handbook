# Cassandra Down — Fault Isolation

## How It Propagates

Workers consume from Kafka, check Redis for preferences, and successfully send notifications to APNs/Twilio/SendGrid — the user receives the notification. But when the worker tries to write `DELIVERED` status back to Cassandra, the write fails. Cassandra is down.

The notification was delivered. The status was not recorded. Every worker in the pool hits the same wall — Cassandra times out on every write attempt. Workers slow down, Kafka consumer lag starts growing, and status for all in-flight notifications stays `PENDING` indefinitely.

**Critically — delivery is unaffected.** Users still receive their notifications. The only thing broken is the bookkeeping.

---

## Option 1 — Don't Commit Kafka Offset, Replay the Batch

The first instinct: if the status write failed, don't commit the Kafka offset. Let Kafka replay the batch. On replay, the worker sends the notification again and retries the Cassandra write.

```
Batch of 1000 notifications sent to APNs ✓
Cassandra write fails ✗
Don't commit offset → Kafka replays all 1000
→ 1000 notifications sent to APNs again
→ 1000 users receive duplicate notifications
```

This works for the status write — Cassandra eventually recovers and the write succeeds. But every user in the batch gets a duplicate notification. At 3.5M push/sec, that's millions of duplicates per second of Cassandra downtime.

---

## Option 2 — Commit Offset, Status Stays PENDING

The second approach: commit the Kafka offset normally. The batch is done from Kafka's perspective. The status for affected notifications stays `PENDING` in Cassandra — or if Cassandra is fully down, the status simply isn't written at all until recovery.

```
Batch of 1000 notifications sent to APNs ✓
Cassandra write fails ✗
Commit Kafka offset → batch done, no replay
→ no duplicate notifications ✓
→ status stays PENDING in Cassandra ✗ (temporary inconsistency)
```

No duplicates. Status is temporarily wrong — but our NFR explicitly allows eventual consistency for delivery status.

---

## Why Option 1 Loses

Duplicates are a user-facing problem. A user getting the same push notification twice is confusing and annoying — "why did Instagram notify me about the same like twice?" At scale, millions of duplicates per second of downtime is a serious user experience failure.

Stale status in Cassandra is an internal bookkeeping problem. The calling service sees `PENDING` instead of `DELIVERED` for a few minutes — tolerable. The NFR said eventual consistency for delivery status is acceptable. This is exactly that scenario.

> [!danger] Don't sacrifice user experience to preserve internal consistency
> Duplicates are visible to users. Stale status is invisible to users. Always choose the option that protects the user-facing behaviour.

---

## Why Option 2 Wins

Option 2 commits the offset and accepts temporary status inconsistency. This is the right call because:

1. Delivery already happened — the user got the notification
2. Eventual consistency for status is explicitly allowed in the NFR
3. No duplicates means no user-facing degradation
4. Status can be reconciled later via a background job

---

## Background Reconciliation Job

When Cassandra recovers, a background job scans for notifications with stale `PENDING` status — entries where `created_at` is old enough that they should have been delivered by now but status never updated.

The naive fix is to re-send these notifications to Kafka and let workers re-process them. But that causes the same duplicate problem — the notification was already delivered, re-processing sends it again.

The correct fix is to **query the external provider for actual delivery status** without re-sending.

---

## Delivery Receipt APIs — Query APNs/FCM for Actual Status

APNs and FCM provide delivery receipt APIs. Given a `notification_id`, you can query whether the notification was actually delivered to the device. The reconciliation job uses this to resolve stale `PENDING` statuses:

```
Reconciliation job finds: notification_id=xyz, status=PENDING, created_at=10min ago

→ Query APNs: "was notification xyz delivered?"
→ APNs: "yes, delivered at 09:00:44"
→ Update Cassandra: status=DELIVERED, delivered_at=09:00:44
```

No re-send. No duplicate. Just a status correction.

---

## Rate Limiting the Reconciliation Job

The reconciliation job queries APNs/FCM receipt APIs — the same endpoints your push workers use for delivery. If the job runs at full speed, it competes with live notification traffic for APNs capacity.

The job must be rate limited and low priority:

```
Reconciliation job:  100 receipt queries/sec (background, slow)
Normal push workers: 3.5M sends/sec         (foreground, fast)
```

The reconciliation job is a background janitor — slow, patient, never urgent. It runs during off-peak hours where possible and always yields to live traffic.

---

## Detection and Recovery

**Detection:**
- Cassandra write error rate spikes
- Worker processing time increases (timeouts on status writes)
- Kafka consumer lag grows (workers slowing down)
- Alert fires to on-call

**Recovery:**
- Cassandra recovers → workers resume normal status writes
- Reconciliation job scans for stale `PENDING` entries → queries receipt APIs → updates status
- No manual intervention needed — the system self-heals

> [!important] Delivery and status are decoupled by design
> The worker does not need a successful Cassandra write to consider a notification delivered. Delivery and bookkeeping are independent operations. This decoupling is what allows the system to keep delivering notifications even when the DB is down.
