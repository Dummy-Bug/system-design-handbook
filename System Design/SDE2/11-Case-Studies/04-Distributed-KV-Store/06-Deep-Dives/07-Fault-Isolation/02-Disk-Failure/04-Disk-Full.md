## Disk Full — Can Read but Can't Write

The disk runs out of space. The node is alive, the network is fine, the CPU is fine — but there's no room to write anything new. This creates a "half alive" node that can serve reads but fails on writes.

### What breaks when the disk is full

```
WAL append       → fails → new writes rejected on this node
Memtable flush   → fails → memtable stuck in memory, can't accept more writes
Compaction       → fails → SSTables pile up → reads get slower
TTL cleanup      → fails → expired data can't be removed → disk stays full

Reads            → still work (existing SSTables are intact and readable)
Gossip           → still works (node appears "alive" to the cluster)
```

The node looks healthy to the cluster — it responds to pings, participates in gossip, serves reads. But every write that routes to it fails. This is worse than a dead node in some ways — a dead node triggers hinted handoff immediately, but a "half alive" node might accept the request and then fail partway through.

### What happens to writes

The coordinator sends a write to Node B, Node C, and Node D (N=3). Node D's disk is full — WAL append fails:

```
Coordinator sends write to 3 nodes:
  Node B: WAL append ✓ → memtable insert ✓ → ack ✓
  Node C: WAL append ✓ → memtable insert ✓ → ack ✓
  Node D: WAL append ✗ → disk full → nack ✗

  W=2 satisfied by Node B and Node C → write succeeds
  Node D missed the write → same as a node failure for this key
```

Quorum saves us — the write succeeds as long as W=2 nodes have space. Node D's missed write will be caught later by read repair or anti-entropy, same as any other failure.

### The compaction death spiral

The real danger of a full disk isn't individual write failures — it's the **compaction death spiral**:

```
Disk full → compaction can't run
  → SSTables pile up (no merging)
  → Expired data and tombstones can't be cleaned up
  → Disk stays full even though much of the data is logically dead
  → More SSTables = more files to check per read = reads get slower
  → System degrades further
```

Compaction is what reclaims disk space — it merges SSTables, drops expired entries, removes old tombstones. When compaction can't run, dead data stays on disk permanently, which keeps the disk full, which prevents compaction from running. A vicious cycle.

### Prevention — monitoring and reserved space

This failure is **preventable**. Unlike node crashes or bit flips, disk fullness is gradual and predictable:

```
Prevention strategies:
  → Monitor disk usage — alert at 80%, critical at 90%
  → Reserve disk space for compaction (10-15% of total disk)
     → Compaction can always run even when the disk is "full" from the
        application's perspective
  → Rate limit incoming writes when disk usage exceeds threshold
     → Node starts rejecting writes early, before truly full
     → Coordinator routes to other nodes (same as node failure)
```

The reserved space for compaction is critical. If compaction can always run, it can clean up expired data and tombstones, freeing space naturally. The death spiral only happens when compaction itself is blocked.

> [!tip] Interview framing
> "Disk full is a gradual failure — unlike a crash, it's predictable and preventable. The node can still serve reads but fails on writes. Quorum handles missed writes the same way it handles any node failure. The real danger is the compaction death spiral — if compaction can't run, expired data and tombstones can't be cleaned up, so the disk stays full. We prevent this by reserving 10-15% of disk space specifically for compaction, monitoring disk usage with alerts at 80%, and rate-limiting writes when the threshold is exceeded."
