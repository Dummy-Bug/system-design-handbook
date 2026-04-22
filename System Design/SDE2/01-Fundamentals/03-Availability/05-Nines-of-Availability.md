# Nines of Availability

> [!question] What does 99.9% availability actually mean in real downtime?
> Percentages are abstract. Convert them to minutes and the numbers become real.

---

## What "Nines" Means

"Nines" is industry shorthand for how many 9s are in the availability percentage.

| Term | Availability |
|---|---|
| Two nines | 99% |
| Three nines | 99.9% |
| Four nines | 99.99% |
| Five nines | 99.999% |

---

## The Numbers That Actually Matter

| Availability | Nines | Downtime per year | Downtime per month |
|---|---|---|---|
| 99% | Two nines | 3.65 days | 7.2 hours |
| 99.9% | Three nines | 8.7 hours | 43.2 minutes |
| 99.99% | Four nines | 52 minutes | 4.32 minutes |
| 99.999% | Five nines | 5.2 minutes | 26 seconds |

> [!danger] Memorize these numbers
> These come up in every availability discussion in interviews. The jump from 99.9% to 99.99% — from 43 minutes to 4 minutes per month — is the most important one to know.

---

## What Each Tier Actually Requires

Each additional nine gets **exponentially harder and more expensive** to achieve.

**99% — Two nines**
- Basic redundancy
- Manual failover is acceptable
- Planned maintenance windows are fine
- Startups, internal tools

**99.9% — Three nines**
- Automated failover
- Single region with multiple availability zones
- Most production APIs and SaaS products

**99.99% — Four nines**
- Zero-downtime deployments mandatory — no planned maintenance windows
- Multi-AZ at minimum
- Automated failover in under a minute
- Payment systems, critical APIs

**99.999% — Five nines**
- Multi-region active-active deployment
- Automatic failover under 1 second
- Real-time replication across regions
- Costs orders of magnitude more than 99.9%
- Google, AWS core infrastructure, hospital systems

---

## The Cost of Each Nine

> [!warning] Each additional nine can double or triple your infrastructure cost
> Going from 99% to 99.9% — add redundancy, automate failover. Relatively straightforward.
>
> Going from 99.99% to 99.999% — rearchitect your entire deployment pipeline, multi-region setup, sub-second failover. Completely different scale of investment.

This is why in an interview you always ask: *"What availability SLO are we targeting?"* before designing. The answer completely changes your architecture.

---

## Quick Reference for Interviews

```
99%     = 7.2 hours/month   → basic redundancy
99.9%   = 43.2 minutes/month → automated failover, multi-AZ
99.99%  = 4.32 minutes/month → zero-downtime deploys, multi-AZ mandatory
99.999% = 26 seconds/month  → multi-region active-active
```
