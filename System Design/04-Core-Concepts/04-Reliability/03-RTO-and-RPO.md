# RTO and RPO

> [!question] Your primary database just died. How long can you be down, and how much data can you lose?
> RTO answers the first. RPO answers the second.

---

## The scenario

Your primary database server catches fire. Gone. You need to restore service. Two questions immediately come up:

1. **How long can we be down while we restore?**
2. **How much data can we afford to lose?**

---

## RTO — Recovery Time Objective

**The maximum amount of time your system can be down after a failure.**

This is a business decision, not a technical one. The business decides what's acceptable, and engineering builds to meet it.

- RTO = 4 hours → you have 4 hours to fully restore service
- RTO = 15 minutes → you have 15 minutes
- RTO = 0 → you cannot go down at all (active-active multi-region)

Shorter RTO = more expensive. A 15-minute RTO requires hot standby systems ready to take over instantly. A 4-hour RTO allows you to spin things up from scratch when a failure happens.

---

## RPO — Recovery Point Objective

**The maximum amount of data loss you can accept, measured in time.**

When you restore, you're restoring from a backup. That backup was taken at some point in the past. Everything between that backup and the failure — is gone.

- RPO = 24 hours → you can lose up to 24 hours of data (daily backups are fine)
- RPO = 1 hour → you can lose up to 1 hour of data (hourly backups needed)
- RPO = 0 → zero data loss (every write must be replicated synchronously before confirming)

Lower RPO = more expensive. RPO = 0 means synchronous replication to another datacenter on every single write — that adds latency to every operation.

---

## A concrete example

E-commerce site. Database server dies at 3pm.

```
Last backup was taken at 2pm.

RTO = 2 hours  →  service must be back by 5pm
RPO = 1 hour   →  maximum data loss is 1 hour → orders from 2pm–3pm are lost
```

The business has to decide: is losing 1 hour of orders acceptable? If not, RPO needs to be lower — which means more frequent backups or real-time replication.

---

## How they drive architecture decisions

| RTO | What it requires |
|---|---|
| Hours | Restore from backup — spin up new servers, restore data, verify |
| Minutes | Warm standby — a secondary system already running, just not serving traffic |
| Seconds | Hot standby / Active-Passive with automated failover |
| Zero | Active-Active — multiple live systems, no failover needed |

| RPO | What it requires |
|---|---|
| 24 hours | Daily backups to S3 or similar |
| 1 hour | Hourly snapshots |
| Minutes | Continuous replication with small lag |
| Zero | Synchronous replication — write confirmed only after both primary and replica have it |

---

## The hidden cost of RPO = 0

Synchronous replication adds latency to every write. The write has to travel to the replica and get confirmed before the user gets a response. If the replica is in another datacenter, that's 50–100ms added to every single write operation.

This is why most systems use **asynchronous replication** — slightly higher RPO, but no latency penalty on writes. The business decides which tradeoff is acceptable.

---

## MTTR vs RTO — they sound similar

- **MTTR** — what actually happens on average when things break. A historical measurement.
- **RTO** — what the business says is the maximum acceptable. A target you design to.

You design your system so that MTTR stays below RTO. If your RTO is 30 minutes, your recovery process must consistently complete in under 30 minutes.

---

> [!tip] In an interview — ask for both before designing
> *"What's the RTO and RPO for this system?"*
>
> The answers tell you exactly what backup strategy and replication model to use. A fintech system with RPO = 0 needs synchronous replication. An internal analytics dashboard with RPO = 24 hours needs daily snapshots. Same question, completely different architectures.
