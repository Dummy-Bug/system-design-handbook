# Availability — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions testing availability at scale — Black Friday preparation, five-nines trade-offs, service isolation, and designing for graceful degradation. SDE-3 level — no single right answer, just structured thinking and clear justification.

---

> [!question] Your e-commerce platform has 99.9% SLO. Black Friday is in 3 weeks. Traffic is expected to spike 20x. Walk me through how you prepare.

> [!success]- Answer
>
> **The goal — availability under 20x load with no SLO regression:**
>
> **Step 1 — Load test now, not on the day:**
> ```
> Run load tests at 10x, 15x, 20x expected baseline
> → find where the system breaks before users do
> → identify the bottleneck: DB connections? Cache eviction? Queue backlog?
>
> Without load testing you're guessing — you'll find the limit at the worst moment
> ```
>
> **Step 2 — Establish graceful degradation tiers:**
>
> Not all features are equal. Define what degrades first when resources are tight:
> ```
> Tier 1 — never degrade:  checkout, payment, order confirmation
> Tier 2 — degrade under load: product recommendations, reviews, personalisation
> Tier 3 — turn off entirely: non-critical analytics, A/B test logging, social sharing
>
> 20x traffic → Tier 3 features off → resources freed → Tier 1 protected
> ```
>
> Feature flags must be in place before Black Friday — you can't add them in 3 weeks.
>
> **Step 3 — Scale infrastructure ahead of time:**
> ```
> Auto-scaling reacts — takes 2-5 minutes to spin up new instances
> At 20x spike, 5 minutes of under-provisioning = 5 minutes of degraded availability
>
> Pre-scale manually the night before:
> → set minimum instance count to expected peak capacity
> → pre-warm caches with hot product data
> → increase DB connection pool limits
> ```
>
> **Step 4 — Rate limiting and queuing:**
> ```
> Checkout queue: limit how many checkout requests process simultaneously
> → excess requests wait in queue, not rejected
> → users see "completing your order..." instead of 500 error
> → availability preserved at cost of latency (acceptable trade-off)
> ```
>
> **Step 5 — War room and runbook:**
> ```
> War room: engineering, product, SRE on call simultaneously
> Runbook: pre-written steps for each failure scenario
>          "DB connections maxed" → runbook says: scale connection pool, drop Tier 3 features
>
> No debugging under pressure → pre-agreed playbooks only
> ```
>
> **Step 6 — Staged rollout:**
> ```
> Don't open 100% of traffic at midnight
> Open 10% → watch metrics → open 25% → watch → full open
> Gives time to catch problems before full impact
> ```
>
> > [!important] Graceful degradation is the most important availability technique at scale. You cannot make every feature scale to 20x economically. Defining what you sacrifice — and in what order — is a deliberate architectural decision that must be made before the event.
>
> > [!tip] Interview framing
> > *"Three-week runway: load test immediately to find bottlenecks, establish degradation tiers so Tier 1 (checkout) is protected at the cost of Tier 3 (recommendations), pre-scale the night before instead of relying on auto-scaling, queue checkout instead of rejecting, and run a war room with pre-written runbooks. No heroics under pressure — prepared responses only."*

---

> [!question] Your VP wants to commit 99.999% availability to a new enterprise customer. You're the lead engineer. What's your honest assessment?

> [!success]- Answer
>
> **What 99.999% actually means:**
> ```
> 99.999% = 26 seconds of downtime per month
>           5 minutes of downtime per year
> ```
>
> **The human impossibility:**
> ```
> Incident occurs at 2am
> On-call engineer gets paged: 30-60 seconds to wake up and check phone
> SSH into system: 30 seconds
> Diagnose problem: minutes
>
> You've already burned your entire monthly budget before diagnosis is complete
> ```
>
> 99.999% is physically impossible with any human in the response loop. Every single step — detection, failover, recovery — must be fully automated.
>
> **What must be true to achieve it:**
> ```
> Infrastructure:
> → Multi-region active-active deployment
> → Automated failover at every layer (LB, app, cache, DB)
> → Self-healing: failed instances automatically replaced
> → Zero-downtime deployments (blue-green mandatory)
>
> Monitoring:
> → Sub-second anomaly detection
> → Automated rollback on SLO degradation
> → No manual steps in any failure response
>
> Organisation:
> → Dedicated SRE team with deep runbook investment
> → Chaos engineering programme to find failure modes before production
> → Quarterly game days: simulate failures, verify automated recovery
> ```
>
> **The honest business trade-off:**
> ```
> 99.9%   → ~3 engineers, manual on-call, standard cloud setup
>            ~$50k-100k/year infrastructure overhead
>
> 99.999% → dedicated SRE team, multi-region, full automation
>            potentially $500k-1M+/year engineering + infrastructure overhead
>
> Is this enterprise customer worth it?
> What's the penalty clause in the SLA if you breach?
> ```
>
> **The right answer to give the VP:**
> Not "no" — but "here's what it actually requires and what it costs. Is that investment justified by this customer's contract value?"
>
> If the VP insists without resourcing it: put in writing that the commitment cannot be met with current infrastructure. Protect yourself and the team.
>
> > [!important] 99.999% is an engineering programme, not a configuration setting. It requires months of investment in automation, multi-region architecture, and SRE capability. Committing to it without the infrastructure is a contractual liability.
>
> > [!tip] Interview framing
> > *"26 seconds/month means zero human response time — every failover must be automated. Achieving it requires multi-region active-active, self-healing infrastructure, sub-second detection, and a dedicated SRE programme. I'd present the VP with what it costs to do it right and let them decide if the contract value justifies that investment. If they commit without the infrastructure, that's a contractual liability waiting to happen."*

