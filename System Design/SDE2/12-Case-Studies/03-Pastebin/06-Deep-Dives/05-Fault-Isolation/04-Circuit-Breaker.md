
> [!info] A circuit breaker stops a failing dependency from dragging your service down with it. Instead of waiting for a timeout that never comes, it fails fast and returns a clean error.

---

## The S3 outage scenario

viewData reads paste content from S3 on every cache miss. S3 is an external dependency — it can have outages, elevated latency, or intermittent failures. AWS has had S3 incidents. It will have them again.

Without any protection, here is what happens when S3 goes down:

```
Read request arrives → cache miss → app server calls S3 → S3 hangs
App server waits for S3 response → default timeout: 30 seconds
Thread is blocked for 30 seconds
Next request arrives → another thread blocked
...
All threads blocked waiting for S3 → viewData service becomes unresponsive
New requests queue up → queue fills → requests time out waiting in queue
Result: viewData is down, even though its own code is fine
```

S3 going down has cascaded into viewData going down. Users trying to read pastes get no response — not even an error, just a hang. This is worse than a clean error message.

---

## What a circuit breaker does

A circuit breaker sits between your service and a dependency (S3 in this case). It monitors calls to that dependency and tracks the failure rate.

It has three states:

```
CLOSED   → normal operation, all requests pass through to S3
OPEN     → S3 is failing, requests are rejected immediately without calling S3
HALF-OPEN → test state, a small number of requests are allowed through to check if S3 recovered
```

The transition logic:

```
CLOSED → OPEN:
  Failure rate exceeds threshold (e.g. 50% of last 10 calls failed)
  Circuit opens — all subsequent requests fail immediately

OPEN → HALF-OPEN:
  After a cooldown period (e.g. 30 seconds), allow one test request through
  If it succeeds → transition to CLOSED (S3 recovered)
  If it fails    → stay OPEN, reset cooldown

HALF-OPEN → CLOSED:
  Test request succeeded → circuit closes, normal traffic resumes
```

---

## The result with circuit breaker

```
S3 goes down:
  First few calls fail → failure rate crosses threshold
  Circuit opens
  All subsequent requests: immediate failure, no waiting for timeout
  viewData returns: "content temporarily unavailable" → clean 503
  Threads freed immediately → service stays responsive

S3 recovers:
  Cooldown expires → half-open → test request succeeds
  Circuit closes → normal reads resume
```

The key difference: **fail fast, not fail slow**. Without a circuit breaker, threads pile up waiting 30 seconds each. With a circuit breaker, they fail in milliseconds, threads are freed, and the service stays healthy.

---

## What the client sees

```
Normal:         200 OK — paste content returned
S3 outage:      503 Service Unavailable — "content temporarily unavailable, try again shortly"
Cache hit:      200 OK — paste content returned (S3 outage irrelevant, content already in Redis)
```

Note: cache hits are completely unaffected by an S3 outage. The circuit breaker only matters for cache misses — first reads on pastes not yet in Redis. Hot pastes (the majority of traffic) are served from Redis and never touch S3.

---

> [!tip] Interview framing
> "S3 is an external dependency — it can go down. Without protection, S3 hanging causes threads to pile up waiting for timeouts, which takes down viewData. A circuit breaker monitors S3 call failures — when the failure rate crosses a threshold it opens the circuit, rejecting calls immediately instead of waiting. Service returns a clean 503 instead of hanging. Cache hits are unaffected since they never touch S3. Circuit closes again once S3 recovers, tested via half-open state."
