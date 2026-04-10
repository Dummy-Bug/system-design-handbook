# Sync vs Async Replication

> [!question] When you write to the primary, should it wait for replicas to confirm before returning success — or fire and forget?

This is the core trade-off in replication: **durability vs latency**.

---

## Async Replication — default for most systems

Primary writes, immediately returns success to the app, then sends the copy to replicas in the background.

```
User posts a photo:
→ primary writes photo to disk
→ "post successful" ✓ returned to user immediately
→ replica receives copy milliseconds later (background, non-blocking)
```

```
✓ Fast writes      — replica lag doesn't block the user
✓ High availability — if a replica is slow or down, writes are unaffected
✗ Replication lag  — replica may be slightly behind primary at any moment
✗ Data loss window — if primary crashes before replica received the write,
                     that write is gone
```

For most consumer systems — Instagram, Twitter, news feeds — async replication is the right choice. A post appearing a few milliseconds later on a replica is invisible to users.

### The physical flow — async

The primary writes to its WAL, applies the change, and immediately returns success. The replica has a persistent TCP connection open and streams WAL entries in the background via offset — it tracks where it left off and asks for everything after that position.

```
Primary:
  1. Write to WAL
  2. Apply to data
  3. → "success" to app   ← doesn't wait for anyone

Replica (background, via persistent TCP):
  4. "give me entries after offset 500"
  5. Receives WAL entry
  6. Applies it to its own data
```

The primary never waits for the replica. The replica catches up on its own time.

---

## Sync Replication — for when data loss is unacceptable

Primary writes, then **waits** for at least one replica to confirm it received the write, then returns success.

```
User transfers money:
→ primary writes transaction
→ waits for replica to confirm receipt  ← blocking
→ replica confirms
→ "transfer successful" returned to user
```

```
✓ Zero lag         — replica always has latest data when write is confirmed
✓ Zero data loss   — replica confirmed receipt before success was returned
✗ Slower writes    — every write waits for at least one replica round-trip
✗ Availability risk — replica is down or slow → writes are blocked
```

Used for financial systems, payment ledgers, and anything where "we told the user it succeeded but then lost the data" is a serious problem.

### The physical flow — sync

The primary writes to its WAL, pushes the entry to the replica over the persistent TCP connection, and **holds the success response** until it receives an ACK back.

```
Primary:
  1. Write to WAL
  2. Apply to data
  3. Push WAL entry to replica over TCP
  4. WAIT...

Replica:
  5. Receives WAL entry
  6. Writes it to its own WAL on disk  ← durable first
  7. → sends ACK back over the same TCP connection

Primary:
  8. Receives ACK
  9. → "success" to app   ← only now
```

The replica doesn't need to fully apply the change before ACK-ing — it only needs to confirm it wrote the entry to its own WAL. That's enough, because the WAL is on disk. If the replica crashes before applying, it will read its own WAL on restart and apply the pending entry then.

```
Replica crashes before applying:
  → restarts
  → reads its own WAL
  → sees unapplied entry
  → applies it
  → data recovered ✓
```

This is why the guarantee holds: when the user sees "success", at least one replica has the write durably on disk — even if it hasn't applied it yet.

> [!important] What if both primary and replica crash simultaneously?
> The replica wrote to its WAL before ACK-ing. WAL is on disk — it survives crashes. When the replica restarts it replays its WAL and recovers the entry. The only scenario where data is truly lost is if the replica's disk itself fails — hardware failure, not a replication design problem.

---

## Semi-Sync Replication — the pragmatic middle ground

A common production compromise: require **at least one** replica to confirm, but not all of them.

```
Primary writes
→ waits for one replica to confirm (not all)
→ returns success

Result:
✓ Guaranteed copy on at least one other server — data loss requires two simultaneous failures
✓ Only one replica round-trip — faster than waiting for all replicas
✓ System can tolerate one replica being slow without blocking writes
```

This is what MySQL semi-sync replication does. It's widely used in financial and e-commerce systems that need durability without fully sacrificing write speed.

### The physical flow — semi-sync

Same as sync, but the primary only waits for the **fastest replica** to ACK. The others receive the WAL entry asynchronously in the background.

```
Primary:
  1. Write to WAL
  2. Apply to data
  3. Push WAL entry to all replicas over TCP
  4. WAIT for any one ACK...

Replica 1 (fast):
  5. Writes to its own WAL
  6. → ACK

Replica 2, 3 (slow or lagging):
  5. Receive entry in background, apply later

Primary:
  7. Receives ACK from Replica 1
  8. → "success" to app   ← doesn't wait for Replica 2 or 3
```

Data loss now requires two simultaneous failures — the primary and the one replica that ACK'd both have to lose their disks at the same time. That's an extremely unlikely hardware event, which is why semi-sync is considered durable enough for most financial systems.

---

## The trade-off summarised

```
Async  → fast writes, tiny data loss window on failover
         use for: social feeds, caches, analytics, most consumer systems

Sync   → slow writes, zero data loss, availability depends on replica health
         use for: financial ledgers, payment systems, stock brokers

Semi-sync → one replica must confirm, others async
            use for: systems that need durability but can't afford full sync latency
```

> [!important] The choice affects your RPO
> RPO (Recovery Point Objective) — how much data can you lose in a failure?
> Async replication → RPO = seconds (whatever was in-flight when primary died)
> Sync replication  → RPO = 0 (no committed write can be lost)
> This is why the sync vs async decision is fundamentally an RPO decision.
