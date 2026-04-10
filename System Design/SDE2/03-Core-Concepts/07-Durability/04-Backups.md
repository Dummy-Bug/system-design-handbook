# Backups

## Why Replication Is Not Enough

Replication copies data across nodes and regions in real time. That's the problem.

```
Bug runs → deletes all 50M user records
Deletion replicates to all regions in milliseconds
All regions now have zero user records

Replication faithfully copied the corruption everywhere
```

You need a **point-in-time snapshot** taken before the corruption happened. That's a backup.

---

## Full Backup

A complete copy of all data at a specific point in time.

```
Sunday 2am → full backup → copy all 10TB to backup storage
```

**Restore is simple:**
```
Corruption detected → restore Sunday 2am snapshot → done
Lost: everything since Sunday 2am
```

**Problem:** Copying 10TB every day is expensive and slow. Doing it hourly is impractical.

---

## Incremental Backup

Only copy data that **changed** since the last backup.

```
Sunday 2am  → Full backup      → 10TB copied
Monday 2am  → Incremental      → only 50GB changed → copy 50GB
Tuesday 2am → Incremental      → only 30GB changed → copy 30GB
Wednesday 2am → Incremental    → only 80GB changed → copy 80GB
```

**Much cheaper.** But restore is more complex:

```
Corruption on Wednesday 3pm:

  Step 1: Restore Sunday full backup    → database at Sunday 2am state
  Step 2: Apply Monday incremental      → database at Monday 2am state
  Step 3: Apply Tuesday incremental     → database at Tuesday 2am state

  Lost: Tuesday 2am → Wednesday 3pm
```

Think of it like Git:
```
Full backup   = initial commit (entire codebase)
Incremental   = each subsequent commit (only the diff)
Restore       = checkout initial + apply all commits in order
```

**Problem:** 6 months of daily incrementals = 180 files to apply on restore. Very slow recovery.

---

## The Middle Ground Strategy

Take a fresh full backup periodically, incrementals in between:

```
Week 1 Sunday  → Full backup        (reset the chain)
Mon → Sat      → Daily incrementals (max 6 files to apply)
Week 2 Sunday  → Full backup        (reset the chain)
Mon → Sat      → Daily incrementals
```

**Worst case restore:** Full backup + 6 incrementals. Manageable.

---

## Backup Frequency and RPO

> [!important] Backup frequency directly determines your RPO

```
Full backup every week, incrementals every day:
  Corruption Wednesday 3pm
  Last backup: Tuesday 2am
  Data lost: ~37 hours → RPO = 37 hours

Incrementals every hour:
  Corruption Wednesday 3pm
  Last backup: Wednesday 2pm
  Data lost: 1 hour → RPO = 1 hour

Continuous backup (WAL archiving):
  Stream WAL to backup storage in real time
  RPO = seconds
```

More frequent backups = smaller RPO = less data loss = higher cost.

---

## Backups vs Replication — Not Alternatives

> [!warning] These solve different problems

| | Protects Against | Does NOT protect against |
|---|---|---|
| **Replication** | Hardware failure, node/DC outage | Logical corruption (replicates instantly) |
| **Backups** | Logical corruption, accidental deletion | Hardware failure during backup window |

**Use both:**
```
Replication → keeps system available when hardware fails
Backups     → lets you recover from bugs, accidental deletes, ransomware
```

> [!tip] Interview framing
> *"I'd use replication for hardware failure and availability. Backups — full weekly, incremental daily — for logical corruption and accidental deletion. Backup frequency determines RPO — for critical data I'd do hourly incrementals or continuous WAL archiving to get RPO under an hour."*
