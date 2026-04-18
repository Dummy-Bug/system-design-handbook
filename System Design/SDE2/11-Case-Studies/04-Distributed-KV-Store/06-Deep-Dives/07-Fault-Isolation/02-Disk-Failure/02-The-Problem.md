## What Is a Disk Failure?

A disk failure is when the physical storage device on a node stops working correctly. It comes in three flavors, each with very different levels of danger:

### 1. Total disk death — the disk stops responding

The disk is completely gone. The node can't read or write anything. The CPU and network are fine, but the node is useless for storage.

This is actually the **least dangerous** type. From the cluster's perspective, it's identical to a node failure — the node stops serving requests, gossip detects it as down, and the same three recovery layers kick in (hinted handoff → read repair → anti-entropy). We already handle this well.

### 2. Silent data corruption — the sneaky one

The disk is "working" but returns **wrong data**. A bit flips, a sector goes bad, and when the node reads an SSTable entry it gets garbage instead of the real value. The node has no idea anything is wrong — it happily serves corrupted data to clients.

This is the **most dangerous** type because the system doesn't know it's broken. A client reads `get("user:123")` and gets garbage bytes. No error, no alarm, no retry — just silently wrong data returned with full confidence.

```
Normal read:
  Read SSTable → "Alice" → return to client ✓

Corrupted read:
  Read SSTable → "Al\x00\xFFe" → return to client
  Node thinks everything is fine. Client gets garbage.
```

Unlike a dead node (which triggers hinted handoff and gossip detection), a node serving corrupted data looks perfectly healthy to the cluster. It responds to pings, it participates in gossip, it accepts writes — it just returns wrong values on reads.

### 3. Disk fills up — can't write, can still read

The disk runs out of space. The node can still read existing data from SSTables, but it can't write anything new. WAL appends fail, memtable flushes fail, compaction can't run.

This is dangerous because it's a slow death:
- New writes start failing on this node → quorum may still succeed on other replicas
- Compaction can't run → SSTables pile up → reads get slower (more SSTables to check)
- Expired data and tombstones can't be cleaned up → disk stays full even though data is logically dead

```
Disk at 100%:
  WAL append      → fails → new writes rejected
  Memtable flush  → fails → memtable stuck in memory, can't accept more writes
  Compaction      → fails → SSTables accumulate → reads degrade
  
  Meanwhile, reads still work (existing SSTables are fine)
  The node looks "half alive" — reads succeed, writes fail
```
