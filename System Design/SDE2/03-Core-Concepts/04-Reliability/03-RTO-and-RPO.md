> [!question] Your primary database just died. How long can you be down, and how much data can you lose?
> RTO answers the first. RPO answers the second.

---

## The scenario

Your primary database server catches fire. Gone. You need to restore service. Two questions immediately come up:

1. **How long can we be down while we restore?**
2. **How much data can we afford to lose?**

---

## RTO — Recovery Time Objective

**The maximum amount of time your system can be down per incident — from the moment of failure until service is fully restored.**

This is a business decision, not a technical one. The business decides what's acceptable, and engineering builds to meet it.

Note: RTO is a per-failure time budget, not a monthly or annual allowance. If your database dies at 3pm, an RTO of 4 hours means you must be back by 7pm — that single event.

- RTO = 4 hours → each failure must be recovered within 4 hours
- RTO = 15 minutes → each failure must be recovered within 15 minutes
- RTO = 0 → you cannot go down at all (active-active multi-region)

Shorter RTO = more expensive. A 15-minute RTO requires hot standby systems ready to take over instantly. A 4-hour RTO allows you to spin things up from scratch when a failure happens.

---

## RPO — Recovery Point Objective

**The maximum amount of data you can afford to lose per incident, measured as a time window.**

When you restore, you're restoring from a backup. That backup was taken at some point in the past. Everything written between that backup and the moment of failure — is gone.

- RPO = 24 hours → per failure, you can lose up to 24 hours of data (daily backups are fine)
- RPO = 1 hour → per failure, you can lose up to 1 hour of data (hourly backups needed)
- RPO = 0 → zero data loss per failure (every write must be replicated synchronously before confirming)

Lower RPO = more expensive. RPO = 0 means synchronous replication to another datacenter on every single write — that adds latency to every operation.

---

## Two completely different recovery strategies

Before going further — there are two fundamentally different ways to recover from a dead database. The notes above use the word "restore" loosely. Here's what they actually mean:

**Strategy 1 — Restore from snapshot (backup)**
A snapshot is a frozen, point-in-time dump of your data written to a file and stored somewhere safe (S3, remote datacenter — never the same disk as your primary, because fire kills both). When the primary dies, you spin up a new server and load the file back in. This takes hours. This is the slow path.

**Strategy 2 — Promote a replica**
A replica is a live database server on a different machine, continuously receiving every write from the primary. It's always running, always current. When the primary dies, you promote the replica to leader. Producers and consumers are redirected. This takes seconds. This is the fast path.

```
Primary DB dies at 3pm

Path 1 — no replica, restore from snapshot:
→ Snapshot was taken at 2pm (last backup)
→ Spin up new server, load snapshot, verify → takes 2-4 hours
→ Back online at 5-7pm
→ Orders from 2pm–3pm are gone (RPO = 1 hour, RTO = hours)

Path 2 — replica exists on a different machine:
→ Replica was in sync up to ~3pm (async lag: seconds)
→ Promote replica to leader → takes seconds to minutes
→ Back online by 3:01pm
→ At most a few seconds of data loss (RPO ≈ 0, RTO = seconds)
```

> [!important] When someone says "RTO = 4 hours" it means they are on Path 1 — no replica, restoring from a backup file. When someone says "RTO = seconds" they are on Path 2 — a live replica exists and gets promoted. These are different architectures, not just different speeds of the same thing.

> [!warning] Snapshots must never be stored on the same disk as the primary. A disk failure or fire destroys both. Snapshots go to object storage (S3, GCS) in a different datacenter or region — built to survive hardware failure independently of your DB server.

---

## A concrete example

E-commerce site. Database server catches fire at 3pm.

```
Scenario A — snapshot only (no replica):
Last snapshot was taken at 2pm, stored in S3.

RTO = 2 hours  →  spin up new server, restore from S3 snapshot, back by 5pm
RPO = 1 hour   →  orders placed 2pm–3pm are lost forever

Scenario B — replica on a standby server:
Replica was receiving writes continuously, last write ~3pm.

RTO = 30 seconds  →  promote replica to leader, redirect traffic
RPO ≈ 0           →  at most a few seconds of async lag lost
```

Scenario B costs more (you're running two servers all the time). The business decides which trade-off is worth it.
