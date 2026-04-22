
> [!info] Your SLO doesn't just define a target — it defines how much failure you're allowed
> 99.99% availability sounds like "almost never fail." What it actually means is: you have a budget of 0.01% failures. How you spend that budget determines how aggressively you can evolve the system.

---

## What the budget actually is

Our SLO says 99.99% availability. That means 0.01% of requests are allowed to fail.

At 330K requests/second (300K reads + 30K writes), here's what 0.01% looks like:

```
Per second:   330,000 × 0.0001 = 33 failed requests allowed
Per minute:   33 × 60           = 1,980 failed requests allowed
Per hour:     1,980 × 60        = 118,800 failed requests allowed
Per day:      118,800 × 24      = 2,851,200 failed requests allowed
Per month:    2,851,200 × 30    = 85,536,000 failed requests allowed

In time:      0.01% of 525,600 minutes/year = 52.56 minutes of total downtime
```

52 minutes and 34 seconds per year. That is the entire error budget for availability.

Every 503 quorum failure, every 500 error, every timeout, every rate-limited request — it all eats into those 52 minutes. Once the budget is gone, any further failures breach the SLO.

---

## What consumes error budget in a KV store

Unlike a simple web app where failures are mostly "server crashed," our KV store has many different failure modes, each consuming budget differently:

```
Failure mode                    Budget impact at our scale
────────────                    ──────────────────────────
Single node failure             Minimal — quorum still met, hinted handoff covers it
                                Maybe 0-10 failed requests during detection window

Rack failure (10 nodes)         Moderate — some key ranges temporarily lose quorum
                                ~1,000 failed requests over 30 seconds until
                                gossip detects and reroutes

Network partition (5 minutes)   Significant — SC reads fail for affected key ranges
                                ~50,000 failed SC reads over 5 minutes

Bad deploy (1 hour)             Major — elevated 500 errors across the cluster
                                ~500,000 failed requests over 1 hour

Compaction storm (all nodes)    Indirect — latency SLO breached, not availability
                                Burns latency error budget, not availability budget
```

A single node failure barely dents the budget. A 5-minute network partition eats ~0.06% of monthly budget. A bad deploy that runs for an hour could consume 0.6% — noticeable but recoverable. The real danger is **multiple incidents in the same month** compounding.

---

## Error budget for latency SLOs

Error budget applies to latency SLOs too, not just availability.

Our p99 < 10ms SLO for EC reads means: 99% of requests must complete under 10ms. The remaining 1% is the latency error budget — those requests are allowed to be slow.

At 250K EC reads/second (assuming 250K of 300K reads are eventual):

```
1% of 250,000 = 2,500 EC reads per second allowed to exceed 10ms
```

If 5,000 EC reads per second are exceeding 10ms, you're burning latency budget at 2× the allowed rate. Common causes:

```
Latency budget consumers:
  → Compaction running → disk I/O contention → SSTable reads slower
  → Cold page cache after node restart → every read hits physical disk
  → Bloom filter false positives → wasted SSTable lookups
  → SSTable accumulation (compaction falling behind) → more files to check
  → Read repair overhead → extra background writes after stale reads
```

---

## How error budget changes engineering behaviour

Without error budget thinking, questions like "should we deploy this risky migration?" or "can we run anti-entropy more aggressively?" are subjective arguments. Error budget makes them concrete:

```
Error budget remaining this month: 80%  → plenty of runway
  → Safe to deploy the new compaction strategy
  → Can run experimental Bloom filter sizing
  → Can schedule maintenance (anti-entropy full rebuild on degraded nodes)
  → Can try aggressive compaction tuning

Error budget remaining: 20%  → getting tight
  → Slow down risky changes
  → No experimental deploys
  → Review what consumed 80% — was it a single incident or steady bleed?
  → Focus on reliability improvements

Error budget remaining: 0%  → SLO already breached this period
  → Freeze all feature work and risky changes
  → Every engineering hour goes to reliability
  → No deploys unless they fix the reliability issue
  → Post-mortem on what consumed the budget
```

The budget creates alignment between the team maintaining the KV store and the teams depending on it. It's not "the infra team is being too cautious" vs "the product team wants to move fast." It's: here is the number. The number decides.

---

## Error budget and deployments in a 1,200-node cluster

Deploying changes to 1,200 nodes is inherently risky. A bad binary rolled out to all nodes simultaneously would breach SLO immediately. This is why KV store deployments are done as **rolling deploys** — update a few nodes at a time, monitor SLIs, proceed if healthy.

```
Rolling deploy strategy:
  Phase 1: Deploy to 10 nodes (canary) → monitor SLIs for 10 minutes
  Phase 2: Deploy to 100 nodes         → monitor SLIs for 10 minutes
  Phase 3: Deploy to remaining 1,090   → monitor SLIs continuously

If SLI degrades at any phase → automatic rollback
```

The error budget guides how aggressive the rollout can be:

```
Budget > 50%:   deploy canary to 10 nodes, wait 5 minutes, then full rollout
Budget 20-50%:  deploy canary to 10 nodes, wait 30 minutes, then slow rollout
Budget < 20%:   deploy only critical fixes, manual approval required
Budget = 0%:    no deploys unless they directly fix the reliability issue
```

---

## Error budget across consistency levels

An interesting nuance: the error budget applies to the overall 99.99% availability SLO, but SC reads and EC reads consume budget differently:

```
EC reads (R=1):  rarely fail — any single replica being alive is enough
                 consume almost no error budget

SC reads (R=2):  fail when quorum can't be met — more fragile
                 consume most of the error budget

Writes (W=2):    fail when quorum can't be met — similar to SC reads
                 second largest consumer
```

If you're burning through error budget fast, one strategy is to encourage more services to use eventual consistency where possible. Every SC read that could be an EC read is saving error budget — because EC reads survive partial failures that SC reads can't.

---

> [!tip] Interview framing
> "99.99% availability means 0.01% failure budget — at 330K req/sec that's 52 minutes of total downtime per year, or about 33 failed requests per second allowed. Every 503, 500, and timeout eats into that budget. Error budget makes reliability decisions concrete: when budget is full, we deploy aggressively with rolling updates. When budget is low, we freeze risky changes and focus on reliability. It also guides architectural decisions — if SC reads are burning budget during partitions, we encourage services to use EC reads where possible. Same concept applies to latency: 1% of EC reads are allowed to exceed 10ms, and we track how fast that 1% is being consumed."
