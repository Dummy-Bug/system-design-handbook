# Interview Cheatsheet — Reliability

> [!question] When does reliability come up in an interview and what do you actually say?
> Three moments — requirements, component design, and failure discussion.

---

## Moment 1 — Requirements Phase

Before designing, ask two questions:

*"What's the RTO — how long can the system be down after a failure?"*
*"What's the RPO — how much data loss is acceptable?"*

Then use the answers to justify your architecture:

| RTO | What to build |
|---|---|
| Hours | Restore from backup on failure |
| Minutes | Warm standby — secondary system ready but idle |
| Seconds | Hot standby — Active-Passive with automated failover |
| Zero | Active-Active multi-region |

| RPO | What to build |
|---|---|
| 24 hours | Daily backups |
| 1 hour | Hourly snapshots |
| Minutes | Async replication with small lag |
| Zero | Synchronous replication — warn about write latency cost |

> [!tip] These two questions immediately signal seniority
> Most candidates start drawing boxes. You're quantifying failure tolerance first.

---

## Moment 2 — Distinguishing Availability from Reliability

When an interviewer asks *"how do you handle failures?"* — most candidates only talk about uptime. Go further:

*"I'd separate availability and reliability as two distinct SLIs. For availability I'd track request success rate and eliminate SPOFs with redundancy. For reliability I'd track error rate — 500s, wrong responses, stale data — separately. A system can be fully available and completely unreliable at the same time."*

Then give a concrete example relevant to the system you're designing:
- E-commerce → pricing service bug returning $0 for all products
- Chat app → replication lag causing messages to appear out of order
- News feed → stale cache showing 3-hour-old posts as new

---

## Moment 3 — Failure Discussion

When asked *"what happens when this component fails?"* — cover both MTBF and MTTR:

*"To keep MTBF high I'd use canary deployments and chaos testing to catch weaknesses before they hit production. But failures are inevitable at scale — so I'd focus equally on MTTR: automated alerting so we know within seconds, runbooks so engineers aren't improvising during incidents, and automated rollback for bad deploys."*

Then tie it back to your RTO:

*"Our RTO is 15 minutes, so our entire recovery process — detection, diagnosis, rollback — needs to consistently complete in under 15 minutes. That drives the investment in observability and automation."*

---

## The Reliability Checklist for Every Design

- [ ] Asked for RTO and RPO before designing
- [ ] Separated availability SLI (uptime) from reliability SLI (error rate)
- [ ] Identified at least one way the system can be available but return wrong data
- [ ] Specified replication strategy based on RPO (async vs sync)
- [ ] Specified recovery strategy based on RTO (backup restore / warm standby / hot standby / active-active)
- [ ] Addressed both MTBF (prevention) and MTTR (fast recovery)

---

## Quick Reference

```
Reliability  =  correct answers consistently over time
Availability =  can users reach the system?
               (a system can be both available AND unreliable)

MTBF  =  Total uptime / Number of failures       (higher = better)
MTTR  =  Total downtime / Number of failures      (lower = better)
Availability = MTBF / (MTBF + MTTR)

RTO  =  max acceptable downtime after failure     (drives recovery architecture)
RPO  =  max acceptable data loss after failure    (drives replication strategy)

503  →  availability problem  (server never received the request)
500  →  reliability problem   (server received it, processed it, failed)
```
