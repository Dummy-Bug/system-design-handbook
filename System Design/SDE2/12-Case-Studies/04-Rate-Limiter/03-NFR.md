### Availability — fail open, never block all traffic

A rate limiter sits in the critical path of every single request. If it goes down or becomes unreachable, it has two choices: allow all requests through (fail open), or reject all requests (fail closed).

Fail closed sounds safer — no unprotected traffic during the outage. But think about what it actually means: every legitimate user gets a 429 for the duration of the partition. The entire product is down. A 30-second network partition between the rate limiter and its counter store becomes a full outage visible to every user.

Fail open is the right choice. A short window of unprotected traffic — say 30 seconds while the partition resolves — is an acceptable risk. Your downstream services have their own circuit breakers, concurrency limits, and autoscaling as a second line of defense. The rate limiter is the first gate, not the only one. A brief gap in rate limiting is recoverable. Blocking all legitimate users is not.

This makes the rate limiter an **AP system** in CAP terms — availability and partition tolerance over strict consistency.

> [!important] The "autoscaling has lag" problem
> Autoscaling takes minutes to spin up new servers, so during a fail-open partition window, downstream services can get hit with more traffic than they can handle. This is why fail open alone isn't enough — downstream services must have their own concurrency limits (thread pool sizes, connection limits) as a hard floor, independent of the rate limiter.

---

### Low Latency — under 10ms added to every request

The rate limiter adds a synchronous hop to every request. A user hits the API gateway, the gateway calls the rate limiter, the rate limiter checks the counter store, returns allow/block, then the gateway forwards the request. If this adds 100ms, you've made every API call in your product 100ms slower.

The target is **under 10ms end-to-end** for the allow/block decision. This is achievable because the rate limiter does almost no work — a counter lookup and an increment, both in memory. This target directly rules out any solution that requires a DB query or a synchronous network call to a slow store.

---

### Scalability — 400K QPS, horizontally scalable

The rate limiter must handle 400K requests per second at peak. No single machine can do this. The system must scale horizontally — add more rate limiter nodes to handle more traffic. This means the rate limiter nodes themselves must be stateless (all state lives in the shared counter store), so any node can handle any request.

---

### Fault Tolerance — one component down must not cascade

If one rate limiter node crashes, traffic must route to other nodes automatically. If one shard of the counter store goes down, it should only affect the keys on that shard — not the entire system. Fault isolation is a hard requirement. A single component failure must not be visible to users as a full outage.

---

### Accuracy — never over-count, under-counting is acceptable

This NFR is specific to rate limiters and easy to get wrong.

There are two directions of counting error:

**Over-counting** — the rate limiter thinks a user has made 105 requests when they actually made 98. Result: a legitimate user gets blocked with a 429. They did nothing wrong. This is a false positive and it is unacceptable. Blocking innocent users destroys trust in the product.

**Under-counting** — the rate limiter thinks a user has made 95 requests when they actually made 102. Result: a few extra requests leak through. The system is slightly less protected than intended, but no legitimate user is harmed.

The asymmetry matters: under-counting has low cost, over-counting has high cost. This directly influences algorithm choice in the deep dive — any algorithm that introduces over-counting bias is disqualified, while algorithms that occasionally under-count are acceptable.

---

### Configurability — rules changeable at runtime without restart

Rate limit rules must be updatable without redeploying the service. If `/login` needs to drop from 10 req/min to 5 req/min because of a brute-force attack pattern, an engineer should be able to make that change and have it take effect within seconds — not after a deployment pipeline finishes. This means rules are stored externally (config service or DB), not hardcoded.

---

### Observability — SLOs, alerting, and error budget

The rate limiter sits in the critical path of every API call. Without visibility into what it's doing, you cannot tell whether it's protecting the system or silently failing open. Three things are required:

**Decision latency SLO: p99 < 10ms** — measured via histograms per node, merged at fleet level. Alert at 8ms (warning) before the SLO breaches at 10ms.

**Availability SLO: 99.99% decision availability** — is the rate limiter returning decisions? Separate from protection availability (is it actually consulting Redis?) which has a softer 99.9% target acknowledging brief fail-open windows.

**False positive SLO: < 0.01%** — rate limiters specifically need to track over-counting. Blocking legitimate users is a product failure. Sample decisions and audit blocks to detect over-counting bugs.

**Error budget** — 99.99% availability = 346 failed decisions per day budget. A 30-second bad deployment at 400K QPS × 1% error rate burns 120,000 errors — 12× the daily budget. Forces careful deployment planning.

---

## NFR Summary

```
1. Availability    — fail open during partition (AP system)
                     downstream services act as second line of defense

2. Low latency     — <10ms added per request (p99)
                     in-memory counter lookup only, no DB queries

3. Scalability     — 400K QPS at peak, horizontally scalable
                     rate limiter nodes are stateless

4. Fault tolerant  — single node/shard failure must not cascade
                     affects only traffic on that shard, not the whole system

5. Accuracy        — over-counting is not acceptable (false positives block users)
                     under-counting is acceptable (a few extra requests leak through)

6. Configurability — rules changeable at runtime without restart

7. Observability   — decision latency p99 SLO: <10ms
                     decision availability SLO: 99.99%
                     protection availability SLO: 99.9%
                     false positive SLO: <0.01%
                     error budget: 346 failed decisions/day
```
