
> [!info] Availability is not "is the server alive?" — it's "did the user's request succeed?"
> A server that responds to pings but returns 500 errors to every user is not available. Availability must be measured from the user's perspective.

---

## The health check trap

The instinct when monitoring availability is to ping the server — send a heartbeat request every few seconds, check if it responds. If it responds, it's up. If it doesn't, it's down.

Health checks are genuinely useful. They're how auto-scaling detects dead instances and replaces them. But they do not measure availability.

Consider this scenario:

```
App server is running ✓
Health check endpoint returns 200 ✓
But: Redis circuit breaker is open, DB shard is unreachable
Result: every real redirect request returns 500
```

From Prometheus's health check perspective: server is healthy. From the user's perspective: the service is completely broken. The health check missed the actual failure entirely.

Availability must be measured on **real user requests**, not on synthetic pings.

---

## The availability SLI formula

Availability SLI is simple:

```
Availability = successful requests / total requests
```

Every app server keeps two counters:
- `total_requests` — incremented on every incoming request
- `successful_requests` — incremented when the response is 2xx or 3xx (301 for redirect is a success)

A 500 error, a timeout, a connection reset — none of these increment `successful_requests`.

The metrics collector scrapes both counters from all 20 servers every 15 seconds, sums them up, and computes the ratio.

---

## What counts as a success for the URL shortener

```
GET /:code → 301 redirect       ✓ success  (user gets to destination)
GET /:code → 404 not found      ✓ success  (valid response, code doesn't exist)
GET /:code → 500 server error   ✗ failure  (system broke, not user's fault)
GET /:code → timeout            ✗ failure  (user got nothing)
GET /:code → connection reset   ✗ failure  (user got nothing)
```

404 is counted as a success because the system worked correctly — it looked up the code, didn't find it, returned the appropriate response. That is not a reliability failure.

500 is a failure because the system itself broke down — Redis unreachable, DB query failed, unhandled exception. The user did nothing wrong and got no useful response.

---

## Concrete example

At peak: 1,000,000 requests arrive in one second. 100 return 500 errors (one DB shard is briefly overloaded).

```
successful_requests: 999,900
total_requests:      1,000,000

Availability SLI = 999,900 / 1,000,000 = 99.99%
```

Exactly at the SLO threshold. One more 500 in that second and you're breaching SLO.

---

> [!danger] Common misconception
> Availability is not uptime of the process. It is the fraction of user requests that succeeded. A server can be "up" in every infrastructure sense while being completely unavailable to users.

---

> [!tip] Interview framing
> "Availability SLI is successful requests divided by total requests — measured on real traffic, not health pings. Each app server tracks two counters: total requests and successful requests. 2xx and 3xx are successes, 5xx and timeouts are failures. 404 is a success — the system worked correctly. 500 is a failure — the system broke. Metrics collector scrapes the counters every 15 seconds and computes the ratio fleet-wide."
