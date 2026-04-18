
> [!info] The error budget is the acceptable amount of failure. It exists to make a trade-off explicit: reliability work vs feature work. When the budget is spent, reliability wins.

---

## What the Error Budget Is

An SLO of 99.99% availability doesn't mean "be available 100% of the time minus accidents." It means you have a deliberate budget of 0.01% downtime you're allowed to spend — on deployments, experiments, known risks, or unexpected incidents.

```
SLO             : 99.99% decision availability
Error budget    : 0.01% of decisions can fail
                  = 0.01% × 400,000 req/sec × 86,400 sec/day
                  = 346 failed decisions per day allowed
                  = 10,368 per month
```

346 failed decisions per day sounds like a lot. But the rate limiter is in the critical path of every API call. A deployment that causes 30 seconds of elevated errors at 400K QPS burns:

```
400,000 req/sec × 30 seconds × 1% error rate = 120,000 errors
```

That's 12× the daily budget in one deployment. The error budget forces engineers to think carefully about deployment risk.

---

## How the Error Budget Is Spent

**Planned spending:**
- Deployments — rolling deploys cause brief elevated errors
- Redis cluster maintenance — node restarts cause brief fail-open windows
- Rule DB migrations — brief unavailability during schema changes

**Unplanned spending:**
- Redis node crashes
- Hot key storms overwhelming a node
- Code bugs causing false positives or crashes

---

## What Happens When Budget Is Exhausted

When the monthly error budget is gone:

```
Feature work  : paused
Risky deploys : blocked
On-call focus : reliability only — fix what caused the budget burn
```

If a Redis hot key storm burned 80% of this month's budget, the team investigates and fixes it before shipping new features. The error budget makes this conversation data-driven — not "I think we should be more careful" but "we have 2,000 errors left this month, here's what we're not doing until next month."

---

## Error Budget for Protection Availability

The protection availability SLO (99.9%) has its own error budget:

```
SLO             : 99.9% protection availability
Error budget    : 0.1% of decisions can be fail-open
                  = 0.1% × 400,000 × 86,400
                  = 34,560,000 unprotected decisions per day
```

34M unprotected decisions per day sounds alarming but it equals about 86 seconds of full Redis outage per day. The budget acknowledges that brief Redis hiccups are a fact of life at this scale. The alert fires at 99% (10× more fail-open than the budget rate) to catch sustained outages while ignoring brief blips.

---

## Summary

```
Decision availability budget  : 346 failed decisions/day
                                 = 30 seconds of 1% error deployment
                                 budget forces careful deployment planning

Protection availability budget: 86 seconds of full Redis outage/day
                                 brief Redis blips acceptable
                                 sustained outage depletes budget fast

Budget exhausted → reliability wins → feature work paused
```
