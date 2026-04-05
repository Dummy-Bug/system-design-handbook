# Fault Tolerance — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of failure modes, timeouts, retries, circuit breakers, and graceful degradation. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is Fault Tolerance?

> [!question] What does it mean for a system to be fault tolerant? How is it different from high availability?

> [!success]- Answer
>
> **Fault tolerance** is the ability of a system to continue operating correctly even when components fail.
>
> ```
> Fault tolerant system:
>   Payment service goes down
>   → Recommendation service continues working
>   → User feed still loads
>   → Only payment-specific features are affected
>   → System degrades gracefully, doesn't collapse
>
> Non-fault tolerant system:
>   Payment service goes down
>   → Cascading failure: recommendations, feed, login all fail
>   → Entire system unavailable
> ```
>
> **Difference from high availability:**
> ```
> High availability = keep the system up as much as possible
>                     (redundancy, failover, replicas)
>
> Fault tolerance   = limit the blast radius when something does fail
>                     (circuit breakers, bulkheads, graceful degradation)
>
> HA prevents downtime. Fault tolerance contains it.
> ```
>
> A system can be highly available but not fault tolerant — if one failing component cascades and takes everything down.
>
> > [!tip] Interview framing
> > *"Fault tolerance is about containing failures — ensuring one failing component doesn't take down the whole system. High availability is about preventing downtime. HA prevents outages; fault tolerance limits their scope when outages do happen."*

---

## Q2 — Three Failure Modes

> [!question] In what three ways can a downstream service fail? Why does it matter which type it is?

> [!success]- Answer
>
> **The three failure modes:**
>
> | Type | What happens | Example | Detection |
> |---|---|---|---|
> | **Crash** | Service dies, unreachable | Server OOM-killed | Health check returns nothing |
> | **Slow** | Service responds but very slowly | DB under load | Request timeout fires |
> | **Byzantine** | Service runs but returns wrong data | Bug in pricing service | Data validation, monitoring |
>
> **Why the type matters — each requires a different fix:**
>
> ```
> Crash    → redundancy fixes it
>             add replicas, automatic failover
>             crash is detected quickly by health checks
>
> Slow     → timeout + circuit breaker fixes it
>             without timeout: threads block indefinitely
>             slow service exhaust your thread pool → you go down too
>             this is the most dangerous in cascading failure scenarios
>
> Byzantine → hardest to detect and fix
>             service looks healthy in all monitoring
>             health checks pass, latency looks normal
>             only way to detect: validate outputs, business metrics
> ```
>
> **Slow failures cause the most cascading damage:**
> ```
> Slow service → your threads block waiting for response
>               → your thread pool exhausts
>               → you stop responding to new requests
>               → your callers' threads start blocking on you
>               → cascade propagates up the call chain
> ```
>
> > [!important] Slow is more dangerous than crash. A crashed service fails fast — callers know quickly. A slow service causes threads to pile up silently until the system collapses.
>
> > [!tip] Interview framing
> > *"Three failure modes: crash (dead, fast detection), slow (dangerous, causes cascading thread exhaustion without timeouts), and Byzantine (wrong answers, hardest to detect — looks healthy in all monitoring). Always set timeouts to defend against slow failures."*

---

## Q3 — Timeouts and Retries

> [!question] What is a timeout? What is a retry? What can go wrong with retries?

> [!success]- Answer
>
> **Timeout:**
> A maximum time a caller will wait for a response before giving up.
>
> ```
> Without timeout:
>   Downstream service slow → caller thread blocks forever
>   100 concurrent requests → 100 threads blocked → thread pool exhausted
>   New requests can't be handled → caller goes down too
>
> With timeout (200ms):
>   Downstream slow → after 200ms caller gets TimeoutException
>   Thread is freed → can handle other requests
>   Caller degrades (returns error or fallback) → doesn't collapse
> ```
>
> **Retry:**
> After a failure, try the request again — useful for transient failures (momentary blip, brief network hiccup).
>
> **What can go wrong with retries:**
>
> **1. Retry storms (thundering herd):**
> ```
> Service goes down momentarily
> 1000 clients all retry immediately at the same time
> → service comes back up → immediately overwhelmed by 1000 retries
> → goes down again → all retry again → cycle repeats
>
> Fix: exponential backoff
>      retry after 1s, then 2s, then 4s, then 8s — spread the load
>
> Fix: jitter — add random delay to backoff
>      clients desynchronize their retry timing
> ```
>
> **2. Retrying non-idempotent operations:**
> ```
> POST /payments — creates a charge
> Request times out — did the charge process?
> Retry → might charge twice
>
> Fix: idempotency keys — only retry safe (GET) or idempotent operations
>      for payments: send a unique request ID, server deduplicates
> ```
>
> > [!important] Never retry without exponential backoff + jitter. Never retry non-idempotent operations (payments, creates) without idempotency keys.
>
> > [!tip] Interview framing
> > *"Timeouts free threads — without them a slow downstream exhausts your thread pool. Retries handle transient failures — but always use exponential backoff with jitter to prevent retry storms. Never retry payments or creates without idempotency keys — you risk duplicate charges."*

