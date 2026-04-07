# Timeout, Retry, and Exponential Backoff

> [!abstract] These three work as a unit — timeout detects the problem, retry attempts recovery, backoff prevents making things worse.

---

## Timeout — Don't Wait Forever

### The Problem

```
Checkout service calls Payment service
Payment is slow — taking 30 seconds per request
Checkout thread sits waiting...
...and waiting...
...and waiting...
Thread stuck for 30 seconds → bulkhead fills → cascading failure
```

### The Fix

Set a **maximum wait time**. If no response arrives in time — give up and fail fast.

```
Checkout calls Payment
Timeout = 2 seconds

t=0ms    → request sent
t=2000ms → no response → timeout fires → fail fast
```

> [!success] Without timeout → thread stuck 30 seconds
> With timeout → thread freed in 2 seconds

### Types of Timeouts

| Timeout Type | What it covers | Example |
|---|---|---|
| **Connect timeout** | Time to establish connection | Server unreachable — fail fast |
| **Read timeout** | Time waiting for response after connected | Server connected but not responding |
| **Write timeout** | Time to send the request | Slow upload, large payload |

```python
# Python httpx
import httpx
client = httpx.Client(timeout=httpx.Timeout(connect=1.0, read=2.0, write=2.0))

# Java OkHttp
OkHttpClient client = new OkHttpClient.Builder()
    .connectTimeout(1, TimeUnit.SECONDS)
    .readTimeout(2, TimeUnit.SECONDS)
    .writeTimeout(2, TimeUnit.SECONDS)
    .build();
```

---

## Retry — Try Again

Timeout fired — request failed. Now what? Try again.

Not all failures are permanent. A brief network hiccup, a momentary server overload — a retry often succeeds.

```
Request fails → retry immediately
Succeeds on retry → user never noticed the first failure
```

> [!warning] But retrying immediately can make things worse

If 1000 users all hit a slow Payment service, all timeout at the same time, and all retry **immediately** — you just sent 2000 requests to an already-struggling service. Retry storm.

---

## Exponential Backoff — Retry Smartly

Wait before retrying. And wait **longer** each time.

```
Request fails    → wait 100ms  → retry
Fails again      → wait 200ms  → retry
Fails again      → wait 400ms  → retry
Fails again      → wait 800ms  → retry
Fails again      → give up → graceful degradation
```

Each wait doubles — that's exponential backoff. The struggling service gets breathing room to recover.

### Jitter — Add Randomness

Even with backoff, if 1000 users all started at the same time they'll all retry at the same intervals — still synchronized.

Add **jitter** (random noise) to desynchronize:

```
Without jitter:  all 1000 users retry at exactly t=100ms → spike
With jitter:     user 1 retries at 94ms, user 2 at 112ms, user 3 at 87ms → spread out
```

```python
import random
import time

def retry_with_backoff(fn, max_retries=4):
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) * 100  # exponential: 100, 200, 400, 800ms
            jitter = random.randint(0, 50)  # add up to 50ms randomness
            time.sleep((wait + jitter) / 1000)
```

---

## The Three Together

```
Service call fails
    ↓
Timeout fires (don't wait forever)
    ↓
Retry with exponential backoff + jitter (try again, smartly)
    ↓
Max retries exhausted
    ↓
Graceful degradation (return something useful)
```

> [!tip] Interview framing
> *"I'd set connect and read timeouts on every service call — no unbounded waits. On failure, retry with exponential backoff and jitter — doubles the wait each attempt, randomness prevents synchronized retry storms. After max retries, fall back to cached data or a degraded response."*

---

## What Not to Retry

> [!danger] Never retry non-idempotent operations blindly

| Operation | Retry safe? | Reason |
|---|---|---|
| GET request | ✅ Yes | Reading data — safe to repeat |
| PUT (full update) | ✅ Yes | Idempotent — same result each time |
| DELETE | ✅ Yes | Idempotent |
| POST (create order) | ❌ No | Could create duplicate orders |
| Payment charge | ❌ No | Could charge twice |

For non-idempotent operations — use **idempotency keys** so the server can detect and ignore duplicate requests, making retries safe.
