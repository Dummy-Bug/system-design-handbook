
> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed. 99.99% delivery availability means 0.01% of messages can fail. That 0.01% is your error budget.

---

## What the budget actually is

At 100K messages/second peak:

```
Per second:   100,000 × 0.0001 = 10 failed messages allowed
Per minute:   10 × 60          = 600 failed messages allowed
Per hour:     600 × 60         = 36,000 failed messages allowed
Per day:      36,000 × 24      = 864,000 failed messages allowed

In time: 0.01% of 525,600 minutes/year = 52.56 minutes of total downtime/year
```

52 minutes and 34 seconds per year. That is the entire delivery availability error budget.

Every DynamoDB circuit breaker open event, every connection server crash, every failed message write — it all eats into those 52 minutes.

---

## Connection success budget

At 99.9% SLO:

```
0.1% of 525,600 minutes/year = 525 minutes of total downtime/year
~8 hours 45 minutes per year
```

Connection success has a more relaxed budget — a brief connection storm is bad but recoverable. Message delivery failure is the harder constraint.

---

## How error budget changes engineering behaviour

Without error budget thinking, reliability is vague. "Are we reliable enough?" has no answer. Engineers argue about whether a deployment is safe. Product pushes for features. Nobody has a number.

Error budget makes it concrete: how much budget do we have left this month?

```
Budget remaining: 80%  → plenty of runway
                        → safe to deploy risky changes
                        → can migrate the registry Redis this week
                        → can run load tests on production traffic

Budget remaining: 20%  → getting tight
                        → slow down risky deploys
                        → postpone the Kafka migration to next month
                        → review what consumed the last 60%

Budget remaining: 0%   → SLO already breached this period
                        → freeze all feature work
                        → every engineer focuses on reliability
                        → no deploys until budget recovers next period
```

The budget creates a shared language between engineering and product. It's not "engineers being too cautious" vs "product pushing too hard." It's: here is the number. The number decides.

---

## WhatsApp-specific budget consumers

Some events are predictable budget consumers:

```
Connection server crash (1M users):
  → reconnect storm lasts ~2 minutes
  → delivery disruption for those users during window
  → consumes ~0.4% of yearly delivery budget per occurrence

DynamoDB circuit breaker OPEN (5 minutes):
  → all new message writes fail
  → consumes ~0.95% of yearly budget per occurrence

Redis inbox shard failure (full shard down):
  → 10% of users get slower inbox loads, not delivery failures
  → may not consume delivery budget but hits connection budget

Bad deployment rollback (2-5 minutes of elevated errors):
  → ~0.1-0.4% of yearly budget per incident
```

Tracking which events consumed the most budget guides reliability investment. If DynamoDB circuit breaks twice a year, that's nearly 2% of budget gone — worth investing in DynamoDB capacity planning and connection pool tuning to prevent it.

> [!tip] Interview framing
> "99.99% delivery availability at 100K messages/sec means 52 minutes of total failure per year — that's the budget. When budget is full, move fast. When it's nearly gone, freeze deploys and focus on reliability. WhatsApp's main budget consumers are DynamoDB circuit break events, connection server crashes, and bad deployment rollbacks. Tracking by incident type tells you where to invest reliability work next quarter."
