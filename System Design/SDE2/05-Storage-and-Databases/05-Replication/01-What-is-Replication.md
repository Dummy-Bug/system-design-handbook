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

---

## How the primary streams WAL to replicas

The replica opens a **persistent TCP connection** to the primary — a long-lived network connection that stays open. Once connected, the replica tells the primary exactly where it left off:

```
Replica ──── TCP connection ────► Primary
               "I'm at position 500, send me everything after"
```

From that point, the primary pushes WAL entries down the wire in real time. The moment a new entry is written to the WAL, it goes straight to the replica — this is a live push stream, not a poll.

```
Primary writes entry 501 to WAL
  → immediately pushes entry 501 to replica over TCP
  → replica receives it
  → replica applies it to its own data
  → replica is now in sync
```

### What happens when a replica disconnects

Say the replica crashes for 2 hours. During those 2 hours, the primary kept writing — entries 501 through 2000 were written. The replica missed all of them.

When it reconnects, it asks for everything from entry 501. But here's the problem — the primary doesn't keep the WAL forever. Old entries get cleaned up to save disk space.

```
Replica asks: "send me from entry 501"
Primary:      "entry 501 doesn't exist anymore, I deleted it"
Replica:       ??? stuck — can't catch up from the stream alone
```

At this point the replica needs a **full snapshot** — the primary sends a complete copy of its current data, and the replica rebuilds from scratch. Only then does streaming resume from that point forward.

```
Primary → sends full snapshot → Replica rebuilds from scratch
        → then resumes streaming WAL from that point forward
```

This is why replication lag and replica downtime matters in practice. A replica that's been down too long can't just reconnect and catch up — recovery becomes a full re-sync, which is expensive on a large database.
