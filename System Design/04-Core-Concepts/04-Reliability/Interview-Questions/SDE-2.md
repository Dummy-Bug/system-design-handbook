# Reliability — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around RTO/RPO, recovery strategies, reliability SLIs, and MTTR reduction at scale. Expected at SDE-2 level.

---

## Q1 — Designing for RTO and RPO

> [!question] You're designing a payments database. The business says RTO = 30 seconds and RPO = 0. What architecture does this force and what are the trade-offs?

> [!success]- Answer
>
> **What the requirements mean:**
> ```
> RTO = 30 seconds → if the DB crashes, must be serving traffic again within 30 seconds
> RPO = 0          → zero data loss — every confirmed write must survive the failure
> ```
>
> **What RPO = 0 forces:**
> ```
> Synchronous replication — primary must wait for replica to confirm every write
>                           before acknowledging to the client
>
> Client writes → primary writes → replica confirms → primary responds ✓
>
> If primary crashes between primary write and replica confirm:
>   Write never confirmed to client → client retries → no data loss
>
> Trade-off: higher write latency
>   Primary write: 5ms
>   Replica confirmation (same AZ): +1-5ms
>   Total write latency: 6-10ms instead of 5ms
> ```
>
> **What RTO = 30 seconds forces:**
> ```
> Automated failover — no human can detect, respond, and promote a replica in 30s
>
> Hot standby (Active-Passive):
>   Replica stays in sync via synchronous replication
>   Sentinel / Patroni monitors primary health
>   Primary failure detected → replica promoted automatically → ~10-20 seconds
>   Client connections rerouted via DNS TTL or connection pool → within 30s
> ```
>
> **Full architecture:**
> ```
> Primary DB ←→ Synchronous Replica (same AZ)
>               Health monitor (Patroni/Sentinel)
>               On failure: auto-promote replica → update DNS → done
> ```
>
> **What you're trading:**
> ```
> RPO = 0   → every write pays sync replication latency (small but real)
> RTO = 30s → costs: dedicated standby instance, monitoring infrastructure
>
> If replica is in another AZ: sync replication adds ~2-5ms per write
> If cross-region:             sync adds ~70-200ms per write — may be unacceptable
> ```
>
> > [!tip] Interview framing
> > *"RPO = 0 forces synchronous replication — primary waits for replica confirm before responding. RTO = 30s forces automated failover — hot standby with Patroni/Sentinel, promotes in under 20 seconds. Trade-off: sync replication adds write latency. For cross-region, that latency may be prohibitive — you'd accept a small RPO instead."*

---

## Q2 — Separate Availability and Reliability SLIs

> [!question] Your service SLI shows 99.95% availability but your VP says "users are complaining the service is unreliable." What SLIs are you missing and how do you add them?

> [!success]- Answer
>
> **The gap:**
> ```
> Current SLI: % of requests returning 2xx (availability)
>              → measures: did the system respond?
>              → does NOT measure: was the response correct?
>
> "Users complaining about unreliability" = wrong data, wrong behavior
>              → availability SLI is blind to this
> ```
>
> **What to add — reliability-specific SLIs:**
>
> **1. Error rate by type:**
> ```
> Not all 2xx are healthy. Track:
>   → 2xx with empty response body (should have content)
>   → 2xx with malformed JSON
>   → 5xx (server errors — system failed to process correctly)
>
> SLI: % of requests with valid, non-empty, correct-format response
> ```
>
> **2. Business metrics as SLIs:**
> ```
> Payment service:
>   Duplicate charge rate: # orders charged >1 time / total orders
>   Failed payment reconciliation: charges don't match order amounts
>
> E-commerce:
>   Cart total accuracy: calculated total matches line item sum
>   Inventory accuracy: items oversold rate
> ```
>
> **3. Synthetic transactions:**
> ```
> Run known test scenarios continuously:
>   "Place order with $50 item, expect charge of $50"
>   "Search for 'headphones', expect >0 results"
>   "Update username to X, immediately read profile, expect X"
>
> If synthetic transaction fails → reliability SLI degrades
> Detects semantic bugs that look healthy in infrastructure monitoring
> ```
>
> **4. User-reported error rate:**
> ```
> Track: # of support tickets with "wrong data" complaints
>        # of chargebacks / disputes
>        # of "my order is missing" reports
>
> These are ground-truth reliability signals
> ```
>
> > [!tip] Interview framing
> > *"Availability SLIs measure whether the system responds — not whether it's correct. I'd add: business-level SLIs (duplicate charge rate, cart accuracy), synthetic transactions (known input, verified output), and user-facing error tracking. These catch semantic failures that infrastructure monitoring misses entirely."*

---

## Q3 — Balancing MTBF and MTTR Investment

> [!question] Your engineering team has limited capacity. You can invest in either reducing failure rate (MTBF) or improving recovery speed (MTTR). Which do you prioritize and why?

