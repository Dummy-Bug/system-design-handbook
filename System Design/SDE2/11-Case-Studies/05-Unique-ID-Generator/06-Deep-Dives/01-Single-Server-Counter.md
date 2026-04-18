
## The problem we're solving

The base architecture has a race condition. Two threads handling simultaneous requests both read the counter at the same time — both see `1001`, both return `1001`. Collision.

The naive fix is a lock — only one thread can read-and-increment at a time. But before reaching for horizontal scaling, we need to ask: is locking actually a bottleneck at our scale?

---

## The math

A mutex lock/unlock on a modern CPU takes roughly **50–100ns** (nanoseconds) for an in-memory operation.

```
Max throughput = 1 / 100ns = 10,000,000 requests/second = 10M RPS
```

Our peak requirement from estimation is exactly **10M IDs/second**.

So a single server with an atomic counter can — in theory — handle peak load. Locking is not the bottleneck we thought it was.

> [!info] Why 0.1ms was wrong
> It's tempting to estimate lock overhead at 0.1ms (milliseconds). But that's 100,000ns — 1000x too slow. In-memory mutex operations happen in nanoseconds, not milliseconds. Always think in the right unit: disk I/O is milliseconds, network is microseconds, in-memory is nanoseconds.

---

## So why not just use one server?

The math works, but a single server is a **single point of failure**. If it goes down, no ID can be generated anywhere in the system — every write to every service that depends on this fails instantly.

We need multiple servers. But the moment you add a second server with its own independent counter, both servers start at 1 and immediately collide.

This is the real problem — not concurrency on a single server, but **uniqueness across multiple servers**.
