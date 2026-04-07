# Performance Metrics — SDE-3 Interview Questions

> [!abstract] These questions test deep understanding of failure modes, tail latency math, and architecture-level thinking. SDE-3 candidates are expected to reason about edge cases and make principled tradeoff decisions.

---

> [!question] Your P99 latency is fine at 180ms but your P99.9 is 4 seconds. What could cause this and would you fix it?

> [!success]- Answer
>
> **Common causes of P99 fine but P99.9 blown:**
>
> | Cause | How it creates extreme outliers |
> |---|---|
> | **GC pauses** | Java stop-the-world GC can pause for 2-4 seconds. Rare but affects every in-flight request during the pause |
> | **Cold start** | First request to a new server hits JVM warmup, empty cache, unwarmed connection pool |
> | **DB lock contention** | Two transactions fighting over the same row — one waits. Usually milliseconds but can be seconds under high load |
> | **Retry storms** | Downstream timeout → retry → retry also times out → request waits 3× timeout duration |
> | **TCP retransmission** | Rare packet loss → TCP retransmits → adds 1-3 seconds |
>
> **How you catch it:**
> ```
> 1. Distributed tracing (Jaeger / Zipkin)
>    → traces every request end-to-end
>    → find the exact 1-in-1000 slow requests
>    → see which hop was slow
>
> 2. P99.9 dashboards
>    → must explicitly track it — won't show in P99 or average
>    → alert when P99.9 > threshold
> ```
>
> **Would you fix it?**
>
> > [!important] Depends on the system — this is a business decision, not just a technical one.
>
> | System | Fix it? | Reason |
> |---|---|---|
> | Payment | Yes — immediately | 4 seconds on a payment is unacceptable even for 1 in 1000 users |
> | Social feed | Probably not | Engineering cost exceeds user experience benefit |
> | Medical records | Yes | Trust and reliability are non-negotiable |
> | Background job | No | No user waiting on it |

---

> [!question] You have three services called in parallel. Their P99 latencies are 100ms, 150ms, and 200ms. What is the P99 of the combined response?

> [!success]- Answer
>
> **When services run in parallel, the combined response waits for the slowest one.**
>
> ```
> Service A: P99 = 100ms  ──────────┐
> Service B: P99 = 150ms  ───────────────┐
> Service C: P99 = 200ms  ────────────────────┐
>                                             ↓
>                               Must wait for ALL three
> ```
>
> **Step 1 — Naive answer: 200ms (dominated by slowest)**
> The combined response can't be faster than the slowest service.
>
> **Step 2 — The actual math (SDE-3 level):**
>
> The combined request is slow if **any one** of the three is slow:
>
> ```
> P(A fast) = 0.99
> P(B fast) = 0.99
> P(C fast) = 0.99
>
> P(all three fast) = 0.99 × 0.99 × 0.99 = 0.9703
>
> P(at least one slow) = 1 - 0.9703 = 0.0297 ≈ 3%
> ```
>
> **3% of combined requests are slow → combined system is only at P97 level.**
>
> > [!important] What does P97 mean in time?
> > - P97 of the combined system ≈ **200ms** (C's P99 — when C's slow tail hits)
> > - Combined **P99** = C's P99.7 or higher — could be 300-400ms+
> > - The combined P99 is always **worse** than the worst individual service's P99
>
> **The general rule:**
> ```
> More parallel calls = more coins being flipped
> More coins = higher chance at least one lands on slow tail
> Combined P99 degrades with every parallel dependency added
> ```
>
> **What to do about it:**
> ```
> 1. Set aggressive timeouts + fallbacks
>    → if C doesn't respond in 210ms → return partial result
>    → don't make user wait for full tail
>
> 2. Track end-to-end P99 separately from per-service P99
>    → per-service metrics will look healthy while end-to-end degrades
>
> 3. Hedge requests (advanced)
>    → send duplicate request to a second instance after 190ms
>    → use whichever responds first
>    → trades bandwidth for latency reduction
> ```
>
> > [!tip] Interview framing
> > *"With three parallel calls the combined response waits for the slowest. But it's worse than just 200ms — the probability of hitting any slow tail compounds across all three services. At P99 level, each service has a 1% slow chance — combined that's ~3% slow, meaning combined P99 is around C's P99.7 which could be significantly higher than 200ms. I'd set timeouts with fallbacks and track end-to-end P99 separately."*

---

> [!question] A senior engineer says "we should optimize for P50 latency, not P99 — most users are fine." How do you respond?

> [!success]- Answer
>
> **Challenge the premise first.**
>
> > [!danger] P50 means 50% of requests are fast. That also means 50% are slow. That is not "most users are fine."
>
> **The full argument:**
>
> **1. Challenge the framing:**
> *"P50 optimization means half your users are experiencing slow responses. At 10M requests/day that's 5M slow responses daily — that's not most users being fine."*
>
> **2. The users hitting the slow tail are often your worst-off users:**
> - Users with the most complex data (heaviest queries)
> - Users on slower networks
> - Users on older devices
> Optimizing for P50 actively ignores the users who are already disadvantaged.
>
> **3. The danger of P50 optimization:**
> Engineers can make P50 look great by fixing the fast common path while leaving the slow tail completely untouched. Metrics look great. Users suffer.
>
> **4. When P50 could be acceptable:**
> - Internal batch jobs (no human waiting)
> - Background async processing
> - Data pipeline jobs
> - Any non-user-facing system
>
> **5. The floor for user-facing systems:**
>
> | Target | Use case |
> |---|---|
> | P99.9 | Payments, medical, financial transactions |
> | P99 | User-facing APIs, search, feed loading |
> | P95 | Nice-to-have features, non-critical paths |
> | P90 | Absolute minimum for anything user-facing |
> | P50 | Batch jobs, background processing only |
>
> > [!tip] Interview framing
> > *"I'd push back on P50 — it means half the users are slow. The right floor for any user-facing system is P95 minimum, P99 for critical paths. P50 optimization is only appropriate for background jobs where no user is waiting on the result."*
