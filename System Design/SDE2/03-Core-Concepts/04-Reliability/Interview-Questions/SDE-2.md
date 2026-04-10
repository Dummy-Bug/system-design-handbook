# Reliability — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around recovery strategies, replication choices, standby patterns, and the gap between RTO targets and real MTTR. Expected at SDE-2 level — not just definitions, but understanding when and why decisions matter.

---

> [!question] Your DB dies at 3pm. Last snapshot was at 2pm stored in S3. Walk me through the full recovery step by step.

> [!success]- Answer
>
> **The full recovery timeline:**
> ```
> 3:00pm — primary DB dies
> 3:02pm — monitoring detects it, pages on-call
> 3:05pm — engineer confirms, starts recovery
> 3:07pm — spins up a new DB server
> 3:12pm — pulls snapshot from S3 (depends on snapshot size)
> 3:30pm — restore completes, data verification runs
> 3:45pm — update connection strings, redeploy app, verify end-to-end
> 3:50pm — service restored
>
> RTO  = ~50 minutes
> RPO  = 1 hour (2pm snapshot → 3pm failure = 1 hour of lost data)
> ```
>
> ---
>
> **Step by step explanation:**
>
> **3:07pm — spin up a new DB server:**
> The dead primary is gone. You provision a fresh machine — either a cloud instance or bare metal. It has no data on it yet, just a running DB process waiting to be populated.
>
> **3:12pm — pull snapshot from S3:**
> The snapshot is a compressed dump of your entire database at 2pm, sitting in S3. You download it to the new server. How long this takes depends entirely on snapshot size:
> ```
> 10GB snapshot  → ~2–3 minutes to pull
> 500GB snapshot → ~20–30 minutes to pull
> 5TB snapshot   → could be hours
> ```
> This is often the single biggest time sink in the entire recovery process.
>
> **3:30pm — data verification:**
> You don't send user traffic to a freshly restored DB without checking it first. You're sampling, not scanning every row — but enough to catch a broken restore:
> ```sql
> -- 1. Row count check
> SELECT COUNT(*) FROM orders;
> -- Expected ~2.4 million. Got 0? Restore failed.
>
> -- 2. Latest timestamp check
> SELECT MAX(created_at) FROM orders;
> -- Should be close to 2pm. Got 2023? Wrong snapshot.
>
> -- 3. Spot check critical records
> SELECT * FROM users WHERE id = 1;
> SELECT * FROM payments WHERE id = 999;
> -- Known records — do they look right?
> ```
> None of this is bulletproof — you're sampling. But it catches the obvious failures: corrupt snapshot, wrong snapshot, restore that died halfway through.
>
> **3:45pm — update connection strings, redeploy app:**
> Your app servers are still pointing at the dead primary's address. You update the config to point at the new server:
> ```
> Old: DB_HOST = primary-db-1.internal  ← dead
> New: DB_HOST = restored-db-2.internal ← new server
> ```
> This means updating an environment variable or DNS entry and redeploying. Then you run a full end-to-end smoke test — not just "is the DB up" but "does a real request go through the full stack and return real data."
>
> ---
>
> **What was lost:**
> Every write between 2pm and 3pm — orders, transactions, user events — gone permanently. The business must decide upfront whether losing 1 hour of data is acceptable.
>
> > [!warning] The snapshot must be stored in S3 in a different region — never on the same disk as the primary. A disk failure or fire destroys both. S3 gives 11 nines of durability across multiple AZs independently of your DB server.

---

> [!question] What two things could you have done differently to lose less data and recover faster?

> [!success]- Answer
>
> **Problem 1 — RPO = 1 hour (lost 2pm–3pm data)**
>
> Fix: add a live replica with sync replication.
> ```
> Sync replication → every write goes to primary AND replica before ACKing user
> Primary dies → replica has every single write up to that exact moment
> RPO = 0, zero data loss
> ```
>
> **Problem 2 — RTO = 50 minutes (slow snapshot restore)**
>
> Fix: the live replica is already running — just promote it.
> ```
> No S3 pull. No restore. No verification of a dump file.
> Primary dies → promote replica to primary → redirect traffic
> RTO = 30 seconds
> ```
>
> A live replica with sync replication solves both problems simultaneously:
> ```
> Snapshot only:         RPO = 1 hour,   RTO = 50 minutes
> Replica + async:       RPO = seconds,  RTO = 30 seconds
> Replica + sync:        RPO = 0,        RTO = 30 seconds
> ```
>
> The cost: you're running two full DB servers at all times. For critical systems — billing, payments, user auth — this cost is justified. For internal tools or analytics, snapshot-only may be acceptable.
>
> > [!tip] Interview framing
> > *"Snapshot-only gives RPO = hours and RTO = hours. Add a live replica and you solve both at once — RPO drops to seconds with async, zero with sync, and RTO drops to 30 seconds because you just promote instead of restoring. The right choice depends on how much that data's loss would cost the business."*

---

> [!question] Your RTO is 5 minutes but your MTTR from the last 6 incidents is averaging 12 minutes. What does this mean and what do you do?

> [!success]- Answer
>
> **What it means:**
> ```
> RTO  = 5 min  — the ceiling the business agreed to
> MTTR = 12 min — what's actually happening on average
>
> You are breaching your SLO on every single incident.
> MTTR must stay below RTO. It isn't.
> ```
>
> **Break MTTR into its four components to find where the time goes:**
> ```
> Detection  — how long until the alert fires
> Response   — how long until an engineer is actually looking at it
> Diagnosis  — how long to find the root cause
> Fix        — apply fix, redeploy, verify
>
> Example breakdown of a 12-minute MTTR:
> Detection:  3 min  ← health checks running every 3 minutes
> Response:   4 min  ← engineer was asleep, took time to wake up
> Diagnosis:  3 min  ← unclear dashboards, digging through logs
> Fix:        2 min  ← automated rollback worked once identified
> ```
>
> **The key insight — for a 5 minute RTO, no human can be in the loop:**
> ```
> Even a perfect on-call engineer who wakes up instantly still needs:
> → Time to SSH in
> → Time to understand what's happening
> → Time to make a decision
>
> That alone is 3–5 minutes. You've already blown your budget before touching anything.
> ```
>
> **For a 5 minute RTO, every step must be automated:**
> ```
> Detection  → automated health checks, sub-30 second intervals
> Response   → no human — automated failover fires immediately
> Diagnosis  → irrelevant for infra failures — promote first, diagnose after users are unblocked
> Fix        → automated replica promotion, traffic rerouting
> ```
>
> The architectural fix is automated failover. For a dead DB — don't wait for an engineer to decide. Detect the failure, promote the replica, reroute traffic. All within seconds. The engineer investigates the root cause after service is restored, not before.
>
> > [!important] For infrastructure failures like a dead DB, diagnosis before failover is the wrong order. Restore service first — promote the replica. Diagnose why the primary died afterward, when users are no longer blocked. Every second spent diagnosing before promoting is a second of downtime.
>
> > [!tip] Interview framing
> > *"MTTR of 12 minutes against an RTO of 5 is a breach on every incident. I'd break MTTR into detection, response, diagnosis, and fix to find where the time goes. For a 5-minute RTO, no human can be in the loop — automated failover is the only answer. Detect failure, promote replica, reroute traffic — all automated. Engineer investigates root cause after service is restored, not before."*
