# NFRs — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around NFR conflicts, NFR-driven architecture decisions, and per-feature NFR assignment. Expected at SDE-2 level.

---

## Q1 — NFR Conflict: Consistency vs Availability

> [!question] You're designing a hotel booking system. The PM wants 99.99% availability. The legal team says booking data must always be strongly consistent. Walk me through the conflict and your resolution.

> [!success]- Answer
>
> **The conflict:**
> ```
> Availability NFR: 99.99% → 4.3 minutes/month downtime allowed
>                            system must serve requests even during failures
>
> Consistency NFR: strong consistency → every read sees latest write
>                  during partition: quorum required → may refuse requests
>
> CAP theorem: during a network partition, you can only have one
>   Strong consistency → may refuse requests → availability at risk
>   Always available  → may serve stale data → consistency at risk
> ```
>
> **The resolution — not either/or, but where:**
> ```
> The key insight: strong consistency is required for the BOOKING TRANSACTION
>                  not necessarily for every page load
>
> Check availability page:
>   "Are rooms available for these dates?"
>   → Eventual consistency acceptable: being wrong by 2 seconds won't cause double booking
>   → AP behavior: always show results, may be slightly stale
>   → 99.99% availability maintained ✓
>
> Booking transaction:
>   "Reserve this room" → must not double-book
>   → Strong consistency required → CP behavior
>   → If quorum unavailable: refuse the booking (return 503)
>   → Acceptable: user tries again in 30 seconds → availability still 99.99% if partitions rare
> ```
>
> **The availability math:**
> ```
> Network partitions in same-AZ: rare (~minutes/year)
> 99.99% budget: 4.3 min/month
>
> If partitions cause <4.3 min/month of booking failures:
>   Both NFRs satisfied simultaneously ✓
>   Partitions are rare enough → availability SLO met
>
> Cross-region deployment changes the math:
>   More frequent partitions → CP costs more availability
>   May need to accept 99.9% SLO for cross-region CP booking
> ```
>
> > [!tip] Interview framing
> > *"The conflict is real but manageable. Apply consistency selectively: search/browse → AP (always available, stale results harmless). Booking transaction → CP (refuse on partition, risk double-booking is worse than brief unavailability). If partitions are rare, 99.99% availability and strong booking consistency can coexist."*

---

## Q2 — Per-Feature NFR Assignment

> [!question] A food delivery platform has four features: restaurant menu, live driver tracking, order history, and checkout. Assign latency and consistency NFRs to each and justify.

> [!success]- Answer
>
> **Restaurant menu:**
> ```
> Latency:     P99 < 200ms (user expects fast page load)
> Consistency: Eventual (30-second staleness acceptable)
>
> Why:
>   Menu changes rarely (daily at most)
>   2-second stale menu: user sees yesterday's special → harmless
>   Cache aggressively: Redis cache, 60-second TTL
>   CDN for menu images
>
>   If price changed 10 seconds ago and user doesn't see it: acceptable
>   Show error because cache is down: not acceptable → availability > freshness
> ```
>
> **Live driver tracking:**
> ```
> Latency:     P99 < 500ms (1-second updates to map feel real-time)
> Consistency: Eventual, but fresh (< 5 second staleness)
>
> Why:
>   Location data generated every 2 seconds
>   User expects near-real-time map movement
>   "Strong consistency" for location: quorum on every GPS update → latency unacceptable
>   Eventual with very short TTL: 2-3 second lag → imperceptible to user
>
>   Use: Redis Sorted Set per order, driver writes location, user reads
>        Short TTL + async push via WebSocket
> ```
>
> **Order history:**
> ```
> Latency:     P99 < 1000ms (background page, not critical path)
> Consistency: Read-Your-Writes + Eventual for others
>
> Why:
>   User must see their own just-placed order immediately
>   Other users' orders: don't care about them at all
>   Historical data: last month's orders don't change → can be cached heavily
>
>   Use: read-your-writes guarantee for own orders
>        strong cache for historical orders (24-hour TTL)
> ```
>
> **Checkout:**
> ```
> Latency:     P99 < 500ms (user is at payment step — must feel fast)
> Consistency: Strong for inventory and payment
>
> Why:
>   Inventory: must verify item is available before charging
>              stale → charge user → then "sorry, restaurant closed" → terrible UX
>   Payment:   must not double-charge → idempotency + strong consistency
>
>   No cache for inventory at checkout: read from DB primary
>   Payment: synchronous processing, quorum write
>   500ms budget: tight but achievable with DB optimization
> ```
>
> > [!tip] Interview framing
> > *"Assign NFRs feature by feature. Menu: fast + stale-ok → cache heavily. Driver: fast + somewhat fresh → Redis with short TTL. Order history: slower ok + read-your-writes. Checkout: fast + strongly consistent → no cache on inventory, quorum on payment. Different NFRs = different architectures per feature."*

