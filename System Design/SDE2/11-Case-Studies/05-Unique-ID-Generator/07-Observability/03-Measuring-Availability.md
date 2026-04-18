# Measuring Availability

## What counts as success

A request is successful if:
- The node returns a valid `int64` ID with HTTP 200
- The ID is unique (no duplicate)

A request is a failure if:
- The node returns a 5xx error
- The request times out
- The load balancer cannot route to any healthy node

A request that waits a few milliseconds due to clock skew and then succeeds is **not a failure** — it's a delayed success.

---

## What counts as failure

| Scenario | Counts as failure? |
|---|---|
| 5xx from node | ✅ yes |
| Request timeout | ✅ yes |
| All nodes down | ✅ yes |
| Clock skew wait (1–10ms) then success | ❌ no — delayed success |
| LB returns 429 rate limit | ✅ yes — caller couldn't get an ID |

---

## Availability calculation

```
Availability = successful requests / total requests

At 99.99% SLO:
Allowed failures = 0.01% of requests
At 1M req/sec → 100 failures/second allowed before breaching SLO
```

Track availability as a rolling 5-minute window and a rolling 1-hour window. Short windows catch sudden outages. Longer windows track slow degradation.

---

## Per-node availability

Track availability per node separately. If Node 3 has 98% availability while Nodes 1 and 2 are at 99.99%, the aggregate might still look healthy — but Node 3 is sick and needs investigation before it fully fails.
