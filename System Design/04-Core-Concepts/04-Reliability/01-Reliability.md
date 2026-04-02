# Reliability

> [!question] Your system is up and users can reach it. But are they getting correct answers?
> That's reliability. And it's a completely different problem from availability.

---

## The Gap Availability Doesn't Cover

You've already covered availability — keeping the system reachable. But a system can be perfectly available and completely broken at the same time.

Reliability is the next layer — ensuring that when the system responds, the response is **correct**.

**Reliability = the system gives correct answers consistently over time.**

Not just "is it running" — but "when it runs, does it do the right thing?"

---

## Available but Wrong — It Happens More Than You Think

**Example 1 — Pricing bug**
Your e-commerce site is up. Users can access it. But due to a bug in the pricing service, every product is showing $0. The system is available — users are getting responses. But it is unreliable — the responses are wrong.

**Example 2 — Message ordering bug**
Your chat app is up. Messages are being delivered. But due to a replication lag bug, some users are seeing messages out of order. Available? Yes. Reliable? No.

**Example 3 — Stale cache**
Your news feed is loading. But the cache hasn't been invalidated and users are seeing posts from 3 hours ago as "new". Available? Yes. Reliable? No — the data is stale.

> [!warning] A hundred servers all returning wrong answers is not reliable — it's just very available at being wrong
> Adding more servers does not fix a reliability problem.

---

## The 5xx Insight

HTTP status codes make the distinction concrete:

- **503 Service Unavailable** — server is overwhelmed and rejecting requests. The server never processed your request. → **Availability problem**
- **500 Internal Server Error** — server received your request, processed it, but threw an internal error. The server was reachable → **Reliability problem**

A 500 means the system is available (it received and processed the request) but not reliable (it couldn't complete it correctly).

> [!info] Availability = can the system receive your request? Reliability = can it handle it correctly?

---

## Availability vs Reliability

| | Availability | Reliability |
|---|---|---|
| **Question** | Can users reach the system? | Are users getting correct answers? |
| **Measures** | Uptime | Correctness over time |
| **Failure looks like** | 503, timeout, connection refused | Wrong data, stale response, corrupt result |
| **Solution** | Redundancy, failover, no SPOF | Fix bugs, fix consistency, fix replication logic |
| **SLI example** | 99.9% uptime | < 0.1% error rate |

---

## Why they need to be designed for separately

Solving availability does not solve reliability. They are independent problems.

- System crashes → availability problem → add redundancy
- System returns stale data → reliability problem → fix cache invalidation
- System is down → availability problem → fix failover
- System corrupts writes under concurrent load → reliability problem → fix locking

Both use the same SLI/SLO framework. Both are measured separately. Both need to be designed for explicitly.

> [!tip] In an interview — address both explicitly
> *"For availability I'd eliminate SPOFs with redundancy and automatic failover. For reliability I'd ensure strong consistency on writes, proper cache invalidation, and monitor error rate as a separate SLI from uptime."*
