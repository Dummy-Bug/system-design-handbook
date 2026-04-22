# SLA / SLO / SLI — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions testing SLO program design, cultural adoption, and complex trade-off reasoning. SDE-3 level — no single right answer, just structured thinking and clear justification.

---

> [!question] You're designing SLOs for a global payments platform serving both free users and enterprise customers paying $500k/year. How do you structure the SLOs?

> [!success]- Answer
>
> **Tier the SLOs by customer value — but don't neglect free users:**
>
> Free users are future paying customers. A bad experience today means they never convert. The SLO gap between tiers should be meaningful but free users can't be treated as second class.
>
> ```
> Free users:       availability SLO = 99.9%   (43 min downtime/month)
> Enterprise:       availability SLO = 99.99%  (4.3 min downtime/month)
>                   + latency SLO = P99 < 200ms
>                   + contractual SLA with financial penalties
>                   + dedicated support response time SLA
> ```
>
> Enterprise customers don't just want higher availability — they want latency guarantees and contractual response times. The SLI itself differs per tier, not just the target number.
>
> **Dependency SLOs must be stricter than service SLOs:**
> Any service Team A depends on must have a stricter SLO than Team A's own SLO. Otherwise dependencies become the bottleneck that prevents hitting the promised SLA.
>
> **Technical enforcement — traffic isolation:**
> SLO tiers are meaningless without infrastructure separation. Free user load spikes must not degrade enterprise experience:
> ```
> Enterprise traffic → dedicated infrastructure / priority queues
> Free user traffic  → shared infrastructure
>
> Free user spike → no impact on enterprise SLO ✓
> ```
>
> **Setting initial SLOs:**
> Check historical SLIs first. If you're currently at 99.5%, promising 99.99% to enterprise on day one is a breach waiting to happen. Start from historical baseline, commit to what's proven, tighten as confidence grows.
>
> > [!important] Traffic isolation is what makes tiered SLOs real. Without it, a free user traffic spike burns enterprise error budget — the tier difference exists only on paper.
>
> > [!tip] Interview framing
> > *"Enterprise gets stricter availability + latency SLOs with contractual SLAs and financial penalties. Free users get meaningful SLOs too — they're future paying customers. Dependencies must have stricter SLOs than the services they serve. Enforce tier isolation at infrastructure level so free user load can't degrade enterprise experience."*

---

> [!question] Your team has maintained 99.95% availability for 6 months — well above your 99.9% SLO. Your VP says "great, let's raise the SLO to 99.95%". You push back. Why?

> [!success]- Answer
>
> **The math — tightening the SLO halves the error budget:**
> ```
> Current:  SLO = 99.9%  → error budget = 43 min/month
> Proposed: SLO = 99.95% → error budget = 21 min/month
>
> Same system, half the budget overnight
> Every deployment now costs twice as much of your budget
> One bad release → SLA breach
> ```
>
> You didn't make the system more reliable — you just gave the team half the room to operate.
>
> **6 months of over-performance doesn't mean the system is ready:**
> ```
> Has the system been stress-tested with a major incident?
> Has the team grown or turned over?
> Are there upcoming infrastructure changes or new features?
> Has traffic grown significantly?
> ```
> Quiet periods look like strong reliability. They're not the same thing.
>
> **The right approach — tighten gradually with evidence:**
> ```
> Month 1–6:  observe 99.95% actual performance
> Month 7:    set SLO to 99.92% — small step, proven achievable
> Month 10+:  if still consistently over-performing, tighten further
> ```
>
> **The cultural risk:**
> Raising SLO to match current performance removes all slack. Engineers start making conservative decisions, avoiding risky-but-necessary work. Innovation slows.
>
> > [!important] Over-performance is a buffer, not a reason to tighten. The gap between actual performance and SLO is working capital — don't give it away.
>
> > [!tip] Interview framing
> > *"Raising SLO to 99.95% halves our error budget without making the system more reliable — we just have less room to operate. 6 months of quiet isn't proof the system can handle a major incident, team growth, or new features. I'd tighten gradually with evidence — small step up, observe, tighten again. Never give away your buffer all at once."*

---

> [!question] You're on call. Your service SLO is 99.9%. At 2am you detect an incident — error rate is 2%. You estimate fixing it properly takes 4 hours. A hacky fix takes 20 minutes but introduces tech debt. Your error budget has 30 minutes left this month. What do you do?

