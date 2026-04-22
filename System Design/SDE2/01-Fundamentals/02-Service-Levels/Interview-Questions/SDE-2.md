# SLA / SLO / SLI — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around error budgets, SLO design, and dependency management. Expected at SDE-2 level — not just definitions, but knowing when and why decisions matter.

---

> [!question] Your error budget is 80% burned with 2 weeks left in the month. The product team wants to ship a major feature release. What do you do?

> [!success]- Answer
>
> **The situation:**
> 80% burned in 2 weeks means you're trending toward burning 160% by month end — you're already on track for an SLA breach. The release decision can't be made in isolation.
>
> **It depends on what kind of release:**
> ```
> Reliability fix          → ship it, reduces burn rate going forward
> New risky feature        → freeze, too close to SLA breach
> Small low-risk change    → negotiate, consider feature flag to limit blast radius
> ```
>
> **The right process:**
> Error budget policy should be agreed upfront by both product and engineering — not decided under pressure at 80% burn. A good policy looks like:
> ```
> 0–50% burned   → normal operations, ship freely
> 50–75% burned  → increased caution, review all releases
> 75–100% burned → freeze non-critical releases, focus on reliability
> 100% burned    → full freeze, post-mortem required
> ```
>
> **First action — understand why you're burning fast:**
> Before the release decision, investigate the burn rate. Something caused 80% consumption in 2 weeks. Fix that first — it might be more urgent than any new feature.
>
> > [!important] Error budget policies should be defined and agreed by both teams before any incident. Making the decision under pressure at 80% burn is too late.
>
> > [!tip] Interview framing
> > *"80% burned in 2 weeks means we're trending toward SLA breach — first investigate why. For the release: reliability fixes ship, risky features freeze. Use feature flags to reduce blast radius if product insists. The error budget policy should be pre-agreed so this isn't a debate — the data makes the decision."*

---

> [!question] You're designing a payment service. Your manager says "set the SLO at 99.999%". What questions do you ask before agreeing?

> [!success]- Answer
>
> **99.999% means 26 seconds of downtime per month.** Before agreeing, validate whether this is achievable and necessary.
>
> **Questions to ask:**
>
> **1. What does our historical SLI show?**
> If the service is currently at 99.5%, promising 99.999% overnight is setting the team up to fail. Start from where you are, improve incrementally.
>
> **2. What's the operational cost?**
> ```
> 99.999% = 26 seconds/month downtime allowed
> → on-call engineer must detect, respond, and resolve in under 26 seconds
> → humanly impossible without fully automated detection + failover
> → months of infrastructure investment required
> ```
>
> **3. Does the business actually need it?**
> 99.9% (43 min/month) might be perfectly acceptable. 99.999% costs exponentially more to achieve and maintain. Justify the cost with actual business impact.
>
> **4. What's our dependency chain?**
> ```
> If you depend on a third-party bank API with 99.9% SLA
> → you mathematically cannot exceed 99.9% yourself
> → your SLO is bounded by your weakest dependency
> ```
>
> > [!important] Your SLO ceiling is set by your weakest dependency. Promising 99.999% while depending on a 99.9% third-party API is a contractual lie.
>
> > [!tip] Interview framing
> > *"Before agreeing I'd ask — what's our current SLI baseline, what's the operational cost of achieving it, does the business need it, and what do our dependencies guarantee? 99.999% means 26 seconds/month — that requires fully automated failover and is only achievable if every dependency also meets that bar."*

---

> [!question] Your service depends on three external APIs. Each has 99.9% uptime SLA. What is the maximum SLO you can realistically promise?

