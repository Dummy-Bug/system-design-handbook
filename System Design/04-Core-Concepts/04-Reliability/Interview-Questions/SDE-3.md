# Reliability — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions testing reliability program design, chaos engineering, organizational reliability culture, and complex trade-offs. SDE-3 level — no single right answer, just structured thinking.

---

## Q1 — Building a Reliability Program from Scratch

> [!question] You've joined a company where "reliability" means "try not to break things." No SLOs, no RTO/RPO, no blameless post-mortems. How do you build a reliability program from scratch?

> [!success]- Answer
>
> **The biggest mistake: starting with tools instead of culture**
>
> Reliability programs fail when engineering leads with Prometheus dashboards and on-call rotations. The real work is cultural: convincing product and leadership that reliability is a feature, not a tax.
>
> **Phase 1 — Make failures visible (weeks 1-4):**
> ```
> You can't fix what you can't measure
>
> Step 1: instrument everything
>   Error rates, latency percentiles, uptime per service
>   Doesn't require any new tooling — add logging, connect to existing metrics
>
> Step 2: observe without targets
>   4-6 weeks of measurement before setting any SLOs
>   Let data tell you what the system actually does
>   Surprises are common: "I thought we were 99.9%, we're actually 99.3%"
>
> Step 3: share the data with leadership
>   "We were down for 4.2 hours this month — here's the business impact"
>   Translate uptime to dollars or user impact
>   This creates the business case for investment
> ```
>
> **Phase 2 — Define SLOs from baselines (month 2):**
> ```
> Deliberately loose initial SLOs:
>   System is actually at 99.4%? Set SLO at 99.0%
>   Gives error budget to work with
>   Success builds credibility — don't start by promising 99.9%
>
> RTO and RPO for critical services:
>   Ask product: "How long can service X be down?"
>   Ask finance: "How much data loss is acceptable for payments?"
>   Now you have targets to engineer toward
> ```
>
> **Phase 3 — Blameless post-mortems (start immediately):**
> ```
> Every significant incident gets a post-mortem
>
> Blameless format:
>   Timeline: what happened and when
>   Contributing factors: what conditions made this possible
>   Action items: what systemic changes prevent recurrence
>
>   NOT: "who made the mistake"
>   NOT: punishment for being on-call during an incident
>
> Cultural shift: incidents are learning opportunities, not career risks
>   Engineers who fear blame hide problems → creates bigger problems
>   Engineers who feel safe reporting → surface problems early
> ```
>
> **Phase 4 — Error budget policies:**
> ```
> Budget nearly exhausted → feature releases freeze, reliability work prioritized
> This is the mechanism that converts SLOs from aspirational to operational
>
> Must be agreed by product AND engineering before any budget crunch happens
> Budget crunch is the wrong time to negotiate this policy
> ```
>
> > [!tip] Interview framing
> > *"Start with measurement, not tooling. Four to six weeks of data before any targets. Use data to build the business case. Set deliberately loose initial SLOs. Blameless post-mortems from day one — the cultural shift is more important than any metric. Error budget policies must be pre-agreed, not negotiated during an incident."*

---

## Q2 — Chaos Engineering Program

> [!question] Your CTO asks you to propose a chaos engineering program. What is it, why does it matter, and how do you roll it out without causing customer harm?

> [!success]- Answer
>
> **What chaos engineering is:**
> ```
> Deliberately introducing failures into your system to:
>   1. Discover weaknesses before they manifest in production unexpectedly
>   2. Verify that reliability mechanisms (failover, circuit breakers) actually work
>   3. Drive MTTR to near-zero by forcing recovery practice
>
> Netflix's premise: failures are inevitable at scale
>   Don't try to eliminate all failures (exponentially expensive)
>   Instead: fail constantly in controlled ways → build muscle memory for recovery
>            MTTR becomes near-zero → system highly available despite frequent failures
> ```
>
> **Why it matters:**
> ```
> Your failover has never failed over in production:
>   The runbook is 18 months old and the person who wrote it left
>   The replica fell behind while nobody noticed
>   DNS TTL is actually 300 seconds, not 30
>
>   You won't know until a real incident — at 3am, under pressure, for real customers
>
> Chaos engineering:
>   Tests these assumptions during business hours, with engineers watching
>   Finds the gaps before customers do
> ```
>
> **Rollout — minimum blast radius:**
> ```
> Stage 1: canary environment (no customer impact)
>   Kill random processes → does the service restart?
>   Introduce 100ms latency → do circuit breakers trip?
>   Kill a DB replica → does Sentinel promote correctly?
>
> Stage 2: production, off-peak hours, small scope
>   Kill one app server (out of 20) → does load balancer reroute?
>   Stop replication for 30 seconds → does system detect and alert?
>
> Stage 3: production, business hours, with full observability
>   Requires: clear abort criteria ("if error rate > 1%, stop immediately")
>   Requires: dedicated monitoring during the experiment
>   Requires: rollback plan ready before starting
>
> Stage 4: automated continuous chaos (Netflix's Chaos Monkey)
>   Only with high confidence in recovery mechanisms
>   Not for most organizations starting out
> ```
>
> **Key guardrails:**
> ```
> Never in production without:
>   Clear hypothesis: "We believe killing one DB replica will trigger Sentinel failover in < 30s"
>   Clear metric: what are we measuring?
>   Abort criterion: what stops the experiment automatically?
>   Business hours + engineers watching: not scheduled for Friday 4pm
> ```
>
> > [!tip] Interview framing
> > *"Chaos engineering finds the reliability gaps before customers do. Start in canary environments, move to off-peak production, then business hours with guardrails. Every experiment needs a hypothesis, a metric, and an abort criterion. The goal is driving MTTR to near-zero through practiced recovery — not creating outages."*

