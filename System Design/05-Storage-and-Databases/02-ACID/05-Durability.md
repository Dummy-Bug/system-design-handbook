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

For durability to hold, the WAL write must be confirmed by the actual disk — not just handed to the OS. The problem is that when the database tells the OS "write this to disk", the OS doesn't do it immediately. It puts the data in a **RAM buffer** first and says done ✓ — because RAM is fast and batching writes are more efficient.

```
Without fsync:
DB → "write this" → OS → RAM buffer → "done ✓"  ← OS is lying
                                           ↓ maybe later → actual disk
```

From the database's perspective the write succeeded. From reality's perspective, the data is still in RAM. One power cut and it's gone — even though the database told the client "committed".

`fsync()` is the database forcing the OS to stop lying:

```
With fsync:
DB → "write this" → OS → RAM buffer → fsync() → physical disk → done ✓
```

The **database blocks and waits until the OS confirms** the data has physically hit the disk. Only then does it return "commit successful" to the client. This is why writes feel slow — you are literally waiting for a physical disk write to complete on every committed transaction.

This forced round-trip to disk is what makes writes slow. There's no shortcut — the database must wait for the physical write to complete before it can respond.

```
HDD:      ~10ms per fsync   ← mechanical seek + write
NVMe SSD: ~0.1ms per fsync  ← still bounded by physical write, just much faster
```

> [!danger] Never turn off fsync for financial or transactional data
> Some databases expose `fsync=off` for testing or speed. This completely breaks the D in ACID — a power cut will corrupt or lose committed transactions. The OS buffer gets wiped, and no WAL survives to recover from. Fine for a throwaway test environment. Catastrophic for money, bookings, or anything a user was told succeeded.

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
