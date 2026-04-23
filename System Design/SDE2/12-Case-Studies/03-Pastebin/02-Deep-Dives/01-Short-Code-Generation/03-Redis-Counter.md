
> [!info] Redis INCR is the simplest correct solution to distributed unique ID generation at Pastebin's scale.
> One atomic operation, no collision check, no retry logic, sub-millisecond latency.

---

## How Redis INCR Works

Redis is single-threaded for command execution. Every command runs atomically — no two commands interleave. INCR takes a key, increments its integer value by 1, and returns the new value. Because Redis is single-threaded, no two INCR calls ever return the same number.

```
App server A calls INCR paste_counter → returns 1001
App server B calls INCR paste_counter → returns 1002
App server C calls INCR paste_counter → returns 1003
```

Even with 10 app servers all calling INCR simultaneously, each gets a unique number. This is the core guarantee: **Redis INCR is collision-free by design.**

---

## Base62 Encoding the Counter

The counter returns an integer. To get a short code, encode that integer in Base62.

```
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def base62_encode(n):
    if n == 0:
        return alphabet[0]
    result = ""
    while n > 0:
        result = alphabet[n % 62] + result
        n //= 62
    return result.zfill(6)   # pad to 6 chars
```

**Examples:**
```
counter = 1          → base62 → "000001"
counter = 62         → base62 → "000010"  (like carrying in decimal)
counter = 3844       → base62 → "000100"
counter = 1,000,000  → base62 → "004c92"
counter = 3,650,000,000 → base62 → 6 chars, fits comfortably (62^6 = 56B)
```

The codes start short ("000001") and grow naturally as the counter increases. For our entire 10-year window (3.65B pastes), all codes fit within 6 Base62 characters.

---

## Why This Is Better Than Hashing the Content

An earlier question in design was: "can we use the content hash as the short code?" 

No — SHA-256 produces a 64-character hex string. Even truncating to 6 chars reintroduces collision risk (birthday problem on a small space). The Redis counter produces a guaranteed unique 6-char code with zero collision risk.

Content hash is used as the **deduplication key** in the content table. Short code is a separate, user-facing identifier generated independently.

---

## Latency Impact

Redis INCR latency: 0.1–0.5ms. At 30 writes/sec, this adds less than 0.5ms to write latency. Well within our p99 < 100ms write SLO. Not a bottleneck.

---

## The Counter Persistence Question

Redis is in-memory. If Redis restarts and the counter resets to 0, you'd reissue codes that already exist in the pastes table — collisions.

**Fix: Redis persistence (AOF or RDB)**
- AOF (Append-Only File): every INCR is written to disk before acknowledged. On restart, Redis replays the log and recovers the exact counter value.
- RDB (snapshot): periodic dump to disk. On restart, counter recovers to last snapshot value + a small gap.

AOF is the right choice here — the INCR counter must survive restarts exactly. AOF guarantees this with fsync-per-write mode.

Alternatively: Redis Sentinel or Redis Cluster provides HA — if the primary goes down, a replica takes over with the replicated counter value. Combined with AOF, this is robust.

---

> [!tip] Interview framing
> "Redis INCR is atomic and single-threaded — no two calls return the same value, guaranteed collision-free. Base62 encode the integer → 6-char short code. At 3.65B pastes, counter still fits in 6 chars (62^6 = 56B). Latency: sub-millisecond, negligible impact on write SLO. Redis persistence via AOF ensures counter survives restarts. Redis Sentinel for HA."
