# Failover

> [!question] The primary database server dies. What happens next? How fast does the system recover, and what data is at risk?

---

## What failover is

When the primary dies, a replica must be promoted to take over as the new primary. This process — detecting the failure, electing a new primary, and redirecting traffic to it — is called **failover**.

```
Primary dies
→ health check detects failure (heartbeat timeout — typically 10-30 seconds)
→ leader election — replicas vote, one is promoted to new primary
→ app servers / load balancer redirected to new primary
→ system back online
→ remaining replicas now replicate from new primary
```

Tools like **Patroni** (PostgreSQL) and **Redis Sentinel** handle this automatically. Without them, failover is manual — an engineer wakes up at 3am, picks a replica, runs promotion commands, updates DNS. Automated failover is non-negotiable for production systems.

---

## The failover gap

During the window between the primary dying and the new primary being ready, **writes are unavailable**. Health checks need time to detect the failure. Leader election takes time. DNS propagation or load balancer reconfiguration takes time.

```
T=0    → primary crashes
T=0-15 → health check timeout (detecting the failure)
T=15-25 → leader election, new primary chosen
T=25-30 → app servers redirected to new primary
T=30   → system accepting writes again

~30 second write outage ✗
```

This is your **RTO (Recovery Time Objective)** impact — the time your system cannot take writes. 30 seconds is typical for automated failover. Manual failover can be 30 minutes or more.

---

## Data loss on failover with async replication

With async replication, the promoted replica may be a few seconds behind the primary at the moment of failure. Writes that were committed on the primary but hadn't yet replicated are permanently lost.

```
T=10.000s → user posts a photo
           → primary writes it → "post successful" returned to user ✓
           → replication is async — replica hasn't received it yet

T=10.002s → primary server loses power (disk failure, hardware fault)
           → replica is 2 seconds behind
           → those 2 seconds of writes → never reached the replica
           → gone forever ✗

T=10.030s → replica promoted to primary
           → user refreshes feed → their photo is missing
           → they were told "success" but the data is lost
```

The WAL sits on the primary's local disk. If the primary is unrecoverable, the WAL entries that hadn't streamed to any replica are lost.

This is the core async replication trade-off — fast writes during normal operation, a small data loss window when the worst happens.

---

## How to reduce the data loss window

**Semi-sync replication** — require at least one replica to confirm receipt before returning success. Now the primary can die and the replica that confirmed still has the write.

```
With semi-sync:
  Primary writes → replica confirms → "success" returned
  Primary dies   → promoted replica has the confirmed write ✓
  Data loss: zero for any write that returned success
```

**Increase replication factor** — more replicas means a smaller chance that all of them are lagging on the exact write that was in-flight when the primary died.

**Cross-AZ replication** — run replicas in different availability zones. A datacenter-level failure that kills the primary is unlikely to also kill an AZ-separated replica at the exact same moment.

---

## Avoiding split-brain during failover

A dangerous failure mode: the primary doesn't actually die — it becomes unreachable due to a network issue. The replica gets promoted (thinks primary is dead). Now both think they are primary.

```
Primary is isolated by network partition (alive but unreachable)
→ health check times out → replica promoted → "new primary"
→ old primary: "I'm still primary, accepting writes"
→ new primary: "I'm primary, accepting writes"
→ two primaries, diverging data ✗
```

Fix: **STONITH (Shoot The Other Node In The Head)** — the failover process explicitly fences the old primary (powers it off, revokes its DB credentials, removes it from the network) before the new primary starts accepting writes. Brutal name, effective solution.

> [!tip] Interview framing
> "On primary failure, Patroni automatically promotes the most up-to-date replica. With async replication there's a small data loss window — any writes that hadn't replicated before the crash are lost. For systems where that's unacceptable I'd use semi-sync replication, requiring at least one replica to confirm before returning success."
