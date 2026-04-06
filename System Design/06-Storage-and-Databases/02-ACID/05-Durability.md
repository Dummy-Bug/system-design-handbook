# Durability

> [!info] Durability — once a transaction is committed, that data survives forever. Crashes, power loss, hardware failure — none of it can undo a committed transaction.

---

## The guarantee

When the database says "commit successful," it means the data is on disk. Not in memory. Not in a buffer. On disk. If the server loses power the next millisecond, the data is still there when it restarts.

```
Transaction commits → "Transfer successful" returned to user ✓
Server loses power 2 seconds later

Without durability:
  Data was only in memory → power loss → gone
  → user told "transfer successful" but money never moved ✗
  → Alice debited, system lost the credit to Bob permanently

With durability:
  Committed data written to disk before "success" returned
  → server restarts → data still there ✓
  → transfer stands, ledger intact
```

---

## How the database achieves it — the WAL

Durability is implemented through the **Write-Ahead Log (WAL)**.

The core rule: **before any change is written to the actual data files, the change is first written to the WAL on disk.**

```
Transaction commits:
  Step 1: Write commit record to WAL on disk  ← sync write, mandatory
  Step 2: Return "success" to the application
  Step 3: Apply the change to data pages      ← can happen later, async

Server crashes after step 1, before step 3:
  → WAL has the commit record
  → On restart: DB replays WAL, applies the committed change
  → Data restored correctly ✓

Server crashes before step 1:
  → WAL has no commit record for this transaction
  → On restart: DB sees no commit, treats it as never happened
  → Clean rollback ✓
```

The WAL is the single source of truth for what actually happened. The data files are just a materialized view of the WAL — they can always be reconstructed from it.

---

## Why writes feel slow — fsync

For durability to hold, the WAL write must be confirmed by the disk — not just handed to the OS buffer. The database calls `fsync()` to force the OS to flush its write buffer to physical storage before returning success.

```
DB writes to OS buffer → OS may hold in RAM for performance
DB calls fsync() → OS flushes RAM buffer → physical disk write confirmed
→ now the data truly survives a power cut ✓
```

`fsync()` is slow — it forces a round-trip to disk. This is why:
- Writes on an HDD are slow (~10ms per fsync)
- NVMe SSDs are faster but still bounded by the physical write
- Systems that turn off fsync (some cloud DBs in non-durable mode) are fast but sacrifice durability guarantees

> [!danger] Never turn off fsync in production for financial or transactional data
> Some databases allow `fsync=off` for testing or speed. This completely breaks the D in ACID — a power cut will corrupt or lose committed transactions. Fine for a test environment. Catastrophic for production money or bookings.

---

## Durability and replication

A single-server WAL protects against that server's crashes. But it doesn't protect against:
- Disk failure destroying the WAL itself
- Datacenter fire
- Entire server being lost

This is why **replication** pairs with durability. Replication copies the WAL to other servers. If the primary is unrecoverable, a replica has a copy of the WAL and can be promoted.

```
Durability alone   → survives this server crashing
Durability + sync replication → survives this server being destroyed entirely
```

RPO = 0 requires both durability (WAL on disk) and sync replication (WAL on another server's disk).
