# Interview Cheatsheet — Availability

> [!question] When does availability come up in an interview and what do you actually say?
> Three moments — requirements, component proposals, and scaling discussion.

---

## Moment 1 — Requirements Phase

Before drawing anything, ask:

*"What availability SLO are we targeting — 99.9% or 99.99%?"*

Then use the answer to justify your architecture:

| SLO | What it implies |
|---|---|
| 99.9% | Single region, automated failover, 43 min downtime/month acceptable |
| 99.99% | Multi-AZ mandatory, zero-downtime deployments, 4 min downtime/month |
| 99.999% | Multi-region active-active, sub-second failover, 26 sec downtime/month |

> [!tip] This one question signals seniority immediately
> Most candidates jump straight to designing. You're quantifying the availability requirement first. That's what senior engineers do.

---

## Moment 2 — Every Component You Draw

Every time you add a box to the diagram, the interviewer can ask *"what happens if this goes down?"*

Always follow this pattern:

*"This is a potential SPOF. To eliminate it I'd run [component] in [active-active / active-passive]. Health checks detect failure within seconds and traffic automatically reroutes."*

**For stateless components (app servers, API servers):**
*"I'd run three app servers in active-active behind the load balancer. Any server can handle any request — if one dies the other two absorb the traffic instantly with no failover delay."*

**For stateful components (databases):**
*"I'd run the database in active-passive — primary handles all writes, replica is on hot standby. Automated failover promotes the replica within 30 seconds if the primary dies."*

**For the load balancer itself:**
*"The load balancer is also a SPOF. I'd run two load balancers — if one dies, DNS or a floating IP switches traffic to the second one."*

---

## Moment 3 — Scaling Discussion

When you add multiple servers for throughput, availability comes for free — but say it out loud:

*"I'm adding three app servers behind a load balancer. This handles the throughput requirement AND eliminates the app server as a SPOF — three servers in parallel at 99.9% each gives us 99.9999% availability at that tier."*

Two birds, one stone. Interviewers love when you connect decisions to multiple requirements.

---

## The One Trap to Avoid

Never say *"we'll add redundancy"* without specifying what type and how failover works.

❌ *"We'll make the database redundant"*

✅ *"We'll run the database in Active-Passive — primary handles all writes, replica is on standby. Automated failover promotes the replica within 30 seconds if the primary dies. Until a new replica is provisioned, we're temporarily back to a SPOF — so we'd alert on this and provision a new replica automatically."*

---

## The Full Availability Checklist for Every Design

- [ ] Asked for the availability SLO before designing
- [ ] Every component in the diagram has redundancy — no SPOFs
- [ ] Specified active-active for stateless, active-passive for stateful
- [ ] Mentioned health checks and automatic failover
- [ ] Connected parallel redundancy to the availability math when relevant
- [ ] Measured availability from user perspective (request success rate) not server uptime

---

## Quick Reference

```
Series:   Overall = A × B × C              (gets worse with each component)
Parallel: Overall = 1 - (1-A) × (1-B)     (gets dramatically better)

99%     = 7.2 hours/month downtime
99.9%   = 43.2 minutes/month
99.99%  = 4.32 minutes/month
99.999% = 26 seconds/month
```
