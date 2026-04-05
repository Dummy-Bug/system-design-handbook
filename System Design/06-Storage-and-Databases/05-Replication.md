# Database Replication

---

## Why One Database Server Is Never Enough

You're running Instagram. One database server, 500 million users hitting it simultaneously.

Two problems immediately:

```
1. SPOF — DB goes down, everything goes down
2. Overload — 500M concurrent connections, CPU maxed, disk I/O saturated
              → responses slow → timeouts → collapse
```

The fix is **Replication** — run multiple DB servers and keep them in sync. One server is the source of truth, continuously copying its data to others.

---

## Primary-Replica — The Standard Setup

One **Primary** accepts all writes. One or more **Replicas** receive copies of every write and serve read traffic.

```
App servers
     │
     ├──── writes ────→ Primary DB
     │                      │
     │               replicates to
     │                      │
     └──── reads  ────→ Replica 1
                    ────→ Replica 2
                    ────→ Replica 3
```

Instagram's read/write ratio is roughly 99:1 — users scroll and read far more than they post. Replicas absorb 99% of traffic. Primary only handles writes.

> [!info] **Replication** — continuously copying data from one database server (primary) to others (replicas) so multiple servers have the same data.

---

## Sync vs Async Replication

The key question — when you write to the primary, does it wait for replicas to confirm before returning success?

### Async Replication (default for most systems)

Primary writes, immediately returns success, sends copy to replicas in the background.

```
User posts photo:
→ primary writes photo → "post successful" ✓ returned immediately
→ replica receives copy milliseconds later (background)
```

```
✓ Fast writes     — replica lag doesn't block anything
✓ High availability — replica being slow/down doesn't affect writes
✗ Replication lag — replica may be slightly behind primary
```

### Sync Replication

Primary writes, waits for replica to confirm receipt, then returns success.

```
User posts photo:
→ primary writes photo
→ waits for replica to confirm ← blocking
→ replica confirms
→ "post successful" returned
```

```
✓ Consistency  — replica always has latest data, zero lag
✗ Slower writes — every write waits for replica round-trip
✗ Availability risk — replica slow or down? write is blocked
```

> [!important] Most systems use **async replication** and handle edge cases explicitly. Sync replication is reserved for financial systems where even milliseconds of data loss is unacceptable.

---

## Replication Lag — The Visible Problem

With async replication, replicas are always slightly behind the primary. Normally this is milliseconds — imperceptible.

But one scenario makes it very visible: **you update something and immediately read it back**.

You're on Instagram. You update your profile picture. You immediately refresh your profile page.

```
Write → goes to primary ✓
Read  → hits a replica → replica hasn't caught up yet
      → you see your old profile picture ✗
```

This is a **read-your-own-writes violation** — you were told the write succeeded, but you can't see it yet.

**Fix — read-your-own-writes routing:**

```
User updates profile pic:
→ write goes to primary
→ for this user's next reads → route to primary for a short window
→ after replica catches up → route reads to replica again ✓
```

---

## Failover — When the Primary Dies

When the primary dies, a replica must be promoted to take over. This process is called **Failover**.

```
Primary dies
→ health check detects failure (timeout)
→ leader election — replicas vote, one promoted to new primary
→ app servers redirected to new primary
→ system back online
```

Tools like Patroni (PostgreSQL) and Redis Sentinel handle this automatically. The gap — time between primary dying and new primary ready — is typically **10-30 seconds**. During this window, writes are unavailable.

### Data Loss on Failover

With async replication, the promoted replica may be a few seconds behind. Writes that were committed on the primary but hadn't replicated yet are permanently lost:

```
Primary at T=10s: write committed → "success" returned to user ✓
Replica at T=10s: 2 seconds behind, write not yet received

Primary dies at T=10s
→ replica promoted to primary
→ those 2 seconds of writes → gone forever ✗
→ user was told "success" but data is lost
```

The WAL is on the primary's disk — if the primary is unrecoverable, so is the WAL.

> [!important] This is the fundamental async replication trade-off: fast writes with a tiny data loss window on failover. For most systems this is acceptable. For financial systems, use sync replication or semi-sync (at least one replica must confirm).

---

## Multi-Primary — Multiple Write Nodes

Instead of one primary and multiple replicas, all nodes accept writes simultaneously. No SPOF on the primary — if one node dies, others keep accepting writes.

But this introduces **Split-Brain**.

### Split-Brain

Most commonly triggered by a **network partition** — two primaries lose connection to each other but both stay up:

```
Network partition:
  Primary 1 ←✗→ Primary 2   (can't reach each other)

  Primary 1: "Primary 2 is dead, I'm in charge" → accepts writes
  Primary 2: "Primary 1 is dead, I'm in charge" → accepts writes

  User A updates username on Primary 1 → "alice_new"
  User B updates same username on Primary 2 → "alice_123"

  Both succeed ✓ — but both primaries now have different data ✗

  Partition heals → two diverged histories → conflict resolution nightmare
  Which write wins? Last-write-wins? Merge? → lossy, business-specific
```

> [!danger] Split-brain is one of the hardest problems in distributed databases. The fix is **quorum** — a node only accepts writes if it can confirm a majority of nodes are aware. If it can't reach a majority, it refuses writes rather than risk divergence. Better to be unavailable than wrong.

---

## Summary

```
Primary-Replica   → one writer, many readers
                    simple, widely used, SPOF on primary (mitigated by failover)

Sync replication  → zero data loss, slower writes, availability risk
                    use for: financial systems, anything where data loss = unacceptable

Async replication → fast writes, tiny data loss window on failover
                    use for: most systems, Instagram, Twitter, feeds

Replication lag   → replica slightly behind primary
                    visible as: read-your-own-writes violations
                    fix: route user's reads to primary for short window after write

Failover          → 10-30 second gap, possible data loss with async
                    automated with Patroni (PostgreSQL), Sentinel (Redis)

Multi-Primary     → no write SPOF, but split-brain risk
                    requires quorum to prevent divergence
```
