> [!question] When does fault tolerance come up in an interview?
> It comes up the moment you add any dependency — a database, a downstream service, a third-party API. The interviewer will ask "what happens when X fails?" — this cheatsheet is your answer.

---

## The One-Line Answer

*"I design for failure as the default, not the exception — timeouts on every call, retries with backoff, circuit breakers for sustained failures, bulkheads to contain blast radius, and graceful degradation so users always get something useful."*

---

## Moment 1 — "What happens when Service X fails?"

Walk through the full failure handling chain:

*"If Payment service fails — first, timeouts ensure we don't wait forever, freeing threads quickly. Retries with exponential backoff handle transient failures. If failures are sustained, the circuit breaker opens — requests fail immediately instead of waiting, no resource waste. The bulkhead ensures Payment's failure doesn't starve Recommendations or Notifications. And graceful degradation means the user sees a clear error on payment while the rest of the app works normally."*

---

## Moment 2 — "What are the different ways a service can fail?"

The three failure modes:

| Type | Description | Detection | Fix |
|---|---|---|---|
| **Crash** | Service dies, unreachable | Health check, heartbeat | Redundancy + failover |
| **Slow** | Alive but too slow | Timeout | Timeout → retry → circuit breaker |
| **Byzantine** | Running but wrong answers | Data validation, anomaly detection | Checksums, monitoring, alerts |

---

## Moment 3 — "How do you prevent cascading failures?"

Two tools — always mention both:

**Bulkhead:**
*"Each downstream service gets its own thread pool — Payment's slowness exhausts its own 20 threads, not the shared pool. Recommendations and Notifications are completely unaffected."*

**Circuit Breaker:**
*"After N consecutive failures, the circuit opens — no more requests to the broken service. Fail immediately, free threads instantly, check recovery every 30 seconds."*

---

## Graceful Degradation Decision Framework

> [!important] Not everything should degrade gracefully

| Can it degrade? | Examples |
|---|---|
| ✅ Yes | Recommendations, search suggestions, social features, non-critical UI |
| ❌ No | Payments, bank balance, medical data, anything where wrong data = harm |

**The rule:** If wrong data causes financial loss, legal liability, or safety issues — **fail hard**.

---

## The Full Fault Tolerance Checklist

- [ ] Named all three failure modes — crash, slow, byzantine
- [ ] Timeouts on every downstream call — connect + read + write
- [ ] Retries with exponential backoff + jitter for transient failures
- [ ] Identified which operations are safe to retry (idempotent) vs not (payments, creates)
- [ ] Circuit breaker for sustained failures — N failures → open → test every 30s
- [ ] Bulkhead — isolated thread/connection pools per downstream service
- [ ] Graceful degradation — decided which paths can degrade and which must fail hard
- [ ] Mentioned redundancy for crash failures

