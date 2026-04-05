# Consistency Models — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around consistency model selection, read-your-writes violations, causal ordering, and the latency-consistency trade-off. Expected at SDE-2 level.

---

## Q1 — Per-Feature Consistency in Social Media

> [!question] You're designing Instagram. Different features have different consistency needs. Walk me through which consistency model you'd apply to: like counts, your own posts, your own profile, and direct messages.

> [!success]- Answer
>
> **The question to ask for each: what is the cost of showing stale data?**
>
> **Like counts — Eventual:**
> ```
> User sees: 1,241 likes (actual: 1,242)
> Cost of staleness: imperceptible — user doesn't know the exact count
> What matters: availability, throughput (billions of likes/day)
>
> → Eventual consistency
>   Write to any replica, sync in background
>   Cassandra with consistency ONE → fastest writes, highest throughput
> ```
>
> **Your own posts appearing on your profile — Read-Your-Writes:**
> ```
> User posts a photo → immediately views profile → photo must be there
>
> Without read-your-writes:
>   POST goes to replica A
>   Profile read goes to replica B (hasn't synced)
>   Photo not visible → user thinks upload failed → posts again → duplicate
>
> → Read-Your-Writes
>   Route this user's reads to the same replica they just wrote to
>   Or: carry write version in session → reject reads from behind replicas
> ```
>
> **Your own profile settings (bio, username) — Read-Your-Writes:**
> ```
> Same as posts — user updates profile → must see change immediately
> Same mechanism: sticky read routing or version tokens
> ```
>
> **Direct messages — Causal:**
> ```
> Alice: "Are you free tonight?"
> Bob:   "Yes, what time?"  ← causally depends on Alice's message
>
> Without causal: Bob's reply visible before Alice's question → incoherent
>
> → Causal consistency
>   Causal token: Bob's message carries "I depend on Alice's message M42"
>   Replica must have M42 before delivering Bob's reply
>   All users see messages in causal order
>
> Not strong consistency → WhatsApp stays available for 2B users even on bad networks
> ```
>
> > [!tip] Interview framing
> > *"Vary consistency by feature based on cost of staleness. Like counts: eventual (nobody cares about exact count). Own posts/profile: read-your-writes (users notice missing their own changes). Messages: causal (replies must appear after their parent). Strong consistency only where stale data causes real harm."*

---

## Q2 — Read-Your-Writes Implementation

> [!question] You're building a feature: user updates their settings → gets immediately redirected to a page that reads those settings. Your system uses async replication. How do you guarantee read-your-writes?

> [!success]- Answer
>
> **The problem:**
> ```
> User updates email: PUT /settings/email
>   → Write to primary replica
>   → Async replication: propagates to read replicas in ~100ms
>
> User redirected to /settings page: GET /settings
>   → Request routed to read replica
>   → Replica hasn't received update yet (100ms lag)
>   → User sees old email → "My change didn't save" → tries again
> ```
>
> **Solution 1 — Read from primary after write:**
> ```
> After any write: route reads for that user to primary for 1 second
>   → Always sees latest write ✓
>   → Cost: primary handles more reads → less efficient
>   → Best for: when most reads should still go to replicas but critical read-after-write cases need freshness
> ```
>
> **Solution 2 — Version/timestamp token in session:**
> ```
> Write returns: { success: true, write_version: 12345 }
> Store write_version in user's session cookie
>
> Read request: sends cookie with write_version: 12345
> API server checks: is replica at version ≥ 12345?
>   Yes → serve from replica ✓
>   No  → route to primary or wait for replica to catch up
>
> Clean: replicas serve most reads, only primary used when replica is behind
> ```
>
> **Solution 3 — Sticky session routing:**
> ```
> After a write, pin user's requests to the same replica for 2 seconds
> Same replica that has the write
>
> Simpler to implement, but less precise
> Problem: if pinned replica goes down, user loses the pin
> ```
>
> **Solution 4 — Synchronous replication for settings (tier it):**
> ```
> Settings writes → synchronous replication → RPO = 0, all replicas updated
> Feed reads → async replication → eventual consistency
>
> Pay sync cost only where read-your-writes matters
> ```
>
> > [!tip] Interview framing
> > *"Route read to primary if within 1 second of write — simple but adds primary load. Version tokens are cleaner — write returns a version, reads check if replica has caught up to that version before serving. Sticky routing is middle ground. Synchronous replication on settings makes it moot but adds write latency."*

---

## Q3 — Causal Consistency in Collaborative Editing

> [!question] Two users are editing a shared Google Doc. User A types "Hello", User B replies by adding "World" after it. Without causal consistency, what can go wrong? How does causal consistency fix it?

