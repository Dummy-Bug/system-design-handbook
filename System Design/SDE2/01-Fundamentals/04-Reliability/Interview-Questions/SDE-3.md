# Reliability — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions testing reliability at scale — RPO/RTO under high throughput, quorum consensus, tiered replication strategies, and designing for disaster recovery. SDE-3 level — no single right answer, just structured thinking and clear justification.

---

> [!question] You're the lead engineer at a fintech company processing 100,000 transactions per second. The CTO says "RPO = 0, RTO = 30 seconds." Walk me through your architecture.

> [!success]- Answer
>
> **First reaction — stress test the requirements:**
> ```
> RTO = 30 seconds → no human can be in the loop, everything must be automated
> RPO = 0          → zero data loss, sync replication required
> 100k writes/sec  → cross-datacenter sync replication will destroy write latency
> ```
>
> ---
>
> **The naive answer and why it breaks:**
>
> Active-Active with sync replication across datacenters:
> ```
> 100,000 writes/sec × 50–100ms cross-datacenter sync round trip
> → 5,000–10,000 writes in-flight at any moment waiting for ACK
> → queue builds faster than it drains
> → timeouts cascade
> → system starts rejecting writes
> ```
> Speed of light makes cross-datacenter sync replication at this throughput essentially impossible.
>
> ---
>
> **The split-brain problem with active-active:**
>
> If both nodes accept writes simultaneously and a network partition occurs:
> ```
> Node A and Node B both think they're primary
> Both accept conflicting writes
> Partition heals → conflict: which write wins?
> Last-write-wins? Merge? → lossy, business-specific, often wrong
> ```
>
> Solved with quorum — **R + W > N:**
> ```
> N = 3 total nodes
>
> W=1, R=3 → write to 1, read from all 3
> W=2, R=2 → write to 2, read from 2  ← typical production choice
> W=3, R=1 → write to all 3, read from any 1
>
> R + W > N guarantees the read set and write set always overlap
> → at least one node in your read set has the latest write
> → consensus on correct data is always possible
> ```
>
> Standard production: **W=2, R=2, N=3** — balanced latency, tolerates 1 node failure.
>
> ---
>
> **The real answer — tiered replication:**
>
> You cannot avoid cross-region replication entirely — a same-datacenter fire takes out both primary and local replica. But you can be smart about which replication is sync and which is async:
>
> ```
> Same datacenter  → sync replication  → +1–2ms per write   → RPO = 0
> Cross-region     → async replication → +50–100ms, background → RPO = seconds
> ```
>
> This gives you the best of both worlds:
> - Local replica handles the 99% case (server dies, disk fails) → instant failover, zero data loss
> - Cross-region replica handles the 1% catastrophic case (entire DC fire) → seconds of data loss, business survives
>
> The business explicitly accepts: losing 2 seconds of transactions in a full datacenter disaster is acceptable. Losing data in a routine server failure is not.
>
> ---
>
> **Final architecture:**
>
> ```
> Region A (Primary)
> ├── Primary DB
> │     ↓ sync replication (+1–2ms)
> └── Local Replica (same DC)
>       ↓ async replication (+50–100ms, background)
>
> Region B (Disaster Recovery)
> └── Cross-region Replica
> ```
>
> **Failure behaviour:**
>
> ```
> Routine failure — Primary DB dies:
> → Local replica promotes automatically
> → Automated health check detects failure in <10 seconds
> → Automated failover promotes local replica, reroutes DNS/LB
> → RTO = 30 seconds ✓, RPO = 0 ✓
> → Cross-region replica unaffected, keeps syncing
>
> Catastrophic failure — entire Region A datacenter fire:
> → Cross-region replica in Region B promoted
> → Some manual steps involved (or pre-configured automated failover)
> → RTO = minutes
> → RPO = seconds (async lag window)
> → Business survives, minor data loss explicitly accepted
> ```
>
> **Components:**
> ```
> Primary DB              → handles all writes
> Local sync replica      → RPO = 0 guarantee, 30-second failover
> Cross-region async replica → disaster recovery only
> Automated health check  → detects primary failure in <10 seconds
> Automated failover      → promotes local replica, no human in the loop
> DNS / load balancer     → reroutes traffic to new primary automatically
> ```
>
> > [!important] RPO = 0 is achievable — but only when your replica is physically nearby. The moment you go cross-region for sync replication, you're fighting the speed of light at 100k writes/sec and you will lose. Tiered replication — sync locally, async cross-region — is the standard production answer for fintech at scale.
>
> > [!tip] Interview framing
> > *"RPO = 0 with RTO = 30 seconds at 100k writes/sec can't be solved with cross-datacenter sync replication — the latency makes it impossible. The answer is tiered replication: sync to a local replica in the same DC for RPO = 0 and 30-second automated failover, async to a cross-region replica for disaster recovery where we accept a few seconds of data loss in a full DC failure. The business has to explicitly sign off on that trade-off."*
