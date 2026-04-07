# Performance Metrics — SDE-2 Interview Questions

> [!abstract] These questions test design decisions and tradeoffs — not just definitions. At SDE-2 level you must justify your metric choices and know how they interact with system architecture.

---

> [!question] You're designing a video streaming platform like YouTube. An interviewer asks you to define the performance targets. Which metrics do you pick, which percentiles, and why?

> [!success]- Answer
>
> **Metrics to track:**
>
> | Metric | What to measure | Percentile | Why |
> |---|---|---|---|
> | Latency | Time to first frame (TTFF) | P99 | User-facing — directly impacts experience |
> | Throughput | Sustained delivery rate per stream | P95 | Occasional dips absorbed by buffer |
> | Jitter | Variance in delivery latency | Keep low | Spiky delivery empties buffer → rebuffering |
> | Bandwidth | Total capacity planning | N/A | Planning number, not per-request metric |
>
> **Why P99 for latency:**
> Scale is massive. 1% of users at YouTube scale = millions of people experiencing buffering. Not P99.9 because video stutter is annoying but not catastrophic like a failed payment.
>
> **Why P95 for throughput:**
> Video players have buffers — occasional throughput dips don't immediately affect the user if the buffer absorbs them.
>
> **Why jitter matters more than raw latency:**
> A consistently 200ms delivery is better than delivery that jumps between 50ms and 800ms. The buffer drains during the 800ms gaps → visible stutter.
>
> **Why bandwidth is a planning number:**
> Bandwidth = concurrent streams × average bitrate. This is used for capacity planning, not per-request measurement.
>
> > [!tip] Interview framing
> > *"For video streaming I'd track time to first frame at P99, sustained throughput per stream at P95, and jitter. Bandwidth is a capacity planning number — at peak concurrent streams × average bitrate we size CDN and origin capacity accordingly."*

---

> [!question] Your service has P99 latency of 800ms but your SLO target is P99 < 200ms. The team suggests increasing the SLO to 800ms to match reality. What do you say?

> [!success]- Answer
>
> **Changing the SLO to match bad performance is wrong.**
>
> > [!danger] Never adjust the target to match the measurement. Fix the system.
>
> **Why it's wrong:**
> 1. **SLO exists to protect user experience** — relaxing it hides the problem, doesn't solve it
> 2. **SLA is derived from SLO** — relaxing SLO to 800ms means your SLA with customers becomes ~1000ms. That's a contractual regression.
> 3. **Error budget burns faster** — at 800ms P99 you're likely already burning error budget, limiting deployment velocity
>
> **The right response — investigate why:**
> - Was the 200ms SLO unrealistic for this system to begin with?
> - Is there a slow query, missing cache, or bug causing the regression?
> - Is it a scaling issue — too much load for current capacity?
>
> **The correct relationship:**
> ```
> SLI (what you measure): P99 = 800ms  ← problem is here
> SLO (internal target):  P99 < 200ms  ← keep this
> SLA (external contract): P99 < 300ms  ← never breach this
> ```
>
> Fix the SLI to meet the SLO. Never move the SLO to meet a broken SLI.

---

> [!question] You have two services called sequentially — Service A (P99 = 50ms) and Service B (P99 = 50ms). What is the P99 latency of the combined request?

> [!success]- Answer
>
> **Not 100ms. It's worse.**
>
> Percentiles don't add linearly. Here's why:
>
> ```
> P99 of A = 50ms → 1% of A requests take longer than 50ms
> P99 of B = 50ms → 1% of B requests take longer than 50ms
>
> Combined is slow if A is slow OR B is slow:
> P(combined slow) = 1 - (0.99 × 0.99) = ~2%
>
> So combined is only at ~P98 level
> Combined P99 > 100ms + network overhead
> ```
>
> **Plus network overhead** — each hop adds serialization, network transit, deserialization time.
>
> **The rule:** For N sequential services at P99, combined tail latency compounds. This is called **tail latency amplification**.
>
> > [!warning] Tail Latency Amplification
> > With 10 sequential microservices each at P99, the combined system may only be at P90. This is why engineers set per-service latency budgets and use timeouts at every hop.
>
> > [!tip] Interview framing
> > *"Percentiles don't add linearly — the combined P99 is worse than the sum because the slow tails of each service can compound on the same request. With N sequential calls I'd track end-to-end P99 separately from per-service P99 and use timeouts at each hop."*

---

> [!question] Your service has great average latency of 20ms but users are complaining about slow experience. What do you investigate first and how?

> [!success]- Answer
>
> **Investigate P99 immediately — average is meaningless when users are complaining.**
>
> > [!quote] Average latency means nothing — everything before "but" is irrelevant.
>
> **Investigation steps:**
>
> ```
> Step 1: Pull P95, P99, P99.9 from your monitoring dashboard
>         → identify where the tail starts blowing up
>
> Step 2: Use distributed tracing (Jaeger / Zipkin)
>         → find which specific requests are slow
>         → identify which service hop is the bottleneck
>
> Step 3: Correlate with system events
>         → GC pauses? (Java)
>         → DB lock contention?
>         → Cold starts from recent scale-out?
>         → Downstream service degradation?
> ```
>
> **Why average hides this:**
> If 95% of requests take 5ms and 5% take 400ms — average = ~25ms. Looks fine. But 5% of users at scale is millions of people.

---

> [!question] You're designing a ride-hailing app like Uber. What metrics, what percentiles, and why?

> [!success]- Answer
>
> **Metrics to track:**
>
> | Metric | What | Percentile | Why |
> |---|---|---|---|
> | Latency | Matching request → driver assigned | P99 | High-anxiety user moment — must be fast |
> | Latency | Live location update during ride | P95 | Slightly stale location tolerable |
> | Throughput | Driver location write QPS | Track | Millions of drivers updating every 3-5s = massive write volume |
> | Throughput | User map read QPS | Track | Users checking map constantly = heavy read load |
>
> **Why not bandwidth:**
> Location payload = `{lat, lng, timestamp}` ≈ 50 bytes. Even at 10M drivers updating every 3 seconds = negligible bandwidth. Not worth tracking.
>
> **Bandwidth rule of thumb:** Only track bandwidth when data size is large enough to cause performance issues (video, large files, images). For small payloads it's irrelevant.
>
> **The key insight — two different latency targets:**
> - Matching phase (user requesting ride) → P99, sub-second. Stale location here = driver dispatched to wrong spot.
> - Live tracking during ride → P95. 5 seconds stale is fine — user is watching a smooth animation anyway.
>
> > [!tip] Interview framing
> > *"For Uber I'd track latency at P99 for the matching phase — that's the high-anxiety moment. For live tracking during the ride P95 is fine, a few seconds stale doesn't affect experience. Throughput is critical on the write side — millions of drivers pushing location every 3-5 seconds. Bandwidth I wouldn't track — location payloads are tiny."*
