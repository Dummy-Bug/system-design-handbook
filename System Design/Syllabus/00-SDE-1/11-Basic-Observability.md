# Basic Observability

> This is a bonus strong hire signal for SDE-1. Most junior candidates never mention it.
> You don't need deep knowledge — you need to know enough to say the right thing when asked
> "how do you know this system is working?"

---

## The Core Question

Every production system needs an answer to: **"How do you know it's healthy?"**

At SDE-1, the interviewer is not expecting a full observability platform. They want to hear that you've thought beyond just "build the feature." Mentioning logging and metrics unprompted puts you ahead of most junior candidates.

---

## Logging

- **What it is** — record of events that happened inside your system, written to a central store
- **Structured logs** — log as JSON key-value pairs, not plain text strings. Machines can search and filter them.
  ```
  {"timestamp": "2024-01-01T10:00:00Z", "level": "ERROR", "service": "url-shortener",
   "message": "DB connection failed", "request_id": "abc-123"}
  ```
- **Log levels** — DEBUG (everything), INFO (normal events), WARN (unexpected but not broken), ERROR (something failed). Only ship WARN and above in production.
- **Correlation ID** — attach a unique ID to every request at the entry point, pass it through every service call, include it in every log line. When something fails, search logs by that ID to trace exactly what happened.

---

## Metrics — The Three That Always Matter

Track these three for every system you design:

| Metric | What it tells you | Example |
|---|---|---|
| **Error rate** | % of requests failing | "5xx responses / total requests" |
| **Latency P99** | Worst-case response time for 99% of users | "99% of redirects complete in < 50ms" |
| **QPS** | Current load on the system | "12,000 reads/sec" |

- Stack: **Prometheus** (collect and store metrics) + **Grafana** (visualize them on dashboards)
- **Alert on error rate and latency** — not CPU or disk space. CPU at 90% with 0% errors is fine. 2% errors with 10% CPU is a page.

---

## What to Say in an Interview

When you finish your design, add one sentence before the interviewer has to ask:

> "For observability I'd add structured logging with a correlation ID on every request, and track three key metrics — error rate, P99 latency, and QPS — with an alert if error rate exceeds 1% or P99 crosses our latency SLO."

That one sentence tells the interviewer:
- You know what a correlation ID is and why it exists
- You know which metrics matter (not "I'd monitor everything")
- You know to alert on symptoms, not causes
- You've thought about production, not just the happy path

---

## What NOT to do at SDE-1

- Do not go deep on distributed tracing, Prometheus federation, or sampling strategies — those are SDE-3 topics
- Do not say "I'd add monitoring" without saying what you'd monitor
- Do not confuse logging and metrics — logs are events ("error happened at 10:00"), metrics are numbers over time ("error rate is 2%")
