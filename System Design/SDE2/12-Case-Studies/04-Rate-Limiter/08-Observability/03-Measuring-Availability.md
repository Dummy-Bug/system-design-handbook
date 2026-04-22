
> [!info] Availability for a rate limiter has a subtlety — fail open means the system is "available" even when it's not actually rate limiting. You need to measure both dimensions.

---

## What Counts as Available

For most services, availability = successful responses / total requests.

For a rate limiter, this definition is tricky. When Redis goes down and the rate limiter fails open, it returns 200 allow for every request — the decision endpoint is "available" and "successful." But it's not actually doing its job.

You need two availability measurements:

**Decision availability** — is the rate limiter making decisions?
```
successful decisions / total decisions
success = any allow or block response returned without error
failure = timeout, connection refused, unhandled exception
```

**Protection availability** — is the rate limiter actually enforcing limits?
```
decisions backed by Redis / total decisions
= (total decisions - fail-open decisions) / total decisions
```

Protection availability drops when Redis is unreachable. Decision availability stays high because fail-open still returns a response. Tracking both reveals the difference between "the service is up" and "the service is working."

---

## Calculating Decision Availability

Every rate limiter instance emits two counters:
```
total_decisions    — incremented on every call
failed_decisions   — incremented on timeout, connection error, exception
```

```
decision_availability = 1 - (failed_decisions / total_decisions)
```

At fleet level, sum counters across all nodes before computing the ratio.

---

## Calculating Protection Availability

Every rate limiter instance emits:
```
redis_backed_decisions    — decisions where Redis was successfully consulted
fail_open_decisions       — decisions where Redis was unreachable, allowed through
```

```
protection_availability = redis_backed_decisions / total_decisions
```

This number drops during Redis outages. It tells you what fraction of traffic is actually being rate limited vs flowing through unprotected.

---

## The 99.99% Target

99.99% availability means:

```
Allowed downtime per year  : 52 minutes
Allowed downtime per month : 4.4 minutes
Allowed downtime per day   : 8.6 seconds
```

For a rate limiter making decisions at 400K QPS, 8.6 seconds of downtime = 3.4M unprotected requests per day budget. This sounds like a lot — but in a DDoS scenario, 8.6 seconds of open exposure is significant.

The 99.99% target applies to decision availability. Protection availability has a softer target (99.9%) because fail-open during Redis hiccups is an accepted tradeoff from the NFRs.

---

> [!tip] Interview framing
> "Two availability metrics for a rate limiter. Decision availability: is it returning responses? Fail-open counts as available here. Protection availability: is it actually consulting Redis? This drops during Redis outages. 99.99% SLO on decision availability, 99.9% on protection availability — the gap acknowledges that brief fail-open windows are acceptable."
