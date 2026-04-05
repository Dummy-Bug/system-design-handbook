# Durability — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around backup strategies, replication design, WAL, and RPO vs performance trade-offs. Expected at SDE-2 level.

---

## Q1 — Backup Strategy Design

> [!question] You're designing the backup strategy for a payments database. The RPO requirement is 5 minutes. What's your strategy?

> [!success]- Answer
>
> **What RPO = 5 minutes means:**
> ```
> Worst case: DB fails, you can lose at most 5 minutes of payment data
> ```
>
> **Why daily backups are completely insufficient:**
> ```
> Daily backup: RPO = up to 24 hours
>               If DB fails at 11:59pm: lose 24 hours of payments
>               For a payment system: catastrophic
> ```
>
> **The solution — continuous WAL archiving:**
> ```
> PostgreSQL: continuous WAL archiving to S3 (or equivalent)
>
> How it works:
>   Every transaction generates WAL entries
>   WAL segments are shipped to S3 continuously (every 30 seconds or per segment)
>   On recovery: restore latest base backup, then replay WAL to any point in time
>
> RPO = time since last WAL segment shipped
>   → typically: seconds to 1-2 minutes
>   → well within 5-minute requirement ✓
> ```
>
> **Combined strategy:**
> ```
> Weekly: full base backup (RDS automated snapshot, or pg_basebackup)
>         → stored in S3 with 30-day retention
>
> Continuous: WAL segments to S3
>             → retained for 7 days
>             → enables point-in-time recovery (PITR) to any second
>
> Syncs:
>   Week 1 full + continuous WAL → can restore to any point in week 1
>   Week 2 full + continuous WAL → can restore to any point in week 2
> ```
>
> **Testing:**
> ```
> Monthly restore test: restore to a test environment from last week's backup
>                       verify payment data integrity
>                       without testing, backups are assumptions
> ```
>
> > [!tip] Interview framing
> > *"RPO = 5 minutes requires continuous WAL archiving to S3 — WAL segments shipped every 30-60 seconds. Combined with weekly full backups for the base. This enables point-in-time recovery to any second within the retention window. Monthly restore tests to verify the process actually works."*

---

## Q2 — Multi-Region Durability

> [!question] Your database has synchronous replication to a replica in the same data center. The entire data center catches fire. What data is lost and how do you redesign for this?

> [!success]- Answer
>
> **What's lost with same-DC replication:**
> ```
> Current setup:
>   Primary (DC East) ←synchronous→ Replica (DC East)
>   Both in same physical facility
>
> Fire destroys DC East:
>   Primary: gone
>   Replica: also gone (same building)
>   Both copies of data: destroyed
>
>   All data since last off-site backup: LOST ✗
> ```
>
> **The root cause:**
> Replication protects against node failure. Not against facility failure. Both nodes sharing the same failure domain is not redundancy — it's a single point of failure at the facility level.
>
> **Redesign — two layers of replication:**
>
> **Layer 1: Same-region, cross-AZ (synchronous):**
> ```
> Primary (AZ-1a) ←synchronous→ Replica (AZ-1b)
>   Same region, different physical data centers
>   Network latency: ~1ms → sync adds minimal write latency
>   RPO = 0 for AZ-level failures
>   Cost: slight write latency increase
> ```
>
> **Layer 2: Cross-region (asynchronous):**
> ```
> Primary (US-East) ──async──→ Replica (US-West)
>   Network latency: ~70ms → sync would add 70ms to every write (unacceptable)
>   Async: primary responds after local write, replicates in background
>   RPO: minutes (whatever the async lag is)
>   Protects against: full regional disaster
> ```
>
> **Layer 3: Off-site backups:**
> ```
> WAL archived continuously to S3 (cross-region bucket)
> Even if both regions have an incident: backups survive
> ```
>
> > [!tip] Interview framing
> > *"Same-DC replication shares a failure domain — fire takes both nodes. Fix: sync replication across AZs within the region (1ms latency, RPO=0 for AZ failures), async replication cross-region (70ms sync cost is prohibitive, so async with small RPO). Plus continuous WAL archiving to cross-region S3 as the last line of defense."*

---

## Q3 — Durability vs Performance

> [!question] Your team wants to use Redis as the primary store for user session data and order drafts. A colleague says Redis isn't durable. How do you evaluate whether this is acceptable?

> [!success]- Answer
>
> **Your colleague is right by default — Redis with no persistence is not durable:**
> ```
> Redis defaults: all data in RAM
> Server crash or restart: all data gone
> RPO: everything since last restart
> ```
>
> **But "not durable" isn't automatically wrong — it depends on what the data is:**
>
> **User session data:**
> ```
> What happens if sessions are lost?
>   → All users are logged out
>   → They log in again (20 seconds)
>   → Annoying, but not catastrophic
>
> "Durability" cost of a crash: user inconvenience
> This IS acceptable for session data
> ```
>
> **Order drafts:**
> ```
> What happens if order drafts are lost?
>   → User was building a cart, hasn't submitted yet
>   → Draft disappears → they start over
>   → Annoying, potential order abandonment
>
> More concerning, but still not financial loss
> Borderline acceptable
> ```
>
> **When to add Redis persistence (if needed):**
> ```
> AOF (Append Only File) — appends every write to disk
>   → RPO: near zero (lose at most 1 second of data)
>   → Cost: ~10-15% performance overhead
>
> RDB (periodic snapshots) — snapshot every N minutes
>   → RPO: up to N minutes
>   → Cost: low overhead
>
> For sessions: RDB every 60 seconds is fine
>               User loses 60 seconds of session activity — tiny impact
>
> For order drafts: AOF if any draft loss is unacceptable
> ```
>
> **The key question to always ask:**
> ```
> What is the business impact of losing this data on crash?
> Measure it. Then decide.
>
> Sessions: low impact → plain Redis (no persistence) is fine
> Payments: high impact → never Redis as primary → PostgreSQL with WAL
> ```
>
> > [!tip] Interview framing
> > *"Durability is a spectrum. For sessions, Redis without persistence is acceptable — users log in again. For order drafts, borderline — consider RDB snapshots. For financial data, Redis is never the primary store — use PostgreSQL with WAL. The question is: what's the business impact of this specific data being lost?"*

