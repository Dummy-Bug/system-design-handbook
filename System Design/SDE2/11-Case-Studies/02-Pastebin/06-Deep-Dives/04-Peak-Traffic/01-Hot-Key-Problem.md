
> [!info] Before adding infrastructure to solve a problem, verify the problem actually exists at your scale. Numbers first, solution second.

---

## The scenario

Pastebin is a link-sharing service. Someone with 100k Twitter followers pastes an incident log or a config snippet and tweets the link. Within minutes, tens of thousands of people click the same URL. One specific short code is now receiving a disproportionate share of all read traffic — this is called the **hot key problem**.

The question is: does this actually break anything?

---

## Step 1 — Understand what "hot key" means for Redis

Redis is a single-threaded in-memory store. All reads and writes go through one event loop. Its throughput limit for simple GET operations is approximately **100,000 operations per second** on a single instance.

That means if one key is being read 100,000 times per second, Redis is at capacity — serving nothing else.

The hot key problem becomes real when a single key's traffic approaches or exceeds the single-instance throughput limit.

---

## Step 2 — What is our total peak read QPS?

From estimation:

```
DAU:              2M
Reads per DAU:    0.5 pastes/day × 100 (read:write ratio) = 50 reads/DAU/day
Total reads/day:  2M × 50 = 100M reads/day
Avg read QPS:     100M / 100,000 = 1,000 reads/sec
Peak read QPS:    1,000 × 3 = 3,000 reads/sec
```

Our entire system — all short codes combined — peaks at **3,000 reads/sec**.

---

## Step 3 — What fraction could a single hot key receive?

Assume worst case: a viral paste captures 10% of all peak traffic. That is an extreme assumption — 10% of all Pastebin reads going to one link simultaneously.

```
Hot key traffic = 10% × 3,000 = 300 reads/sec
```

Even at this extreme, one hot short code is seeing **300 reads/sec**.

Redis capacity is **100,000 ops/sec**.

```
300 / 100,000 = 0.3% of Redis capacity
```

A hot key consuming 0.3% of Redis capacity is not a problem. Redis has **333× headroom** above this load.

---

## Step 4 — The verdict

```
Redis capacity:          100,000 ops/sec
Total system peak QPS:     3,000 reads/sec
Headroom factor:              33×

Even a hot key at 10% of peak:
  300 reads/sec vs 100,000 ops/sec = 0.3% utilisation
```

The hot key problem does not exist at this scale. Our peak read traffic is too low to stress a single Redis instance, let alone a single key within it.

> [!important] Recognising when a problem doesn't exist is as important as knowing how to solve it. Jumping to "add Redis replicas for hot keys" without checking the numbers is over-engineering — it adds complexity without solving a real bottleneck.

---

## When would it become a problem?

If Pastebin scaled to 100× current traffic:

```
Peak read QPS:  300,000 reads/sec
Hot key (10%):   30,000 reads/sec
Redis capacity: 100,000 ops/sec
```

Now a hot key at 10% of peak is consuming 30% of Redis capacity. Still not broken, but worth watching. At 1,000× current traffic (30M reads/sec), hot keys become a genuine problem.

At that scale, the solutions are:

```
1. Redis read replicas — distribute reads across multiple Redis nodes
2. Local in-process cache on app servers — serve the hottest keys from 
   app server memory, zero network hop, unlimited throughput per server
```

But those are Google-scale problems. At Pastebin's current scale, the right answer is: **check the numbers, conclude no problem exists, move on.**

---

> [!tip] Interview framing
> "I considered the hot key problem — a viral paste could concentrate reads on one short code. Our peak read QPS is 3k. Even if 10% hits one key, that's 300 reads/sec against Redis's 100k ops/sec capacity — 0.3% utilisation. Hot keys are not a concern at this scale. If traffic grew 100×, I'd add Redis read replicas or local in-process caching on app servers. For now, the numbers don't justify the complexity."
