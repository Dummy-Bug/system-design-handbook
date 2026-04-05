# Network Partitions — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around partition handling, quorum design, split-brain recovery, and serve vs refuse decisions for specific systems. Expected at SDE-2 level.

---

## Q1 — Designing for Partition in a Booking System

> [!question] You're designing a seat reservation system for concerts (like Ticketmaster). A network partition splits your database cluster. Walk me through your decision on how to handle it and why.

> [!success]- Answer
>
> **What the system does:**
> Sells seats for concerts — each seat can only be sold once. Users buy specific seats (Row A, Seat 12).
>
> **During partition — the decision:**
> ```
> Serve stale data → potential double-sell
>   User A: reads Seat A12 as available → books it
>   User B: reads Seat A12 as available (stale data) → books it
>   Partition heals: two confirmed bookings for one seat ✗
>   One user gets a cancellation email → broken trust, refund, angry customer
>
> Refuse requests → temporary unavailability
>   Users see "booking temporarily unavailable, please try again in a few minutes"
>   Both users retry when partition resolves → one gets the seat → fair ✓
> ```
>
> **Decision: refuse requests (CP behavior)**
>
> **The key reasoning:**
> ```
> Cost of double-sell:
>   Financial refund to one user
>   Operational cost of handling complaint
>   Reputation damage
>   In worst case: user bought flight/hotel based on confirmed ticket
>
> Cost of temporary unavailability:
>   User waits a few minutes
>   Retries successfully
>   Gets the ticket
>
> Unavailability is recoverable → wrong data is not → refuse
> ```
>
> **How to signal this to users:**
> ```
> HTTP 503 with Retry-After header:
>   "Service temporarily unavailable. Please try again in 2 minutes."
>
> In-app: "We're experiencing high demand. Your seat is being held. Please wait..."
>         (Actually, don't hold the seat during partition — that's a soft hold
>          that also needs the DB, which is exactly what's failing)
>
> Honest: "Temporary technical issue. Seats are available once service recovers."
> ```
>
> > [!tip] Interview framing
> > *"Concert seats: double-sell is catastrophic — user bought travel based on confirmed booking, then gets cancellation. Refuse during partition (CP). Serve 503 with Retry-After. Unavailability is recoverable — double-sell may not be. The cost asymmetry drives the decision."*

---

## Q2 — Quorum Configuration

> [!question] You have a 5-node database cluster. A single node goes down. A network partition splits the cluster 3-2. What happens with quorum = 3? What if you set quorum = 2?

> [!success]- Answer
>
> **Single node failure:**
> ```
> 5 nodes running → quorum = 3
> Node 5 fails
>
> Remaining: 4 nodes
> Quorum still achievable: 4 ≥ 3 ✓
> Cluster continues serving ✓
> ```
>
> **3-2 partition with quorum = 3:**
> ```
> Group A (3 nodes): has quorum (3 ≥ 3)
>   → stays primary, continues writes ✓
>
> Group B (2 nodes): no quorum (2 < 3)
>   → steps down, refuses writes ✓
>   → no split-brain ✓
>
> System available to 3-node group's clients
> 2-node group's clients: see errors
> ```
>
> **3-2 partition with quorum = 2:**
> ```
> Group A (3 nodes): has quorum (3 ≥ 2) → thinks it's primary
> Group B (2 nodes): has quorum (2 ≥ 2) → ALSO thinks it's primary
>
> Both groups accept writes → split-brain ✗
> Partition heals → conflicting data → unresolvable ✗
>
> Quorum = 2 on a 5-node cluster defeats the purpose of quorum
> ```
>
> **The formula:**
> ```
> Quorum = floor(N/2) + 1
> N=5: quorum = floor(5/2) + 1 = 2 + 1 = 3 ✓
>
> This guarantees: only one group can have quorum during any partition
> Two groups can't both have majority of a 5-node cluster simultaneously
> ```
>
> > [!tip] Interview framing
> > *"Quorum formula: floor(N/2) + 1. For 5 nodes: quorum = 3. A 3-2 partition: Group of 3 has quorum, continues. Group of 2 steps down. Setting quorum = 2 allows both groups to claim quorum — split-brain. Quorum must be a strict majority to guarantee only one group can lead."*

---

## Q3 — Split-Brain Recovery

> [!question] A split-brain occurred in your database before quorum was enforced. Both nodes accepted writes during the partition. Now the partition is healed. How do you recover?

