
## Sliding Window Counter

Fixed Window Counter has a boundary bug — 2× burst at window edges. Sliding Window Log fixes it perfectly but memory explodes with high limits. Sliding Window Counter fixes both: rolling window accuracy with fixed memory cost.

---

## The Problem It Solves

Fixed Window Counter stores one integer per user. Fast, cheap — but lets through 2× the limit at window edges.

Sliding Window Log stores every request timestamp. Perfect accuracy — but memory scales with the limit. A limit of 1000 req/min means 1000 timestamps per user. At 1M active users that's 58GB just for rate limit state.

Sliding Window Counter keeps the memory of Fixed Window Counter (2 integers per user) while getting close to the accuracy of Sliding Window Log. It does this with an approximation.

---

## The Core Idea

Instead of storing individual timestamps, keep two Fixed Window counters — the current window and the previous window. When a new request arrives, use both counters together to estimate how many requests happened in the true rolling 60-second window.

The insight: the rolling window always overlaps partially with the previous window. How much it overlaps depends on how far into the current window you are. Use that overlap fraction to weight the previous window's count.

```
estimate = (previous_window_count × overlap_fraction) + current_window_count
```

Two integers. One multiplication. One addition. That's the entire algorithm.

---

## How the Overlap Fraction Works

Say the window is 1 minute. A request arrives at **02:45**.

```
Previous window : 01:00 - 02:00  →  8 requests
Current window  : 02:00 - 03:00  →  3 requests so far
Request arrives : 02:45
```

The rolling window = last 60 seconds = **01:45 to 02:45**.

```
01:00        02:00        02:45        03:00
|--prev window--|----current window----|
          |←  last 60 seconds  →|
        01:45                 02:45
```

The rolling window overlaps with:
- Previous window from **01:45 to 02:00** = 15 seconds out of 60 → **25% of previous window**
- Current window from **02:00 to 02:45** = 45 seconds → **all of current window so far**

```
seconds into current window = 02:45 - 02:00 = 45 seconds
overlap fraction = (60 - 45) / 60 = 15/60 = 0.25

estimate = (8 × 0.25) + 3 = 2 + 3 = 5
```

In general:
```
seconds_elapsed  = current_timestamp % window_size
overlap_fraction = (window_size - seconds_elapsed) / window_size
estimate         = (prev_count × overlap_fraction) + curr_count
```

---

## The Full Algorithm Step by Step

Request arrives at Unix timestamp **1745000145** for user `abc` hitting `/search`. Limit = 5 per minute.

```
seconds_elapsed      = 1745000145 % 60        = 45
current_window_id    = floor(1745000145 / 60) = 29083335
previous_window_id   = 29083334
overlap_fraction     = (60 - 45) / 60         = 0.25

Redis keys:
  prev : user:abc:/search:29083334  →  8
  curr : user:abc:/search:29083335  →  3

estimate = (8 × 0.25) + 3 = 5

5 >= 5 → BLOCK
```

If estimate was 4:
```
4 < 5 → INCR user:abc:/search:29083335 → ALLOW
```

---

## The Approximation Tradeoff

The formula assumes requests were **evenly distributed** across the previous window. In reality they might not be — all 8 requests could have arrived at 01:59, making the true rolling count much higher than 2.

This is an approximation error. Is it acceptable?

Yes — for two reasons.

First, the system is already AP. You chose availability over perfect consistency in the NFRs. A small counting approximation fits the same philosophy — you accept slight inaccuracy in exchange for simplicity and memory efficiency.

Second, the error is bounded and averages out. Over many requests and many users, the assumption of uniform distribution holds reasonably well. The estimate is rarely far off from reality. A brief over-allowance of a few requests is not meaningfully different from the boundary bug in Fixed Window — and it's far less predictable, so it can't be deliberately exploited.

> [!important] This is why Nginx and Cloudflare use this algorithm
> The approximation is good enough for production. The memory efficiency is critical at their scale. Sliding Window Counter is the right balance.

---

## Memory Comparison

```
Fixed Window Counter:
  Per user : 1 integer = 8 bytes
  1M users : 8MB

Sliding Window Log (limit = 5):
  Per user : 5 timestamps × ~58 bytes = ~290 bytes
  1M users : ~290MB

Sliding Window Log (limit = 1000):
  Per user : 1000 timestamps × ~58 bytes = ~58KB
  1M users : 58GB  ← unusable

Sliding Window Counter (any limit):
  Per user : 2 integers × 8 bytes = 16 bytes
  1M users : 16MB  ← same as Fixed Window regardless of limit
```

Sliding Window Counter uses the same memory as Fixed Window Counter no matter how high the limit is. That's the key advantage over Sliding Window Log.

---

## Atomicity Problem

The algorithm needs three Redis operations per request:

```
1. GET previous window key
2. GET current window key
3. INCR current window key (only if allowed)
```

These three operations are not atomic. Two rate limiter nodes serving the same user simultaneously can both read the same counts, both calculate the same estimate, both decide to allow, both INCR — letting through one extra request.

The fix is a **Lua script** — Redis executes the entire script as a single atomic operation. No other command can interrupt between the GET and the INCR. This is covered in full in the Distributed Rate Limiting deep dive.

---

## Summary

```
Storage       : 2 integers per user (prev window + curr window)
                memory cost is fixed regardless of limit size
Redis ops     : GET + GET + INCR = 3 ops (wrapped in Lua script for atomicity)
Accuracy      : approximate — assumes uniform distribution within window
                slight error is acceptable for most use cases
Memory        : 16MB for 1M users — same cost as Fixed Window Counter
Atomicity     : requires Lua script
Best for      : general API rate limiting at scale
                used by Nginx, Cloudflare in production
Not for       : cases where even slight approximation is unacceptable
                (use Sliding Window Log for those — /login, /payment)
```