---

## Q3 — Reliability in a Microservices Architecture

> [!question] You have 50 microservices. Each has 99.5% reliability. A user request touches 10 services sequentially. What is the end-to-end reliability and how do you get to 99.9% without rewriting every service?

> [!success]- Answer
>
> **The math:**
> ```
> 0.995^10 = 0.951 = 95.1% end-to-end reliability
>
> 95.1% means: 1 in 20 user requests fails on average
> This is catastrophic for a user-facing product
> ```
>
> **How to get to 99.9% without rewriting 50 services:**
>
> **Step 1 — Classify the 10 dependencies:**
> ```
> Are all 10 truly required for every request?
>
> 4 critical (request cannot succeed without them):
>   Auth, product catalog, inventory, payments
>
> 6 non-critical (request degrades gracefully without them):
>   Recommendations, A/B testing, analytics, enrichment services, notifications, logging
>
> For non-critical: implement circuit breaker + fallback
>   0.995^4 = 0.980 = 98.0% — much better
>   Still not 99.9%, but progress
> ```
>
> **Step 2 — Caching for critical dependencies:**
> ```
> Product catalog: rarely changes → cache aggressively
>   If catalog service is down: serve from cache
>   Stale for 5 minutes → acceptable for browse
>   Cache hit rate: 95% → catalog service rarely in critical path
>
>   Effective reliability for this hop: ~99.9% (cache + live service)
>
> Auth service: tokens can be cached (short-lived, within expiry)
>   JWT: verify signature locally, no auth service call needed
>   Auth service only needed for token refresh
> ```
>
> **Step 3 — Async for non-critical work:**
> ```
> Analytics, logging, notifications: fire-and-forget
>   Request completes → response returned to user
>   Background: publish to Kafka → downstream services consume asynchronously
>
>   These services are now off the critical path entirely
>   Their reliability doesn't affect the user-facing reliability calculation
> ```
>
> **Step 4 — Service mesh or API gateway reliability:**
> ```
> Automatic retry with idempotency checking
> Automatic timeout enforcement
> Circuit breaking at infrastructure layer
>
>   Developer doesn't need to implement these — platform does it automatically
> ```
>
> **The result:**
> ```
> Critical path: 4 services (auth/JWT local, catalog from cache, inventory, payments)
>   0.999 × 0.999 × 0.995 × 0.999 ≈ 99.2%
>
> Good, but still short of 99.9%
> Final step: each critical service's SLO must be 99.97%+ 
>   to achieve 99.9% end-to-end across 4 services
> ```
>
> > [!tip] Interview framing
> > *"0.995^10 = 95% — catastrophic. Three fixes: classify and degrade non-critical services (removes them from multiplication), cache critical services (reduces effective failure rate), and async non-critical work (removes them from critical path entirely). Goal: reduce critical path to 2-3 services, each at 99.97%+."*

---

## Q4 — On-Call Program Design

> [!question] Engineers are burning out from on-call. Alerts are noisy, false positives dominate, and on-call engineers can't resolve issues without waking up the senior team. Design a better on-call program.

