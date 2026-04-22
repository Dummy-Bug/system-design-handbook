
> [!info] Alerts should fire when something needs human attention. Too sensitive and engineers ignore them. Too loose and real problems go undetected.

---

## Alert 1 — Decision Latency p99 > 8ms (Warning) / > 10ms (Critical)

```
Threshold : warning at 8ms, critical at 10ms (the SLO target)
Window    : 5-minute rolling average
Pages     : critical pages on-call immediately
```

Why warn at 8ms before the SLO breaches at 10ms? Latency tends to climb gradually before spiking. A warning at 8ms gives engineers time to investigate — check Redis latency, check hot key patterns, check node load — before users are impacted.

Likely causes when this fires:
- Redis node overloaded (hot key storm)
- Lua script contention — too many concurrent requests on one Redis node
- Network degradation between rate limiter and Redis cluster

---

## Alert 2 — Decision Availability < 99.99% (Critical)

```
Threshold : below 99.99% in a 5-minute window
Pages     : immediately
```

Decision errors mean the rate limiter is returning 5xx or timing out on requests. This is a service health issue — the rate limiter is malfunctioning, not just slow.

Likely causes:
- Rate limiter nodes crashing (OOM, code bug)
- Network partition between API gateway and rate limiter nodes
- Misconfigured health checks causing LB to route to dead nodes

---

## Alert 3 — Protection Availability < 99% (Warning)

```
Threshold : below 99% in a 5-minute window
Pages     : warning, not immediate page
```

Protection availability dropping means Redis is unreachable for a significant fraction of requests — fail-open is happening at scale. Traffic is flowing through without rate limiting.

This is less urgent than a full outage (system is still responding, just not protecting) but needs investigation quickly. A prolonged fail-open window during an attack is a serious risk.

Likely causes:
- Redis cluster degradation (multiple nodes down)
- Network partition between rate limiter and Redis
- Redis memory exhaustion causing connection drops

---

## Alert 4 — Block Rate Spike on Sensitive Endpoint (Warning)

```
Threshold : block rate on /login or /payment increases by 5× over 5-minute baseline
Window    : compared to same time previous day (day-over-day comparison)
Pages     : warning — may be an attack, may be a bug
```

A sudden spike in block rate on a sensitive endpoint is either:
- A credential stuffing or brute-force attack — expected, rate limiter doing its job
- An over-counting bug causing false positives — rate limiter blocking legitimate users

The alert fires in both cases. On-call investigates: if attack traffic is visible in logs, no action needed. If legitimate users are getting 429s unexpectedly, it's a false positive bug requiring immediate fix.

---

## Alert 5 — Rule Cache Staleness > 5 Minutes (Warning)

```
Threshold : last successful Rule DB poll > 5 minutes ago
Pages     : warning
```

The rate limiter polls the Rule DB every 30 seconds. If the last successful poll was more than 5 minutes ago, the Rule DB is either down or unreachable. Rules are stale. Any admin rule changes made in the last 5 minutes have not propagated.

Not a critical alert because stale rules from 5 minutes ago are usually fine. But if an admin just applied an emergency rate limit reduction (e.g., dropping /login from 10 to 2 req/min because of an active attack), the change isn't taking effect. That needs investigation.

---

## Alert Summary

```
Alert                           Threshold           Severity
────────────────────────────────────────────────────────────────
Decision latency p99            > 8ms (warning)     Warning
                                > 10ms               Critical
Decision availability           < 99.99%             Critical
Protection availability         < 99%                Warning
Block rate spike (sensitive)    5× baseline          Warning
Rule cache staleness            > 5 minutes          Warning
```
