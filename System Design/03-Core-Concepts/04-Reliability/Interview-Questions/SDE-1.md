# Reliability — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of MTBF, MTTR, RTO, RPO, snapshots vs replicas, and replication trade-offs. Every SDE candidate is expected to answer these confidently.

---

> [!question] What is MTBF and MTTR? Give a one-line definition for each.

> [!success]- Answer
>
> **MTBF — Mean Time Between Failures:**
> How long your system runs on average before something breaks.
>
> **MTTR — Mean Time To Recovery:**
> How long it takes to restore service after something breaks — detection + diagnosis + fix + deploy + verify.
>
> ```
> MTBF = Total uptime / Number of failures
>
> System up for 300 hours, failed 3 times
> MTBF = 300 / 3 = 100 hours between failures
>
> MTTR = Total downtime / Number of failures
>
> 3 failures, each took 30 minutes to fix
> MTTR = 90 / 3 = 30 minutes per failure
> ```

---

> [!question] How do MTBF and MTTR connect to availability? Give me the formula.

> [!success]- Answer
>
> ```
> Availability = MTBF / (MTBF + MTTR)
>
> MTBF = 99 hours, MTTR = 1 hour
> Availability = 99 / (99 + 1) = 99/100 = 99%
> ```
>
> **Why increasing MTBF still improves availability even though the denominator also increases:**
>
> The cleaner way to see it is to rewrite the formula:
> ```
> Availability = 1 / (1 + MTTR/MTBF)
> ```
>
> What drives availability is the **ratio** of MTTR to MTBF — not their absolute values. As MTBF grows, MTTR/MTBF shrinks — MTTR becomes a smaller and smaller fraction of the whole. Availability climbs toward 1.
>
> Two completely different strategies to improve availability:
> ```
> Increase MTBF → system breaks less often  → MTTR/MTBF shrinks
> Decrease MTTR → system recovers faster    → MTTR/MTBF shrinks
> ```
>
> > [!tip] Interview framing
> > *"Availability is driven by the ratio of MTTR to MTBF. You can improve it by breaking less often — higher MTBF — or recovering faster — lower MTTR. Netflix focuses almost entirely on MTTR: break things constantly in production and drive recovery time to near-zero rather than trying to prevent every failure."*

---

> [!question] What is RTO? If someone says "our RTO is 4 hours" — does that mean 4 hours per month, per year, or per incident?

> [!success]- Answer
>
> **RTO — Recovery Time Objective:**
> The maximum time your system can be down per incident — from the moment of failure until service is fully restored.
>
> RTO is a **per-incident** budget, not monthly or annual.
>
> ```
> "RTO = 4 hours" means:
> → Database dies at 3pm
> → You must be fully restored by 7pm
> → That single failure event
>
> Not: "4 hours of downtime allowed this month"
> Not: "4 hours across the year"
> ```
>
> > [!important] RTO and availability nines are different measurements. Availability (99.9% = 43 min/month) is a cumulative monthly budget. RTO is a per-incident ceiling. You need both: availability tells you how often you can fail, RTO tells you how fast you must recover each time.

---

> [!question] What is RPO? What's the difference between RTO and RPO?

> [!success]- Answer
>
> **RPO — Recovery Point Objective:**
> The maximum amount of **data** you can afford to lose per incident, measured as a time window.
>
> ```
> RTO = how long can the system be DOWN       → time to restore service
> RPO = how much DATA can we afford to lose   → time window of acceptable data loss
> ```
>
> Concrete example:
> ```
> Database dies at 3pm. Last snapshot was at 2pm.
>
> RPO = 1 hour → orders placed 2pm–3pm are gone. Acceptable.
> RPO = 0      → zero data loss. Every write must survive.
> ```

---

> [!question] RTO = 4 hours vs RTO = 30 seconds — what are you actually running differently in each case?

> [!success]- Answer
>
> They are completely different architectures, not just different speeds of the same thing.
>
> **RTO = 4 hours → snapshot restore path:**
> ```
> No live replica needed.
> Primary dies → spin up a new server → pull snapshot from S3 → restore → verify → back online
> Takes hours. Acceptable when the business can tolerate the downtime.
> ```
>
> **RTO = 30 seconds → replica promotion path:**
> ```
> A live replica is already running on a separate machine, continuously syncing.
> Primary dies → promote replica to primary → redirect traffic → done
> Takes seconds. No restore needed — the data is already there.
> ```
>
> ```
> RTO = hours    → snapshot restore (cheap infrastructure, slow recovery)
> RTO = minutes  → warm standby replica (idle, manual promotion)
> RTO = seconds  → hot standby replica (live, automated promotion)
> RTO = 0        → active-active (no failover needed at all)
> ```
>
> > [!tip] Interview framing
> > *"RTO = 4 hours means we're on the snapshot path — no live replica, spin up from scratch. RTO = 30 seconds means we have a live replica with automated failover. Two completely different architectures. I'd ask for the RTO before designing — it determines everything about the standby strategy."*

---

> [!question] You have a replica with async replication. Primary dies. Can you still lose data? Why?

> [!success]- Answer
>
> **Yes — because of replication lag.**
>
> With async replication, the primary ACKs the write to the user immediately, then replicates to the replica in the background.
>
> ```
> User writes → Primary writes → ACKs user ✓
>                    ↓ (background, slight delay)
>               Replica receives write
>
> Primary dies while some writes are in-flight (not yet replicated):
> → Those writes exist on primary only
> → Primary is dead → writes are lost forever
> → RPO = the size of the replication lag window (typically seconds)
> ```
>
> This is why async replication gives RPO of seconds, not zero.

---

> [!question] When would you switch to sync replication, and what does it cost?

> [!success]- Answer
>
> **When to use sync:**
> Critical systems where data loss is unacceptable and write latency is a secondary concern.
> ```
> Financial transactions  → every cent must survive
> Billing records         → double charges or lost charges = disaster
> Medical records         → legal requirement, no loss acceptable
>
> Analytics events        → losing a few events is fine → async is better
> Ad click logs           → minor inaccuracy tolerable  → async is better
> ```
>
> **The cost:**
> With sync replication, the write is not ACKed to the user until **both** the primary and the replica have confirmed it. Your write latency is now determined by the slowest replica in the chain.
>
> ```
> Same datacenter replica:    +1–5ms per write   → manageable
> Cross-datacenter replica:   +50–100ms per write → painful
> ```
>
> Speed of light is the hard limit. If your replica is in another datacenter, every single write pays a 50–100ms round-trip tax.
>
> At 100,000 writes/sec, adding 100ms to every write means:
> - Users feel every interaction slow down
> - Queue backlogs build up under load
> - Timeouts start cascading
>
> This is why sync replication is reserved only for data where loss is truly unacceptable. For everything else — async replication with an acceptable RPO window is the right call.
>
> > [!important] There is no free option. Async replication = fast writes, small data loss window. Sync replication = zero data loss, higher write latency. The business decides which cost is acceptable based on the data's criticality.
>
> > [!tip] Interview framing
> > *"For billing and financial data I'd use sync replication — RPO = 0, accept the write latency. For analytics and event data I'd use async — RPO of a few seconds is fine and write latency stays low. Same cluster, different replication mode per topic based on how much that data's loss would hurt."*