> [!success]- Answer
>
> **The math forces the decision:**
> ```
> Error budget = 43 min/month total, 30 min remaining
>
> During incident: 2% error rate vs 0.1% allowed
> = burning budget at 20x normal rate
>
> Budget exhausted in: 30 min ÷ 20 = ~1.5 minutes of incident
>
> 4 hours at 2% error rate = SLA breach in the first 2 minutes
> then 3 hours 58 minutes of contractual violation
> ```
>
> **Decision: deploy the quick fix immediately.**
>
> The 4-hour proper fix is not viable. You're already in SLA breach territory within minutes. The priority is stopping the bleeding.
>
> **How to deploy the quick fix safely:**
> ```
> 1. Deploy behind a feature flag → instant rollback if it makes things worse
> 2. Monitor for 15 minutes after deploy → confirm error rate drops
> 3. Create a high-priority ticket for root cause fix
> 4. Document the tech debt introduced
> ```
>
> **Root cause fix — business hours, not 2am:**
> Proper fixes done at 2am under pressure introduce new bugs. Schedule it for the next morning when the team is fresh, has context, and can review properly.
>
> **Post-incident:**
> Run a blameless post-mortem. Why did this happen? Why did the quick fix exist as an option at all? Use it to prevent recurrence, not assign blame.
>
> > [!important] Stop the bleeding first, fix the wound later. Never do a complex root cause fix at 2am under pressure — that's how you introduce new incidents.
>
> > [!tip] Interview framing
> > *"The math is clear — 4 hours at 2% error rate burns the budget in 2 minutes and means 4 hours of SLA breach. Deploy the quick fix with a feature flag, confirm error rate drops, create a ticket for root cause. Proper fix in business hours when the team is fresh. Document the tech debt. Post-mortem next day."*

---

> [!question] Your SLO is measured monthly. A massive incident takes down your service for 6 hours on the 1st of the month. Your VP says "we're fine, we have the rest of the month to recover". What's wrong with this thinking?

> [!success]- Answer
>
> **Mathematically — the budget is gone, you can't recover it:**
> ```
> 6 hours of downtime = 360 minutes
> Monthly budget at 99.9% = 43 minutes
>
> Budget burned on day 1: 360 min >> 43 min
> Remaining budget for the next 29 days: 0
>
> Any incident at all for the rest of the month = immediate SLA breach
> ```
>
> You can't "recover" error budget by having a good rest of the month. The SLO window is measured over the full month — the damage is already done.
>
> **Operationally — the team is paralysed for 29 days:**
> ```
> No deployments
> No experiments
> No infrastructure changes
> No risky features
>
> One small blip in the next 29 days = SLA breach + customer credits
> ```
>
> **Culturally — this mindset is dangerous:**
> If engineers hear "we're fine, we have time to recover", it signals that big incidents early in the month are acceptable. That's exactly the wrong incentive.
>
> **The right response:**
> ```
> 1. Immediate post-mortem — what caused 6 hours of downtime?
> 2. Freeze all non-critical releases for the rest of the month
> 3. Full focus on reliability and preventing recurrence
> 4. Communicate to customers proactively — don't wait for them to notice
> ```
>
> > [!danger] Error budget is not a bank account. You cannot earn it back by being reliable later in the month. Once burned, it's gone until the next measurement window.
>
> > [!tip] Interview framing
> > *"6 hours burns the entire monthly budget on day 1 — there's nothing to recover. For the next 29 days, any incident at all is an immediate SLA breach. The team is paralysed. The right response is immediate post-mortem, release freeze, and full focus on reliability — not optimism about the rest of the month."*

---

> [!question] You're a new SRE at a company. They have no SLOs defined at all — just a vague "we try to keep the service up". Walk me through how you build an SLO program from scratch.

> [!success]- Answer
>
> **Culture first — without buy-in, the program dies:**
> SLOs only work if both engineering and product own them. The shift from "we try to keep it up" to "we commit to 99.9% with defined consequences" is a cultural change, not just a technical one. Get leadership aligned before writing a single target number.
>
> No service ships without SLOs defined. No exceptions. Make it as non-negotiable as code review.
>
> **Step-by-step:**
>
> **1. Instrument first — you can't target what you can't measure:**
> Add SLI instrumentation to all services — request success rate, P99 latency, error rate. Start measuring before setting any targets.
>
> **2. Observation period — 4 to 6 weeks:**
> No targets, just measurement. Let the data tell you what the system actually does. This becomes the baseline.
>
> **3. Set initial SLOs — deliberately loose:**
> Use the baseline to set targets you're confident of hitting even on a bad week. Aggressive SLOs on day one without data = guaranteed breach.
>
> **4. Define error budget policies upfront:**
> ```
> 0–50% burned   → normal, ship freely
> 50–75% burned  → increased caution
> 75–100% burned → freeze non-critical releases
> 100% burned    → full freeze, post-mortem required
> ```
> The policy must be pre-agreed by both product and engineering. This is what removes the debate when budget runs low.
>
> **5. No deploy without SLOs for new services:**
> Enforce this as a hard gate. New service = SLO defined before launch. Creates the right habits from the start.
>
> **6. Quarterly SLO reviews:**
> Review actual performance vs targets. Tighten where there's consistent headroom. Investigate where there's consistent struggle.
>
> **7. Make data the decision-maker:**
> Error budget replaces "are we reliable enough?" debates with a number. Product can't argue for a risky release when the budget is gone — the data settles it. This is the cultural payoff.
>
> > [!important] The hardest part of an SLO program is not the math — it's the culture. Engineers need to believe SLOs protect them from unreasonable demands, not just add bureaucracy.
>
> > [!tip] Interview framing
> > *"Culture first — both teams must own it. Then instrument, observe baseline, set loose initial SLOs, define budget policies upfront. No deploy without SLOs for new services. Quarterly reviews to tighten. The goal is making data the decision-maker — error budget replaces reliability debates with a number both teams already agreed on."*
