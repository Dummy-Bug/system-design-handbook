# Interview Cheatsheet — SLI / SLO / SLA / Error Budget

> [!question] When does this come up in an interview and what do you actually say?
> Two situations — requirements phase and reliability deep dive. Always go SLI → SLO → SLA in that order.

---

## The Order That Always Works

Never mix these up. The logical flow is:

```
SLI → SLO → SLA → Error Budget
```

1. **SLI** — what are we measuring? (the number)
2. **SLO** — what should that number be? (the internal target)
3. **SLA** — what do we promise customers? (the external contract)
4. **Error Budget** — how much failure are we allowed? (the decision tool)

---

## Situation 1 — Requirements Phase

When clarifying NFRs at the start of a design question, use SLOs to make your requirements concrete.

**Weak:**
*"The system should be highly available"*

**Strong:**
*"What availability SLO are we targeting — 99.9% or 99.99%? Because that's the difference between 43 minutes and 4 minutes of allowed downtime per month, and it significantly changes the architecture."*

> [!tip] This one question instantly signals seniority
> Most candidates say "high availability" and move on. You're quantifying it before designing. That's what senior engineers do.

---

## Situation 2 — Reliability Deep Dive

When the interviewer asks *"how would you ensure reliability of this system?"*

**Weak:**
*"We'd add redundancy and monitoring."*

**Strong:**
*"First we'd define our SLIs — the key metrics that reflect user experience directly, like P99 latency and error rate. Then set SLOs — internal targets like P99 under 200ms and error rate below 0.1% over a 30 day window. We'd derive an error budget from the SLO — at 99.9% that gives us 43 minutes of allowed downtime per month — which governs how aggressively the team can deploy. For enterprise customers we'd back this with an SLA offering service credits if we breach 99.9% availability."*

---

## Quick Reference — the numbers that matter

| SLO Target | Error Budget per month | What it means in practice |
|---|---|---|
| 99% | 7.2 hours | Startups, internal tools |
| 99.9% | 43.2 minutes | Most production APIs |
| 99.99% | 4.32 minutes | Payment systems, critical infra |
| 99.999% | 26 seconds | Google, AWS core services |

> [!warning] The stricter the SLO, the more expensive the architecture
> 99.999% requires multi-region active-active deployment, automatic failover under 1 second, and zero-downtime deployments. This costs orders of magnitude more than 99.9%. Always ask the interviewer which tier before designing.

---

## SLOs drive architecture decisions

| SLO | Architecture implication |
|---|---|
| 99.9% availability | Single region, redundant servers, automated failover |
| 99.99% availability | Multi-AZ deployment, no single point of failure |
| 99.999% availability | Multi-region active-active, real-time replication |
| P99 latency < 100ms | Caching layer mandatory, read replicas, CDN |
| P99 latency < 10ms | In-memory data store, co-located services |
| Error rate < 0.1% | Circuit breakers, retries with backoff, DLQ |

---

## The one-liner for every design question

Before drawing a single box, say this:

*"Before I start designing, I want to define our SLOs — what availability and latency targets are we committing to? That will drive every architecture decision I make."*

Then listen to the answer and design accordingly.
