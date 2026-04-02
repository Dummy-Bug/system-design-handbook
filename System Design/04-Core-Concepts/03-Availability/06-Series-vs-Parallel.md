# Series vs Parallel Availability

> [!question] You know the availability of each component. But what's the availability of the whole system?
> It depends on whether components are in series or parallel — and the math is completely different.

---

## Components in Series

Series means a request must go through **all** components to succeed. If **any one** fails, the whole request fails.

A typical request flow:
```
User → Load Balancer → App Server → Database
```

All three must be working. If the database goes down, it doesn't matter that the load balancer and app server are fine — the request fails.

### Why you multiply

For the request to succeed, the load balancer must work **AND** the app server must work **AND** the database must work.

AND conditions = multiply probabilities. This is basic probability.

Why not add? Adding 99.9% + 99.9% + 99.9% = 299.7% — over 100%, which makes no sense for a probability.

```
Overall Availability = A × B × C

Load Balancer: 99.9%  →  0.999
App Server:    99.9%  →  0.999
Database:      99.9%  →  0.999

Overall = 0.999 × 0.999 × 0.999 = 99.7%
```

> [!warning] Each component added in series makes the system less available
> Three components each at 99.9% — combined they give only 99.7%.
> The chain is only as strong as its weakest link.

---

## Components in Parallel

Parallel means multiple copies of the same component. The request only needs **one** of them to succeed.

Example — two app servers. If one dies, the other handles the request.

### Why you can't just add

Adding 99.9% + 99.9% = 199.8% — again over 100%. Adding probabilities only works for mutually exclusive events.

### The correct approach — calculate from the failure side

The only way a parallel system fails is if **every single copy fails simultaneously**.

```
Chance Server A fails = 0.001
Chance Server B fails = 0.001

Chance BOTH fail simultaneously = 0.001 × 0.001 = 0.000001

Overall Availability = 1 - 0.000001 = 99.9999%
```

The `1 -` means: *"everything except the case where all copies fail."*

Two servers each at 99.9% — combined in parallel they give 99.9999%.

> [!tip] This is the mathematical proof of why redundancy works
> Adding a second server takes you from 99.9% to 99.9999%. That's the difference between 43 minutes and 26 seconds of downtime per month.

---

## The Real World Nuance — Theoretical vs Observed Availability

The calculations above are **theoretical** — they assume the load balancer detects failure instantly and routes perfectly.

In reality, availability is slightly lower because of:

- **Detection delay** — load balancer health checks run every 5-30 seconds. In that window, some requests get routed to a dead server
- **In-flight failures** — a server can die mid-request, after already receiving it. That specific request fails even though the load balancer didn't know yet
- **Retry overhead** — the client retries, the retry succeeds, but the user still experienced a failure

> [!info] This is why you measure availability from the user's perspective — not from component uptime
>
> *"Our servers were up 99.99% of the time"* — theoretical, measured from component health
>
> *"99.98% of requests succeeded"* — observed, what users actually experienced
>
> The SLI (request success rate) is what actually matters in production. The calculations are useful for architecture planning and comparing designs — not for production monitoring.

---

## Combining Both — A Real System

Most real systems have series AND parallel components together:

```
Users → Load Balancer (×2, parallel) → App Servers (×3, parallel) → Database (primary + replica, parallel)
```

Calculate step by step:
1. Two load balancers in parallel → very high availability
2. Three app servers in parallel → very high availability
3. Primary + replica DB in parallel → very high availability
4. All three tiers in series → multiply them together

> [!tip] In an interview
> When asked about availability, identify which components are in series and which are parallel. Then explain: "each tier in series reduces overall availability, which is why we add redundancy within each tier — the parallel redundancy compensates for the series penalty."
