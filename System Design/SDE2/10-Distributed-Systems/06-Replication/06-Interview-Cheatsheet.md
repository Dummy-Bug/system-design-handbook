# Replication — Interview Cheatsheet

---

## When to mention replication

```
"How do you handle DB failure?"          → replication + failover
"How do you scale read traffic?"         → read replicas
"What's your RPO?"                       → sync vs async replication
"How do you serve global users?"         → multi-primary + conflict resolution
Any system with > 10K read QPS          → read replicas
```

---

## The standard move — always say this first

> [!tip] Replication before sharding
> "I'd add read replicas to distribute read traffic — Instagram's read/write ratio is 99:1 so replicas absorb almost all traffic. If write throughput or storage becomes the bottleneck, I'd then consider sharding."

Replication is simpler, safer, and sufficient for most read-heavy systems. Sharding is the escalation path.

---

## Decisions to state explicitly

**Sync vs async — always justify**

> "I'd use async replication for low write latency. The trade-off is a small data loss window on failover, which is acceptable here because [reason]. For the payment ledger specifically, I'd use semi-sync — requiring at least one replica to confirm before returning success."

**Replication lag + read-your-own-writes fix**

> "With async replication, replicas lag by milliseconds. To prevent read-your-own-writes violations — where a user updates something and immediately sees the old value — I'd route that user's reads to the primary for a short window after their write."

**Failover**

> I'd use Patroni for automated failover. On primary failure it promotes the most up-to-date replica and redirects traffic — typically a 20-30 second write outage. To reduce data loss I'd configure semi-sync for critical writes.

**Multi-primary (only if global)**

> "For a globally distributed system I'd use multi-primary so users in each region write to a nearby node. Conflict resolution: last-write-wins for non-critical data, single-primary routing for financial operations."

---

## One-line definitions

> [!info] Replication
> Continuously copying every write from a primary database to one or more replicas so multiple servers hold the same data.

> [!info] Async replication
> Primary returns success before replica confirms. Fast writes, small data loss window on failover.

> [!info] Sync replication
> Primary waits for replica to confirm before returning success. Zero data loss, slower writes.

> [!info] Replication lag
> The delay between a write landing on the primary and that write appearing on a replica. Normally milliseconds; visible as read-your-own-writes violations.

> [!info] Failover
> Promoting a replica to primary when the primary fails. Automated with Patroni (PostgreSQL) or Redis Sentinel. Typically 20-30 second write outage.

> [!info] Split-brain
> Two nodes both believe they are the primary and accept writes simultaneously, causing data divergence. Prevented by quorum — a node only accepts writes if it can reach a majority of peers.

---

## The RPO framing

| Replication type | RPO | Write latency | Use for |
|---|---|---|---|
| Async | Seconds (in-flight writes) | Fastest | Social feeds, caches, most systems |
| Semi-sync | Zero (confirmed writes) | Slightly slower | E-commerce, critical data |
| Sync | Zero | Slowest | Financial ledgers, payments |
