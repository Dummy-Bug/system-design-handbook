### The Problem It Solves

You have one rule: User A can make maximum 5 requests per minute to `/search`.

When a request arrives, you need to answer one question: how many requests has this user already made in the current minute? If less than 5 — allow. If 5 or more — block.

That's it. Fixed Window Counter answers this question using a single counter per user per window.

---

### How the Window ID Works

Every request arrives with a timestamp. To figure out which 1-minute bucket this request belongs to, you divide the Unix timestamp by 60 and take the floor:

```
window_id = floor(unix_timestamp / 60)
```

Unix timestamp is just seconds since Jan 1 1970 — an ever-increasing number. Dividing by 60 groups all timestamps within the same 60-second block into the same bucket:

```
timestamp T+0  → floor = W      ← same window
timestamp T+30 → floor = W      ← same window
timestamp T+59 → floor = W      ← same window
timestamp T+60 → floor = W+1    ← new window starts
timestamp T+90 → floor = W+1    ← still new window
```

The denominator IS the window size. Want 10-second windows? Divide by 10. Want 1-hour windows? Divide by 3600. W keeps increasing forever — but that's fine, it just needs to be a unique identifier for each window. Old keys expire via TTL and never accumulate.

---

### Redis Implementation

The Redis key encodes the user, endpoint, and window:

```
user:{user_id}:{endpoint}:{window_id}
e.g. user:abc:/search:28350000
```

On every request:

```
count = INCR user:abc:/search:W
if count == 1 → EXPIRE user:abc:/search:W 60
if count <= 5 → allow
else          → block
```

**Why INCR and not GET then SET?**

GET then SET is two separate operations. At 400K QPS, two requests for the same user can arrive at the same millisecond on different rate limiter nodes:

```
Node 1: GET → reads 4
Node 2: GET → reads 4       ← both read 4 before either writes
Node 1: 4 < 5 → SET 5 → allow
Node 2: 4 < 5 → SET 5 → allow   ← both allowed, but limit was 5
```

Both got through when only one slot remained. This is a race condition.

INCR is different. Redis is single-threaded — every command executes one at a time, in order. INCR is a single atomic operation: read, add 1, write, return new value — all in one uninterruptible step:

```
Node 1: INCR → Redis returns 5 → allow
Node 2: INCR → Redis returns 6 → block   ← correct behaviour
```

Internally INCR does the same read-add-write, but as one operation that nothing can interrupt. No race condition possible.

**Why set TTL only when count == 1?**

If you call EXPIRE on every request, a request arriving at second 59 of the window resets the TTL to 60 — the key now lives until second 119. The window bleeds into the next one, and in the worst case you hold twice the memory you planned. Set TTL once, on the first request only, when the key is first created.

---

### The Boundary Condition Bug

Fixed Window Counter has one known problem. The window resets at fixed clock boundaries — every time W increments.

User sends 5 requests at **00:58** and 5 more at **01:02**:

```
Window W   (00:00–01:00): 5 requests → counter = 5, at limit, allowed
Window W+1 (01:00–02:00): 5 requests → counter = 5, at limit, allowed
```

Both windows look fine. But in the real 60-second span from 00:58 to 01:58, the user made **10 requests** — double the limit.

```
|-------- Window W --------|-------- Window W+1 --------|
00:00                    01:00                         02:00
                    00:58 ↑↑↑↑↑  01:02 ↑↑↑↑↑
                          └── 10 requests in 60 seconds ──┘
```

This is the boundary condition. At the window edge, a user can burst to 2× the intended limit.

---

### Is This a Dealbreaker?

It depends on the use case.

For most endpoints — `/search`, `/feed`, general API access — a brief 2× burst at a window boundary is acceptable. The system isn't meaningfully harmed by 10 requests instead of 5 for a few seconds.

For sensitive endpoints — `/login`, `/payment`, `/password-reset` — even brief bursts can be exploited. 10 login attempts per minute instead of 5 doubles the brute-force attack surface. Here the boundary bug matters.

Fixed Window Counter is the right choice when simplicity and speed matter more than perfect accuracy. For sensitive endpoints, you need a better algorithm.

---

### Summary

```
Storage       : one counter per (user + endpoint + window)
Redis ops     : INCR + EXPIRE on first request, INCR only after
Accuracy      : slight over-allowance at window boundaries (up to 2×)
Complexity    : very simple — 1-2 Redis operations per request
Best for      : general API rate limiting where small bursts are acceptable
Not for       : sensitive endpoints where boundary bursts can be exploited
```
