
> [!info] SLO is the target. SLI is the measurement. Writing a number in the NFR is easy — knowing whether you're actually hitting it in production requires instrumentation.

---

## The Gap Between Design and Reality

When you design the rate limiter, you estimate: Redis Lua script takes 0.1ms, network round trip 0.05ms, total decision time under 1ms. Well under the <10ms SLO.

But those are estimates. Production is not a whiteboard.

Maybe Redis is under memory pressure from too many keys accumulating. Maybe a hot key is causing contention on one node, making Lua scripts queue up. Maybe the consistent hashing is uneven and one Redis node is handling 3× the expected load. Maybe the in-process local counter is misconfigured and every request is hitting Redis instead of being filtered locally.

None of this shows up in your estimates. It only shows up when you measure.

---

## What SLI Actually Means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   p99 rate limit decision latency < 10ms
SLI (reality):  actual measured p99 = 3.2ms  ← this is what you observe in production
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## Rate Limiter SLOs and Their SLIs

From the NFRs:

```
SLO 1:  p99 rate limit decision latency < 10ms
SLI 1:  actual p99 measured on every rate limit check call
        from API gateway receiving the call to returning allow/block

SLO 2:  99.99% availability of the rate limit decision
SLI 2:  successful decisions / total decisions
        a "successful decision" = any allow or block response
        a failure = timeout, connection error, or unhandled exception

SLO 3:  false positive rate < 0.01%
SLI 3:  requests blocked that should have been allowed
        measured via sampling + manual audit
        tracks over-counting errors
```

SLO 3 is specific to rate limiters — most systems don't need a false positive SLO. But blocking legitimate users is a product failure, not just a performance issue. Tracking it explicitly keeps it visible.

---

## Why Availability and Latency Are Separate SLOs

A rate limiter can be available but slow. A slow rate limiter adds 500ms to every API call — availability SLO passes (decisions are being made), but the system is effectively broken from a user experience perspective.

A rate limiter can also be fast but unavailable — if it fails open, every decision "succeeds" instantly (by not being made at all), but the system is unprotected.

Separate SLOs catch both failure modes independently.

---

> [!tip] Interview framing
> "SLO is the target from the NFR. SLI is what we measure in production. Three SLOs for the rate limiter: decision latency p99 < 10ms, availability 99.99%, and false positive rate < 0.01%. The false positive SLO is rate-limiter specific — blocking legitimate users is a product failure that needs its own tracking."
