# Observability — Error Budget

> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed. 99.99% stream start availability means 0.01% of stream attempts can fail. That 0.01% is your error budget.

---

## What the Budget Actually Is

At 20M peak concurrent viewers, stream starts happen constantly. At roughly 2 stream starts per user per hour:

```
20M concurrent viewers × 2 stream starts/hour = 40M stream starts/hour
40M / 3600 = ~11,000 stream starts/second at peak
```

At 99.99% SLO:

```
Failed stream starts allowed per second:  11,000 × 0.0001 = 1.1
Failed stream starts allowed per minute:  1.1 × 60         = 66
Failed stream starts allowed per hour:    66 × 60           = 3,960
Failed stream starts allowed per day:     3,960 × 24        = 95,040

In time: 0.01% of 525,600 minutes/year = 52.56 minutes of total downtime per year
```

52 minutes and 34 seconds per year. That is the entire stream start availability error budget.

Every CDN node failure, every BFF outage, every circuit breaker opening — it all eats into those 52 minutes.

---

## TTFF Budget

TTFF is harder to express as a time budget because it degrades gradually rather than being binary. Instead of minutes of downtime, track it as percentage of stream starts that breached the 2-second target.

```
SLO: 99% of stream starts have TTFF < 2 seconds
Budget: 1% of stream starts can exceed 2 seconds

At 11,000 stream starts/second:
  110 stream starts per second can have TTFF > 2s before breaching SLO
```

A CDN node going cold after a deployment might push 5% of stream starts in one region above 2 seconds for 10 minutes. That burns through a significant fraction of the monthly TTFF budget in a single incident.

---

## How Error Budget Changes Engineering Behaviour

Without error budget thinking, reliability is vague. "Are we reliable enough?" has no concrete answer. Product teams push features. Engineering teams worry about stability. Nobody has a number to point to.

Error budget makes it concrete: how much budget do we have left this month?

```
Budget remaining: 80%  → plenty of runway
                        → safe to deploy risky changes
                        → can roll out new CDN node configuration this week
                        → can test new transcoding pipeline in production

Budget remaining: 20%  → getting tight
                        → slow down risky deploys
                        → postpone the Redis cluster migration
                        → review what consumed the last 60%

Budget remaining: 0%   → SLO already breached this period
                        → freeze all feature work
                        → every engineer focuses on reliability
                        → no deploys until budget recovers next period
```

The budget creates a shared language between engineering and product. It is not "engineers being too cautious" vs "product pushing too fast." It is: here is the number. The number decides.

---

## Netflix-Specific Budget Consumers

Some events are predictable budget consumers:

```
CDN node failure (1 region, 30 minutes):
  → stream starts in that region fail until failover completes
  → consumes ~3-5% of yearly stream start budget

BFF pre-scaling missed — spike absorbed at 50 instances instead of 500:
  → 80% of requests 503'd for ~5 minutes
  → consumes ~40% of yearly budget in a single incident

Redis cache cold start on release night (double-checked locking saves DB, but TTL expired):
  → 2-3 minutes of elevated TTFF while cache warms
  → consumes ~0.5% of yearly TTFF budget

Bad deployment — new BFF version with memory leak:
  → instances OOM every 20 minutes, rolling restart cycle
  → consumes ~2% of budget per hour until rollback completes
```

Tracking which events consumed the most budget guides reliability investment. If CDN node failures account for 60% of the yearly budget, that points directly to CDN redundancy and faster failover as the highest-leverage reliability investment.

> [!tip] Interview framing
> "99.99% stream start availability at 11,000 starts/second means 52 minutes of total failure per year — that's the budget. When budget is full, move fast. When nearly gone, freeze deploys. Netflix's main budget consumers are CDN node failures, missed pre-scaling on release nights, and bad deployments. Tracking by incident type tells you where to invest reliability work next quarter."
