# Replication as Durability

## Why WAL Alone Is Not Enough

WAL survives crashes on a single server. But what if the disk itself physically fails?

```
Server disk burns out
WAL is on that disk
Database files are on that disk
Everything gone — WAL can't save you
```

The fix — keep copies of the data on **multiple independent machines**.

---

## The Three Layers of Replication

### Layer 1 — Multiple Nodes, Same Data Center

```
Primary node  ──WAL──▶  Replica 1  (same rack)
              ──WAL──▶  Replica 2  (different rack)
```

**Survives:** Single node disk failure, single server crash
**Doesn't survive:** Entire data center power failure, fire, flood

---

### Layer 2 — Multiple Data Centers, Same Region

```
Data Center A (Primary)  ──replicate──▶  Data Center B (Standby)
```

**Survives:** Single data center failure — fire, flooding, power grid
**Doesn't survive:** Regional disaster — earthquake, widespread outage

---

### Layer 3 — Multi-Region Replication

```
US-East (Primary)  ──replicate──▶  EU-West
                   ──replicate──▶  AP-Southeast
```

**Survives:** Entire region going offline
**Doesn't survive:** Logical corruption — deletion replicates to all regions instantly

---

## The Replication Durability Problem

> [!danger] Replication copies everything — including mistakes

```
Bug runs → deletes all user records from primary
Deletion replicates to EU-West    → also deleted
Deletion replicates to AP-Southeast → also deleted

All three regions now have zero user records
Replication made the corruption worse — faster and wider
```

This is why replication and backups are **complementary, not alternatives:**
- Replication protects against **hardware failure**
- Backups protect against **logical corruption**

---

## Synchronous vs Asynchronous Replication — The Durability Tradeoff

> [!important] How you replicate determines your RPO

**Synchronous replication:**
```
Write to primary
Wait for replica to confirm write
Only then → confirm to user

RPO = 0  (zero data loss — replica always in sync)
Cost     = higher latency (user waits for replica confirmation)
```

**Asynchronous replication:**
```
Write to primary
Confirm to user immediately
Replica catches up in background (milliseconds to seconds behind)

RPO > 0  (small data loss possible if primary dies before replica syncs)
Cost     = lower latency (user doesn't wait for replica)
```

| System | Replication Type | Reason |
|---|---|---|
| Banking, payments | Synchronous | RPO = 0, cannot lose transactions |
| Social media feed | Asynchronous | Slight staleness acceptable, latency matters more |
| E-commerce orders | Synchronous | Money involved |
| Analytics data | Asynchronous | Slight delay acceptable |

> [!tip] Interview framing
> *"I'd use synchronous replication for anything involving money or user data — RPO must be zero. For read replicas serving non-critical data, async replication is fine — the latency cost of synchronous isn't worth it there."*
