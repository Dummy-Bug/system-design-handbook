# Durability

## What it is

> [!info] Durability = data survives after it has been successfully written. Once the system says "saved" — it means it, no matter what fails next.

**The Google Docs example:**
You type 3 pages of notes. Laptop dies — battery dead, no warning. You open it back up. Notes are still there.

That's durability — the data was persisted to disk before the crash, so it survived.

---

## What Durability Protects Against

```
Single server crash      → power cut, OS crash, process killed
Node disk failure        → hard disk burns out, SSD fails
Data center failure      → fire, flood, power grid failure, earthquake
Logical corruption       → bug deletes all records, ransomware, accidental DROP TABLE
```

Each threat requires a different tool — covered in the files in this folder.

---

## Durability vs Availability — Independent Problems

> [!important] A system can be durable but unavailable, or available but not durable. These are separate guarantees.

```
Durable but NOT available:
  Database crashes → server is down → users can't access data
  But data is safely on disk → restart → data is back
  Unavailable for 5 minutes. Zero data lost.

Available but NOT durable:
  Redis cache with no persistence → fast responses, always up
  Power cut → all data in memory gone forever
  Available right up until the moment everything is lost.

Both durable AND available:
  Replicated database with WAL → data safe + system stays up
  The goal for production systems
```

> [!example] Real world
> A Redis cache is available but not durable by default. A PostgreSQL database with replication is both. Choosing which you need is a design decision — not every system needs both.

---

## The Four Layers of Durability

```
Layer 1 — WAL
  Survives: single server crash, power loss, partial write

Layer 2 — Replication
  Survives: single node disk failure

Layer 3 — Multi-region replication
  Survives: entire data center failure

Layer 4 — Backups
  Survives: logical corruption, accidental deletion, ransomware
```

Each layer covers a failure that the one above it cannot handle. They are complementary — not alternatives.
