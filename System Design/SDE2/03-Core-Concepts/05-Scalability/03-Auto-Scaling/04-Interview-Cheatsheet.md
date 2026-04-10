# Interview Cheatsheet — Auto-Scaling

> [!question] When does auto-scaling come up in an interview and what do you actually say?
> It comes up at two moments — when you discuss handling variable load, and when the interviewer asks "what happens when traffic spikes?"

---

## Moment 1 — Requirements Phase

When discussing non-functional requirements, ask:

*"What does the traffic pattern look like? Is it steady, does it have daily peaks, or are there unpredictable spikes?"*

The answer shapes your scaling strategy:

| Traffic Pattern | Strategy |
|---|---|
| Steady, predictable | Fixed capacity or light auto-scaling |
| Daily peaks (9am, weekends) | Predictive scaling — pre-scale before known peaks |
| Unpredictable spikes (viral content, flash sales) | Reactive auto-scaling + warm pool for fast response |
| Scheduled events (product launch, show release) | Manual pre-scaling + predictive scaling |

---

## Moment 2 — "What Happens When Traffic Spikes?"

Walk through the full picture:

*"I'd configure auto-scaling on the app server tier — CPU above 70% for one minute triggers scale-out, adds servers from a warm pool for near-instant capacity. New servers boot from pre-baked AMIs — everything pre-installed, ready in 90 seconds. For known traffic patterns like daily peaks, I'd add predictive scaling rules that pre-scale 15 minutes before the expected spike so cold start is off the critical path entirely."*

Then address scale-in:

*"For scale-in — when CPU drops below 30% for 15 consecutive minutes — I'd drain connections first. The load balancer stops sending new requests to terminating servers, existing in-flight requests complete, then the server is removed. No user-facing errors from the scale-in."*

---

## The Statelessness Point — Say It Out Loud

Auto-scaling only works if servers are stateless. Always mention this:

*"For auto-scaling to work correctly, app servers must be stateless — no session data in memory. Sessions live in Redis, all persistent state in the database. Servers are interchangeable and disposable — any server can handle any request."*

This shows you understand the architectural constraint, not just the scaling mechanism.

---

## The Full Auto-Scaling Checklist

- [ ] Asked about traffic patterns before designing
- [ ] Specified which tier scales (app servers — not databases, not load balancers)
- [ ] Named the metric triggering scale-out (CPU, queue depth, custom)
- [ ] Mentioned asymmetry — aggressive scale-out, conservative scale-in
- [ ] Addressed cold start — AMIs, warm pools, or predictive scaling
- [ ] Mentioned connection draining for scale-in
- [ ] Confirmed servers are stateless

---

## Quick Reference

```
Scale out trigger:  CPU > 70% for 1 min  → add servers immediately
Scale in trigger:   CPU < 30% for 15 min → drain + remove slowly

Cold start fixes:
  Pre-baked AMI   → 7 min boot → 90 seconds
  Warm pool       → 90 seconds → 5 seconds
  Predictive      → cold start happens before spike, not during

Connection draining:
  1. Stop new requests to terminating server
  2. Let in-flight requests complete
  3. Terminate when 0 active connections (or timeout)

Stateless requirement:
  Sessions    → Redis
  State       → Database
  Servers     → disposable, interchangeable
```
