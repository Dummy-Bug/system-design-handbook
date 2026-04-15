
> [!info] Circuit breaker — stopping the cascade when DynamoDB goes down
> When DynamoDB goes down, requests don't just fail — they hang, consuming threads and memory while waiting for timeouts. Without protection, the entire app server pool gets exhausted waiting for a DB that isn't responding. The circuit breaker stops this cascade.

---

## The problem without a circuit breaker

DynamoDB goes down. The app server keeps trying to write messages. Each write attempt hangs for the full timeout duration (say 5 seconds). Meanwhile, new requests keep arriving. All threads in the thread pool are now blocked waiting for DynamoDB timeouts.

```
DynamoDB down
→ Request 1: write → hangs 5s → timeout error
→ Request 2: write → hangs 5s → timeout error
→ Request 3: write → hangs 5s → timeout error
...
→ All 200 threads blocked waiting for timeouts
→ Thread pool exhausted
→ App server stops responding entirely
→ Cascade failure
```

The app server didn't fail because of DynamoDB — it failed because it kept trying to reach a dead DynamoDB.

---

## The circuit breaker

The circuit breaker sits between the app server and DynamoDB. It monitors the success/failure rate of DB calls and opens the circuit when failures exceed a threshold — stopping further requests from reaching DynamoDB at all.

**Three states:**

```
CLOSED (normal operation):
  All requests flow through to DynamoDB.
  Circuit breaker monitors error rate.

OPEN (DB is down):
  No requests reach DynamoDB.
  All calls return immediately with fallback response.
  A timer runs — after N seconds, move to HALF-OPEN.

HALF-OPEN (testing recovery):
  One test request allowed through to DynamoDB.
  Success → move to CLOSED (DB is back)
  Failure → move back to OPEN (DB still down)
```

---

## What triggers the circuit to open

The threshold is driven by your SLO. If the SLO requires 99.9% of messages delivered successfully, you open the circuit before the error rate breaches that:

```
Threshold: error rate > 1% over last 30 seconds
           AND minimum 20 requests observed (avoid opening on 1/2 failures)
→ circuit opens
```

The minimum request count prevents the circuit from opening on a single transient failure during low traffic.

---

## What the circuit breaker prevents

```
Without circuit breaker:
DynamoDB down → threads hang → thread pool exhausted → app server dead → cascade

With circuit breaker:
DynamoDB down → circuit opens → requests fail fast → threads free → app server alive
             → fallback response returned to client immediately
             → system degrades gracefully instead of collapsing
```

> [!tip] Interview framing
> "The circuit breaker opens when the DynamoDB error rate exceeds 1% over 30 seconds. In open state, requests fail fast instead of hanging — threads stay free, the app server stays alive. The half-open state probes for recovery every N seconds. This prevents a DynamoDB outage from cascading into a full app server failure."
