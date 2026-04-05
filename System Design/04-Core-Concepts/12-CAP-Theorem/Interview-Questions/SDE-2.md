# CAP Theorem — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around CP vs AP decisions, tunable consistency, database selection, and real-world system behavior during partitions. Expected at SDE-2 level.

---

## Q1 — CP or AP for Distributed Cache

> [!question] You're adding a distributed cache (Redis Cluster) to your e-commerce platform. During a partition, some cache nodes become unreachable. Should the cache behave CP or AP?

> [!success]- Answer
>
> **What the cache stores:**
> ```
> Product listings        → cached for fast browse
> Search results          → cached to reduce search DB load
> User session data       → cached for authentication
> Cart data               → maybe cached for fast reads
> Inventory counts        → maybe cached (dangerous)
> ```
>
> **The fundamental question: what's the cost of serving stale data?**
>
> **For product listings and search → AP:**
> ```
> Cache partition: some nodes unreachable
>
> AP behavior: serve from reachable nodes (may be stale)
>   User sees products at prices from 30 seconds ago → harmless
>   User sees search results from 30 seconds ago → harmless
>
> CP behavior: refuse cache reads during partition → hit DB directly
>   DB suddenly gets all traffic → overloaded → latency spikes
>   Worse outcome than serving slightly stale cache data
>
> → For product/search cache: AP ✓
> ```
>
> **For session data → AP with care:**
> ```
> Session cache miss: user appears logged out → must re-authenticate
> Sessions can be reloaded from DB if cache misses
> Stale session: usually fine — token expiry handles actual security
>
> → Session cache: AP ✓ (miss gracefully, fall through to DB)
> ```
>
> **For inventory counts → NEVER cache without strong consistency:**
> ```
> Stale inventory: user sees "3 in stock" → item was sold out → oversell
>
> Either: don't cache inventory counts (read from DB)
>         or: cache with very short TTL (5 seconds) + accept small window of oversell risk
>
> → Inventory: skip cache OR very short TTL with oversell protection downstream
> ```
>
> > [!tip] Interview framing
> > *"Cache AP by default — cache miss falls through to DB, stale data beats cache unavailability for most data types. Exception: inventory counts should not be cached, or cached with very short TTL and validated on purchase. Serving stale inventory → oversell → serious business problem."*

---

## Q2 — Same Database, Different Behavior

> [!question] Your colleague uses Cassandra with consistency level ONE for social features and consistency level QUORUM for a payment feature — in the same service. Is this correct? Explain.

> [!success]- Answer
>
> **Yes — this is the correct approach. Tunable consistency per operation.**
>
> **Cassandra's consistency levels:**
> ```
> ONE:     Write/read confirmed by 1 node → responds immediately
>          Fast, low latency
>          Data may be stale (replicas not yet synced)
>          → AP behavior
>
> QUORUM:  Write/read confirmed by majority (e.g., 2 of 3 nodes)
>          Slower (waits for majority)
>          Guarantees: R + W > N → always reads latest write
>          → CP behavior
>
> ALL:     All nodes must confirm
>          Slowest, strongest consistency
>          Any unreachable node = failure
>          → CP with strictest availability cost
> ```
>
> **Why this is the right design:**
> ```
> Social feed post (consistency ONE):
>   Write to 1 node → responds immediately
>   Other nodes sync in background
>   Latency: ~1ms
>   Stale feed: harmless ✓
>
> Payment record (consistency QUORUM):
>   Write confirmed by 2/3 nodes before responding
>   Latency: ~20-50ms (wait for network round trip to second node)
>   No stale read possible (R + W > N)
>   Slightly stale payment record: dangerous ✗ → justify the latency
> ```
>
> **The per-operation pattern:**
> ```
> session.execute(
>     "INSERT INTO feed_posts ...",
>     consistency_level=ConsistencyLevel.ONE  # fast, AP
> )
>
> session.execute(
>     "INSERT INTO payment_records ...",
>     consistency_level=ConsistencyLevel.QUORUM  # safe, CP
> )
> ```
>
> **This is exactly why Cassandra is powerful:**
> One database, tuned to the exact consistency requirement of each operation.
>
> > [!tip] Interview framing
> > *"Tunable consistency is correct and intentional. ONE for social features: fast, eventual, AP behavior. QUORUM for payments: slower, guaranteed fresh, CP behavior. Same Cassandra cluster, per-operation decision. This is better than two separate databases — simpler infrastructure, appropriate guarantees per use case."*

---

## Q3 — When CP Causes Availability Problems

> [!question] Your CP database is unavailable for 90 seconds during a partition. Your SLO is 99.9% (43 min/month). How much of your error budget does this burn and what are the implications?

