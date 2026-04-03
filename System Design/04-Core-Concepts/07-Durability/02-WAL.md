# Write-Ahead Log (WAL)

## The Problem

```
User places an order
Database starts writing order to disk
Power cuts out mid-write
Half the data is written — half is not
Database restarts → corrupted record → order in unknown state
```

Without a safety mechanism, a crash at any point during a write can corrupt data permanently.

---

## What WAL Is

> [!info] WAL = Write the INTENTION to a log first, before touching the actual data. On recovery, replay the log to finish what was interrupted.

**The sequence:**

```
Without WAL:
  1. Write data directly to disk
  2. Power cuts mid-write
  3. Data partially written → corrupted → unrecoverable

With WAL:
  1. Append operation to WAL log file  ← crash here → no data changed, safe
  2. WAL write confirmed
  3. Write actual data to disk         ← crash here → replay WAL on recovery
  4. Mark operation complete in WAL
```

If a crash happens **before** step 1 — nothing was written, user gets an error. Clean state.
If a crash happens **after** step 1 — on recovery, read WAL, see incomplete operation, replay it. Data safe.

---

## Why WAL Writes Are Safe

> [!question] Why is writing to WAL safe when writing to the database isn't?

**WAL is append-only and sequential:**

```
DB write  → find the right page on disk → update it in place
            random I/O — disk head jumps around
            partial write possible mid-page

WAL write → just append to end of log file
            sequential I/O — no seeking, just write next bytes
            atomic at OS level — either appended or not, no partial state
```

Sequential writes are 10-100x faster than random writes on spinning disks. Even on SSDs, sequential writes are more reliable. A small append to a log file is effectively atomic — it either completes or it doesn't.

---

## WAL in Replication

WAL is also the mechanism databases use to replicate data to other nodes:

```
Master receives write
  ↓
Master writes to its WAL
  ↓
WAL entry shipped to replicas
  ↓
Replicas apply the same WAL entry to their own data
  ↓
Master commits to its database
  ↓
Replicas commit to their databases
```

This is how PostgreSQL streaming replication works — replicas are essentially replaying the primary's WAL in real time.

---

## What WAL Does NOT Protect Against

> [!warning] WAL only protects a single server from crashes. It does not help if:
> - The entire disk physically fails (burns out) — WAL is on that disk too
> - The data center loses power permanently
> - A bug corrupts data — WAL faithfully replays the corrupted write

For these, you need replication and backups — covered in the next files.

> [!tip] Interview framing
> *"WAL ensures durability at the single server level — any crash is recoverable by replaying the log. For disk failure or data center failure, I'd add replication. For logical corruption, backups."*
