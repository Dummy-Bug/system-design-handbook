# SLO — Service Level Objective

> [!question] Your SLI says P99 latency = 180ms. Is that good or bad?
> Nobody knows without a target. That target is your SLO.

---

## What it is

An SLO is the **target you set for your SLI**.

Your team sits down and agrees — *"P99 latency must stay under 200ms"*. That's your SLO.

- SLI says: *"here's the number"*
- SLO says: *"here's what that number should be"*
- Together they give you a verdict: **good or bad**

> [!info] SLO on its own is useless. SLI on its own is meaningless. They only work together.

---

## SLOs are internal

No customer sees your SLO. No contract. No penalties. It's purely your team's internal definition of "good enough."

If you breach your SLO, your team knows something is wrong and needs fixing — before it becomes a customer-facing problem.

---

## Setting the right SLO

The SLO must be tight enough to catch real problems but realistic enough that you're not breaching it constantly.

| SLO | Problem |
|---|---|
| P99 < 5000ms when you typically run at 180ms | Too loose — won't catch real problems, completely useless |
| P99 < 150ms when you typically run at 180ms | Too tight — breaching constantly, team ignores alerts, becomes noise |
| P99 < 200ms when you typically run at 180ms | Just right — achievable under normal conditions, breached when something is actually wrong |

> [!tip] The sweet spot
> Set your SLO at a level that is **achievable under normal conditions but will be breached when something is genuinely wrong**.

---

## SLOs always have a time window

Not just *"P99 must be under 200ms"* but:

*"P99 must be under 200ms **measured over a rolling 30 day window**"*

The time window matters because:
- A 5 minute spike doesn't mean your system is broken — it could be a one-off deployment hiccup
- Consistently slow over 30 days means something is fundamentally wrong

The time window filters out noise and surfaces real structural problems.

---

## Examples

| System | SLI | SLO |
|---|---|---|
| Chat app | P99 message delivery latency | Must be under 200ms over 30 days |
| Payment API | Error rate | Must stay below 0.1% over 7 days |
| Search | P99 query latency | Must be under 500ms over 30 days |
| Storage | Read success rate | Must be above 99.99% over 30 days |