> [!success]- Answer
>
> **The budget calculation:**
> ```
> Monthly error budget at 99.9% SLO:
>   30 days × 24h × 60min = 43,200 minutes
>   0.1% × 43,200 = 43 minutes = 2,580 seconds
>
> Incident burned: 90 seconds
>
> Remaining budget: 2,580 - 90 = 2,490 seconds (~41.5 minutes)
>
> That's 3.5% of monthly budget consumed in one 90-second CP incident
> ```
>
> **The implication — this is a real cost of CP:**
> ```
> Choosing CP means: during partitions, you accept unavailability
>
> If partitions happen:
>   Once/month: 90s → 3.5% budget → manageable
>   Once/week: 360s → 14% budget → concerning
>   Daily: 2,520s → 98% of budget → SLO constantly at risk
>
> CP is only viable if partitions are rare
> ```
>
> **What drives partition frequency:**
> ```
> Same cloud AZ: partitions rare (< once/year for most deployments)
>   → CP is viable
>
> Cross-region: partitions happen more frequently (cloud provider issues, BGP)
>   → Each CP unavailability is costly
>   → May push to AP for cross-region, CP only within-region
> ```
>
> **The design implication:**
> ```
> For cross-region CP systems:
>   Accept that SLO must be lower (e.g. 99.5% not 99.9%) to account for partition-induced unavailability
>   Or: sync within region (CP), async across regions (AP) for disaster recovery only
>   Or: pay for extremely reliable network infrastructure
> ```
>
> > [!tip] Interview framing
> > *"90 seconds at 99.9% SLO = 3.5% of monthly budget. CP's availability cost is real and budget-denominated. For within-region deployments, partitions are rare — CP is viable. For cross-region CP, partitions are more frequent — each one burns budget. Design cross-region as async (AP) for reads, synchronous (CP) only for critical writes within the primary region."*

---

## Q4 — Leader Election: Why CP

> [!question] You're building a distributed job scheduler. Only one server should run a given job at a time. Should the leader election mechanism be CP or AP? Why?

> [!success]- Answer
>
> **What happens with AP leader election:**
> ```
> 3 servers, quorum-free leader election
>
> Network partition: Server A ✗ Server B, Server C
>
> Server A thinks: "B and C are unreachable — I must still be leader"
>   → continues running jobs
>
> Servers B and C think: "A is unreachable — we should elect a new leader"
>   Server B wins election → becomes leader
>   → also runs the same jobs
>
> Two leaders → both run the same jobs simultaneously:
>   Duplicate email sends → users receive same email twice
>   Duplicate DB writes → data corruption
>   Duplicate payment processing → double charges
> ```
>
> **Why CP is required:**
> ```
> CP: a server only claims leadership if it can reach a majority
>
> Server A (partitioned alone):
>   "I can only reach 1 node (myself) — I don't have quorum"
>   → steps down, refuses to run jobs
>
> Servers B and C:
>   "We have quorum (2/3)"
>   → B elected leader → runs jobs safely
>
> Only one leader at a time → no duplicate execution ✓
> ```
>
> **Tools to use:**
> ```
> Zookeeper:  CP, designed for coordination, leader election primitive
> etcd:       CP, Raft consensus, used by Kubernetes for exactly this
> Redis with SET NX + TTL: approximate CP (TTL provides lock expiry)
>
> NOT Cassandra: AP, not designed for coordination use cases
> ```
>
> **The broader principle:**
> ```
> Any "exactly-once" guarantee requires CP
>   Leader election: exactly one leader
>   Distributed locks: exactly one holder
>   Unique ID generation: exactly one issuer of each ID
>
>   All require CP — stale "I'm still the leader" belief is catastrophic
> ```
>
> > [!tip] Interview framing
> > *"Leader election must be CP — with AP, a partitioned node stays leader, creating two simultaneous leaders and duplicate job execution. CP (quorum): only one group can have majority → only one can claim leadership → no duplicates. Use Zookeeper or etcd — both are CP systems designed for coordination."*

---

## Q5 — Multi-Service CP vs AP Decisions

> [!question] You're designing Twitter's architecture. The tweet posting service, timeline delivery service, and ad impression tracking service all have different consistency needs. Assign CP or AP and justify each.

> [!success]- Answer
>
> **Tweet posting service — CP:**
> ```
> Why: a tweet is durable user content
>   User posts tweet → "Your tweet was posted" confirmation
>   If AP: confirmation returned but tweet lost on node failure
>   User would see "I confirmed posting but it's gone" → serious UX bug
>
>   Also: tweet IDs must be globally unique
>          duplicate tweet creation → content duplication
>
> CP choice: write confirmed by quorum → durable, unique ✓
> DB: PostgreSQL or Spanner for tweet metadata
>     Might be eventually consistent for delivery (separate concern)
> ```
>
> **Timeline delivery service — AP:**
> ```
> Why: showing slightly stale feed is harmless
>   User sees tweets from 30 seconds ago → acceptable
>   Feed unavailability is unacceptable — Twitter is a real-time product
>
>   During partition: serve stale timeline
>   Do not refuse to show feed → users would see blank timeline
>
> AP choice: serve from nearest available replica, even if stale ✓
> DB: Cassandra — designed for AP, read from any replica
>     Fan-out cached timelines: serve from Redis even if origin is partitioned
> ```
>
> **Ad impression tracking — AP:**
> ```
> Why: losing 0.1% of ad impression events is acceptable
>   Revenue impact: tiny
>   User experience impact: none
>
>   During partition: drop events if necessary
>   Do not block ad serving to ensure 100% impression capture
>
> AP choice: best-effort event capture
>            Kafka with at-least-once delivery (small duplicates acceptable)
>            Deduplicate in batch processing → eventual accuracy
>
> Alternative frame: durability tradeoff, not consistency
>   Events are write-only — no reads needed for real-time serving
> ```
>
> **Summary:**
> ```
> Tweet posting: CP — durability of user content is non-negotiable
> Timeline:      AP — availability > freshness, stale feed is acceptable
> Ad tracking:   AP — eventual accuracy is fine, real-time completeness isn't critical
> ```
>
> > [!tip] Interview framing
> > *"Same platform, three different CP/AP decisions based on failure cost. Posting: CP — user confirmed but tweet lost is a serious bug. Timeline: AP — stale feed beats blank feed. Ad impressions: AP — small data loss acceptable, don't block serving. Assign CP/AP per feature, not per platform."*