> [!success]- Answer
>
> **The math:**
> ```
> Current: MTBF = 200 hours, MTTR = 4 hours
> Availability = 200 / (200 + 4) = 98%
>
> Option A: Double MTBF (fewer failures)
>   MTBF = 400 hours, MTTR = 4 hours
>   Availability = 400 / 404 = 99%
>
> Option B: Halve MTTR (faster recovery)
>   MTBF = 200 hours, MTTR = 2 hours
>   Availability = 200 / 202 = 99%
>
> Same availability improvement — but which is more valuable?
> ```
>
> **Why MTTR investment is usually more cost-effective:**
>
> **1. Diminishing returns on MTBF:**
> ```
> Eliminating the first 50% of failures: relatively easy (fix common bugs, add tests)
> Eliminating the next 25%: much harder (edge cases, hardware failures)
> Eliminating the last 10%: extremely hard (cosmic rays, DC floods, zero-days)
>
> Each MTBF improvement costs exponentially more
> ```
>
> **2. MTTR improvements are achievable and high-leverage:**
> ```
> Better alerting (PagerDuty, sub-minute detection): weeks of work, huge impact
> Runbooks for top 5 failure modes: days of work, eliminates improvisation
> Automated rollback for bad deploys: weeks of work, instant recovery
>
> These are mostly tooling and process — not hard engineering problems
> ```
>
> **3. Netflix philosophy:**
> Netflix's chaos engineering deliberately lowers MTBF — by breaking things in production. This forces MTTR to near-zero. A system that recovers in seconds can fail frequently and still be highly available.
>
> **When to prioritize MTBF instead:**
> ```
> Safety-critical systems: planes, medical devices, nuclear
>   → MTTR of "minutes" is unacceptable even once
>   → MTBF must be extremely high
>
> Early-stage: before monitoring is in place
>   → Can't improve MTTR if you can't detect failures
>   → Fix the worst failure modes first
> ```
>
> > [!tip] Interview framing
> > *"MTTR first for most systems — automated alerting, runbooks, and automated rollback are achievable investments with big availability impact. MTBF improvement gets exponentially expensive. Exception: safety-critical systems where even one failure is unacceptable."*

---

## Q4 — RTO vs RPO Trade-off

> [!question] A startup says "our RTO is 4 hours and our RPO is 24 hours." What does this tell you about their architecture, and under what conditions would these be acceptable?

> [!success]- Answer
>
> **What these numbers imply:**
> ```
> RTO = 4 hours → when DB crashes, restore manually → 4 hours before serving traffic
>                  architecture: restore from backup + restart
>                  manual process, no automated failover
>
> RPO = 24 hours → last backup was yesterday midnight
>                   up to 24 hours of data loss on failure
>                   architecture: daily full backup
>                   no incremental backups, no real-time replication
> ```
>
> **This is the cheapest possible architecture:**
> ```
> Single DB instance
> Daily backup to S3 (or similar cold storage)
> No replicas, no hot standby, no Sentinel
>
> Total extra cost: storage for backups (pennies/GB/month)
> Recovery: manual restore → restart → DNS update → verify
> ```
>
> **When is this acceptable?**
> ```
> Internal admin tool:        4h downtime? IT team is annoyed, not catastrophic
> Dev/staging environment:    24h data loss? Acceptable — it's test data
> Content-only website:       4h downtime during maintenance? Users wait
>
> When is it NOT acceptable:
> Any system storing financial transactions → 24h data loss = potentially millions lost
> SaaS with SLA commitments → 4h downtime = SLA breach + customer credits
> E-commerce → 4h downtime during business hours = significant revenue loss
> ```
>
> **The business question to ask:**
> ```
> What is 1 hour of downtime worth in lost revenue?
> What is 1 day of data loss worth in customer and financial impact?
>
> If the answer is "millions" → this architecture is unacceptable
> If the answer is "we'd be embarrassed but not catastrophically harmed" → acceptable
> ```
>
> > [!tip] Interview framing
> > *"RTO 4h + RPO 24h is backup-only architecture — no replicas, manual restore. Cheapest possible option. Acceptable for internal tools, dev environments, and low-traffic non-critical services. Not acceptable for anything with financial data or an SLA. The design choice follows from the cost of downtime and data loss, not from arbitrary standards."*

---

## Q5 — Reliability in a Microservices System

> [!question] You have a service with 99.9% reliability. It depends on 5 microservices, each with 99.9% reliability. What is your end-to-end reliability, and how do you fix it?

> [!success]- Answer
>
> **The math:**
> ```
> Sequential dependencies — all 5 must work correctly for a request to succeed:
>
> 99.9% × 99.9% × 99.9% × 99.9% × 99.9% × 99.9% (including your service)
> = 0.999^6 = 0.994 = 99.4%
>
> You promised 99.9% — you're delivering 99.4%
> ```
>
> **Why this happens:**
> Each service has a 0.1% chance of failure. Six sequential chances to fail.
>
> **Fix 1 — Graceful degradation for non-critical dependencies:**
> ```
> Of the 5 dependencies, classify each:
>   Critical (request cannot complete without it) → 2 services
>   Non-critical (request degrades but succeeds without it) → 3 services
>
> Remove non-critical services from the success calculation:
>   99.9% × 99.9% × 99.9% (you + 2 critical dependencies)
>   = 99.7% — much better
>
> For non-critical: circuit breaker → return fallback → service still "succeeds"
> ```
>
> **Fix 2 — Improve reliability of critical dependencies:**
> ```
> Your service's reliability ceiling = weakest critical dependency
>
> Work with dependency teams: their SLI must be stricter than your SLO
>   Your SLO: 99.9% → dependencies must be at least 99.95%
>   99.95% × 99.95% × 99.9% ≈ 99.8% — approaching your SLO
> ```
>
> **Fix 3 — Caching dependency responses:**
> ```
> Some responses don't need to be real-time:
>   User profile data → cache 5 minutes → serve from cache if service down
>   Permission data   → cache 1 minute → serve from cache during blip
>
>   Cache hit during dependency failure → request succeeds ✓
> ```
>
> > [!tip] Interview framing
> > *"Six services at 99.9% each = 99.4% end-to-end — well below the 99.9% SLO. Fix: classify dependencies as critical vs non-critical. Non-critical ones get circuit breakers and fallbacks — removed from the multiplication. Critical ones must have stricter SLOs than your own. Cache frequently-read dependency data to survive blips."*
