# What are Service Levels?

> [!question] You already have percentiles to measure if your system is doing well. So what problem does this framework solve?
> Percentiles give you the raw numbers. Service Levels give those numbers meaning — a target, an agreement, and consequences.

---

## The Problem

You've built a system. It's running in production. Thousands of users are using it.

How do you know if it's working well?

You could wait for users to complain. But by the time they complain, the damage is done. And "users are complaining" is not a useful signal — how many? About what exactly? How bad is it?

You need something more structured. You need to:
1. **Measure** specific things about your system continuously
2. **Agree** on what "good enough" looks like before anything goes wrong
3. **Commit** to those standards externally so there are real consequences for failure

That's exactly what SLI, SLO, and SLA are.

---

## But We Already Have Percentiles — What's the Difference?

Percentiles tell you the **shape of your performance**. P99 latency = 180ms. That's a measurement.

But percentiles alone don't answer:
- Is 180ms **good or bad** for this system?
- Who **agreed** that 180ms is the target?
- What **happens** if it goes to 300ms?

Percentiles are just raw numbers. This framework is what you build **around** those numbers.

> [!info] Percentiles feed INTO this framework — they don't replace it
> - **SLI** — P99 latency = 180ms ← this IS a percentile
> - **SLO** — P99 latency must stay under 200ms ← target set around that percentile
> - **SLA** — if P99 exceeds 200ms for more than 1 hour per month, customers get a refund ← consequence

---

## The Three Layers at a Glance

| Term | Full name | What it is | Who it's for |
|---|---|---|---|
| **SLI** | Service Level Indicator | The actual measurement | Engineering team |
| **SLO** | Service Level Objective | The internal target | Engineering team |
| **SLA** | Service Level Agreement | The external contract | Customers / business |

---

## Without vs With This Framework

**Without:**
*"Is the system healthy?"*
*"Yeah it seems fine... it's not throwing errors?"*

**With:**
*"Our SLI shows P99 latency at 180ms. Our SLO is 200ms — we're within target. Error rate is 0.3%, SLO is 1%. We have 72% of our error budget remaining for the month."*

Same question. Completely different answer. The second engineer sounds like a senior engineer.
