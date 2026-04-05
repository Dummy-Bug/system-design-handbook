# PACELC — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around PA/EL vs PC/EC decisions, latency-consistency trade-offs in normal operation, and database selection using PACELC framing. Expected at SDE-2 level.

---

## Q1 — Database Selection Using PACELC

> [!question] You're designing a global ride-hailing platform (like Uber). The driver location service needs to handle 500k location updates per second worldwide. Select a database and justify using PACELC framing.

> [!success]- Answer
>
> **Analysis — Partition behavior (PA or PC):**
> ```
> Driver location update:
>   Location is approximate — a driver's exact GPS coordinate isn't financially critical
>   Stale location (2 seconds old): acceptable — the map shows approximate position
>
>   During partition: serve stale location data → rider sees driver was there 2 seconds ago
>   Refusing location updates: map shows static driver → worse experience
>
>   → PA: stay available, accept potential staleness
> ```
>
> **Analysis — Normal operation (EL or EC):**
> ```
> 500k location updates per second, globally
>
>   EC (wait for replicas): each driver's location write waits for quorum confirmation
>   Quorum across global regions: ~100-200ms per write
>   500k writes × 100ms wait = system cannot keep up
>   Every driver's location update is seconds behind reality
>   → EC is operationally impossible at this volume and global distribution
>
>   EL (respond immediately): update written locally, replicate in background
>   Write latency: ~1ms
>   Location is eventually replicated to all regions in milliseconds
>   → Acceptable — driver location being 200ms stale is imperceptible
>
>   → EL: low latency writes, eventual replication
> ```
>
> **PACELC label: PA/EL**
>
> **Database choice:**
> ```
> Cassandra ✓
>   → PA/EL by default
>   → Designed for massive write throughput
>   → Horizontally scalable across global regions
>   → Consistent hashing → no hot spots
>   → Write to nearest node, async replication globally
>
> DynamoDB (Global Tables) ✓
>   → Also PA/EL
>   → Managed service, less operational overhead
> ```
>
> > [!tip] Interview framing
> > *"Driver location: PA/EL. During partition, 2-second stale location is acceptable — PA. 500k writes/sec globally: waiting for quorum is operationally impossible — EL. Cassandra is the natural fit: designed for PA/EL, scales horizontally, handles massive write throughput globally."*

---

## Q2 — EL vs EC: The Latency Impact

> [!question] Your team is debating whether to use EC or EL for a product inventory system. EC ensures inventory is always fresh. EL responds faster. Walk through the quantitative impact of each choice.

> [!success]- Answer
>
> **Setup:**
> ```
> Primary DB: US-East
> Replica: US-West (70ms away)
> Replication lag (async): ~100ms
>
> SLO: P99 API latency < 200ms
> Inventory read + application logic: ~30ms
> ```
>
> **EC — strongly consistent reads:**
> ```
> Quorum read: must confirm with majority of nodes before responding
> (Primary + at least one replica must agree)
>
> Latency breakdown:
>   DB query: 10ms
>   Wait for US-West quorum: 70ms round trip
>   Application processing: 20ms
>   Total: ~100ms
>
>   P99 impact: 100ms of the 200ms budget consumed by inventory read alone
>   Leaves 100ms for everything else (auth, other DB calls, response)
>   → Tight, but within SLO
> ```
>
> **EL — eventual consistency reads:**
> ```
> Read from nearest replica, no quorum wait
>
> Latency breakdown:
>   DB query (local replica): 5ms
>   Application processing: 20ms
>   Total: ~25ms
>
>   P99 impact: only 25ms for inventory read
>   Leaves 175ms for everything else → comfortable headroom
> ```
>
> **The staleness window:**
> ```
> EL: read may be up to ~100ms stale (replication lag)
>
>   Scenario: item goes out of stock → user reads EL → sees "in stock" → adds to cart
>   100ms later: replication caught up → system knows it's out of stock
>   At checkout: perform EC read for inventory decrement
>   Checkout fails: "sorry, item is out of stock" → user disappointed but no oversell
>
>   Two-tier approach:
>     EL for browse/search: fast, slightly stale, acceptable
>     EC at checkout: consistent, user already committed to buying
> ```
>
> **Recommendation:**
> ```
> EL for browse and search → 25ms reads, comfortable P99 headroom
> EC at checkout (inventory decrement) → correct, user expects to wait slightly
>
> Best of both: EL for 90% of reads, EC for the critical 10% (actual purchase)
> ```
>
> > [!tip] Interview framing
> > *"EC adds 70ms+ of quorum wait per read — expensive at 200ms P99 budget. EL costs 5ms. Two-tier: EL for browse (fast, slight staleness acceptable), EC at checkout (correct inventory decrement matters). Pay the consistency cost only when the user is actually purchasing."*

---

## Q3 — MongoDB's PA/EC Position

> [!question] Your colleague says "MongoDB is AP — it prioritizes availability." Another says "MongoDB is CP — it has strong consistency." Who's right?

