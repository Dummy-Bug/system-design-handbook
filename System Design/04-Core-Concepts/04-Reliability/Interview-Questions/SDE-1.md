# Reliability — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of reliability, MTBF, MTTR, RTO, RPO, and how reliability differs from availability. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is Reliability?

> [!question] What is reliability, and how is it different from availability?

> [!success]- Answer
>
> **Reliability** is whether a system returns **correct answers** consistently over time.
>
> **Availability** is whether a system **responds at all**.
>
> ```
> Available but unreliable:
>   Product prices showing $0       → 200 OK, available ✓, reliable ✗
>   Search returning wrong results  → 200 OK, available ✓, reliable ✗
>   Messages arriving out of order  → 200 OK, available ✓, reliable ✗
>
> Unavailable but (potentially) reliable:
>   DB crash → no response → unavailable ✗
>   But the data on disk is intact → reliable ✓
> ```
>
> A simple ping or health check tells you if the system is **available**. It tells you nothing about whether the responses are **correct**.
>
> > [!important] Availability asks "is it responding?" Reliability asks "can you trust what it returns?" A system can fail reliability while passing every availability check.
>
> > [!tip] Interview framing
> > *"Availability is uptime — is the system responding? Reliability is correctness — is it responding with the right answer? The hardest failures are Byzantine: the system looks healthy in monitoring but is producing wrong results."*

---

## Q2 — MTBF and MTTR

> [!question] What are MTBF and MTTR? How do they connect to availability?

> [!success]- Answer
>
> **MTBF — Mean Time Between Failures:**
> How long the system runs on average before something breaks.
> ```
> MTBF = Total operational time / Number of failures
>
> System ran 300 hours, failed 3 times
> MTBF = 300 / 3 = 100 hours
> ```
> Higher MTBF = the system breaks less often.
>
> **MTTR — Mean Time To Recovery:**
> When something breaks, how long until it's working again.
> ```
> MTTR = Total downtime / Number of failures
>
> 3 failures, each took 30 minutes to fix
> MTTR = 90 / 3 = 30 minutes per failure
> ```
> Lower MTTR = you recover faster.
>
> **The availability connection:**
> ```
> Availability = MTBF / (MTBF + MTTR)
>
> MTBF = 100 hours, MTTR = 1 hour
> → 100 / 101 = 99% availability
> ```
>
> **Two completely different engineering strategies:**
> ```
> Improve MTBF → prevent failures (testing, chaos engineering, canary deploys)
> Improve MTTR → recover faster (automated alerts, runbooks, auto-rollback)
>
> Netflix approach: accept low MTBF, invest heavily in near-zero MTTR
> ```
>
> > [!tip] Interview framing
> > *"MTBF is how often you fall down. MTTR is how fast you get back up. Both feed directly into availability. At scale, improving MTTR is often more cost-effective than eliminating every possible failure."*

---

## Q3 — RTO and RPO

> [!question] What are RTO and RPO? Give me a one-line definition and an example for each.

> [!success]- Answer
>
> **RTO — Recovery Time Objective:**
> The maximum acceptable time the system can be down after a failure.
> ```
> RTO = 15 minutes
> → if the DB crashes at 3am, the system must be serving traffic again by 3:15am
> ```
>
> **RPO — Recovery Point Objective:**
> The maximum acceptable amount of data loss after a failure.
> ```
> RPO = 1 hour
> → if the DB crashes at 3am, we can tolerate losing up to 1 hour of writes
>    (last backup was at 2am)
> ```
>
> **How they drive architecture:**
>
> | RTO | Architecture required |
> |---|---|
> | Hours | Restore from backup |
> | Minutes | Warm standby — secondary ready but idle |
> | Seconds | Hot standby — Active-Passive with automated failover |
> | Zero | Active-Active multi-region |
>
> | RPO | Architecture required |
> |---|---|
> | 24 hours | Daily backups |
> | 1 hour | Hourly snapshots |
> | Minutes | Async replication |
> | Zero | Synchronous replication |
>
> > [!important] RTO drives your recovery architecture. RPO drives your replication and backup strategy. Ask both during requirements — they're the two questions that tell you what to build.
>
> > [!tip] Interview framing
> > *"RTO is how long you can be down. RPO is how much data you can lose. I'd ask both during requirements — an RPO of zero forces synchronous replication and higher write latency. An RTO of seconds forces automated failover with a hot standby."*

