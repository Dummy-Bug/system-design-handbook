# Redis — Single-Threaded Event Loop & Performance Ceilings

> [!info] Redis handles millions of requests per second with a single thread. Understanding why this works — and where it eventually breaks down — is what separates candidates who say "Redis is fast" from candidates who know exactly how fast, and why.

---

## Why single-threaded works — no I/O to wait for

A traditional server spends most of its time waiting, not working:

```
Traditional server handling one request:
  Request arrives
  → thread picks it up
  → thread waits for disk read       ← sitting idle, doing nothing
  → disk responds (10ms later)
  → thread processes result (200ns)
  → thread waits for network send    ← sitting idle again
  → done

Actual CPU work: ~200ns
Total time: ~10ms
CPU utilisation: 200ns / 10ms = 2%

The thread is idle 98% of the time, just waiting.
```

This is why traditional servers need many threads — while Thread 1 is waiting on disk, Thread 2 can be doing real work. But threads are expensive: each one costs memory, context switching overhead, and coordination complexity.

Redis's insight: **eliminate the waiting entirely.**

Redis keeps everything in RAM. No disk reads. A RAM lookup takes nanoseconds — the thread never waits for storage.

```
Redis handling one request:
  Request arrives
  → thread picks it up
  → RAM lookup (200ns)     ← no disk, no waiting
  → responds
  → next request

CPU utilisation: ~100%
One thread is enough because it's never idle.
```

---

## The event loop — handling thousands of connections with one thread

The question remains: how does one thread handle 10,000 simultaneous connections without them queuing up?

A traditional approach would be one thread per connection:

```
Traditional (one thread per connection):
  Thread 1 → connection A
  Thread 2 → connection B
  Thread 3 → connection C
  ...
  Thread 10,000 → connection 10,000
  
  10,000 threads × ~8MB stack = 80GB of RAM just for threads ✗
  Massive context switching overhead ✗
```

Redis uses an **event loop** instead — one thread, all connections:

```
Event loop (single thread):
  → "is anyone ready to be served?"
  → Connection A has data  → GET user:123 → RAM lookup → respond → 200ns → done
  → Connection B has data  → SET post:456 → RAM write  → respond → 200ns → done
  → Connection C has data  → INCR views   → RAM write  → respond → 200ns → done
  → nobody ready           → wait 1 microsecond → check again
  → repeat forever
```

The thread never blocks. It processes one request fully (200ns), then immediately moves to the next. Because each operation is so short, thousands of connections can be served in the time a traditional server spends on one disk read.

```
10,000 connections, each making 1 request every 10ms:
→ 1,000 requests per second arriving
→ each takes 200ns to process
→ 1,000 × 200ns = 200 microseconds of actual work per second
→ single thread has 999,800 microseconds of spare capacity per second
→ 10,000 connections served with room to spare ✓
```

> [!important] Redis's single thread works because operations are nanoseconds, not milliseconds. Remove the I/O wait, and one thread is more than enough for most systems.

---

## The three performance ceilings

Every Redis instance eventually hits one of three limits. The numbers tell you which one you're actually approaching.

```
1. RAM         → how much data you can store
2. Network     → how much data you can send/receive per second
3. CPU         → how many operations per second the single thread can process
```

**RAM ceiling:**
```
Typical production Redis server: 64–256GB RAM
Average value size: ~1KB

256GB instance:
256,000,000,000 bytes ÷ 1,000 bytes = 256,000,000 keys
→ ~256 million cached objects maximum
```

**Network ceiling:**
```
Typical server NIC: 10 Gbps = 1.25 GB/second

For 1KB values:
1,250,000,000 bytes/sec ÷ 1,000 bytes = 1,250,000 responses/sec
→ network saturates at ~1.25M ops/sec

For tiny values (100 bytes — flags, counters, booleans):
1,250,000,000 bytes/sec ÷ 100 bytes = ~12,500,000 ops/sec
→ network not the bottleneck for small values
```

**CPU ceiling (single thread):**
```
Redis benchmark on modern hardware: ~1,000,000 ops/second
→ at this point the single thread is fully saturated
→ requests start queuing → latency spikes → timeouts
```

---

## Which ceiling do you hit? — the two scenarios

The ceiling you hit first depends entirely on your access pattern.

---

### Scenario A — Data-heavy, low traffic (RAM ceiling)

You're caching 256 million user profiles. Each profile is 1KB.

**RAM calculation:**
```
256,000,000 profiles × 1,000 bytes
= 256,000,000,000 bytes
= 256 GB
→ fills the entire RAM ✓  ← RAM is the ceiling
```

**CPU check:**
```
100,000 reads/sec requested
÷ 1,000,000 ops/sec (thread capacity)
= 10% CPU utilisation
→ thread is idle 90% of the time ✓  ← CPU is nowhere near the limit
```

```
RAM:  100% used  ← ceiling hit here
CPU:  10% used   ← no problem

Solution: shard data across multiple Redis nodes (each holds a fraction)
```

---

### Scenario B — Small data, high traffic (CPU ceiling)

You're caching 10 million feature flags. Each flag is 100 bytes (just a yes/no value).

**RAM calculation:**
```
10,000,000 flags × 100 bytes
= 1,000,000,000 bytes
= 1 GB
→ barely uses the 256GB RAM ✓  ← RAM is nowhere near the limit
```

**CPU check:**
```
2,000,000 reads/sec requested
- 1,000,000 ops/sec is all the single thread can handle
= 1,000,000 requests/sec have nowhere to go
→ they queue up → latency spikes → timeouts ✗  ← CPU is the ceiling
```

```
RAM:  1GB / 256GB = 0.4% used  ← no problem
CPU:  200% overloaded           ← ceiling hit here

Solution: shard reads across multiple Redis nodes
          OR use Memcached (multi-threaded, uses all CPU cores)
```

---

## Summary

```
Why single-threaded works:
  → everything in RAM → no I/O wait → 200ns per operation
  → event loop cycles through connections at nanosecond speed
  → one thread is enough when it's never waiting

Three ceilings:
  RAM     → how much data fits (256M keys on 256GB with 1KB values)
  Network → bandwidth (1.25M ops/sec for 1KB values, 12M for 100 bytes)
  CPU     → thread throughput (~1M ops/sec)

Which ceiling you hit:
  Scenario A (large values, moderate traffic) → RAM first → shard data
  Scenario B (small values, extreme traffic)  → CPU first → shard reads
                                                 see 09-Key-Value-Stores/03-Memcached.md
                                                 for when multi-threading helps here
```
