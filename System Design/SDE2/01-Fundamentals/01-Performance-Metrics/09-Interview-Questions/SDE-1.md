# Performance Metrics — SDE-1 Interview Questions

> [!abstract] These are foundational questions testing basic understanding of latency, throughput, bandwidth and percentiles. Every SDE candidate is expected to answer these confidently.

---

> [!question] What is latency? Give me a one-line definition and a real-world example.

> [!success]- Answer
> Latency is the total time from the moment a request leaves the client to when the response arrives back.
>
> **Real-world example:** You click "Pay" on Amazon. The time between your click and the "Order Confirmed" page appearing = latency.
>
> > [!tip] Note
> > Latency can be measured one-way (client → server) or round-trip. In practice, **round-trip latency** is what matters because the user waits for the full response.

---

> [!question] What is the difference between throughput and bandwidth?

> [!success]- Answer
>
> | | Definition | Unit |
> |---|---|---|
> | **Throughput** | Number of requests completed per second | RPS / QPS |
> | **Bandwidth** | Total data transferred per second | Mbps / Gbps |
>
> **Example:**
> - A server handling 10,000 API requests/second = throughput
> - A video stream consuming 25 Mbps of network capacity = bandwidth
>
> > [!tip] Rule of thumb
> > Bandwidth matters when **data size is large** (video, files). Throughput matters when **request volume is large** (APIs, messaging).

---

> [!question] What is P99 latency and why do we care about it more than average latency?

> [!success]- Answer
> **P99 = 99% of requests complete within this time.** The remaining 1% take longer.
>
> **Why averages lie:**
> ```
> 9 requests × 10ms = 90ms
> 1 request  × 500ms = 500ms
> ──────────────────────────
> Average = 59ms  ← looks fine
> P99     = 500ms ← 1 in 100 users waiting 500ms
> ```
>
> At scale — 10M requests/day → 1% = **100,000 users** having a bad experience daily. Average hides every one of them.
>
> > [!warning] Averages hide outliers. Percentiles expose them.

---

> [!question] Which percentile would you use for a payment system vs a social media feed? Why?

> [!success]- Answer
>
> | System | Percentile | Reason |
> |---|---|---|
> | Payment | **P99.9** | Money involved — even 1 in 1000 slow transactions is unacceptable at scale |
> | Social feed | **P95** | Occasional slow feed refresh is annoying but not damaging |
>
> **The rule:** The more money or trust involved, the higher the percentile you target.
>
> > [!tip] Interview framing
> > *"For payments I'd target P99.9 — at our scale even 0.1% of failed or slow transactions represents thousands of users losing trust. For a social feed P95 is the right balance between user experience and engineering cost."*

---

> [!question] What is the latency vs throughput tradeoff? Give a simple example of when optimizing one hurts the other.

> [!success]- Answer
> Optimizing for throughput often increases latency for individual requests, and vice versa.
>
> **Classic example — batching:**
> ```
> Without batching:
>   Each DB write executes immediately
>   Latency: 5ms per request ✓
>   Throughput: limited by individual write overhead
>
> With batching:
>   100 writes collected → executed together
>   Latency: each request waits for batch to fill → 50-100ms ✗
>   Throughput: 10x improvement ✓
> ```
>
> Batching dramatically improves throughput (more work per second) but each individual user waits longer.
>
> > [!tip] Other examples
> > - **Compression** — reduces bandwidth (good) but adds CPU time (increases latency)
> > - **Connection pooling** — improves throughput but adds queue wait time under load
