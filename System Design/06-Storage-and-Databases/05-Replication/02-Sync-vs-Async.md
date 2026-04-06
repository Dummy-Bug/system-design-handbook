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