---

## Q4 — WAL Under the Hood

> [!question] Walk me through what happens to data during a PostgreSQL write, from the client sending SQL to the data being durable. Where can it fail and what survives?

> [!success]- Answer
>
> **The write path:**
>
> ```
> 1. Client sends: INSERT INTO orders (user_id, total) VALUES (123, 50.00)
>
> 2. PostgreSQL writes to WAL (Write-Ahead Log):
>    → Sequential append to WAL file on disk
>    → fsync() called — OS confirms data is on physical disk, not just OS buffer
>    → ONLY after this does PostgreSQL consider the write safe
>    → Responds "success" to client
>
> 3. In background: PostgreSQL writes to actual data pages
>    → Updates the physical table files (heap files)
>    → This may happen seconds or minutes later
>    → If crash here: WAL will replay on restart to complete the write
>
> 4. Checkpoint: periodically, PostgreSQL flushes dirty pages to disk
>    → WAL entries before checkpoint can be pruned
> ```
>
> **What survives at each failure point:**
>
> ```
> Crash before step 2 (WAL write):
>   → Nothing written to WAL → transaction never committed
>   → On restart: no record of this write → nothing to recover
>   → Client will get an error or timeout → must retry ✓
>
> Crash after step 2 (WAL written), before step 3 (data pages):
>   → WAL has the intention recorded
>   → On restart: PostgreSQL replays WAL → completes the write to data pages
>   → Data is recovered ✓ → client gets the confirmation it received
>
> Crash after step 3:
>   → Data already in both WAL and data pages → fully durable ✓
> ```
>
> **Why sequential writes make WAL fast:**
> ```
> WAL writes: sequential → disk head moves predictably → fast
> Data page writes: random I/O → disk head jumps → slow
>
> WAL lets you: do the fast sequential write first → acknowledge to client
>               do the slow random write later → asynchronously
> ```
>
> > [!tip] Interview framing
> > *"PostgreSQL writes to WAL first (sequential, fast, fsynced to disk), then responds to client. Data pages updated asynchronously. On crash: replay WAL to recover any writes that hadn't reached data pages. fsync is the key — without it, WAL entry could be in OS buffer only, lost on power failure."*

---

## Q5 — Choosing Between Sync and Async Replication

> [!question] You have a 3-node database cluster. Node A is in London, Node B is in Frankfurt, Node C is in New York. Should replication be synchronous or asynchronous? What's the impact on RPO and write latency?

> [!success]- Answer
>
> **Network latency between nodes:**
> ```
> London ↔ Frankfurt: ~20ms
> London ↔ New York:  ~75ms
> Frankfurt ↔ New York: ~90ms
> ```
>
> **Option 1: Fully synchronous (all 3 nodes):**
> ```
> Write on London (primary)
> → wait for Frankfurt confirm: +20ms
> → wait for New York confirm: +75ms
>
> Write latency: 5ms (local) + 75ms (slowest replica) = 80ms per write
> RPO = 0 → every confirmed write exists on all 3 nodes
>
> Problem: 80ms per write is extremely high for most systems
>          An app making 10 writes per request → 800ms total → unacceptable
> ```
>
> **Option 2: Synchronous to Frankfurt, async to New York:**
> ```
> Write on London
> → wait for Frankfurt confirm: +20ms
> → New York replicates in background
>
> Write latency: 5ms + 20ms = 25ms per write ✓
> RPO for London failure: 0 (Frankfurt has everything)
> RPO for London + Frankfurt simultaneous failure: seconds (New York lag)
>
> This is the common production approach for Europe-based systems
> ```
>
> **Option 3: Fully asynchronous:**
> ```
> Write on London → respond immediately
> → Frankfurt and New York replicate in background
>
> Write latency: 5ms ✓ (fastest)
> RPO for London failure: lag amount (could be seconds to minutes)
>
> Acceptable for: non-financial data, where some loss is acceptable
> Not acceptable for: payments, where RPO = 0 is required
> ```
>
> **The recommended approach for this topology:**
> ```
> London → Frankfurt: synchronous (20ms cost, provides RPO=0 for single-node failure)
> London → New York:  asynchronous (disaster recovery, ~seconds lag, no latency cost)
>
> This matches the common "synchronous to same-region, async cross-region" pattern
> Synchronous cross-continental is generally too expensive latency-wise
> ```
>
> > [!tip] Interview framing
> > *"Fully synchronous across continents adds 75ms+ to every write — too expensive. Standard approach: synchronous to nearby replica (Frankfurt, 20ms overhead, RPO=0 for single-node failure), async to distant replica (New York, disaster recovery with seconds RPO, no write latency cost)."*
