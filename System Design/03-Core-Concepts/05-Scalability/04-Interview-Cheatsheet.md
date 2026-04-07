# Interview Cheatsheet — Scalability

> [!question] When the interviewer says "now scale it to 10x traffic" — what do you actually say?
> You don't just say "add more servers." You walk through where it breaks, what you scale, and what constraints that creates.

---

## The Mental Model — Bottleneck → Fix → Next Bottleneck

Scalability is never one decision. It's a sequence:

```
10x traffic hits
  ↓
App servers CPU saturated → add servers (horizontal scaling)
  ↓
Database now the bottleneck → read replicas, caching, sharding
  ↓
Network bandwidth saturated → CDN for static content, compression
  ↓
New bottleneck revealed → repeat
```

Always present it as a chain, not a single fix.

---

## The Four Questions to Ask First

Before designing anything, ask these during requirements:

1. **"What's the expected traffic?"** — orders of magnitude matter (100 RPS vs 100,000 RPS require very different designs)
2. **"What's the traffic pattern?"** — steady, daily peaks, unpredictable spikes, scheduled events
3. **"What's the read/write ratio?"** — read-heavy systems scale differently than write-heavy ones
4. **"Are there SLA requirements?"** — latency targets constrain what you can do (sharding adds latency)

---

## What to Actually Say — The Script

### Phase 1 — App tier

*"The first bottleneck under load is the app servers. I'd scale horizontally — add servers behind a load balancer. Round robin for stateless services, least connections if request durations vary significantly. App servers must be stateless — all session data in Redis, all persistent state in the database. Stateless servers are disposable and interchangeable."*

### Phase 2 — Database

*"Once the app tier scales out, the database becomes the bottleneck. For reads, I'd add read replicas and put a cache (Redis) in front of the database — most reads hit the cache, reducing DB load by 80–90%. For writes, if a single primary can't keep up, I'd shard — partition data horizontally across multiple databases by user ID or geographic region."*

### Phase 3 — Network / static content

*"For media, images, and static assets, I'd push them to a CDN. The CDN serves content from edge nodes close to users — reduces latency and removes that traffic from our origin servers entirely."*

---

## The Three Bottlenecks — One-Line Each

| Bottleneck | Symptom | Fix |
|---|---|---|
| CPU (app servers) | High CPU, slow response times | Horizontal scaling + load balancer |
| Database | Slow queries, connection pool exhaustion | Read replicas + caching + sharding |
| Network | High bandwidth costs, slow static loads | CDN for assets, compression |

---

## Vertical vs Horizontal — Know When to Use Each

| | Vertical (bigger server) | Horizontal (more servers) |
|---|---|---|
| Use when | Quick fix, stateful systems, early stage | Production scaling, stateless services |
| Limit | Hardware ceiling — can't go beyond the biggest machine | Practically unlimited |
| Cost | Expensive at the top end | Linear cost scaling |
| Risk | Single point of failure | Redundant by nature |

*"I'd use vertical scaling as a quick fix early on or for stateful systems like databases. Horizontal scaling is the answer for the app tier — it's effectively unlimited and provides redundancy for free."*

---

## Statelessness — The Prerequisite

Horizontal scaling only works cleanly with stateless servers. Always say this:

*"Before horizontal scaling works, servers must be stateless — no session data in memory. Sessions in Redis, state in the database. Then any server can handle any request, servers are interchangeable, and auto-scaling works cleanly."*

---

## Auto-Scaling — What to Mention

*"I'd configure auto-scaling on the app tier — CPU above 70% for one minute triggers scale-out. Pre-baked AMIs get boot time under 90 seconds. For known peaks like daily traffic spikes, predictive scaling pre-scales 15 minutes early so cold start is off the critical path. Scale-in is conservative — CPU below 30% for 15 minutes — with connection draining to prevent in-flight request errors."*

---

## The Full Scalability Checklist

- [ ] Asked about traffic volume and pattern before designing
- [ ] Identified which tier is the first bottleneck (app vs DB vs network)
- [ ] Horizontal scaling on app tier — servers are stateless
- [ ] Load balancer in front of app servers — named the algorithm
- [ ] Sessions → Redis, state → database
- [ ] Cache (Redis) in front of database for reads
- [ ] Read replicas for read-heavy workloads
- [ ] Sharding only if write volume exceeds single primary
- [ ] CDN for static assets and media
- [ ] Auto-scaling with appropriate metrics, AMIs, warm pools
- [ ] Presented as a bottleneck chain, not a single answer

---

## Quick Reference

```
Bottleneck chain:
  App servers → DB → Network

App tier fix:
  Stateless servers + load balancer + auto-scaling

DB fix (reads):
  Redis cache → read replicas → sharding (last resort)

DB fix (writes):
  Vertical first → then sharding by user ID / region

Network fix:
  CDN for static assets + media

Auto-scaling trigger:
  CPU > 70% for 1 min → scale out
  CPU < 30% for 15 min → drain + scale in

Statelessness rule:
  Sessions → Redis
  State    → Database
  Servers  → disposable, interchangeable
```