---

> [!question] You're designing a ride-hailing platform. The matching service (driver ↔ rider) calls 5 downstream services: payments, maps, driver profiles, surge pricing, and notifications. Any one of them going down can take matching down with it. How do you architect matching to be resilient?

> [!success]- Answer
>
> **The core problem — tight coupling collapses the call chain:**
> ```
> Matching → calls Payments → Payments slow/down
>                             → Matching threads block waiting
>                             → Matching thread pool exhausted
>                             → Matching goes down
>                             → Every ride request fails
>
> One non-critical downstream (notifications) can cascade to kill the critical path
> ```
>
> **Technique 1 — Circuit Breaker:**
> ```
> Normal state:   Matching calls Payments → success → circuit CLOSED
>
> Payments slow:  5 consecutive failures → circuit OPEN
>                 Matching stops calling Payments immediately
>                 Returns fallback response
>
> After timeout:  circuit enters HALF-OPEN → send one test request
>                 If success → circuit CLOSED again
>                 If failure → stay OPEN
>
> Benefit: thread exhaustion prevented, Matching stays up
> ```
>
> **Technique 2 — Bulkhead pattern:**
> Separate thread pools per downstream service. One slow dependency can only exhaust its own pool.
> ```
> Payments thread pool:       10 threads  → Payments slow → only these 10 blocked
> Maps thread pool:           20 threads  → unaffected
> Notifications thread pool:  5 threads   → unaffected
> Matching core pool:         50 threads  → completely unaffected
> ```
>
> **Technique 3 — Classify dependencies by criticality:**
> ```
> Critical (matching cannot proceed without):
> → Maps (need route/ETA to match), Driver profiles (need driver status)
> → These are synchronous, circuit-broken, with tight timeouts
>
> Non-critical (matching proceeds without, just degraded):
> → Notifications (rider gets SMS after match, not during)
> → Surge pricing (fall back to base price if surge service is down)
> → These are async via message queue
> ```
>
> **Async via message queue for non-critical:**
> ```
> Matching completes → publishes event to Kafka
> Notification service → consumes from Kafka → sends SMS
>
> Notification service goes down:
> → event sits in Kafka queue
> → matching is completely unaffected
> → SMS delivered when notification service recovers
> ```
>
> **Graceful degradation for surge pricing:**
> ```
> Surge service unavailable → fall back to base fare
> Matching continues at standard price
> Not ideal → but infinitely better than matching going down
> ```
>
> **Timeouts on every call — mandatory:**
> ```
> No timeout = thread blocks forever
> Every downstream call must have an explicit timeout
> Maps call: 200ms timeout → if exceeded → use cached route
> ```
>
> > [!important] The goal is not to prevent downstream failures — they will happen. The goal is to ensure downstream failures cannot propagate upward to take down the critical path. Circuit breakers contain the blast radius. Bulkheads contain the thread exhaustion. Async queues decouple non-critical work entirely.
>
> > [!tip] Interview framing
> > *"Classify dependencies as critical vs non-critical. Critical ones (maps, driver status) get circuit breakers with tight timeouts — they fail fast and return a fallback. Non-critical ones (notifications, analytics) get decoupled via async message queue — matching doesn't wait for them at all. Bulkhead each downstream in its own thread pool so one slow service can't exhaust Matching's resources. The system stays up even when multiple downstream services fail simultaneously."*