> [!success]- Answer
>
> **Why the current program is broken:**
> ```
> Alert fatigue: engineers receive so many alerts they start ignoring them
>   → Real incidents missed in the noise
>   → Goodhart's Law: "silence the alert" becomes the goal, not "fix the problem"
>
> Helpless on-call: engineers can't resolve issues → escalate everything
>   → Senior team burned out
>   → On-call rotation becomes unusable → junior engineers quit
> ```
>
> **Fix 1 — Alert quality over quantity:**
> ```
> Audit every alert:
>   "Has this alert fired in the past 30 days?"
>   "What did the on-call engineer do each time?"
>
>   Category A: alert fired → engineer took action → alert is valid
>   Category B: alert fired → engineer ignored or did nothing → alert is noise → delete it
>   Category C: alert fired → engineer acknowledged but problem resolved itself → reduce sensitivity
>
>   Target: 90% of pages require action
>           If < 90%: alert program is broken
>
>   Every alert must be actionable:
>     What does the engineer do when this fires?
>     If the answer is "check Grafana and wait" → it's not an alert, it's a notification
> ```
>
> **Fix 2 — Runbooks for every alert:**
> ```
> Alert: "DB connection pool > 80%"
> Runbook:
>   Step 1: Check pg_stat_activity for long-running queries
>   Step 2: Kill queries blocking the pool
>   Step 3: If still high, check PgBouncer configuration
>   Step 4: If unresolved in 10 minutes: escalate
>
>   Engineer doesn't improvise → follows playbook → resolves without escalation
>
>   First time an engineer follows a runbook and succeeds:
>     Update the runbook with what actually worked
>     Living document, not a one-time creation
> ```
>
> **Fix 3 — Severity tiers:**
> ```
> P1 (page immediately, any hour): customer-facing outage, revenue loss
> P2 (page during business hours): degraded but not down, fix today
> P3 (Slack notification): non-critical, fix in next sprint
>
>   90% of current pages are probably P2 or P3 → should not wake people up
> ```
>
> **Fix 4 — On-call rotation practices:**
> ```
> Primary on-call: handles all P1s
> Secondary on-call: backup if primary unreachable
>
>   Rotation: never more than 1 week at a time
>   Handoff: written summary of ongoing issues → no context lost
>
>   Post on-call: dedicate time to fixing what broke on your watch
>                 On-call debt compounds if not addressed
> ```
>
> > [!tip] Interview framing
> > *"Fix alert fatigue first: audit and delete non-actionable alerts. Target 90% of pages requiring action. Runbook every alert so on-call engineers can resolve without escalating. Tier alerts by severity: most 'pages' should be Slack notifications, not 2am wake-ups. Rotation hygiene: maximum one week, written handoff, dedicated time post-rotation to fix what broke."*

---

## Q5 — Reliability vs Feature Velocity

> [!question] The product team says "we need to ship 3 new features per week to stay competitive. Reliability work slows us down." How do you respond and what program do you propose?

> [!success]- Answer
>
> **The framing problem:**
> ```
> Product sees: reliability work = time not spent on features
>
> The reality: unreliability IS a feature problem
>
>   Every outage:
>     Engineering time lost to firefighting (not feature work)
>     User trust eroded (churn, support tickets)
>     On-call burnout → engineer attrition → slower feature work long-term
>
>   "Ship 3 features/week" math:
>     Each outage takes 4 engineers × 4 hours = 16 person-hours
>     At 2 incidents/month = 32 person-hours/month
>     That's 1 engineer-week of feature capacity lost every month
>
>   Reliability work IS feature velocity
> ```
>
> **The proposal — use error budget as the arbiter:**
> ```
> SLO and error budget policies agreed upfront by both teams:
>
>   Budget healthy (> 50% remaining):
>     Ship features freely — reliability is good
>     No reliability tax on feature work
>
>   Budget cautious (< 50%):
>     Engineering includes 20% reliability work in sprints
>     Still shipping 80% of feature capacity
>
>   Budget exhausted:
>     Feature freeze until budget recovers
>     100% focus on reliability
>     No exceptions (including the VP's pet feature)
>
>   This converts reliability from "slows us down" to
>   "data says we can or can't ship right now"
>   Neither team decides — the error budget decides
> ```
>
> **What this requires from product:**
> ```
> Pre-agreement on the policy before any budget crunch
> When budget is healthy: no friction, ship everything
> When budget is tight: product team understands why the freeze exists
>
> If product pushes back during a freeze:
>   "The data says we've used our monthly reliability budget
>    Shipping more features now increases the risk of an outage
>    that will cost more feature time to fix than we'd gain by shipping now"
>
>   Data beats opinion every time
> ```
>
> **The cultural argument:**
> ```
> Companies that win on reliability:
>   Google's SRE model: product teams lose feature velocity if they burn error budget
>   → Reliability is incentivized, not taxed
>
>   Teams that ignore reliability:
>   Technical debt compounds → incidents get worse → team burns out
>   → Eventually lose engineers → feature velocity collapses
> ```
>
> > [!tip] Interview framing
> > *"Unreliability costs feature velocity too — every incident is engineering hours not spent on features. The solution is error budget: pre-agreed policy converts reliability from debate to data. Budget healthy → ship freely. Budget exhausted → freeze. Neither team decides — the SLO does. Make data the arbiter before any budget crunch happens."*
