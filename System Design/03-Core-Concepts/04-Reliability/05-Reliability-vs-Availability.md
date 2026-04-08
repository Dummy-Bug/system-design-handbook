> [!question] Both measure how "healthy" a system is. So why are they different?
> Because a system can be perfectly available and completely broken at the same time.

---

## The core distinction

**Availability** asks: *can users reach the system?*
**Reliability** asks: *when they reach it, do they get correct answers?*

These are independent. You can have any combination:

|                  | Available                             | Not Available                                      |
| ---------------- | ------------------------------------- | -------------------------------------------------- |
| **Reliable**     | System is up, responses are correct ✅ | System is down, but when it was up it was correct  |
| **Not Reliable** | System is up, responses are wrong ❌   | System is down and was returning wrong data anyway |

The dangerous quadrant is **available but not reliable** — users are reaching the system, getting responses, and trusting those responses. But the responses are wrong.

---

## Same failure, different diagnosis

| What happened | Which problem |
|---|---|
| Server crashes, users get connection refused | Availability — system unreachable |
| Server is up, pricing bug returns $0 for all products | Reliability — wrong response |
| DB goes down, users get 503 | Availability — dependency failure |
| DB replication lag, users see stale data | Reliability — incorrect data |
| Too many requests, server rejects with 503 | Availability — overwhelmed |
| Too many concurrent writes, data gets corrupted | Reliability — correctness failure under load |

---

## The 5xx reminder

HTTP status codes make the split concrete:

- **503** — server never processed the request → **Availability problem**
- **500** — server processed it but failed → **Reliability problem**

A 500 means the system was available enough to receive and process your request — it just couldn't complete it correctly.

---

## Different solutions

Solving availability does **not** solve reliability. They require completely separate engineering work.

| Problem | Solution |
|---|---|
| System crashes | Add redundancy, automated failover |
| System returns stale data | Fix cache invalidation |
| System is overloaded | Add capacity, load balancing |
| System corrupts writes under concurrency | Fix locking, transactions |
| System is unreachable | Fix network, eliminate SPOF |
| System returns wrong results | Fix the bug, fix replication logic |

> [!warning] Adding more servers does not fix a reliability problem
> A hundred servers all returning wrong answers is not reliable — it's just very available at being wrong.

---

## Measured separately as SLIs

Because they're independent problems, they need independent measurements:

```
Availability SLI  =  successful requests / total requests        target: 99.9%
Reliability SLI   =  correct responses / total responses         target: < 0.1% error rate
```

A system can hit its availability SLO (99.9% uptime) and completely miss its reliability SLO (2% error rate) at the same time.

> [!tip] In an interview — always address both explicitly
> *"For availability I'd eliminate SPOFs with redundancy and automatic failover. For reliability I'd ensure strong consistency on writes, proper cache invalidation, and track error rate as a separate SLI from uptime."*
