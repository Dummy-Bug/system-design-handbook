### Starting point — Daily Active Users

Assume the rate limiter is protecting a system at Google Search scale. Total internet users are roughly 5-6B, of which about 1B use Google Search regularly. Of those, 200M are daily active users.

### Steady-state QPS

200M DAU, each doing ~10 searches per day = 2B requests per day.

```
2B requests/day ÷ 100,000 seconds/day ≈ 20,000 req/sec steady state
```

This gives **~20K req/sec steady state.**

### Peak QPS

Traffic is never uniform. A major news event — a geopolitical crisis, a sports final, a product launch — can spike traffic. A realistic multiplier for organic spikes is 10-20x. 50x sounds dramatic but organic traffic doesn't behave that way — even a 9/11-level event pushes 5-10x, not 50x. 20x is the right upper bound for planning.

```
Peak = 20K × 20 = 400,000 req/sec = 400K req/sec
```

This is the number that matters for capacity planning. The rate limiter has to make allow/block decisions at 400K QPS. That means the decision path must be extremely fast — single-digit milliseconds at most.

---

## Storage — What a Rate Limiter Actually Stores

The first instinct is to store every incoming request — request ID, user ID, status, timestamp, attempt number, metadata. That adds up to ~50 bytes per request. At 400K QPS, that's 20MB/sec of writes, 50TB+ over a quarter.

That is the wrong model entirely.

A rate limiter does not store requests. It stores **counters**. To decide whether to allow a request, the only thing the rate limiter needs to know is: *how many requests has this user/endpoint made in the current window?* A single integer. That's it.

### Three key types

The rate limiter needs three types of counters, each keyed differently:

```
user:{user_id}:{window}                    → integer count
endpoint:{endpoint}:{window}               → integer count
user_endpoint:{user_id}:{endpoint}:{window} → integer count
```

### How many active keys at peak?

At peak, 20% of 200M DAU are active during the peak hour = 40M users active in one hour.

```
40M users / 60 minutes = ~670K users active per 1-minute window
```

Round up to **1M active users per minute** to account for burstiness.

Each key is small:
```
user_id    : 8 bytes
endpoint   : 16 bytes
count      : 4 bytes
window     : 4 bytes
overhead   : ~68 bytes (Redis key string, pointers, metadata)
             ─────────
Total      : ~100 bytes per key
```

Three key types per user, 1M active users:

```
1M × 3 keys × 100 bytes = 300MB live state
```

### The TTL insight — storage never grows

Here is the critical insight: rate limit counters are only useful for the duration of their window. A 1-minute counter from 3 minutes ago tells you nothing about whether to allow the current request. So every key gets a TTL equal to the window size (with a small buffer — say 2× the window to handle clock skew).

```
Window = 1 minute → TTL = 2 minutes
```

This means keys expire automatically. The total live state is always bounded at ~300MB regardless of how long the system has been running. It never accumulates. Compare this to a logging system where data grows forever — the rate limiter's state is effectively constant in size.

**300MB is tiny.** This fits comfortably in memory on a single machine, let alone a Redis cluster. Storage is not the hard problem.

---

## Why Retry Priority Is Not a Rate Limiter Concern

During estimation, a natural question comes up: should the rate limiter give priority to requests that have been retried multiple times — rewarding patience?

The answer is no, and the reasoning matters.

**It rewards the wrong caller.** The clients that retry most aggressively are not patient legitimate users — they are automated scripts and attackers. Prioritizing by retry count gives priority to exactly the traffic you are trying to suppress.

**It breaks the state model.** A rate limiter stores a single counter per key. To track retry history ("this request has been rejected 3 times before"), you would need to store per-request history per user — the storage model collapses from 300MB back into the territory of logging systems. The decision path becomes a complex lookup instead of a counter check.

**The window reset is already the fairness mechanism.** When the rate limiter blocks a request, it returns a Retry-After time. When that window expires, the counter resets to zero. The blocked user gets a clean slate, exactly equal to any new user. This is fair by design — no priority queue needed.

**Priority does exist, just not here.** If you want premium users to get higher limits than free users, you configure different rule thresholds per user tier. That is handled in the rules configuration, not by tracking retry counts at runtime. Priority at the infrastructure level belongs in the load balancer (health checks over regular traffic during a spike), not the rate limiter.

---

## Estimation Summary

```
Steady-state QPS : ~20K req/sec
Peak QPS         : ~400K req/sec  (20× spike)

Active users/min : ~1M  (20% of 200M DAU concentrated in peak hour)
Key size         : ~100 bytes
Key types        : 3  (per-user, per-endpoint, per-user-per-endpoint)
Live state       : 1M × 3 × 100B = ~300MB

TTL              : 1–2× window size  (keys self-expire, state stays bounded)
Storage growth   : none — always ~300MB
```
