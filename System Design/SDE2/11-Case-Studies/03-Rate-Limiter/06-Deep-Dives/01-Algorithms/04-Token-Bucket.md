
## Token Bucket

Window-based algorithms control average rate but can't control instantaneous bursts. Token Bucket solves this with two separate knobs — one for burst size, one for sustained rate.

---

## The Problem It Solves

With Sliding Window Counter, the limit is say 60 requests per minute. A user can send all 60 in the first second of the window — all allowed. Then silence for 59 seconds. Then another 60 in the first second of the next window.

```
second 0   : 60 requests → all allowed  (window just reset)
second 1-59: silence
second 60  : 60 requests → all allowed  (new window)
```

The backend sees **120 requests in 2 seconds**. The rate limiter said "60 per minute" but the backend got hammered with a spike it wasn't designed for.

This creates two problems:

**Backend gets overwhelmed** — a backend designed for 1 req/sec average suddenly absorbs 60x load for 1 second. Circuit breakers trip, latency spikes, cascading failures start.

**Bad user experience** — user sends 60 requests at second 0, all go through. Sends 1 more at second 30 — blocked. They've waited 30 full seconds but the window hasn't reset yet. From their perspective the rate limiter is broken.

Window-based algorithms control **average rate** but not **instantaneous burst**. Token Bucket controls both.

---

## The Core Idea

Imagine a bucket that holds tokens. The bucket has a maximum capacity — say 20 tokens. Tokens refill at a steady rate — say 5 tokens per second.

Every incoming request consumes 1 token. If the bucket has tokens — allow, decrement. If the bucket is empty — block.

```
Bucket capacity : 20 tokens  (maximum burst a user can ever send)
Refill rate     : 5 tokens/sec  (sustained average rate over time)

User arrives, bucket full (20 tokens):
  Request 1  → bucket = 19 → allow
  Request 2  → bucket = 18 → allow
  ...
  Request 20 → bucket = 0  → allow
  Request 21 → bucket = 0  → BLOCK

1 second passes → 5 tokens refilled → bucket = 5
  Request 22 → bucket = 4 → allow
  ...
```

Two separate knobs:
```
Capacity    → controls maximum burst size
Refill rate → controls average sustained rate
```

This is the fundamental advantage over window-based algorithms. You can say: "allow bursts of up to 20 requests, but sustain no more than 5 per second on average." Window-based algorithms can only express one number — requests per window.

---

## Why Background Job Refill Fails

The naive approach to refilling: run a background job every second that increments every active user's token count by the refill rate.

```
Every second:
  FOR each active user:
    INCR user:{id}:tokens by 5
    CAP at capacity (20)
```

At 1M active users this becomes:

```
1M users × 1 INCR per second = 1,000,000 Redis writes per second
                                just for refilling — before any actual requests
```

Our entire request budget is 400K QPS. The refill job alone would need 1M ops/sec — 2.5× our total request capacity, just to keep tokens topped up. And this runs constantly whether users are making requests or not.

Beyond the Redis load, you'd need a distributed scheduler to coordinate which worker refills which users, handle failures, avoid double-refills. An entire infrastructure component just to increment counters.

This is the wrong approach entirely.

---

## Lazy Refill — No Background Job

Instead of refilling on a timer, calculate the refill **lazily** — only when a request actually arrives.

Store two things per user in Redis:
```
current_tokens     : how many tokens the user currently has
last_refill_time   : Unix timestamp of the last time tokens were calculated
```

When a request arrives at timestamp T:
```
time_passed    = T - last_refill_time
tokens_to_add  = time_passed × refill_rate
new_tokens     = min(current_tokens + tokens_to_add, capacity)
```

`min(..., capacity)` is critical — the bucket can never overflow beyond capacity. Even if a user goes idle for 10 hours:

```
capacity = 20, refill = 5/sec, idle for 10 hours = 36,000 seconds
tokens_to_add = 36,000 × 5 = 180,000
new_tokens    = min(0 + 180,000, 20) = 20  ← capped at capacity
```

No background job. No scheduler. No distributed coordination. Just arithmetic at request time. A user who hasn't made a request in an hour gets exactly the same treatment as one who just started — their bucket refills to capacity and stops there.

---

## The Full Algorithm Step by Step

User `abc` hitting `/search`. Capacity = 20, refill rate = 5 tokens/sec.

Redis state before request:
```
user:abc:/search:tokens          = 3
user:abc:/search:last_refill     = 1745000100
```

Request arrives at T = **1745000145**:

```
time_passed    = 1745000145 - 1745000100 = 45 seconds
tokens_to_add  = 45 × 5 = 225
new_tokens     = min(3 + 225, 20) = 20   ← bucket full, user was idle

new_tokens > 0:
  decrement → 20 - 1 = 19
  update Redis:
    current_tokens   = 19
    last_refill_time = 1745000145
  → ALLOW

If new_tokens == 0:
  → BLOCK (return retry_after = 1/refill_rate = 0.2 seconds)
```

---

## Two Knobs — Capacity vs Refill Rate

This is what makes Token Bucket expressive for real production systems.

```
Capacity    = maximum burst the system tolerates
Refill rate = sustained throughput you're willing to allow
```

Examples:

```
/search endpoint (generous):
  capacity    = 100   (allow a burst of 100 for autocomplete UX)
  refill rate = 10/sec (sustain 10 req/sec average)

/login endpoint (strict):
  capacity    = 5    (never allow more than 5 attempts at once)
  refill rate = 0.08/sec (5 per minute sustained = 0.083/sec)

/payment endpoint (very strict):
  capacity    = 3
  refill rate = 0.016/sec (1 per minute)
```

Window-based algorithms can only say "N requests per window." Token Bucket can say "allow a burst of N, then throttle to M per second." Far more expressive for real API behaviour.

---

## Why AWS and Stripe Use This

Real API clients are naturally bursty. A mobile app on startup makes 10 API calls in 2 seconds — profile fetch, feed load, notification count, settings sync. Then it goes quiet for minutes.

Window-based algorithms see the startup burst as an attack pattern and throttle it. Token Bucket sees it as a legitimate burst within capacity and allows it, then smoothly limits the sustained rate.

Stripe's API allows bursts for webhook retries — a payment failure triggers multiple rapid retries in quick succession. Token Bucket handles this gracefully. A sliding window would block the retries mid-sequence.

AWS API Gateway uses Token Bucket at the account level — burst limit (capacity) and rate limit (refill rate) are two separately configurable parameters, exactly matching the two knobs.

---

## Atomicity

Token Bucket requires four Redis operations per request:
```
1. GET current_tokens
2. GET last_refill_time
3. SET new_tokens (after calculation)
4. SET last_refill_time = T
```

These four operations must be atomic. Two rate limiter nodes serving the same user simultaneously would both read the same token count, both calculate the same new count, both decrement — letting through one extra request.

The fix is a Lua script — all four operations wrapped in a single atomic unit. Covered in full in the Distributed Rate Limiting deep dive.

---

## Summary

```
Storage       : 2 values per user (current_tokens + last_refill_time)
Redis ops     : GET + GET + SET + SET = 4 ops (Lua script for atomicity)
Accuracy      : exact — no approximation
Burst control : capacity knob controls maximum burst size
Rate control  : refill rate knob controls sustained average
Refill model  : lazy — calculated at request time, no background job
Best for      : APIs with legitimate bursty clients (mobile apps, webhooks)
                used by AWS API Gateway, Stripe in production
Not for       : cases where you want strictly zero burst tolerance
                (use Leaky Bucket for that)
```
