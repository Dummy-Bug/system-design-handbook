# Interview Cheatsheet — Durability

> [!question] When does durability come up in an interview?
> Any time you store data. The interviewer will ask "what happens if the server crashes?" or "what's your RPO?" — this cheatsheet is your answer.

---

## The Four Layers — Always Present as a Chain

*"Durability has four layers — each covers a failure the previous one can't handle."*

```
Layer 1 — WAL
  What it covers: single server crash, power loss, partial write
  How: append intention to log before writing data → replay on recovery

Layer 2 — Replication (same data center)
  What it covers: single node disk failure
  How: WAL shipped to replicas in real time

Layer 3 — Multi-region replication
  What it covers: entire data center failure
  How: async or sync replication across geographic regions

Layer 4 — Backups
  What it covers: logical corruption, accidental deletion, ransomware
  How: point-in-time snapshots that replication cannot corrupt
```

---

## Moment 1 — "What happens if the database server crashes?"

*"WAL ensures no data is lost on a single server crash. Every write is logged before it touches the data — on recovery the database replays the log and completes any interrupted operations. The user either got a confirmed write or an error. No corrupted in-between state."*

---

## Moment 2 — "What's your RPO?"

Connect RPO directly to your backup strategy:

| Backup Strategy | RPO |
|---|---|
| Weekly full only | Up to 7 days |
| Weekly full + daily incremental | Up to 24 hours |
| Weekly full + hourly incremental | Up to 1 hour |
| Continuous WAL archiving | Seconds |

*"RPO is determined by backup frequency. For this system I'd do weekly full backups with hourly incrementals — RPO of one hour. For the payment data specifically, continuous WAL archiving to get RPO under a minute."*

---

## Moment 3 — "Why do you need backups if you have replication?"

*"Replication copies everything in real time — including mistakes. A bug that deletes all user records replicates to every region in milliseconds. Replication can't save you there. Backups are point-in-time snapshots taken before the corruption — they're the only way to recover from logical failures. Replication handles hardware failures, backups handle logical failures. You need both."*

---

## Durability vs Availability — State the Difference

> [!important] These are independent guarantees — don't conflate them

```
Durable but unavailable:
  DB crashes → users can't access data → but data is safe on disk
  Restart → data back → zero data lost

Available but not durable:
  Redis with no persistence → always up → power cut → all data gone
```

*"Durability and availability are independent. Redis by default is available but not durable. PostgreSQL with replication is both. I'd choose based on what the data represents — session cache can be non-durable, user orders cannot."*

---

## The Full Durability Checklist

- [ ] Mentioned WAL for single server crash survival
- [ ] Mentioned replication — at least node level, ideally multi-region
- [ ] Stated sync vs async replication and justified the choice (RPO = 0 → sync)
- [ ] Mentioned backups — full + incremental strategy
- [ ] Connected backup frequency to RPO
- [ ] Explained why replication and backups are complementary, not alternatives
- [ ] Distinguished durability from availability

---

## Quick Reference

```
Four layers:
  WAL              → survives: crash, power loss
  Replication      → survives: disk failure, node failure
  Multi-region     → survives: data center failure
  Backups          → survives: logical corruption, accidental deletion

Backup strategy:
  Full weekly + incremental daily  → RPO 24h
  Full weekly + incremental hourly → RPO 1h
  Continuous WAL archiving         → RPO seconds

Sync vs async replication:
  Sync  → RPO = 0, higher latency  → payments, banking
  Async → RPO > 0, lower latency   → social feeds, analytics

Durability ≠ Availability:
  Redis  → available, not durable (no persistence)
  Postgres + replication → both
```
