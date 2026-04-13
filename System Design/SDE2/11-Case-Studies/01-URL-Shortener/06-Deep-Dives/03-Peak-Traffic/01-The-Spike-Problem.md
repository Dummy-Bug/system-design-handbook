
> [!info] The problem
> Estimation gives you average numbers. But URL shorteners don't have average traffic — they have spikes. A celebrity tweets a link and traffic goes 10x in seconds. The base architecture and caching layer were designed for average load. This deep dive is about surviving the spike.

---

## The numbers

From estimation:

```
Average read load  → 100k reads/sec
Peak read load     → 1M reads/sec  (10x spike — viral link, celebrity tweet)
```

After caching (80% hit rate):

```
Average case:
  Total reads       → 100k/sec
  Cache hits (80%)  → 80k/sec  hitting Redis
  Cache misses      → 20k/sec  hitting DB

Peak case:
  Total reads       → 1M/sec
  Cache hits (80%)  → 800k/sec hitting Redis
  Cache misses      → 200k/sec hitting DB
```

---

## What breaks at peak

**Redis:**
A single Redis node handles roughly 100k–1M ops/sec. At 800k ops/sec, you are at the ceiling with zero headroom. Worse — all 800k of those hits might be for the **same viral URL**, all going to the **same Redis node** via consistent hashing. This is the hot key problem.

**Database:**
200k reads/sec reaching the DB at peak. A single Postgres instance handles 10k–50k reads/sec. Even with read replicas, you need enough replicas to absorb this load.

**App servers:**
1M requests/sec arriving at the system. A single app server handles maybe 10k-50k requests/sec depending on work per request. You need a fleet of app servers and something in front to distribute traffic.

---

## The three problems to solve

```
1. Hot key problem    → one viral URL overwhelming one Redis node
2. DB read load       → 200k cache misses/sec at peak
3. Traffic distribution → 1M requests/sec needs a fleet + load balancer
```

Each gets its own solution. Together they handle the spike.

---

**Next:** The hot key problem — what it is, how to detect it, and two ways to fix it.
