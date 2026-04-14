
> [!info] SLO is the target. SLI is the measurement. Writing a number in the NFR is easy — knowing whether you're actually hitting it in production requires instrumentation.

---

## The gap between design and reality

When you design Pastebin, you calculate: Redis hit rate 80%, S3 fetch 100ms, DB lookup 5ms. You conclude p99 read latency should be around 30ms. Well under the 50ms SLO.

But those are estimates. Production is not a whiteboard.

Maybe Redis is under memory pressure and LRU is evicting hot pastes faster than expected — hit rate drops to 60%. Maybe a viral paste is getting hammered and S3 is returning 200ms instead of 100ms. Maybe the Postgres standby failover added 30 seconds of elevated latency you never accounted for.

None of this shows up in your estimates. It only shows up when you measure.

---

## What SLI actually means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   p99 read latency < 50ms
SLI (reality):  actual measured p99 = 38ms  ← this is what you observe in production
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## Pastebin's SLOs and their SLIs

From the NFR:

```
SLO 1:  p99 read latency < 50ms
SLI 1:  actual p99 measured on every GET /api/v1/pastes/:shortCode request

SLO 2:  99.99% read availability
SLI 2:  successful read requests / total read requests, measured continuously

SLO 3:  99.9% write availability
SLI 3:  successful write requests / total write requests, measured continuously
```

Reads and writes get separate availability SLOs because they run on separate fleets. Reads are the critical path — users viewing pastes. Writes are important but a slightly lower bar is acceptable (paste creation failing is worse than viewing being slightly degraded, but creation is less frequent and less latency-sensitive).

---

## Two services — measure each independently

Because pasteData and viewData are separate services on separate fleets, you measure SLIs separately per service:

```
viewData SLIs:   read latency p99, read availability
pasteData SLIs:  write latency p99, write availability
```

If you aggregate them together, a pasteData outage dilutes the viewData metrics. You'd miss a full write outage because reads look fine. Separate measurement means separate alerting — a pasteData failure pages someone even while viewData is healthy.

---

> [!tip] Interview framing
> "SLO is the target from the NFR. SLI is what we measure in production. Two services means two sets of SLIs: viewData gets read latency and read availability, pasteData gets write latency and write availability. Measuring them separately is important — aggregating them would hide a full write outage behind healthy read metrics."
