
> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed
> 99.99% availability sounds like "almost never fail". What it actually means is: you have a budget of 0.01% failures. How you spend that budget determines how aggressively you can move.

---

## What the budget actually is

Your SLO says 99.99% availability. That means 0.01% of requests are allowed to fail.

At 1M requests/second, here's what 0.01% looks like over time:

```
Per second:   1,000,000 × 0.0001 = 100 failed requests allowed
Per minute:   100 × 60           = 6,000 failed requests allowed
Per hour:     6,000 × 60         = 360,000 failed requests allowed
Per day:      360,000 × 24       = 8,640,000 failed requests allowed
Per year:     8,640,000 × 365    = 3,153,600,000 failed requests allowed

In time:      0.01% of 525,600 minutes/year = 52.56 minutes of total downtime allowed
```

52 minutes and 34 seconds per year. That is your entire error budget for availability.

Every 500 error, every timeout, every connection reset — it all eats into those 52 minutes. Once the budget is gone, any further failures breach the SLO.

---

## How error budget changes engineering behaviour

Without error budget thinking, reliability is vague. "Are we reliable enough?" is a subjective question. Engineers argue about whether it's safe to deploy. Product managers push for features. Nobody has a number to point to.

Error budget makes it concrete. How much budget do we have left this month?

```
Error budget remaining: 80%  → plenty of runway
                              → safe to deploy risky changes
                              → can run experiments, try new things
                              → can schedule maintenance windows

Error budget remaining: 20%  → getting tight
                              → slow down risky deploys
                              → no experiments on production
                              → review what's been consuming budget

Error budget remaining: 0%   → SLO already breached this period
                              → freeze all feature work
                              → every engineering hour goes to reliability
                              → no deploys until budget recovers
```

The error budget creates a shared language between engineering and product. It's not "the engineers are being too cautious" vs "product is pushing too hard". It's: here is the number. We have X% left. The number tells us what we can do.

---

## Error budget and deployments

Deployments are the most common source of reliability incidents. New code introduces bugs. Memory leaks. Unexpected edge cases under real traffic. Every deploy carries some probability of consuming error budget.

When budget is plentiful, that risk is acceptable — you move fast, you learn fast. When budget is nearly gone, the same deploy that would have been fine last week is now too risky. You're one incident away from breaching SLO.

This is why many teams run automated error budget policies:

```
Budget > 50%   → deployments proceed normally, auto-approval
Budget 20-50%  → deployments require manual approval
Budget < 20%   → deployments frozen unless explicitly overridden
```

The policy removes the human judgement call on whether to deploy. The budget decides.

---

## Error budget for latency SLOs

Error budget applies to latency SLOs too, not just availability.

Your p99 < 50ms SLO means: 99% of requests must complete under 50ms. The remaining 1% is your latency error budget — those requests are allowed to be slow.

At 1M requests/second:

```
1% of 1,000,000 = 10,000 requests per second allowed to exceed 50ms
```

If 15,000 requests per second are exceeding 50ms, you're burning latency budget at 1.5× the allowed rate. Sustained over a month, you're breaching SLO.

---

> [!tip] Interview framing
> "99.99% availability means 0.01% failure budget — at 1M req/sec that's 52 minutes of total downtime per year. Error budget makes reliability actionable: when budget is full, you move fast and take risks. When budget is nearly gone, you freeze deploys and focus on reliability. It removes the subjective argument about whether it's safe to ship — the budget is the answer. Same concept applies to latency SLOs: 1% of requests are allowed to be slow, and you track how fast you're burning through that 1%."
