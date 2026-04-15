
> [!info] The problem
> The base architecture has a single database handling all reads. At 100k reads/sec on average and 1M/sec at peak, this is the first thing that breaks. Understanding exactly why — and why caching is the right fix — is what this file covers.

---

## What the base architecture looks like under load

In the base architecture, every redirect hits the database:

```
User clicks bit.ly/x7k2p9
→ App server queries DB: SELECT long_url WHERE short_code = 'x7k2p9'
→ DB responds with long URL
→ App server returns 301
```

Simple and correct. But now apply the load numbers from estimation:

```
Average read load  → 100,000 requests/second
Peak read load     → 1,000,000 requests/second (viral link, celebrity tweet)
```

Every single one of those requests hits the database. The DB has to execute a query, do an index lookup, and return a result — 100,000 times per second on average.

---

## Why a single Postgres instance can't handle this

A single Postgres instance — on good hardware, with a well-designed covering index — handles roughly **10,000 to 50,000 reads/second** under real conditions.

The exact number depends on:
- Hardware (CPU, RAM, disk type — NVMe SSD vs spinning disk)
- Query complexity (our covering index helps a lot — one index read, no row lookup)
- Connection overhead (each connection has a cost)

Even in the best case, 50k reads/sec is the ceiling. Our average load is 100k. Peak is 1M. The database falls over.

```
DB capacity  → ~50k reads/sec (optimistic)
Average load → 100k reads/sec  ← already 2x over capacity
Peak load    → 1M reads/sec    ← 20x over capacity
```

---

## Why adding more DB replicas alone is expensive and inefficient

The instinct is: if one DB can't handle 100k reads/sec, add more DB replicas and spread the load.

This works — but it's expensive. Each replica is a full copy of the database, running on its own machine, with its own disk storing the full 250TB dataset. You'd need at least 2-3 replicas to handle average load, more for peak.

More importantly — it misses the fundamental nature of this workload.

**URL redirects are not random reads.** When a celebrity tweets a link, that single short code gets clicked millions of times. The same key is read over and over. Spreading those reads across 3 DB replicas still means 3 machines executing the same query on the same row millions of times.

The real fix is to stop hitting the database for the same data repeatedly.

---

## Why caching is the right fix

A cache sits in front of the database and stores recently accessed results in memory. RAM access is orders of magnitude faster than disk:

```
RAM access    → ~100 nanoseconds
SSD access    → ~100 microseconds  (1,000x slower than RAM)
Network + DB  → ~1-10 milliseconds (10,000-100,000x slower than RAM)
```

If the most popular short codes are stored in Redis, the redirect flow becomes:

```
User clicks bit.ly/x7k2p9
→ App server checks Redis: GET x7k2p9
→ Redis returns long URL from memory  ← no DB involved
→ App server returns 301
```

The database never sees the request. At 100k reads/sec, if 80% of requests are served from cache, only 20k/sec reach the database — well within its capacity.

---

> [!important] Caching before replication
> The instinct to add DB read replicas is not wrong — but it's the wrong first move. Replicas help with distributing load. Caching eliminates load entirely for the hottest keys. Always add a cache before reaching for more DB replicas. You solve a $10 problem with a $1 fix first.

---

