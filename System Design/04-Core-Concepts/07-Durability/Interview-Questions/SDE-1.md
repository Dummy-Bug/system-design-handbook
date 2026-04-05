# Durability — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of durability, WAL, replication vs backups, and RPO. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is Durability?

> [!question] What is durability in the context of a database? How is it different from availability?

> [!success]- Answer
>
> **Durability** is the guarantee that once a write is confirmed, the data is permanently stored — it will not be lost even if the server crashes, power fails, or the disk dies immediately after.
>
> ```
> User submits an order
> DB says "confirmed"
> Server crashes 1 millisecond later
> User reboots app
>
> Durable DB: order is there ✓
> Non-durable: order is gone ✗
> ```
>
> **Durability vs Availability:**
> ```
> Durable but unavailable:
>   DB crashes → users can't access data (unavailable)
>   DB restarts → data is all there (durable)
>
> Available but not durable:
>   Redis with no persistence → always responds (available)
>   Power cut → all data gone (not durable)
> ```
>
> These are independent guarantees. Redis caches are deliberately non-durable — losing cache data is acceptable. User orders must be durable — losing a confirmed order is catastrophic.
>
> > [!important] Durability and availability are independent. Redis is available but not durable by default. A PostgreSQL replica is both. Choose based on what the data represents — can you afford to lose it?
>
> > [!tip] Interview framing
> > *"Durability means confirmed writes survive crashes. Availability means the system is responding. They're independent — Redis is available but not durable. PostgreSQL with replicas is both. Session caches can be non-durable. User orders cannot."*

---

## Q2 — Write-Ahead Log (WAL)

> [!question] What is a Write-Ahead Log and why does every production database use one?

> [!success]- Answer
>
> **The problem WAL solves:**
> Writing to disk isn't atomic. A database might update 10 pages for one transaction. If the server crashes after updating 3 of them, the data is in a corrupt, half-written state.
>
> **What WAL does:**
> ```
> Before touching any data pages:
>   1. Write the INTENTION to a log file (sequential, fast append)
>   2. Log is fsynced to disk (confirmed written)
>   3. Now apply the change to actual data pages
>
> If crash happens after step 1 but before step 3:
>   On restart → replay the log → complete the write → data intact ✓
>
> If crash happens before step 1:
>   Transaction never started → nothing to recover ✓
> ```
>
> **Why WAL is fast:**
> ```
> Log writes are sequential → fast (disk is good at sequential writes)
> Data page writes are random → slow
>
> WAL lets you:
>   Append to log (fast) → acknowledge to user
>   Apply to data pages (slow) → do asynchronously
> ```
>
> **What WAL protects against:**
> ```
> ✓ Server crash mid-write
> ✓ Power failure
> ✓ OS crash
> ✗ Disk hardware failure (need replication for this)
> ✗ Data center failure (need multi-region for this)
> ✗ Accidental DELETE (need backups for this)
> ```
>
> > [!tip] Interview framing
> > *"WAL writes the intention before touching data pages. On crash, replay the log to complete interrupted writes. Protects against single-server crashes — not against disk failure or accidental deletions. That's why we need replication and backups on top."*

---

## Q3 — Replication vs Backups

> [!question] You have a database with 3 replicas. Do you still need backups? Why or why not?

> [!success]- Answer
>
> **Yes — absolutely. Replication and backups protect against completely different failure types.**
>
> **What replication protects against:**
> ```
> ✓ Single node hardware failure → replica takes over
> ✓ Disk failure on one node    → other replicas have the data
> ✓ AZ or data center failure   → cross-region replica unaffected
> ```
>
> **What replication does NOT protect against:**
> ```
> ✗ Accidental DELETE FROM users  → replicated to all 3 replicas in milliseconds
> ✗ Bug that corrupts data         → corruption propagates to all replicas
> ✗ Ransomware                    → encrypts primary, replication propagates encryption
> ✗ Dropped table                 → propagated immediately
> ```
>
> **Replication copies everything — including mistakes:**
> ```
> Bug causes:  UPDATE orders SET price = 0 WHERE 1=1
> Runs at:     3:15am
> Replicated:  3:15:00am to replica 1, replica 2, replica 3
>
> All 4 nodes now have $0 prices
> Failover to any replica: same corrupted data
> ```
>
> **What backups protect against:**
> ```
> ✓ Logical corruption (bugs, accidental deletion, ransomware)
> ✓ You can restore to a point in time before the corruption
> ```
>
> **The combined strategy:**
> ```
> Replication → hardware failures, node failures, AZ failures
> Backups     → logical failures, human errors, corruption
> Both are required — they're complementary, not alternatives
> ```
>
> > [!important] Replication is real-time copying — it copies corruptions too. Backups are point-in-time snapshots that can restore to before the corruption. You need both.
>
> > [!tip] Interview framing
> > *"Replication protects against hardware failures. Backups protect against logical failures — bugs, accidental deletions, ransomware. They're complementary. A bug that wipes your data propagates to all 3 replicas in milliseconds. Only a backup from before the bug can save you."*

