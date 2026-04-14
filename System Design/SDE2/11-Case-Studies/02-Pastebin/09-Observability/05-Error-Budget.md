
> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed. 99.99% availability means 0.01% of requests can fail. That 0.01% is your error budget.

---

## What the budget actually is

At 3,000 read requests/sec peak:

```
Per second:   3,000 × 0.0001 = 0.3 failed requests allowed
Per minute:   0.3 × 60       = 18 failed requests allowed
Per hour:     18 × 60        = 1,080 failed requests allowed
Per day:      1,080 × 24     = 25,920 failed requests allowed
Per year:     25,920 × 365   = 9,460,800 failed requests allowed

In time: 0.01% of 525,600 minutes/year = 52.56 minutes of total downtime/year
```

52 minutes and 34 seconds per year. That is the entire read availability error budget.

Every 503 from an S3 outage, every 500 from an unhandled exception, every timeout — it all eats into those 52 minutes. The Postgres failover window (10-30 seconds) alone consumes a chunk of the budget if it happens multiple times.

---

## Write availability error budget

At 99.9% SLO and 30 writes/sec peak:

```
Per year: 0.1% of 525,600 minutes = 525 minutes of total downtime allowed
```

About 8 hours 45 minutes per year for writes. A significantly more relaxed budget than reads — which reflects the product reality. Paste creation being down for an hour is bad but recoverable. Paste viewing being down for 52 minutes for the whole year is the hard constraint.

---

## How error budget changes engineering behaviour

Without error budget thinking, reliability is vague. "Are we reliable enough?" is a subjective question with no answer. Engineers argue about whether a deployment is safe. Product managers push for features. Nobody has a number.

Error budget makes it concrete: how much budget do we have left this month?

```
Budget remaining: 80%  → plenty of runway
                        → safe to deploy risky changes
                        → can run experiments on production traffic
                        → can schedule the Postgres maintenance window this week

Budget remaining: 20%  → getting tight
                        → slow down risky deploys
                        → postpone the Redis migration to next month
                        → review what consumed the last 60%

Budget remaining: 0%   → SLO already breached this period
                        → freeze all feature work
                        → every engineer focuses on reliability
                        → no deploys until budget recovers in next period
```

The budget creates a shared language between engineering and product. It's not "engineers being too cautious" vs "product pushing too hard." It's: here is the number. We have X% left. The number tells us what we can do.

---

## Pastebin-specific budget consumers

Some events are predictable budget consumers:

```
Postgres failover:           10-30 seconds per occurrence
                             → consumes ~0.5% of yearly budget per failover

S3 outage (circuit OPEN):    depends on duration
                             → 5 minutes = ~0.16% of yearly budget

Cleanup job DB contention:   can spike read latency during heavy nightly runs
                             → mitigated by running off-peak, but still watch it

Bad deployment rollback:     typically 2-5 minutes of elevated errors
                             → ~0.1% of yearly budget per incident
```

Tracking which events consumed the most budget guides reliability investment. If Postgres failover happens twice a year and each costs 0.5%, that's 1% of budget gone — worth investing in faster failover detection or a read replica to keep reads alive during the window.

---

> [!tip] Interview framing
> "99.99% availability at 3k reads/sec means 52 minutes of total downtime per year — that's the error budget. When budget is full, move fast and take risks. When it's nearly gone, freeze deploys and focus on reliability. It removes the subjective argument: the number decides. Pastebin's main budget consumers are Postgres failovers (10-30 seconds each), S3 outages (circuit breaker open duration), and bad deployment rollbacks. Tracking these by incident type tells you where to invest reliability work."