---

## Q3 — Durability vs Latency: Messaging

> [!question] A messaging app must guarantee messages are never lost (durability NFR) AND deliver them in under 200ms (latency NFR). These conflict. How do you resolve it?

> [!success]- Answer
>
> **The conflict:**
> ```
> Durability: write confirmed to disk + replicated before acknowledging
>             Synchronous replication to 2 replicas: +30-70ms write latency
>             WAL fsync: +5-10ms per write
>
> Total durable write: 40-80ms for the message write alone
> Plus: auth, routing, delivery: another 50-100ms
> Total: 90-180ms → tight but feasible for P99 200ms
>
> Harder case: cross-region durability
>   Sync replication to EU from US: +75ms
>   Total: 175ms → barely within budget at P50, blown at P99
> ```
>
> **Resolution — decouple acknowledgment from durability:**
>
> ```
> Approach 1: Acknowledge fast, guarantee durability async (fire-and-forget with guarantee)
>
>   Client sends message
>   Server:
>     1. Write to WAL on primary (5ms)
>     2. Push to delivery queue immediately (for fast delivery)
>     3. Acknowledge to sender: "message sent" ← respond here (< 10ms)
>     4. Replicate to secondary (async, 30ms)
>     5. Confirm delivery to recipient
>
>   User experience: message appears to send instantly
>   Durability: WAL write before step 3 = message is durable
>               even before secondary replication completes
>
>   If primary fails between step 1 and 4:
>     WAL recovers the message on restart
>     OR: new primary replays from WAL
>     Message not lost, delivery may be delayed
> ```
>
> **Approach 2 — Separate durability from freshness:**
> ```
> Persist to DB asynchronously with guaranteed delivery queue
>
>   Redis Streams or Kafka as buffer:
>     Write message to Kafka (< 5ms, Kafka is fast durable append)
>     Acknowledge to sender immediately
>     Consumer writes to DB for permanent storage (async)
>
>   Kafka: replication factor 3, in-sync replicas = 2 → durable ✓
>   DB write: happens asynchronously → no impact on 200ms latency
> ```
>
> > [!tip] Interview framing
> > *"Decouple acknowledgment from durability. Write to WAL first (durable within one node), acknowledge to sender immediately, replicate async. Or use Kafka as durable buffer: write to Kafka (fast + replicated), ack sender, DB write happens asynchronously. Both give <200ms latency with durability guarantees."*

---

## Q4 — Scalability NFR Drives Architecture

> [!question] You're designing a URL shortener that must handle 10,000 redirect requests per second and 100 writes per second. How do the NFRs drive your architecture differently than if the requirements were reversed?

