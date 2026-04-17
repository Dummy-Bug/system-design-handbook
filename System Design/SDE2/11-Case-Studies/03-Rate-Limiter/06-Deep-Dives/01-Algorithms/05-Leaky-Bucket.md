
## Leaky Bucket

Token Bucket allows controlled bursts. Leaky Bucket allows zero burst — a perfectly smooth, constant output rate regardless of how many requests arrive. Used when the downstream system is fragile or contractually limited.

---

## The Problem It Solves

Some downstream systems cannot handle bursts at all:

- **SMS gateway** — Twilio says "accept max 10 messages/sec." Even 11 in one second breaks the contract and they start dropping messages.
- **Payment processor** — external bank API with a hard throughput contract.
- **Hardware devices** — sensors, printers, embedded systems that physically cannot handle spikes.

Token Bucket would allow a burst up to capacity — say 20 requests at once. That's fine for your own backend. But if you're forwarding to Twilio, those 20 requests hit Twilio simultaneously and they drop 10 of them.

Leaky Bucket solves this. Requests go into a queue. They drip out at a fixed, constant rate. The downstream always sees exactly N requests per second — no spike, no burst, perfectly smooth.

```
Requests in  →  [queue]  →  drip out at constant rate  →  downstream
                           never faster, never slower
```

---

## The Core Idea

Two knobs:
```
Max queue size : how many requests can wait before being blocked
Drain rate     : how fast requests drip out to downstream (req/sec)
```

If a request arrives and the queue has space — add it, allow. If the queue is full — block immediately with 429. Requests in the queue are processed at the drain rate — the user waits (spinner) until their request drips out.

This is the user experience tradeoff: instead of an immediate block, requests can wait in queue. But if the queue is full, immediate block.

---

## Lazy Drain — Same Pattern as Token Bucket

Like Token Bucket, you don't run a background job to drain the queue every second. You calculate lazily at request time.

Redis stores per user:
```
queue_size          : current number of requests waiting
last_processed_time : timestamp when queue was last calculated
```

When a request arrives at timestamp T:
```
time_passed       = T - last_processed_time
requests_drained  = time_passed × drain_rate
new_queue_size    = max(queue_size - requests_drained, 0)

if new_queue_size < max_queue_size:
    new_queue_size = new_queue_size + 1  → allow
    update Redis: queue_size = new_queue_size, last_processed_time = T
else:
    block (429)
```

`max(..., 0)` ensures the queue never goes negative — same as Token Bucket's `min(..., capacity)` ceiling, just inverted.

---

## Worked Example

User `abc` hitting a `/sms` endpoint. Max queue = 10, drain rate = 2 req/sec.

Redis state before request:
```
queue_size          = 8
last_processed_time = 1745000100
```

Request arrives at T = **1745000105**:

```
time_passed      = 1745000105 - 1745000100 = 5 seconds
requests_drained = 5 × 2 = 10
new_queue_size   = max(8 - 10, 0) = 0   ← queue drained, user was slow

0 < 10 (max queue):
  new_queue_size = 0 + 1 = 1
  update Redis: queue_size = 1, last_processed_time = 1745000105
  → ALLOW

If queue_size was 10 after drain calculation:
  10 >= 10  → BLOCK (429)
```

---

## Token Bucket vs Leaky Bucket — Mirror Images

They are the same algorithm, flipped:

```
Token Bucket:
  Stores   : tokens available + last refill time
  Fills up : over time (refill rate)
  Drains   : as requests arrive (each request consumes a token)
  Allows   : bursts up to capacity

Leaky Bucket:
  Stores   : queue occupancy + last processed time
  Fills up : as requests arrive (each request adds to queue)
  Drains   : over time (drain rate)
  Allows   : zero burst — constant output rate only
```

Token Bucket is generous — it saves up tokens for bursts. Leaky Bucket is strict — it never lets requests out faster than the drain rate, no matter how long the user waited.

---

## Atomicity

Same atomicity requirement as Token Bucket. Three Redis operations:
```
1. GET queue_size
2. GET last_processed_time
3. SET new_queue_size + last_processed_time
```

Must be wrapped in a Lua script for atomicity. Covered in the Distributed Rate Limiting deep dive.

---

## Summary

```
Storage       : 2 values per user (queue_size + last_processed_time)
Redis ops     : GET + GET + SET = 3 ops (Lua script for atomicity)
Accuracy      : exact — no approximation
Burst control : zero burst — requests queue up, never spike downstream
Output rate   : perfectly constant at drain_rate
User experience : requests wait in queue (spinner) until slot available
                  if queue full → immediate 429
Best for      : forwarding to downstream systems with strict rate contracts
                (SMS gateways, external payment APIs, hardware devices)
Not for       : user-facing APIs where waiting in a queue is unacceptable
                (use Token Bucket instead — burst is better UX)
```
