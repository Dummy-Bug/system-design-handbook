
> [!info] Redis goes down — the cache layer disappears entirely
> Redis is the shield between your app servers and your DB. At steady state it absorbs 80%+ of all reads. When it disappears, 1M reads/sec lands directly on 16 DB read nodes that were sized for 200k/sec. Without a plan, this is a cascading failure.

---

## What happens without any protection

Redis goes down. App servers still receive 1M redirect requests/sec. Every request misses cache and falls through to DB.

```
Normal state:
1M reads/sec → Redis absorbs 800k → DB sees 200k/sec → 12.5k per node ✓

Redis down, no protection:
1M reads/sec → Redis fails → all 1M hit DB → 62.5k per node
```

Postgres handles ~10k-50k reads/sec per node depending on query complexity. At 62.5k/sec per node you are at or over the limit. Queries start queuing. Latency spikes. Connections pile up. DB nodes start timing out.

Now the app servers are waiting on timed-out DB connections. Those threads are held. New requests queue behind them. The queue grows faster than it drains. The system tips into **cascading failure** — each layer failing makes the next layer fail harder.

---

## Problem 1 — No circuit breaker makes it worse

Without a circuit breaker, every request to the dead Redis waits for a timeout before falling back to DB. Say Redis timeout is 500ms.

```
1M requests/sec × 500ms timeout = every request stalls for 500ms
→ Latency jumps from ~5ms to ~500ms
→ Thread pool exhausted waiting for timeouts
→ DB gets hit with a thundering herd all at once when timeouts expire
```

The circuit breaker fixes this. After N consecutive Redis failures in T seconds, the circuit **opens** — app servers stop trying Redis entirely and go straight to DB without waiting for a timeout.

```
Redis healthy     → circuit closed  → requests go to Redis normally
Redis failing     → 5 failures in 10s → circuit opens
Circuit open      → requests skip Redis → go straight to DB → no 500ms wait
Redis recovers    → circuit half-opens → one test request to Redis
Test succeeds     → circuit closes → traffic back to Redis
```

With the circuit breaker, the fallback to DB is immediate. No wasted timeout overhead. Latency is higher than normal (DB is slower than Redis) but not catastrophically so.

---

## Problem 2 — DB capacity under full load

Even with the circuit breaker, 1M reads/sec hitting the DB is too much. The numbers:

```
DB read capacity per node:     ~50k reads/sec (generous estimate)
Read nodes available:          16 (8 shards × 2 secondaries)
Total DB read capacity:        16 × 50k = 800k reads/sec

Incoming at peak:              1,000,000 reads/sec
Shortfall:                     200,000 reads/sec over capacity
```

The DB cannot absorb the full load even at best case. You are over capacity.

Auto-scaling helps but not fast enough — spinning up a new Postgres replica takes minutes. The traffic surge is immediate.

---

## The fix — throttle at API Gateway

The API Gateway is the entry point for all traffic. When Redis goes down and DB is approaching capacity, the API Gateway rate-limits incoming read (redirect) requests:

```
Redis down → circuit breaker opens → DB load climbs
→ API GW detects DB latency spike (or Redis health check fails)
→ API GW throttles GET /:code requests
→ Returns 503 Service Unavailable to some percentage of redirect requests
→ DB load drops to sustainable level
→ System stays alive, degraded but functional
```

**Availability takes a hit** — some users get a 503 instead of a redirect. But the system does not collapse entirely. Creation still works. The DB does not cascade. When Redis recovers, throttling is lifted and full capacity is restored.

This is the correct trade-off: **partial availability is better than total failure**.

---

## The full failure and recovery sequence

```
T=0s    Redis cluster goes down
T=0s    App servers start getting Redis connection errors
T=10s   Circuit breaker opens (5 failures in 10s threshold)
T=10s   All requests skip Redis, go straight to DB
T=10s   DB load: 1M reads/sec → nodes approaching capacity
T=15s   API GW detects DB latency spike → throttles read requests
T=15s   DB load drops to ~600k/sec → within capacity
T=15s   System running degraded: some 503s, higher latency, but alive

[Redis cluster recovers — say 20 minutes later]

T=20m   Redis nodes come back up
T=20m   Circuit breaker half-opens → sends test request to Redis
T=20m   Test succeeds → circuit closes
T=20m   API GW lifts throttling
T=20m   Traffic flows back to Redis → DB load drops to 200k/sec
T=20m   System fully restored
```

---

> [!danger] The trap — assuming auto-scaling saves you
> Auto-scaling is not instant. Spinning up a new Postgres replica takes minutes — provisioning, WAL catch-up, health checks. The traffic surge is immediate. Auto-scaling is useful for gradual growth, not for sudden cache failure. The real protection is circuit breaker + API GW throttling, not auto-scaling.

---

> [!tip] Interview framing
> "Redis down → circuit breaker opens immediately, requests skip Redis and go straight to DB. Without circuit breaker, 500ms timeouts per request cause thundering herd. DB can't absorb 1M reads/sec — API GW throttles redirect requests, returns 503 to some percentage. Partial availability beats total failure. When Redis recovers, circuit half-opens, test request succeeds, circuit closes, throttling lifts."