> [!success]- Answer
>
> **The problem without causal consistency:**
> ```
> User A (US-East): types "Hello" → write to US-East replica
>   US-East → propagates async to EU-West: arrives at T=1000ms
>
> User B (EU-West): sees "Hello" → types "World" after it → write to EU-West replica
>   EU-West → propagates to US-East: arrives at T=800ms
>
> (EU-West's write travels faster in this scenario)
>
> US-East sees:
>   T=800ms: " World" (B's addition) arrives
>   T=1000ms: "Hello" (A's original) arrives
>
>   Document shows: " WorldHello" (order reversed)
>
>   User B's edit appears before User A's text it was meant to follow ✗
> ```
>
> **Causal consistency fix:**
> ```
> Causal tracking: every operation carries metadata about what it depends on
>
> User B's write includes:
>   "I depend on User A's write at version V42"
>   ("I typed 'World' after seeing 'Hello' — I causally depend on A's write")
>
> US-East receives B's write "World":
>   Check: do I have A's write V42?
>   No → hold B's write in a buffer
>   T=1000ms: A's write "Hello" V42 arrives → apply it
>   Now apply B's "World" (dependency satisfied)
>
>   Document: "Hello World" ✓ — causal order preserved
> ```
>
> **Why not strong consistency:**
> ```
> Strong consistency (quorum):
>   User A types → wait for majority of replicas to confirm → then apply
>   Every keystroke adds 100ms+ network latency
>   Typing feels laggy → unusable for real-time collaboration
>
> Causal consistency:
>   User A types → apply locally immediately (fast)
>   Causal tokens ensure ordering → applied in correct order on all replicas
>   No latency for the user → feels instant
> ```
>
> > [!tip] Interview framing
> > *"Without causal consistency, B's response can appear before A's original text — network timing breaks ordering. Causal tokens: B's write carries 'I depend on A's V42'. Replicas hold B's write until A's arrives. Strong consistency would make every keystroke wait for quorum — unacceptably laggy for real-time editing."*

---

## Q4 — Strong vs Eventual: Shopping Cart

> [!question] Amazon uses eventual consistency for shopping carts. A staff engineer says "this is wrong — if I add an item and it disappears, I'll never trust the cart." How do you defend eventual consistency here?

> [!success]- Answer
>
> **The trade-off at Amazon's scale:**
> ```
> Amazon processes ~$1M in sales per minute
> Millions of concurrent cart operations globally
>
> Strong consistency for carts:
>   Every add/remove: quorum write → wait for majority of replicas
>   Adds ~50-100ms latency per cart operation
>   At 1% of adds → system degrades → cart unavailable
>
>   If the quorum nodes partition:
>     Cart write fails → user gets an error → "you can't add items right now"
>     → user abandons cart → Amazon loses sale
> ```
>
> **The defense of eventual consistency:**
>
> **1. Cart is a pre-commitment artifact:**
> ```
> Cart ≠ order
> Cart = "I might buy this eventually"
>
> If a cart add is lost:
>   User re-adds the item → minor inconvenience
>   vs
>   User can't add anything → loses ability to purchase → guaranteed lost sale
>
> Temporary staleness: inconvenient
> Unavailability: catastrophic
> ```
>
> **2. The vector clock approach (Amazon's actual approach):**
> ```
> Amazon uses vector clocks on cart data
> If two replicas have conflicting versions of the cart:
>   "User added X on replica 1, User removed Y on replica 2"
>   → Show both versions → let user reconcile
>   → "We noticed some changes to your cart — please review"
>
> Conflict resolution surfaced to user, not silently lost
> ```
>
> **3. Read-your-writes on top of eventual:**
> ```
> The "I added item and it disappeared" complaint is actually a
> read-your-writes violation, not pure eventual consistency
>
> Fix: read-your-writes guarantee for cart operations
>      User always sees their own adds/removes immediately
>      Other users' concurrent cart edits: eventually consistent
>
>      Now: "it disappeared" can't happen for your own adds ✓
> ```
>
> > [!tip] Interview framing
> > *"Amazon's cart uses eventual consistency because cart unavailability is worse than momentary staleness — a failed add is a minor inconvenience, a cart that can't be modified loses the sale. The 'item disappeared' concern is a read-your-writes violation, solved separately. Vector clocks surface conflicts instead of silently discarding them."*

---

## Q5 — Consistency Downgrade During Incidents

> [!question] Your system uses strong consistency (quorum reads/writes). During a major incident, quorum is not achievable. Should you downgrade to eventual consistency to stay available? What are the risks?

> [!success]- Answer
>
> **The situation:**
> ```
> N=5 nodes, quorum = 3
> Incident: 2 nodes unreachable
>
> Quorum not achievable → strong consistency writes fail
> Users getting errors → service appears down
>
> Option: lower consistency requirement temporarily
>         respond from any available node (eventual)
>         → service stays available
>         → but reads may return stale data
> ```
>
> **The answer depends entirely on what data the system holds:**
>
> **If it's financial/payment data: do NOT downgrade:**
> ```
> Stale balance → user sees $1000, actual is $0 (after fraud)
>   → approves purchase against non-existent funds → financial loss
>
> Stale inventory → user buys last item, it was already sold
>   → oversell → unfulfillable order → broken trust
>
> Temporary unavailability is recoverable (user tries again)
> Wrong financial data may not be recoverable
>
> Correct answer: serve errors, NOT stale data
>                 "Service temporarily unavailable" is the right response
> ```
>
> **If it's social/content data: downgrade may be acceptable:**
> ```
> Feed temporarily shows 2-minute-old posts → users don't notice
> Like counts slightly off → harmless
>
> Availability > fresh data for content
> Downgrade: serve stale → users get degraded but functional experience
> ```
>
> **The meta-decision:**
> ```
> This decision must be pre-made, not made under pressure at 2am
>
> In design: define per-service degradation policy
>   "Payment reads: never downgrade consistency"
>   "Feed reads: acceptable to serve stale during quorum failure"
>   "User auth: never downgrade — stale token data could allow unauthorized access"
>
> Pre-agreed runbook: incident → check service type → follow policy
> ```
>
> > [!tip] Interview framing
> > *"Whether to downgrade depends on what staleness costs. Financial data: never downgrade — serve errors. Content feeds: downgrade may be acceptable — stale posts beat an error page. This decision must be pre-made, not improvised during an incident. Define a per-service degradation policy and put it in the runbook."*