---

## Q4 — Circuit Breaker

> [!question] What is a circuit breaker pattern? When does it open and what happens while it's open?

> [!success]- Answer
>
> **The analogy:**
> An electrical circuit breaker stops current flow when there's a fault, preventing damage. The software pattern does the same — stops sending requests to a broken service.
>
> **The three states:**
>
> ```mermaid
> flowchart LR
>     A["CLOSED<br/>Normal operation<br/>Requests flow through"] -->|"N consecutive failures"| B["OPEN<br/>Requests fail immediately<br/>No calls to downstream"]
>     B -->|"Timeout period"| C["HALF-OPEN<br/>Send one test request"]
>     C -->|"Success"| A
>     C -->|"Failure"| B
>     style A fill:#d4edda,stroke:#28a745,color:#000
>     style B fill:#f8d7da,stroke:#dc3545,color:#000
>     style C fill:#fff3cd,stroke:#ffc107,color:#000
> ```
>
> **What happens in each state:**
> ```
> CLOSED:    all requests pass through normally
>
> OPEN:      circuit detects N consecutive failures
>            → stops calling the downstream service entirely
>            → requests fail immediately (no waiting)
>            → threads freed instantly, no cascading
>
> HALF-OPEN: after a timeout (e.g. 30 seconds)
>            → sends ONE test request
>            → success → circuit CLOSES, normal operation resumes
>            → failure → circuit stays OPEN, wait again
> ```
>
> **Why it's valuable:**
> ```
> Without circuit breaker:
>   Downstream down → your threads wait for timeout → timeout → retry → wait again
>   Thread pool slowly exhausts → you go down
>
> With circuit breaker:
>   Downstream down → N failures → circuit OPENS
>   Subsequent requests fail immediately (microseconds, not seconds)
>   Threads freed → you stay up
>   Downstream recovers → HALF-OPEN detects it → normal operation resumes
> ```
>
> > [!tip] Interview framing
> > *"Circuit breaker has three states: closed (normal), open (fail fast, don't call downstream), half-open (test recovery with one request). It prevents thread exhaustion by failing immediately instead of waiting for timeouts on every request."*

---

## Q5 — Graceful Degradation

> [!question] What is graceful degradation? Give me an example of a feature that should degrade gracefully and one that should not.

> [!success]- Answer
>
> **Graceful degradation:**
> When a non-critical component fails, the system continues serving the most important functionality — just with reduced features. Users get something useful, not an error page.
>
> ```
> Netflix example:
>   Recommendation service goes down
>   → Graceful degradation: show "Top 10 most popular" (static list)
>   → Users can still browse, search, and watch
>   → Just no personalised recommendations
>
> vs.
>   Video player service goes down
>   → Cannot degrade gracefully — video watching IS the product
>   → Must show an error and focus on recovery
> ```
>
> **Should degrade gracefully — non-critical features:**
> ```
> ✓ Personalised recommendations  → show trending instead
> ✓ Search suggestions            → show no suggestions, search still works
> ✓ Social features (likes, shares) → disable temporarily
> ✓ Non-critical notifications    → skip or queue for later
> ✓ Analytics event logging       → drop events, not critical
> ```
>
> **Should NOT degrade gracefully — critical or safety-sensitive:**
> ```
> ✗ Payment processing    → wrong charge = financial loss
> ✗ Bank balance display  → wrong amount shown = financial decision made on bad data
> ✗ Medical dosage data   → wrong value = patient harm
> ✗ Inventory counts      → overselling = unfulfillable orders
> ```
>
> **The rule:**
> If wrong data causes financial loss, legal liability, or safety issues — **fail hard, don't degrade**.
>
> > [!important] Graceful degradation only works for non-critical features. When wrong data is worse than no data, fail with a clear error rather than serving an approximation.
>
> > [!tip] Interview framing
> > *"Graceful degradation means non-critical features fail silently while the core product continues. Recommendations → show trending. Search suggestions → disable autocomplete. But payments and balances must fail hard — wrong financial data is worse than no response."*