> [!success]- Answer
>
> **The state after split-brain:**
> ```
> Node A (was primary): order_1 = {status: CONFIRMED, updated_at: 14:01:00}
> Node B (split brain):  order_1 = {status: CANCELLED, updated_at: 14:00:45}
>
> Both writes were committed locally
> Now they must be reconciled
> ```
>
> **Step 1 — Identify conflicting writes:**
> ```
> Compare WAL logs from both nodes
> Find entries that diverged after partition start time
> Identify which records have conflicting versions
> ```
>
> **Step 2 — Pick a resolution strategy:**
>
> **Last-write-wins (by timestamp):**
> ```
> Compare updated_at timestamps
> Node A: 14:01:00 > Node B: 14:00:45 → Node A's version wins
>
> Problems:
>   Clock skew: Node B's clock may be 2 seconds fast → B's 14:00:47 = "later" than A's 14:01:00 in real time
>   Causality lost: the "later" write may be based on stale data
>
>   For many business cases: acceptable as a pragmatic choice
>   For financial data: dangerous
> ```
>
> **Application-level merge:**
> ```
> For some data types: both writes can be merged
>
>   Shopping cart:
>     A: [item1, item3], B: [item1, item2]
>     Merge: [item1, item2, item3] → union of both
>
>   Counter (views, likes):
>     A: count = 50, B: count = 48
>     Merge: max(50, 48) = 50, then reconcile delta
> ```
>
> **Human review for critical data:**
> ```
> Orders, payments, bookings → no automated resolution
>   → Flag both versions for manual review
>   → Customer service contacts affected users
>   → Refund or honor whichever is appropriate
>
> This is why preventing split-brain matters more than recovering from it
> ```
>
> > [!tip] Interview framing
> > *"Split-brain recovery: identify diverging writes, then choose strategy. Last-write-wins by timestamp works for non-critical data but has clock skew risks. Application-level merge works for CRDTs (carts, counters). Financial/booking data needs human review — automated resolution risks financial errors. Prevention (quorum) is always better than recovery."*

---

## Q4 — Geo-Distributed Cluster Partitions

> [!question] Your database cluster has nodes in US-East and US-West. A transatlantic network issue prevents them from communicating for 3 minutes. Both serve traffic. What's the damage and how do you design to minimize it?

> [!success]- Answer
>
> **What happens during 3 minutes of partition:**
> ```
> Both US-East and US-West accept writes
> (If quorum = 1 or region-local, both believe they're primary)
>
> US-East:
>   User A updates profile: name = "Alice Smith"
>   User B places order: order_123
>
> US-West:
>   User A updates profile: name = "Alice Johnson" (simultaneous edit)
>   Order_123's inventory decremented (didn't know about US-East's order)
>
> 3 minutes later: partition heals
>   "Alice Smith" vs "Alice Johnson" → conflict
>   Inventory count is inconsistent across regions
> ```
>
> **Design to minimize damage:**
>
> **Option 1: Single-region active, other read-only (Active-Passive):**
> ```
> US-East = primary (writes go here)
> US-West = read-only replica
>
> Partition occurs:
>   US-West refuses writes → no conflicting data ✓
>   US-West serves reads from local replica (slightly stale) → acceptable
>   Write users routed to US-East (may have latency impact from US-West users)
> ```
>
> **Option 2: Active-Active with conflict-tolerant data structures:**
> ```
> Accept that conflicts happen, minimize their impact
>
>   Inventory: never decrement below 0 (each region has its own allotment)
>   User writes: last-write-wins by timestamp (acceptable for non-critical profile data)
>   Financial data: only one region owns it, route all financial writes to that region
>
> Partition damage: limited to non-critical data that can be auto-resolved
> ```
>
> **Option 3: Region-based ownership:**
> ```
> US users' data → US-East owns it (canonical home)
> EU users' data → EU-West owns it
>
> US user writes: always go to US-East regardless of CDN routing
> US user reads: can be served from any region
>
> Partition: US-West can't accept US user writes → serves read from cache → acceptable
> ```
>
> > [!tip] Interview framing
> > *"3 minutes of split-brain creates conflicting writes. Minimize with: Active-Passive (West refuses writes), regional ownership (each user's writes have a home region), or accept conflicts in non-critical data only. Financial and inventory data must have a single authoritative region — never split-brain these."*

---

## Q5 — Detecting Partitions

> [!question] Your monitoring shows "Node B is unreachable from Node A." Is Node B down or is there a network partition? How do you detect which it is, and does your response differ?

> [!success]- Answer
>
> **Why the distinction is hard:**
> ```
> From Node A's perspective: Node B sends no heartbeat response
>
> Possible explanations:
>   1. Node B crashed (process died, OOM kill, kernel panic)
>   2. Network partition (Node B alive, link between A and B broken)
>   3. Node B overloaded and GC-paused (briefly unresponsive)
>   4. A specific link failed (B reachable from C but not from A)
>
> Node A CANNOT tell which scenario — it only knows "B didn't respond"
> ```
>
> **Detection techniques:**
>
> **Ask a third party:**
> ```
> Node A cannot reach Node B
> Node A asks Node C: "Can you reach Node B?"
>
> C says yes → likely partition between A and B (B is alive)
> C says no  → likely Node B crashed
>
> 3-node cluster: minority node asking majority for perspective
> ```
>
> **Multiple health check points:**
> ```
> Node A to Node B: timeout ← unreachable
> AWS health check to Node B: responding ← Node B is alive
>
> Conclusion: network partition, not crash
> ```
>
> **Does the response differ?**
> ```
> Node B crashed:
>   → Failover: promote a replica to replace B
>   → More urgent: B is truly gone, cluster is degraded permanently until replaced
>   → Might need to add a new node for redundancy
>
> Network partition:
>   → Wait: B will likely reconnect when network is restored
>   → Do NOT immediately replace B — once partition heals, you'd have two nodes
>      trying to be the same node (data conflict)
>   → Let quorum handle it: B steps down while isolated, resumes when reconnected
>   → Only failover if partition lasts beyond a threshold (e.g. 5 minutes)
> ```
>
> > [!tip] Interview framing
> > *"Crashed vs partition: ask a third node or use external health checks to check if B is alive from another vantage point. Response differs: crash → failover immediately. Partition → wait (with timeout), quorum protects consistency, B resumes on reconnect. Premature failover during a partition creates two nodes trying to be primary."*
