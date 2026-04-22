# ACID — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around ACID properties in real systems. Expected at SDE-2 level — not just definitions, but understanding when and why guarantees break, and what to do about it.

---

> [!question] You're designing a payment system. A user initiates a transfer — debit Alice, credit Bob. Halfway through, the app server crashes. When it restarts, how does the database ensure Alice's money isn't lost permanently?

> [!success]- Answer
>
> On restart, the database reads the WAL and looks for transactions with no `COMMIT` marker:
>
> ```
> WAL on restart:
>   → "deduct $100 from Alice"  ← logged
>   → no COMMIT marker          ← transaction never finished
>   → rollback: restore Alice to original balance ✓
> ```
>
> This is Atomicity in action. The WAL recorded what was done before the crash. On restart, the DB uses that record to undo the partial work — as if the transaction never started.
>
> The COMMIT marker is the dividing line:
> ```
> No COMMIT in WAL → atomicity kicks in → undo (rollback)
> COMMIT in WAL    → durability kicks in → redo (recovery)
> ```
>
> Same WAL, opposite direction depending on whether the transaction completed.
>
> > [!tip] Interview framing
> > *"On restart the DB scans the WAL for incomplete transactions — those with no COMMIT marker. It uses the WAL entries to reverse the partial changes. If it finds a COMMIT marker, it replays the transaction instead. Same WAL, opposite direction — that's the difference between atomicity and durability."*

---

> [!question] You're building an e-commerce checkout. Two users add the last item in stock to their cart simultaneously and both hit "place order" at the same time. Both see "Order confirmed". How did this happen and which ACID property failed?

> [!success]- Answer
>
> **Isolation failed first, Consistency failed as a result.**
>
> The specific isolation failure is a **lost update**:
>
> ```
> T1: read stock = 1
> T2: read stock = 1
> T1: write stock = 1 - 1 = 0  ← T1's update
> T2: write stock = 1 - 1 = 0  ← T2 overwrites T1, T1's update is LOST
> ```
>
> T2 read the value before T1 wrote it, then overwrote T1's result. T1's decrement is silently gone. Both transactions thought stock was available — both committed successfully.
>
> > [!important] Why it's a lost update, not a dirty read
> > T2 didn't read T1's uncommitted data — it read the original committed value. But it based its write on a stale read, and its write overwrote T1's result. That's a lost update: two transactions read the same value, both compute a new value from it, the second write silently wipes the first.
>
> Consistency then fails as a consequence:
> ```
> Both orders committed → stock = -1
> → database now in invalid state (negative stock violates constraint)
> ```
>
> **The fix:**
> ```
> Pessimistic locking  → SELECT FOR UPDATE locks the row
>                        T2 waits for T1 to finish before reading
>
> Optimistic locking   → store a version number on the row
>                        T2 checks version before writing — if changed, retry
> ```
>
> > [!tip] Interview framing
> > *"Isolation failed — specifically a lost update. Both transactions read stock=1 simultaneously, both decided to proceed, T2's write overwrote T1's. Consistency then broke as a consequence — stock went to -1. Fix with pessimistic locking (SELECT FOR UPDATE) or optimistic locking with version numbers."*

---

> [!question] A junior engineer says "we can turn off fsync to make writes 3x faster — we have replication anyway, so if this server dies we just failover to the replica." Is he right?

