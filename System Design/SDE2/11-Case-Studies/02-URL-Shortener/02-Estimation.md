
> [!info] The goal of estimation
> Estimation is not about getting exact numbers. It is about understanding the scale of the system so every design decision that follows is justified. A single machine or a thousand? Cache or no cache? One DB or sharded? Estimation answers all of that.

---

## Assumptions — always state these out loud

Before touching a single number, state your assumptions explicitly. The interviewer needs to follow your reasoning.

```
MAU         → 100M users
DAU         → 30% of MAU are daily active = 30M DAU
URL creators → 30% of DAU create URLs = 10M users/day
URLs/user   → 3 URLs per user per day
```

---

## Write QPS

```
URLs created per day = 10M users × 3 URLs = 90M/day
Seconds in a day     = 86,400 ≈ 10^5 (round up for easier math)

Write QPS = 90M / 100,000 = 900 writes/second ≈ 1k writes/second
```

---

## Read QPS

URL shorteners are extremely read-heavy. A single viral link can be clicked millions of times. A ratio of **100x reads to writes** is a reasonable assumption.

```
Read QPS = 1k × 100 = 100k reads/second (average)
```

> [!important] Average vs peak
> 100k/sec is the average. URL shorteners have massive traffic spikes — a celebrity tweets a link and 10x traffic hits in seconds. Peak QPS can be 1M+/sec. This is why caching becomes critical — you cannot hit the database on every redirect at peak load.

---

## Storage

Each URL entry stores:
```
Short URL code  →  ~50 bytes
Long URL        →  ~250 bytes  (average URL length)
ID + metadata   →  ~200 bytes  (timestamps, user info, expiry)

Total per entry →  ~500 bytes
```

```
Writes per day  = 90M entries/day
Writes per year = 90M × 365 ≈ 30B entries/year
Peak year       = ~50B entries (buffer for growth)

Storage per year = 50B × 500 bytes = 25,000 GB = 25TB/year
Storage for 10 years = 250TB
```

> [!danger] Common mistake
> Do not confuse the number of records with the storage size. 50 billion records × 500 bytes = 25TB — not 50GB. Always multiply record count by record size.

250TB over 10 years cannot fit on a single machine. This tells you upfront that **the database will need to be sharded**. You don't design sharding now — but you flag it so the interviewer knows you see it coming.

---

## Bandwidth

On every redirect, the system sends the long URL back over the network.

```
Read QPS        = 100k requests/second
Payload per req = ~300 bytes (long URL + headers)

Bandwidth = 100k × 300 bytes = 30 MB/s = 240 Mbps
```

240 Mbps is well within the range of modern infrastructure. Bandwidth is **not a bottleneck** for this system.

---

## Summary

| Metric | Value |
|---|---|
| Write QPS | ~1k/sec |
| Read QPS | ~100k/sec (avg), ~1M/sec (peak) |
| Storage | ~25TB/year |
| Storage (10 years) | ~250TB |
| Bandwidth | ~240 Mbps |

**Key implications:**
- Read-heavy → caching is essential
- 250TB over 10 years → DB sharding required
- Viral spikes → design must handle 10x peak load
