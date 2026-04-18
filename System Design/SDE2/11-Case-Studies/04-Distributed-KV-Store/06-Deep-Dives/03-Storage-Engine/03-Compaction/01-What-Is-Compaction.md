
SSTables keep accumulating on disk. Every time the memtable fills up and flushes, a new SSTable is created. After days of operation, there could be hundreds of SSTables. This causes two problems:

1. **Read amplification** — a read that misses the memtable has to check every SSTable (newest to oldest) until it finds the key. If the key doesn't exist at all, it checks every single one. More SSTables = more disk reads per query.

2. **Wasted space** — the same key can exist in multiple SSTables (an older value in SSTable-1, a newer value in SSTable-5). The old value is stale and useless, but it's still taking up space on disk.

Compaction solves both: merge multiple SSTables into fewer, larger ones, keeping only the latest value for each key.

---

## How Compaction Works — Merge Sort on Sorted Files

Each SSTable is already sorted (it was flushed from a sorted memtable). Merging sorted files is a well-known problem — the **two-pointer merge** technique from merge sort. Walk through both files in order, compare the current entry from each, write the smaller one to the output. When a key appears in both files, compare timestamps and keep only the newer value.

```
SSTable-1: ["a:1", "c:3(ts=100)", "f:6(ts=100)", "z:26"]
SSTable-2: ["b:2", "c:5(ts=200)", "d:4", "f:7(ts=50)"]

Merge with two pointers:
  "a:1"           ← only in SSTable-1
  "b:2"           ← only in SSTable-2
  "c" → ts 200 > 100 → keep "c:5", discard "c:3"
  "d:4"           ← only in SSTable-2
  "f" → ts 100 > 50  → keep "f:6", discard "f:7"
  "z:26"          ← only in SSTable-1

Result: ["a:1", "b:2", "c:5", "d:4", "f:6", "z:26"]
```

The critical thing: this is **not sorting on disk**. We avoided sorting on disk in the first place because it's O(n log n) with random I/O. Compaction is **merging already-sorted files** — O(n) with purely sequential reads from both inputs and one sequential write for the output. The data was sorted for free in memory by the memtable — compaction just preserves that sorted order while combining files.

```
Sorting on disk:       O(n log n), random I/O     ← what we avoided
Merging sorted files:  O(n), sequential I/O only   ← what compaction does
```

---

## Reads During Compaction

Compaction runs in the **background** as a separate process. It doesn't block reads or writes. The old SSTables stay on disk and keep serving reads while the new merged SSTable is being written. Once the merge is fully complete, the system atomically swaps — the new SSTable becomes active, the old ones are deleted.

```
Before compaction:
  SSTable-1, SSTable-2, SSTable-3  ← all serving reads

During compaction (merging SSTable-1 and SSTable-2):
  SSTable-1, SSTable-2, SSTable-3  ← still serving reads
  SSTable-new (being written)      ← not visible to reads yet

After compaction completes:
  SSTable-new, SSTable-3           ← atomic swap, old files deleted
```

At no point does a read see a half-written SSTable or miss data. The transition is seamless.

---

## The Indirect Cost — Compaction Competes for Disk I/O

Compaction doesn't directly affect writes (writes go to WAL + memtable, not SSTables). But it **indirectly** affects the whole system because it consumes disk I/O and CPU in the background. The merge reads two SSTables sequentially and writes one new SSTable — that's disk bandwidth being used by a background process instead of serving client reads or flushing new memtables.

The key design question becomes: **when** do you compact, and **which** SSTables do you merge together? Compact too aggressively and you waste disk I/O on constant merging. Compact too lazily and SSTables pile up, making reads slower. The two main strategies for balancing this trade-off — size-tiered compaction and leveled compaction — are covered next.
