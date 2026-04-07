# What is Replication?

> [!question] Your database is a single server. What happens when it crashes? What happens when 500 million users hit it at the same time?

---

## Why one database server is never enough

You're running Instagram. One database server, 500 million users hitting it simultaneously.

Two problems immediately:

```
1. SPOF — DB goes down, everything goes down
           no redundancy, no fallback, total outage

2. Overload — 500M concurrent reads, CPU maxed, disk I/O saturated
              responses slow → timeouts → cascade collapse
```

Both problems have the same fix: **Replication** — run multiple DB servers and keep them in sync.

> [!info] Replication
> Continuously copying data from one database server (the primary) to one or more others (replicas) so multiple servers hold the same data at all times.

---

## Primary-Replica — the standard setup

One **Primary** accepts all writes. One or more **Replicas** receive a continuous stream of every write and serve read traffic.

```
App servers
     │
     ├──── writes ────→ Primary DB
     │                      │
     │               replicates to
     │                      ↓
     └──── reads  ────→ Replica 1
                    ────→ Replica 2
                    ────→ Replica 3
```

Instagram's read/write ratio is roughly 99:1 — users scroll and browse far more than they post. Replicas absorb 99% of all traffic. The primary only handles writes, keeping it focused and un-overwhelmed.

This setup solves both problems:

```
SPOF?     → primary dies → promote a replica → system stays up
Overload? → reads distributed across replicas → primary handles writes only
```

---

## How replication physically works

When a write lands on the primary, the primary records it in its **WAL (Write-Ahead Log)**. Replicas continuously stream that WAL and apply each entry to their own copy of the data.

```
Write arrives at primary
→ primary writes to WAL
→ primary applies change to its data
→ replica streams WAL entry
→ replica applies same change to its data
→ replica is now in sync
```

This is why CDC (Change Data Capture) is so natural — it taps into the exact same WAL stream that replication already uses. The mechanism already exists; CDC just adds another reader.
