> [!question] You have a replica running. But what is it actually doing while it waits?
> And what does RPO = 0 really cost you?

---

## Warm standby vs hot standby — what's the actual difference

Both have a replica running on a separate machine, continuously syncing with the primary. The difference is what that replica is doing while it waits.

**Hot standby** — the replica is live and actively serving read traffic. Failover is automated: a health check detects the primary is dead and promotes the replica within seconds. No human involved.

```
Primary  ──writes──▶  Replica (serving reads, fully synced)

Primary dies at 3:00:00
Health check fires  at 3:00:05
Replica promoted    at 3:00:08
Traffic redirected  at 3:00:10
RTO = ~10 seconds
```

**Warm standby** — the replica is running and staying in sync, but serving no traffic. It's just sitting there replicating. When the primary dies, someone (or a script) has to manually promote it, update the load balancer config, run health checks, and verify it's ready. That process takes minutes.

```
Primary  ──writes──▶  Replica (syncing, idle — serving nothing)

Primary dies at 3:00:00
Engineer gets paged  at 3:02:00
Promotes replica,
updates config       at 3:08:00
RTO = ~8 minutes
```

| | Hot Standby | Warm Standby |
|---|---|---|
| Serving traffic? | Yes — reads | No — just replicating |
| Failover | Automated, seconds | Manual or scripted, minutes |
| RTO | Seconds | Minutes |
| Cost | Higher (doing real work) | Slightly lower (idle server) |

> [!tip] Warm standby is a spare tyre in the boot — you still have to pull over and change it. Hot standby is a second engine that kicks in automatically.

---

## The hidden cost of RPO = 0

RPO = 0 means zero data loss — every write must be confirmed on the replica before the user gets a response. That's **synchronous replication**.

Synchronous replication adds latency to every write. The write has to travel to the replica and get confirmed before the user gets a response. If the replica is in another datacenter, that's 50–100ms added to every single write operation.

```
Async replication (RPO = seconds):
User writes → Primary confirms → User gets response ✓
                ↓ (background)
            Replica replicates

Sync replication (RPO = 0):
User writes → Primary writes → Replica writes → Both confirm → User gets response ✓
              ←————————— 50–100ms round trip if cross-datacenter ————————————→
```

This is why most systems use **asynchronous replication** — slightly higher RPO (seconds of potential data loss), but no latency penalty on writes. The business decides which trade-off is acceptable.

> [!important] RPO = 0 is not free. Every write pays a latency tax equal to the round-trip time to your replica. At Google scale (100k writes/sec), adding 50ms to every write is a significant cost. Reserve synchronous replication for data where loss is truly unacceptable — financial transactions, billing records.

---

## How they drive architecture decisions

| RTO | Strategy | What it requires |
|---|---|---|
| Hours | Snapshot restore | Backup file in remote storage (S3), no standby server needed |
| Minutes | Warm standby replica | A replica is running but not serving traffic, manual failover |
| Seconds | Hot standby replica | A replica is live, automated failover promotes it instantly |
| Zero | Active-Active | Multiple live primaries, no failover — writes go to all |

| RPO | Strategy | What it requires |
|---|---|---|
| 24 hours | Daily snapshots to S3 | Simplest and cheapest — acceptable for non-critical data |
| 1 hour | Hourly snapshots | Still snapshot-based, just more frequent |
| Minutes | Async replication | Live replica with small replication lag |
| Zero | Sync replication | Write confirmed only after both primary and replica have written it |

## MTTR vs RTO — they sound similar but are different things

- **MTTR** — what *actually happens* on average when things break. A measurement of past incidents.
- **RTO** — what the *business requires* as the maximum acceptable downtime. A target you design to.

You design your system so that MTTR stays below RTO. If your RTO is 30 minutes, your recovery process — detection, failover, verification — must consistently complete in under 30 minutes.

```
RTO = 30 min  (the ceiling the business set)
MTTR = 8 min  (what actually happens based on incident history)

→ You have headroom. You're meeting the SLA comfortably.

If MTTR creeps up to 35 min → you're breaching RTO → time to improve your recovery process.
```

---

> [!tip] In an interview — ask for both before designing
> *"What's the RTO and RPO for this system?"*
>
> The answers tell you exactly what backup strategy and replication model to use. A fintech system with RPO = 0 needs synchronous replication to another datacenter. An internal analytics dashboard with RPO = 24 hours just needs daily snapshots to S3. Same question, completely different architectures.