---

## Q4 — The Reliability SLI

> [!question] Your team tracks request success rate as the main SLI. Your SLI is 99.9%. A bug causes the payment service to process charges twice for every order. The SLI doesn't change. Why not, and what should you track instead?

> [!success]- Answer
>
> **Why the SLI doesn't change:**
> Request success rate only measures whether requests completed without an error. A double-charge still returns HTTP 200 — it's a successful response from the server's perspective. The availability SLI sees nothing wrong.
>
> **This is a reliability failure, not an availability failure:**
> ```
> Availability SLI:  % of requests returning 2xx        → still 99.9% ✓
> Reliability SLI:   % of requests returning correct result → broken ✗
> ```
>
> **What to track instead:**
> For a payment service, reliability-specific SLIs might include:
> ```
> Idempotency rate   → % of charges that match expected amount
> Duplicate charge rate → # of orders charged more than once / total orders
> Business reconciliation → compare charges processed vs orders placed
> Synthetic transactions → known test orders, verify exact charge matches
> ```
>
> The key insight: **reliability SLIs require knowing what the correct answer is**. Availability monitoring is easy — just check for errors. Reliability monitoring requires defining correctness.
>
> > [!important] Availability SLIs (success rate, uptime) cannot detect semantic failures. Reliability requires knowing the expected output and verifying the actual output matches it.
>
> > [!tip] Interview framing
> > *"Request success rate is an availability SLI — it measures whether the system responded, not whether the response was correct. For reliability I'd add business-level SLIs: duplicate charge rate, reconciliation between charges and orders, synthetic test transactions with known expected outputs."*

---

## Q5 — Improving MTTR

> [!question] Your service fails once a month on average (MTBF = 30 days). Each incident takes 2 hours to resolve (MTTR = 2 hours). What are three specific things you'd do to reduce MTTR?

> [!success]- Answer
>
> **Current availability:**
> ```
> Availability = 720 / (720 + 2) = 99.72%
> ```
>
> **Three ways to reduce MTTR:**
>
> **1. Automated alerting — detect instantly:**
> ```
> Without: incident occurs → someone notices → files a ticket → on-call paged
>          time to detection: 10-30 minutes
>
> With:    error rate > 1% for 60 seconds → PagerDuty fires automatically
>          time to detection: under 2 minutes
> ```
>
> **2. Runbooks — eliminate improvisation:**
> ```
> Without: engineer on-call at 2am, guessing steps under pressure
>          diagnosis: 30-60 minutes
>
> With:    pre-written runbook for each known failure type
>          "DB connections maxed: step 1 → check connection pool, step 2 → ..."
>          diagnosis + fix: 5-10 minutes
> ```
>
> **3. Automated rollback — instant recovery for bad deploys:**
> ```
> Without: bad deploy detected → manually revert → test → deploy old version
>          30-60 minutes of manual steps
>
> With:    deploy monitor sees error rate spike → triggers automatic rollback
>          MTTR for deploy-related incidents: under 5 minutes
> ```
>
> **Impact:**
> ```
> MTTR drops from 2 hours to ~15 minutes
> Availability = 720 / (720 + 0.25) = 99.97%
> ```
>
> > [!tip] Interview framing
> > *"MTTR improvement is more cost-effective than MTBF improvement at scale. Three specific levers: automated alerting to eliminate detection lag, runbooks to eliminate improvisation under pressure, and automated rollback to turn deploy incidents from 60-minute manual processes into 5-minute automatic recoveries."*
