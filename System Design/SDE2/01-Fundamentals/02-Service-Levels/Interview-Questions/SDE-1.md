# SLA / SLO / SLI — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of service levels, error budgets, and what makes a good SLI. Every SDE candidate is expected to answer these confidently.

---

> [!question] What is the difference between SLI, SLO, and SLA? Give a one-line definition for each.

> [!success]- Answer
>
> **What each one is:**
>
> | Term | What it is | Example |
> |---|---|---|
> | **SLI** | A measurable metric of your service's behaviour right now | "99.3% of requests succeeded in the last 30 days" |
> | **SLO** | The internal target you set for that metric | "We want 99.9% success rate" |
> | **SLA** | The contractual promise to customers with penalties if breached | "We guarantee 99.5% or you get a refund" |
>
> **The relationship:**
> ```
> SLI — what you measure    (the actual number)
> SLO — what you target     (always stricter than SLA)
> SLA — what you promise    (legal/financial consequences if breached)
> ```
>
> SLI is the raw measurement. SLO is the goal you hold yourself to internally. SLA is what you've legally committed to customers — if you breach it, there are financial penalties or credits.
>
> > [!important] SLI is a specific measurable number, not a vague description. "Service is performing well" is not an SLI. "99.3% of requests returned 2xx in the last 30 days" is an SLI.
>
> > [!tip] Interview framing
> > *"SLI is what you measure — a specific metric like request success rate or latency. SLO is the internal target you set for that metric. SLA is the contractual promise to customers with penalties if breached."*

---

> [!question] Why is the SLO always set stricter than the SLA? What happens if you set them equal?

> [!success]- Answer
>
> **Why stricter:**
> SLO acts as an internal buffer. If you're optimising to hit your SLO, the SLA gets satisfied automatically. The gap between SLO and SLA gives you room to catch and fix problems before they become a customer-facing breach.
>
> ```
> SLO = 99.9%  (internal target)
> SLA = 99.5%  (customer promise)
>
> Miss SLO at 99.7% → internal alarm fires → fix it
> Still above SLA   → no customer impact, no penalties
> ```
>
> **What happens if you set them equal:**
> No buffer. Any SLO miss is immediately an SLA breach — legal penalties, customer credits, reputation damage. You have zero margin for error.
>
> ```
> SLO = SLA = 99.5%
> Service dips to 99.4% → SLA breached immediately
> → customer refunds triggered
> → legal consequences
> → no time to fix before damage is done
> ```
>
> > [!important] The gap between SLO and SLA is your safety margin. It exists so your internal alarm fires before the customer contract is broken.
>
> > [!tip] Interview framing
> > *"SLO is set stricter than SLA to create a buffer — if we miss our internal target we still haven't breached the customer contract. If they're equal, any SLO miss immediately triggers legal penalties with no room to course-correct."*

---

> [!question] What is an error budget and how do you use it?

> [!success]- Answer
>
> **What it is:**
> Error budget is the acceptable failure allowance derived from your SLO. It's the 100% minus your SLO target.
>
> ```
> SLO = 99.9%
> Error budget = 0.1% of requests can fail
>
> 30 days × 24hrs × 60min = 43,200 minutes/month
> 0.1% of 43,200 = 43 minutes of allowed downtime/month
> ```
>
> **How you use it:**
> Error budget is a decision-making tool for the entire engineering team. It's spent on risky activities — deployments, experiments, infrastructure changes, rolling out new features.
>
> ```
> Budget healthy  → move fast, ship features, run experiments
> Budget burning  → slow down, investigate reliability issues
> Budget exhausted → freeze all releases, focus only on stability
> ```
>
> **Why it matters — it aligns two teams:**
> - Product wants to ship fast → burns budget with every risky release
> - SRE wants reliability → protects budget
> - Error budget is the neutral arbiter both teams agreed on upfront
>
> You can't argue "we need to ship faster" when the error budget is gone — the data settles the debate.
>
> > [!important] Error budget isn't just about downtime. It covers any SLO-violating event — slow responses, high error rates, degraded features. Anything that hurts the SLI burns the budget.
>
> > [!tip] Interview framing
> > *"Error budget is the allowed failure room from your SLO — 99.9% SLO means 0.1% budget. It's spent on risky activities like deployments. When it runs low, releases freeze and reliability work takes priority. It aligns product velocity with reliability — both teams agreed on the budget upfront so it's a neutral decision-maker."*

---

> [!question] Your service has 99.9% SLO. How many minutes of downtime are you allowed per month?

> [!success]- Answer
>
> **The calculation:**
> ```
> 30 days × 24 hours × 60 minutes = 43,200 minutes/month
> 0.1% of 43,200 = 43.2 minutes/month
> ```
>
> **Numbers worth memorising:**
>
> | SLO | Downtime/month | Downtime/year |
> |---|---|---|
> | 99% | ~7.2 hours | ~3.65 days |
> | 99.9% | ~43 minutes | ~8.7 hours |
> | 99.99% | ~4.3 minutes | ~52 minutes |
> | 99.999% | ~26 seconds | ~5 minutes |
>
> **Why this matters in interviews:**
> When you propose an SLO in a system design, you need to justify it. "99.99% availability" sounds great until you realise it means your entire on-call team must respond and resolve any incident within 4.3 minutes per month. That's extremely hard to achieve and expensive to maintain.
>
> > [!tip] Know 99.9% = 43 min/month and 99.99% = 4.3 min/month off the top of your head. Interviewers ask this regularly.

---

> [!question] A product manager wants to add a new SLI — "number of features shipped per sprint". You push back. Why?

> [!success]- Answer
>
> **The fundamental problem:**
> SLIs must measure what the **user actually experiences**. "Features shipped per sprint" measures engineering output — it has nothing to do with whether users are having a good experience.
>
> A user doesn't care how many features shipped. They care if the service is fast, available, and correct. You could ship 20 features and still have 500ms P99 latency and a 5% error rate.
>
> **The rule of thumb:**
> ```
> Good SLI → user feels it directly if it degrades
>            request success rate, latency, error rate
>
> Bad SLI  → user has no idea if it changes
>            features shipped, lines of code, sprint velocity
> ```
>
> **What a valid SLI looks like instead:**
> ```
> ✓ % of requests completing under 200ms
> ✓ % of requests returning non-5xx response
> ✓ % of search results returning in under 500ms
> ✗ features shipped per sprint
> ✗ deployment frequency
> ✗ number of tests written
> ```
>
> > [!important] SLIs are always from the **user's perspective**. If a user wouldn't feel the degradation, it's not a valid SLI.
>
> > [!tip] Interview framing
> > *"SLIs must measure what the user experiences directly — availability, latency, error rate, correctness. 'Features shipped' is an engineering velocity metric, not a service reliability metric. A valid SLI for the same concern would be 'percentage of requests completing under 200ms' — that's something a user actually feels."*
