
## Reading — Search Newest to Oldest

SSTables are created in order — SSTable 1 is older, SSTable 3 is newest. For a read, search from newest to oldest and return the first match:

```
Query: "where is driver_1 right now?"

Step 1 → check MemTable first  (most recent, still in memory)
Step 2 → check SSTable 3       (most recent flush)
Step 3 → check SSTable 2
Step 4 → check SSTable 1       (oldest)
→ stop as soon as you find it ✓
```

This works well for "latest value" queries. But if you need driver_1's full route for the day — all entries across all SSTables — you have to scan every file. That's expensive. **LSM Tree is optimised for writes and recent reads, not full historical scans**.

---

## Why LSM Reads Are Slower Than B+ Tree

With B+ Tree you search one structure and you're done. With LSM Tree, in the worst case the key lives in the oldest SSTable — so you've searched every SSTable before finding it:

```
B+ Tree read:
  → binary search 1 tree   → found ✓   → O(log n)

LSM Tree read (worst case):
  → search MemTable         → not found
  → search SSTable 3        → not found
  → search SSTable 2        → not found
  → search SSTable 1        → found ✓

Each SSTable is O(log n). With 10 SSTables → 10 × O(log n).
```

Compaction reduces the number of SSTables over time, which directly improves read speed — fewer files to search through.

---

## Compaction (The "Merge Tree" Part)

Over time, hundreds of SSTables accumulate on disk. Searching through 100 files for every read is slow. The fix — **Compaction**.

Periodically in the background, the database merges multiple SSTables into one bigger sorted SSTable:

```
Before compaction:
  SSTable 1: driver_1→A, driver_1→B, driver_450→X
  SSTable 2: driver_1→C, driver_2→Z
  SSTable 3: driver_1→D, driver_99→Y

After compaction:
  SSTable merged: driver_1→D, driver_2→Z, driver_450→X, driver_99→Y
                  (only latest entry per key kept, duplicates removed)
```

Two benefits:
```
1. Fewer SSTables   → fewer places to search on reads
2. Duplicates gone  → driver_1 had entries in 3 files, now just 1 (the latest)
```

Compaction runs in the background — it doesn't block reads or writes.

---

## The Full Picture

```mermaid
graph LR
    W["Write arrives"] -->|"1 - durability first"| WAL["WAL on disk Sequential append"]
    WAL -->|"2 - then into memory"| MT["MemTable In memory Sorted"]
    MT -->|"3 - MemTable full"| SST["SSTable on disk Sequential write Immutable"]
    SST -->|"4 - many accumulate"| C["Compaction Merge + deduplicate Background"]
    C -->|"5 - result"| SST2["Fewer larger SSTables"]

    style W fill:#dbeafe,stroke:#3b82f6,color:#000
    style WAL fill:#dcfce7,stroke:#16a34a,color:#000
    style MT fill:#fef08a,stroke:#ca8a04,color:#000
    style SST fill:#dcfce7,stroke:#16a34a,color:#000
    style C fill:#f3e8ff,stroke:#9333ea,color:#000
    style SST2 fill:#dcfce7,stroke:#16a34a,color:#000
```

```
Write path:
  write → WAL (durability, sequential) → MemTable (memory) → SSTable (disk, sequential)

Read path:
  MemTable → newest SSTable → older SSTables → stop at first match

Background:
  Compaction → merge SSTables → fewer files, remove duplicates
```

The name explains the structure:
```
Log-Structured  → WAL, append-only sequential writes
Merge Tree      → compaction merges SSTables periodically
```

---

## LSM Tree vs B+ Tree vs Hash Index

```
Hash Index  → O(1) exact lookups, no range queries
              use when: simple key-value lookups only

B+ Tree     → O(log n) lookups + range queries
              random disk I/O on writes
              use when: general purpose — default in all SQL databases

LSM Tree    → sequential writes, extremely high write throughput
              slower reads (check MemTable + multiple SSTables)
              use when: write-heavy workloads
```

> [!info] LSM Tree is used in **Cassandra, RocksDB, LevelDB, HBase** — any system with extreme write throughput requirements. Cassandra uses it specifically because write throughput is more important than read speed for time-series and event data.

> [!important] LSM Tree trades read performance for write performance. Reads must check multiple SSTables. Compaction helps but adds background I/O. It's the right choice when writes vastly outnumber reads and write latency is the bottleneck — not when you need fast complex queries.
