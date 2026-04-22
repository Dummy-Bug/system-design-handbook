
> [!info] Availability is not "is the server running?" — it is "did the user's request succeed?" A viewData instance can be alive and returning 503s for every read. That is not available.

---

## The health check trap

The instinct when monitoring availability is to ping the server — send a heartbeat every few seconds and check if it responds. If it responds, it's up.

Consider this scenario:

```
viewData instance is running ✓
Health check endpoint returns 200 ✓
But: circuit breaker is OPEN, Redis is unreachable
Result: every real read request returns 503
```

From the health check perspective: server is healthy. From the user's perspective: every paste is unreadable. The health check missed the actual failure entirely.

Availability must be measured on real user requests, not synthetic pings.

---

## The availability SLI formula

```
Availability = successful requests / total requests
```

Each viewData instance tracks two counters:
- `total_requests` — incremented on every incoming GET request
- `successful_requests` — incremented when response is 2xx or 4xx

The metrics collector scrapes both counters from all instances every 15 seconds and computes the ratio fleet-wide.

---

## What counts as success for Pastebin reads

```
GET /paste/:shortCode → 200 OK (content returned)     ✓ success
GET /paste/:shortCode → 404 (paste not found/expired) ✓ success
GET /paste/:shortCode → 503 (S3 outage, try later)    ✗ failure
GET /paste/:shortCode → 500 (unhandled server error)  ✗ failure
GET /paste/:shortCode → timeout                        ✗ failure
```

404 is a success — the system worked correctly. The paste doesn't exist or expired. That is the correct response and not a reliability failure.

503 from an S3 outage is a failure — the user asked for a paste that exists and should be readable, but the system couldn't serve it.

---

## What counts as success for Pastebin writes

```
POST /paste → 201 Created (shortCode returned)         ✓ success
POST /paste → 400 Bad Request (invalid input)          ✓ success
POST /paste → 429 Rate Limited                         ✓ success
POST /paste → 500 Server Error                         ✗ failure
POST /paste → timeout                                  ✗ failure
```

400 and 429 are successes — the system responded correctly to bad input or an abusive client. 500 means the system broke.

---

## Separate availability per service

Because pasteData and viewData are separate fleets with separate SLOs:

```
viewData availability SLI:
  successful GET requests / total GET requests
  target: 99.99% (allows ~52 minutes of downtime/year)

pasteData availability SLI:
  successful POST/DELETE requests / total POST/DELETE requests
  target: 99.9% (allows ~8.7 hours of downtime/year)
```

Tracking separately means a pasteData outage triggers its own alert without noise from viewData metrics, and vice versa.

---

> [!tip] Interview framing
> "Availability SLI is successful requests divided by total — measured on real traffic. 200 and 404 are successes (system worked correctly), 500 and 503 are failures (system broke). viewData and pasteData get separate SLIs because they run on separate fleets — aggregating them would hide a full write outage behind healthy read numbers."
