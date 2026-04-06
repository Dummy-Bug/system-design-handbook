# Availability — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of availability, reliability, nines, SPOFs, and downtime. Every SDE candidate is expected to answer these confidently.

---

> [!question] What is availability? Give me a one-line definition and tell me how it's measured.

> [!success]- Answer
>
> **Definition:**
> Availability is the percentage of time a system is operational and successfully serving requests.
>
> **How it's measured:**
> ```
> Availability = Uptime / (Uptime + Downtime) × 100
>
> System up 43,157 min out of 43,200 min in a month
> → 43,157 / 43,200 × 100 = 99.9%
> ```
>
> > [!important] A system can be "responding" but not available — returning 500 errors, timing out, or serving corrupted data. Availability specifically means successfully serving requests, not just being reachable.
>
> > [!tip] Interview framing
> > *"Availability is the percentage of time a system is operational and successfully serving requests. Measured as uptime divided by total time (uptime + downtime) × 100."*

---

> [!question] What is the difference between availability and reliability? They sound the same — convince me they're not.

> [!success]- Answer
>
> **The core difference:**
>
> | | Question it answers | Example |
> |---|---|---|
> | **Availability** | Is the system up? | System responds to requests |
> | **Reliability** | Can you trust what it returns? | System returns correct responses |
>
> A system can be 100% available but completely unreliable:
> ```
> All products showing $0 price    → available ✓, reliable ✗
> Search returning random results  → available ✓, reliable ✗
> Writes silently dropped          → available ✓, reliable ✗
> ```
>
> **Byzantine failures** are the hardest case — the system is up, looks healthy in monitoring, but is producing wrong results. Detecting availability is easy — just ping it. Detecting reliability requires knowing what the correct answer should be.
>
> > [!important] Availability asks — is it up? Reliability asks — can you trust it? A system can fail reliability while passing every availability check.
>
> > [!tip] Interview framing
> > *"Availability is about uptime — is the system responding? Reliability is about correctness — is it responding with the right answer? Byzantine failures are the hardest case — the system is up and looks healthy but producing wrong results. Monitoring availability is easy, monitoring reliability requires knowing what correct looks like."*

---

> [!question] What are the "nines" of availability? Why is the jump from 99.9% to 99.99% much harder than from 99% to 99.9%?

> [!success]- Answer
>
> **The nines:**
>
> | SLO | Downtime/month | Downtime/year |
> |---|---|---|
> | 99% | ~7.2 hours | ~3.65 days |
> | 99.9% | ~43 minutes | ~8.7 hours |
> | 99.99% | ~4.3 minutes | ~52 minutes |
> | 99.999% | ~26 seconds | ~5 minutes |
>
> **Why each additional nine is exponentially harder:**
>
> Each nine reduces the error budget by 10x. But the real reason it's harder is operational:
>
> ```
> 99.9%  → 43 min/month → human detects alert → responds → fixes → deploys
>                          manual on-call process works fine
>
> 99.99% → 4.3 min/month → no human can respond in 4.3 minutes
>                           requires fully automated detection + failover + recovery
>
> 99.999% → 26 sec/month → even automated systems struggle
>                           requires self-healing infrastructure
> ```
>
> The jump isn't just a smaller number — it requires a completely different class of engineering. Manual processes work at 99.9%. At 99.99% everything must be automated.
>
> > [!tip] Know 99.9% = 43 min/month and 99.99% = 4.3 min/month off the top of your head. Interviewers ask this regularly.

---

> [!question] What is the difference between planned and unplanned downtime? Should planned downtime count against your availability SLO?

> [!success]- Answer
>
> **The difference:**
> ```
> Planned downtime   → scheduled maintenance, communicated in advance
>                      DB migration, infrastructure upgrade, deployment window
>
> Unplanned downtime → unexpected failure
>                      bug, hardware failure, traffic spike, cascading failure
> ```
>
> **Should planned downtime count against SLO?**
>
> From the user's perspective — yes. The service is unavailable regardless of why. A customer who can't checkout at 2am during your maintenance window has the same experience as one who can't checkout during an outage.
>
> Some SLAs explicitly exclude scheduled maintenance windows with strict constraints:
> ```
> "Scheduled maintenance (max 4 hours/month,
>  48 hours advance notice) excluded from calculations"
> ```
>
> But the best answer — **design for zero-downtime deployments** so the question becomes irrelevant:
> ```
> Rolling deployments   → update one instance at a time, others serve traffic
> Blue-green deployment → switch traffic between two identical environments
> Canary releases       → route small % to new version, expand gradually
> ```
>
> > [!tip] Interview framing
> > *"Planned downtime should count against SLO — from the user's perspective downtime is downtime. If you must exclude it, define strict constraints in the SLA. But the best systems achieve zero-downtime deployments — rolling, blue-green, canary — so planned downtime doesn't exist."*

---

> [!question] Your service has a single database. It goes down — your entire service goes down. What is this called and what's the solution?

> [!success]- Answer
>
> **What it's called:** Single Point of Failure — SPOF.
>
> Any component where failure causes complete system failure is a SPOF. A single database is the most common one.
>
> **The solution — redundancy:**
> Add replicas. But replicas alone aren't enough — you need three things:
>
> ```
> 1. Replicas          → copies of data on standby nodes
> 2. Automatic failover → when primary dies, replica promotes automatically
> 3. Leader election   → mechanism to choose which replica becomes primary
>                        (Sentinel for Redis, Patroni for Postgres, built into RDS)
> ```
>
> Without automatic failover, replicas require manual intervention — during which your service is still down.
>
> **SPOF exists at every layer:**
> ```
> Single DB           → add replicas + automatic failover
> Single app server   → horizontal scaling + load balancer
> Single load balancer → multiple LBs + DNS failover  ← most commonly missed
> Single data centre  → multi-region deployment
> ```
>
> Availability engineering is systematically finding and eliminating SPOFs one layer at a time.
>
> > [!important] The load balancer is the most commonly missed SPOF in interviews. Multiple app servers behind a single LB — the LB itself is still a SPOF.
>
> > [!tip] Interview framing
> > *"A single database is a SPOF — Single Point of Failure. Solution is redundancy: add replicas with automatic failover and leader election so when primary dies, a replica promotes without human intervention. Every layer can be a SPOF — DB, app servers, load balancer, data centre. Availability work is finding and eliminating each one."*