> [!success]- Answer
>
> **Wrong — replication does not save you when fsync is off.**
>
> The key insight most people miss: the WAL write itself goes through the OS buffer. With `fsync=off`, nothing is guaranteed to be on physical disk — not the data, not the WAL.
>
> ```
> fsync=off:
>   WAL write  → OS buffer  ← not disk
>   Data write → OS buffer  ← not disk
>
> fsync=on:
>   WAL write  → OS buffer → fsync() → physical disk ← truly safe
>   Data write can be async — WAL alone is enough to recover
> ```
>
> With `fsync=off`, replication is a race condition against the crash:
>
> ```
> Transaction commits
> → WAL written to OS buffer (not disk)
> → DB tells client "committed" ✓
> → replication starts shipping WAL to replica...
> → POWER CUT before replication completes
>
> Primary  → OS buffer wiped, WAL entry gone
> Replica  → never received it
> Client   → was told "committed"
> → transaction lost on both servers
> ```
>
> Even if replication completes in time — you've introduced a silent dependency: durability only holds if replication always wins the race against a power cut. That is not a guarantee you can make.
>
> > [!important] Replication protects against hardware failure — a dead server. It does not protect against data that never reached disk in the first place.
>
> > [!danger] fsync=off breaks the WAL itself
> > People assume WAL = safe because it's "on disk". But without fsync, the WAL write goes through the same OS buffer as everything else. The very mechanism that's supposed to guarantee durability is sitting in RAM.
>
> > [!tip] Interview framing
> > *"Replication doesn't save you — because with fsync=off, even the WAL is in the OS buffer, not on disk. A power cut wipes the OS buffer before replication completes, and the transaction is lost on both servers. Replication protects against a dead server, not against data that never hit disk."*

---

> [!question] Your app uses full ACID guarantees on the database. You add Kafka — on order placed, write to DB and publish to Kafka. DB write succeeds, Kafka publish fails. Is ACID still protecting you?

> [!success]- Answer
>
> **No — ACID's scope ends at the database boundary.**
>
> ```
> DB write  → ✓ committed, ACID protects this
> Kafka pub → ✗ failed, ACID has no jurisdiction here
> ```
>
> The DB transaction committed cleanly — from ACID's perspective everything is fine. The inconsistency is between two separate systems, not within the DB. This is the **dual-write problem**: two systems written in one logical operation with no atomic guarantee spanning both.
>
> **The fix — Outbox Pattern:**
> ```
> Instead of:
>   write to DB + publish to Kafka  ← two separate operations, either can fail
>
> Do:
>   write to DB + write event to outbox table  ← one DB transaction, ACID covers both
>   separate process reads outbox → publishes to Kafka → marks as sent
> ```
>
> The event write and DB write are now in the same transaction. ACID covers both. Kafka publishing happens separately and can be retried safely — if it fails, the outbox entry is still there.
>
> > [!tip] Interview framing
> > *"ACID only covers what happens inside a single database transaction. The moment you write to two systems — DB and Kafka — you have a dual-write problem. Fix it with the Outbox Pattern: write the event to an outbox table in the same DB transaction, then a separate process reliably ships it to Kafka."*

---

> [!question] A user reports: "I transferred money and it showed successful, but when I refreshed the page the balance was back to the original amount." Which ACID property failed and what's the most likely cause?

> [!success]- Answer
>
> **Most likely cause: stale replica read — not an ACID failure at all.**
>
> The write succeeded — durability held. The problem is the read after the write returned old data:
>
> ```
> User writes  → goes to primary → committed ✓
> User refreshes → read routes to replica → replica not yet synced
> → user sees old balance
> → read-your-own-writes violation
> ```
>
> This is a **replication lag** issue. ACID guarantees durability on the primary — it does not guarantee that replicas have caught up at the moment of the next read.
>
> **The second possible cause — lost update:**
> ```
> User sends $100    → T1: read balance=500, write 400
> Spouse withdraws   → T2: read balance=500, write 400 (overwrites T1)
> → T1's update gone, balance shows 500 again
> → Isolation failed → lost update
> ```
>
> This would be a genuine ACID failure — Isolation didn't hold.
>
> **How to tell them apart in an interview:**
> ```
> Stale replica read → balance shows exact original value, write vanished entirely
>                      far more common in production
>                      not an ACID failure — replication lag issue
>
> Lost update        → balance shows wrong value (not original, not correct post-transfer)
>                      requires concurrent write from another transaction
>                      genuine Isolation failure
> ```
>
> > [!important] Always give the most likely cause first, then the alternative. Stale replica read is the right first answer — it's far more common and the symptom matches exactly.
>
> > [!tip] Interview framing
> > *"Most likely a stale replica read — the write committed on primary but the read hit an unsynced replica. This is a read-your-own-writes violation caused by replication lag, not an ACID failure. The second possibility is a lost update — a concurrent write overwrote the transfer — but that's less likely and would show a different balance value, not the exact original."*
