# Error Budget — Notification System

> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed.
> 99.99% availability sounds like "almost never fail." What it actually means is: you have a budget of 0.01% failures. How you spend that budget determines how aggressively you can move.

---

## What the Budget Actually Is

The intake API SLO is 99.99% availability. That means 0.01% of requests are allowed to fail.

At 5M notifications/sec intake:

```
Per second:   5,000,000 × 0.0001 = 500 failed requests allowed
Per minute:   500 × 60           = 30,000 failed requests allowed
Per hour:     30,000 × 60        = 1,800,000 failed requests allowed
Per day:      1,800,000 × 24     = 43,200,000 failed requests allowed

In time:      0.01% of 525,600 minutes/year = 52.56 minutes of total downtime allowed
```

52 minutes and 34 seconds per year. That is your entire error budget for intake availability. Every 503, every timeout, every Kafka publish failure eats into it.

---

## Delivery Success Rate Budget

The delivery success rate SLO is implicit — if 5% of push notifications are allowed to fail (95% success rate), the budget per second is:

```
3.5M push/sec × 5% = 175,000 failed pushes allowed per second
```

That sounds like a lot, but consider: if APNs is down for 10 minutes and the circuit breaker trips immediately, all 3.5M/sec × 600 seconds = 2.1B push notifications fail. That's a massive budget burn in a single incident.

This is why the delivery success rate alert threshold (95%) is a floor, not a target. In healthy operation you expect 99%+ success rate. 95% is the "something is seriously wrong" threshold.

---

## How Error Budget Changes Engineering Behaviour

Without error budget thinking, reliability is vague. "Are we reliable enough to deploy?" is a subjective question.

Error budget makes it concrete:

```
Error budget remaining: 80%  → plenty of runway
                              → safe to deploy risky changes
                              → can run A/B experiments on workers
                              → can migrate Kafka brokers with rolling restarts

Error budget remaining: 20%  → getting tight
                              → slow down risky deploys
                              → no rolling Kafka restarts
                              → review what burned the budget

Error budget remaining: 0%   → SLO already breached this period
                              → freeze all feature work
                              → every engineering hour goes to reliability
                              → no deploys until budget recovers
```

---

## Notification-Specific Budget Considerations

**Kafka rolling restarts burn budget.** A 30-second leader election on a Kafka broker during a rolling restart means 30 seconds of intake failures. At 5M/sec, that's 150M failed intake requests — 3.5× the daily budget in one restart. Schedule maintenance during off-peak hours and account for budget burn.

**APNs incidents are the biggest budget risk.** APNs goes down for 10 minutes → millions of failed deliveries → massive budget burn. The circuit breaker limits damage by stopping futile retries, but the failures are already counted. Each major APNs incident can consume weeks of delivery success budget.

**Deployments need budget headroom.** A bad deploy that causes 5 minutes of worker crashes at 3.5M/sec = 1B failed pushes. Always check budget before deploying. If budget is below 30%, defer non-critical deploys.

---

## Error Budget Policy

```
Budget > 50%   → normal operations, deploys proceed, experiments allowed
Budget 20-50%  → slow down, require manual approval for risky deploys
Budget < 20%   → freeze feature deploys, reliability work only
Budget = 0%    → incident declared, all hands on reliability
```

> [!tip] Interview framing
> "99.99% intake availability means 52 minutes of allowed downtime per year — at 5M/sec intake, that budget burns fast. Error budget makes deploy decisions objective: when budget is healthy, move fast. When it's nearly gone, freeze and fix. For a notification system the biggest budget risks are APNs outages and Kafka maintenance windows — both need to be planned around the budget remaining."