---

## Q4 — Sync vs Async Replication

> [!question] What is the difference between synchronous and asynchronous replication? When would you use each?

> [!success]- Answer
>
> **Synchronous replication:**
> ```
> Client writes → Primary writes → waits for replica to confirm → responds to client
>
> Guarantees: replica is always up to date, RPO = 0
> Cost:       write latency = primary write time + network round trip to replica
>             if replica is slow → all writes are slow
>             if replica is unreachable → writes block or fail
> ```
>
> **Asynchronous replication:**
> ```
> Client writes → Primary writes → responds to client immediately
>                                → replicates in background
>
> Guarantees: fast writes
> Cost:       if primary fails before replication completes → data lost
>             RPO > 0 (could lose seconds or minutes of writes)
> ```
>
> **When to use each:**
>
> | Use case | Replication | Reason |
> |---|---|---|
> | Financial transactions | Synchronous | RPO must be 0 — no data loss acceptable |
> | Bank transfers | Synchronous | Losing a confirmed transfer is catastrophic |
> | Social feed posts | Asynchronous | Losing a post on crash is acceptable |
> | Analytics events | Asynchronous | Some event loss tolerable, speed matters |
> | User profile updates | Async or sync | Depends on cost of loss |
>
> **Practical approach:**
> ```
> Use sync for critical data, async for the rest
> Or: sync to one replica (quorum), async to others
>     → RPO = 0 without full latency hit of syncing to all replicas
> ```
>
> > [!tip] Interview framing
> > *"Synchronous gives RPO = 0 at the cost of write latency. Async gives fast writes at the cost of potential data loss on failover. For financial data, sync is non-negotiable. For feeds and analytics, async is fine. Many systems sync to one replica and async to others — balancing safety and performance."*

---

## Q5 — RPO Calculation

> [!question] Your database does full backups every Sunday at midnight and incremental backups every hour. The DB crashes on Wednesday at 2:45pm. What is your RPO, and what data is lost?

> [!success]- Answer
>
> **Timeline:**
> ```
> Sunday midnight    → full backup taken ✓
> Monday 1am         → incremental backup ✓
> Monday 2am         → incremental backup ✓
> ...
> Wednesday 2am      → incremental backup ✓  ← last successful backup
> Wednesday 3am      → incremental would run at 3am... but crash at 2:45pm
> Wednesday 2:45pm   → CRASH ✗
> ```
>
> **What's recoverable:**
> ```
> Restore from: Sunday midnight full + all incrementals through Wednesday 2am
> Last known-good state: Wednesday 2:00am
> ```
>
> **Data lost:**
> ```
> Wednesday 2:00am → Wednesday 2:45pm
> = 45 minutes of data
> ```
>
> **RPO for this setup: 1 hour**
> (worst case: crash happens 59 minutes after last incremental)
>
> **How to improve:**
> ```
> Current RPO:  up to 1 hour
>
> More frequent incrementals (every 15 min) → RPO = 15 min
> Continuous WAL archiving to S3            → RPO = seconds
>                                             can restore to any point in time
> ```
>
> > [!tip] Interview framing
> > *"RPO is driven by backup frequency. Full weekly + hourly incrementals = RPO of 1 hour. For sub-minute RPO you need continuous WAL archiving — every transaction log shipped to storage, enabling point-in-time recovery to any second."*
