
> [!info] Standby nodes are not about throughput — they are about availability. The primary handles all traffic; standbys exist only for when the primary fails.

---

## Why standby nodes

After the sharding analysis, we established that a single Postgres primary handles Pastebin's traffic comfortably:

```
Peak read QPS:   3,000  (primary capacity: 10k–50k reads/sec)
Peak write QPS:  30     (primary capacity: 1k–5k writes/sec)
Postgres storage: ~3TB  (single machine limit: ~10TB)
```

So standby nodes are not needed for throughput or storage. Why add them at all?

Because the primary can crash.

Hardware fails. Power supplies die. Network partitions isolate a node. OS panics happen. If the primary goes down and there is no standby, both pasteData and viewData are dead — writes fail because there's no primary to write to, and reads fail because there's no DB to query.

Standby nodes are an availability mechanism. They sit idle under normal operations, continuously replicating from the primary, ready to take over if the primary fails.

---

## How replication works

Postgres supports **synchronous streaming replication**. Every write committed on the primary is immediately streamed to standby nodes before the commit is acknowledged to the application.

```
Write flow with standbys:
  1. App server sends INSERT/UPDATE to primary
  2. Primary writes to its WAL (write-ahead log)
  3. Primary streams WAL entry to standby nodes
  4. Standby nodes acknowledge receipt
  5. Primary acknowledges commit to app server
```

Because standbys confirm receipt before the commit is acknowledged, they are always at most one commit behind the primary. In practice, with fast network links in the same data centre, standby lag is sub-millisecond.

This means if the primary crashes at any point after step 5, the standby has all committed data. **No committed write is lost in a failover.**

---

## Failover — leader election via etcd

When the primary goes down, one standby must be promoted to primary. This is the leader election problem.

etcd is a distributed key-value store built specifically for coordination and leader election. It uses the Raft consensus algorithm to maintain agreement across nodes even when some are unreachable.

The failover sequence:

```
1. Primary crashes or becomes unreachable
2. Health checks fail — LB and etcd detect primary is down
3. etcd runs leader election among standby nodes
4. Standby with the most up-to-date WAL position wins election
5. Winner is promoted to primary
6. etcd updates the service registry — new primary's address is published
7. pasteData and viewData re-resolve the primary address and reconnect
8. Traffic resumes on the new primary
```

The whole sequence typically takes **10–30 seconds** in a well-configured setup. During this window, writes fail (no primary to accept them) but reads from Redis cache continue uninterrupted — another reason the cache matters beyond latency.

---

## How many standbys?

Two standbys is the standard configuration:

```
Primary  ← handles all reads and writes
Standby 1 ← synchronous replica, first failover candidate
Standby 2 ← synchronous replica, second failover candidate (if Standby 1 also fails)
```

Two standbys gives you one failover with a spare. If both standbys fail simultaneously with the primary, you have a data loss scenario — but three independent simultaneous hardware failures in the same data centre is extremely unlikely and typically requires a multi-region setup to protect against.

---

> [!tip] Interview framing
> "Standby nodes are about availability, not throughput — the primary handles all our traffic comfortably. Two synchronous standbys continuously replicate from the primary via WAL streaming. If the primary crashes, etcd runs leader election among standbys — the node with the most up-to-date WAL wins and is promoted. Failover takes 10–30 seconds. During that window, reads still work from Redis cache. No committed write is lost because synchronous replication means standbys confirm receipt before the commit is acknowledged."