> [!success]- Answer
>
> **Current requirements: 10,000 reads/sec, 100 writes/sec (100:1 ratio)**
>
> **What 10,000 reads/sec forces:**
> ```
> Without cache: 10,000 DB queries/sec
>   PostgreSQL: ~5,000 QPS with good hardware → insufficient
>   Must serve most reads from memory
>
> With Redis cache:
>   Hot URLs (top 1% of URLs serve 90% of traffic)
>   Cache hit: ~1ms, serves 9,000/sec
>   Cache miss: ~5ms DB lookup, serves 1,000/sec
>   → DB sees ~1,000 QPS → comfortable ✓
>
> CDN edge caching:
>   Popular short URLs cached at CDN edge nodes
>   Redirect served without hitting origin
>   Global latency: ~5ms regardless of origin location
> ```
>
> **100 writes/sec causes no scaling concern:**
> ```
> 100 writes/sec: trivially handled by single PostgreSQL instance
> No write sharding needed
> No write queue needed
> Just write to DB, invalidate cache entry
> ```
>
> **If reversed: 10,000 writes/sec, 100 reads/sec**
> ```
> Cache becomes useless:
>   New URL generated every 0.1ms → cache hit rate ≈ 0%
>   Cache is just overhead, skip it
>
> DB cannot sustain 10,000 writes/sec:
>   → Kafka message queue in front
>   → Batch writes: 1,000 inserts/batch every 100ms → 10 batches/sec
>   → DB sees 10 batch operations/sec → manageable ✓
>
>   Or: write sharding → 5 DB shards × 2,000 writes/sec each
>
> Reads become trivial (100/sec): single DB, no cache needed
> ```
>
> **The key insight:**
> ```
> Read-heavy NFR → cache-first architecture
> Write-heavy NFR → queue-first architecture
>
> Same feature, opposite scaling solutions
> NFRs drive the architecture, not intuition about "what shoud be fast"
> ```
>
> > [!tip] Interview framing
> > *"100:1 read/write: cache-first — Redis for hot URLs, CDN at edge, DB only for cache misses. Writes are trivial at 100/sec. Reversed ratio (10k writes, 100 reads): queue-first — Kafka absorbs writes, batch to DB. Cache is useless at 10k writes/sec. Read the NFR before drawing anything."*

---

## Q5 — Security NFR: PCI DSS Requirements

> [!question] Your e-commerce platform stores credit card data. The security NFR requires PCI DSS compliance. What architectural changes does this force?

> [!success]- Answer
>
> **PCI DSS — Payment Card Industry Data Security Standard:**
> The security standard for any system that stores, processes, or transmits credit card data.
>
> **What PCI DSS forces:**
>
> **1. Network segmentation — cardholder data environment (CDE):**
> ```
> Not all your infrastructure is PCI scope
> CDE = the systems that touch card data
>
> Architecture:
>   Public internet → API gateway (not PCI scope)
>   API gateway → Application servers (not PCI scope)
>   Application servers → CDE (isolated network segment)
>
>   CDE contains:
>     Payment processing service
>     Card data vault (encrypted)
>     No direct internet access from CDE
>
>   Scope minimization: reduce CDE to as few systems as possible
>   Every system in CDE = more compliance work
> ```
>
> **2. Encryption at rest and in transit:**
> ```
> Card numbers (PANs): AES-256 encrypted in DB
>                      Keys stored in Hardware Security Module (HSM) or AWS KMS
>                      Not in application code, not in environment variables
>
> CVV: NEVER stored (PCI requirement) — verify at transaction time only
>
> In transit: TLS 1.2+ everywhere within CDE
>             Not optional, not configurable
> ```
>
> **3. Tokenization (the best approach):**
> ```
> Don't store card numbers at all
>   → Use Stripe, Braintree, or similar
>   → They handle CDE compliance
>   → You store only a token (e.g. "tok_abc123") that represents the card
>   → Token is useless to attackers — no card number derivable from it
>
>   Architecture change: no card data in your DB at all
>                        drastically reduces PCI scope
>                        compliance effort: minimal
> ```
>
> **4. Access control and audit logging:**
> ```
> Principle of least privilege:
>   App server: can initiate charges, cannot read raw card numbers
>   DBA: cannot access card vault
>   Developer: no production access to CDE
>
>   Every access to card data: logged immutably
>   Alerts on unusual access patterns
> ```
>
> **Architecture recommendation:**
> ```
> Use Stripe/Braintree tokenization:
>   Card entered in Stripe-hosted field (not your servers)
>   Stripe returns token → your server stores token
>   Your infrastructure is completely out of PCI scope ✓
>
>   vs. handling card data yourself:
>   Months of compliance work, annual audits, significant liability
> ```
>
> > [!tip] Interview framing
> > *"PCI DSS forces: network segmentation (CDE isolated), encryption at rest (AES-256 + HSM for keys), never store CVV, immutable audit logs. Best approach: use Stripe/Braintree tokenization — card data never enters your systems, you're completely out of PCI scope. This is architecturally and economically the right choice for almost every company."*
