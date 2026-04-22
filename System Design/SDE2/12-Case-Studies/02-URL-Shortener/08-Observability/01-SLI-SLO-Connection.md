
> [!info] SLO is the target. SLI is the measurement. You need both.
> Writing "p99 redirect latency < 50ms" in your NFR is easy. Knowing whether you're actually hitting it in production requires something else entirely.

---

## The gap between design and reality

When you design a system, you make assumptions. Redis hit rate will be 80%. DB queries will take 10ms. Network hops will add 5ms. You run the numbers and conclude: p99 latency should be around 20-30ms. Well under the 50ms SLO.

But those are estimates. Production is not a whiteboard.

Maybe the Redis cluster is under memory pressure and LRU is evicting more keys than expected — your actual hit rate is 60%, not 80%. Maybe one DB shard has a hot partition from a viral URL and queries are taking 40ms instead of 10ms. Maybe a network switch between two availability zones is flapping and adding 15ms of jitter you never accounted for.

**None of this shows up in your estimates. It only shows up when you measure.**

---

## What SLI actually means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   p99 redirect latency < 50ms
SLI (reality):  actual measured p99 = 34ms  ← this is what you observe
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

For the URL shortener, the two SLOs from the NFR map directly to two SLIs:

```
SLO 1:  p99 redirect latency < 50ms
SLI 1:  actual p99 latency measured on every GET /:code request

SLO 2:  99.99% availability
SLI 2:  successful requests / total requests, measured continuously
```

---

## Why "checking if the server is alive" is not enough

A common instinct is to ping the server periodically and check if it responds. If it responds, it's up. If it doesn't, it's down.

This is called a health check, and it is useful — but it is not an SLI.

A server can respond "I'm healthy" to a ping while simultaneously returning 500 errors to every real user request. The process is running. The health check passes. But from the user's perspective, the service is completely broken.

SLI measures what users actually experience — did their request succeed, and how long did it take? Not whether the process is alive.

---

> [!tip] Interview framing
> "SLO is the target we committed to. SLI is what we actually measure in production. To know if we're meeting our p99 < 50ms SLO, we measure the actual p99 from every redirect request — that measurement is the SLI. Estimates from design aren't enough because production conditions differ. Health checks aren't availability SLIs because a running process can still return errors."