> [!success]- Answer
>
> **Both are partially right, and both are missing nuance.**
>
> **MongoDB in PACELC is PA/EC:**
> ```
> PA: during partition, MongoDB stays available
>     Primary-less partition: secondary can serve reads (slightly stale)
>     Write operations may fail during partition (cannot reach primary)
>     → Prioritizes availability for reads, not writes, during partition
>
> EC: in normal operation, MongoDB uses strong consistency by default
>     Reads go to primary (always latest data)
>     Writes confirmed by primary before responding
>     → No stale reads during normal operation
> ```
>
> **The confusion comes from tunable consistency:**
> ```
> Read preference PRIMARY (default): EC behavior — always fresh
> Read preference SECONDARY: EL behavior — may be stale, faster
>
> Write concern MAJORITY: waits for majority → more durable
> Write concern 1 (default): responds after primary write → faster, less durable
>
> Depending on configuration: MongoDB can behave like PA/EL or PC/EC
> Default: somewhere in between → PA/EC
> ```
>
> **When MongoDB is right:**
> ```
> ✓ General-purpose applications with mixed consistency needs
> ✓ Systems that need some reads to be fresh, some to be fast
> ✓ Flexible schema with complex documents
>
> ✗ Wrong for: pure CP requirement (use Postgres/Spanner)
>              pure PA/EL requirement (use Cassandra for massive write throughput)
>
> MongoDB is the "comfortable middle ground" — not the best at either extreme
> ```
>
> > [!tip] Interview framing
> > *"MongoDB is PA/EC by default — available during partitions, strongly consistent normally. But it's tunable: secondary reads give EL behavior, majority write concern moves toward PC. It's a general-purpose middle ground. For clear PA/EL (Cassandra) or clear PC/EC (Postgres, Spanner) requirements, use the specialized tool."*

---

## Q4 — Designing for EL in a News Feed

> [!question] Your news feed uses EL consistency — writers respond immediately, read replicas are eventually consistent. A user posts and immediately clicks to their profile. Their post isn't there. How do you fix this?

> [!success]- Answer
>
> **Why it happens with pure EL:**
> ```
> User posts: write to primary → primary responds OK immediately (EL)
>             async replication to read replicas: ~100ms lag
>
> User clicks profile: read from nearest replica
>   Replica hasn't synced yet → post not visible
>   User sees: "My post disappeared" → hits post again → duplicate
> ```
>
> **The problem:** EL is correct for other users reading the feed. But for the author reading their own post, you need read-your-writes.
>
> **Fix 1 — Version token in session:**
> ```
> Write returns: { post_id: 123, write_version: 10042 }
> Store write_version in user's cookie/session
>
> Profile read: "I need data at version ≥ 10042"
> API server checks replica version:
>   If replica_version ≥ 10042 → serve from replica ✓
>   If replica_version < 10042 → serve from primary (or wait for replica)
>
> Only the author's reads are affected
> Everyone else: EL behavior unchanged
> ```
>
> **Fix 2 — Sticky routing for post author:**
> ```
> After a write: pin that user's requests to the primary (or the replica that confirmed)
>               for 2 seconds
>
> Author reads: hit primary → sees their post ✓
> 2 seconds later: replica has caught up → reads switch back to replica
>
> Simple, but adds primary load for 2 seconds after each post
> ```
>
> **Fix 3 — Local cache on client:**
> ```
> After successful post: optimistically add to local UI immediately
> Don't wait for server to confirm on next read
>
> Simpler, no backend changes needed
> Users see their post immediately (from local cache)
> Server eventually confirms → UI stays consistent
>
> Problem: if post was actually lost (network error) → shows post that doesn't exist
>          → error when user tries to interact with it
> ```
>
> **Best approach:** Fix 1 (version tokens) — precise, adds primary load only when needed.
>
> > [!tip] Interview framing
> > *"EL breaks read-your-writes — author can't see their own post before replica syncs. Fix with version tokens: write returns a version, profile reads check if replica has caught up to that version before serving. Only the author's reads are affected — everyone else stays on EL for feed performance."*

---

## Q5 — PACELC in a Multi-Datacenter Setup

> [!question] You're designing a global e-commerce platform with datacenters in US, EU, and APAC. Users write to their local datacenter. How do you label each data flow using PACELC?

> [!success]- Answer
>
> **Setup:**
> ```
> User in EU → writes to EU datacenter (primary for EU users)
> User in US → writes to US datacenter (primary for US users)
> Cross-region replication: EU ↔ US ↔ APAC (async)
> ```
>
> **Data flow 1: Product listings (PA/EL)**
> ```
> Partition behavior (PA):
>   Cross-region partition: EU serves product listings from local data
>   Slightly stale (US price update not yet propagated)
>   → Acceptable: product browsing should always be available → PA
>
> Normal operation (EL):
>   Product catalog changes: replicate to all regions asynchronously
>   EU user sees product update 200ms after US team published it → harmless
>   → EL: low latency writes, eventual global consistency
>
>   Label: PA/EL
> ```
>
> **Data flow 2: User orders (PC/EC)**
> ```
> Partition behavior (PC):
>   Order placed → must be confirmed durably before responding
>   Cross-region partition: refuse order if primary is unreachable
>   → Cannot place order on stale inventory → PC
>
> Normal operation (EC):
>   Order write: confirmed by EU primary + EU replica before responding
>   Replicated to US/APAC asynchronously (for reporting)
>   Reads of order history: served from local region → may be slightly stale for cross-user
>   But user reading their own order: read-your-writes enforced → EC for author
>   → EC: order data always consistent for the ordering user
>
>   Label: PC/EC
> ```
>
> **Data flow 3: Session/auth tokens (PA/EC)**
> ```
> Partition behavior (PA):
>   User already logged in → session token in EU
>   Partition: serve from EU cache → still logged in → don't log out user → PA
>
> Normal operation (EC):
>   New login: write to EU primary, replicate synchronously to EU replica
>   Cross-region (EU → US): async (login recognized globally within seconds)
>   Read of session: from EU primary (EC) → always fresh token validation
>   → EC: valid session always confirmed, not from stale replica
>
>   Label: PA/EC
> ```
>
> > [!tip] Interview framing
> > *"Label each data flow separately. Product listings: PA/EL — always available, EL replication fine. Orders: PC/EC — refuse on partition, always consistent. Sessions: PA/EC — stay logged in during partition (PA), validate against fresh session data in normal ops (EC). Same platform, three PACELC labels."*