> [!success]- Answer
>
> **It depends on how your service uses them — sequential or parallel.**
>
> **Sequential — all three must be up simultaneously:**
> ```
> 99.9% × 99.9% × 99.9% = 99.7%
>
> Max realistic SLO ≈ 99.7%
> Set SLA at 99.5% as buffer
> ```
> Every additional sequential dependency chips away at your availability. Three 99.9% APIs gives you only 99.7%.
>
> **Parallel — redundant, all three must fail simultaneously:**
> ```
> P(all down) = 0.001 × 0.001 × 0.001 = 0.000000001
> Availability = 1 - 0.000000001 ≈ 99.9999999%
>
> Max SLO can be extremely high
> ```
>
> **The real-world catch — independence assumption:**
> The parallel math assumes all three APIs fail independently. In practice:
> ```
> All three APIs on same cloud provider
> → cloud provider has an outage
> → all three go down together
> → parallel calculation completely breaks down
> ```
> True independence is rare. Always validate that redundant dependencies don't share infrastructure.
>
> > [!important] Sequential dependencies multiply your failure probability up. Parallel redundancy multiplies it down — but only if failures are truly independent.
>
> > [!tip] Interview framing
> > *"Sequential: 99.9% × 99.9% × 99.9% = 99.7% — that's your ceiling. Parallel: near-perfect if truly independent. The catch is independence — if all three share the same cloud provider, they'll fail together and the parallel math breaks down."*

---

> [!question] A new service is launching next week with zero historical data. Your manager asks you to define SLOs. How do you approach it?

> [!success]- Answer
>
> **You cannot commit to a meaningful SLO without data.**
>
> **Step 1 — Canary deployment to gather real data:**
> Roll out to a small percentage of traffic first. Measure actual SLIs — request success rate, P99 latency, error rate under real load.
>
> ```
> Week 1–2  → canary 5% traffic  → measure SLIs closely
> Week 3–4  → expand to 20%     → refine measurements
> Month 2   → set initial SLO   → deliberately loose e.g. 99%
> Month 3+  → tighten SLO       → as system proves itself
> ```
>
> **Step 2 — Start with a deliberately loose SLO:**
> Something you're confident of hitting even on a bad week. Committing to 99.99% on day one with no data is how you guarantee an SLA breach.
>
> **Step 3 — Tighten over time:**
> As the system matures, historical data accumulates, and team confidence grows — tighten the SLO incrementally. Each tightening should be justified by data, not ambition.
>
> > [!danger] Committing to an aggressive SLO on day one with no historical data is setting yourself up for an SLA breach. Always start loose, tighten with evidence.
>
> > [!tip] Interview framing
> > *"Without historical data you can't commit to a meaningful SLO. Start with a canary — 5% of traffic, measure SLIs closely. Use that data to set a deliberately loose initial SLO. Tighten it over time as the system proves itself. Ambitious SLOs without data are just promises you can't keep."*

---

> [!question] Two teams are arguing. Team A's service calls Team B's service. Team A has a 99.9% SLO. Team B has a 99.5% SLO. Team A's engineering lead is furious. Why, and how do you resolve it?

> [!success]- Answer
>
> **Why Team A is furious:**
> Team A mathematically cannot achieve 99.9% if it depends on Team B at 99.5%. Every time Team B is down, Team A is also down — Team B's failures directly burn Team A's error budget without Team A doing anything wrong.
>
> ```
> Team B at 99.5% → 0.5% downtime/month → 216 minutes/month
> Team A budget   → 43 minutes/month (99.9% SLO)
>
> Team B alone can burn 5x Team A's entire monthly budget
> Team A can never hit 99.9% as long as Team B is at 99.5%
> ```
>
> **Resolution — two tracks:**
>
> **Organisational:**
> Both teams align on SLOs. Team B must improve to at least 99.9% — or Team A must lower their SLO to reflect the dependency reality. This is a leadership conversation, not just an engineering one.
>
> **Technical:**
> Team A adds a circuit breaker and graceful degradation — if Team B is down, Team A serves a degraded response instead of an error. This decouples Team A's availability from Team B's failures.
>
> ```
> Without circuit breaker: Team B down → Team A errors → Team A SLO breached
> With circuit breaker:    Team B down → Team A degrades gracefully → SLO protected
> ```
>
> > [!important] A service's SLO can never exceed the SLO of its critical dependencies. Dependency SLOs must be defined before the dependent service's SLO is set.
>
> > [!tip] Interview framing
> > *"Team A can't hit 99.9% with a 99.5% dependency — Team B alone can burn 5x Team A's monthly budget. Two fixes: organisational — align SLOs so dependencies are stricter than dependents. Technical — circuit breaker in Team A so Team B failures cause degradation not errors, decoupling their availability."*
