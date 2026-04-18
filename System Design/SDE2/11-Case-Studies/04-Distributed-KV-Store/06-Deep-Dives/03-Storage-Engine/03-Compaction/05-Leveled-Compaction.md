## Leveled Compaction — The Core Rule

Leveled compaction introduces one strict rule that size-tiered doesn't have: **within a level (except Level 0), key ranges never overlap.** Each key exists in exactly one SSTable per level.

```
Level 0: [a-z] [a-z] [a-z]        ← fresh memtable flushes, ranges CAN overlap
Level 1: [a-f] [g-m] [n-z]        ← no overlap — each key in exactly one SSTable
Level 2: [a-c] [d-f] [g-i] ...    ← no overlap, ~10x more data than Level 1
Level 3: [a-b] [c-d] [e-f] ...    ← no overlap, ~10x more data than Level 2
```

Level 0 is the exception — it receives raw memtable flushes, which cover whatever key ranges happened to arrive. But from Level 1 onward, the no-overlap rule is enforced strictly.

---

## How the No-Overlap Rule Helps Reads

In size-tiered compaction, SSTables within a tier have overlapping key ranges. A read for `"user:123"` might need to binary search **all** SSTables in a tier because any of them could contain it.

Leveled compaction eliminates this entirely. Since key ranges don't overlap within a level, a read checks exactly **one** SSTable per level — the one whose range includes the target key.

```
Level 1: [a-f] [g-m] [n-z]

Looking for "user:123" → starts with "u" → falls in [n-z]
  → only check [n-z] SSTable
  → skip [a-f] and [g-m] entirely — they cannot contain "user:123"

Size-tiered: check ALL SSTables in the tier (ranges overlap)
Leveled:     check exactly ONE SSTable per level (no overlap)
```

If there are 4 levels, a read checks at most 4 SSTables (one per level) — regardless of how many SSTables exist in total. Compare that to size-tiered where you might check multiple SSTables per tier.

---

## How the No-Overlap Rule Is Maintained — The Write Cost

Maintaining no-overlap requires more compaction work. When a fresh SSTable flushes from the memtable into Level 0 and needs to be pushed into Level 1, it can't just be dropped in — it might overlap with existing Level 1 SSTables. So it has to be **merged with every Level 1 SSTable whose range overlaps**, and the results are rewritten with new non-overlapping boundaries.

```
Level 0 flush: [d-k]
Level 1 before: [a-f] [g-m] [n-z]

[d-k] overlaps with [a-f] and [g-m]
  → merge all three together → rewrite Level 1

Level 1 after: [a-e] [f-k] [l-m] [n-z]   ← ranges redrawn, no overlaps
```

One small flush from Level 0 caused **two** SSTables in Level 1 to be read and rewritten. And the same cascading happens when Level 1 gets too big and pushes data into Level 2, and Level 2 into Level 3.

This is all **disk I/O** — reading existing SSTables, merging them, writing new ones. The CPU work (comparing keys, picking newer timestamps) is trivial. The bottleneck is disk bandwidth consumed by rewriting SSTables over and over to maintain the no-overlap invariant.

The same key can get rewritten every time it moves through a level — Level 0 → 1 → 2 → 3. Across its lifetime, a key might be rewritten **10-30 times**, compared to 4-5 times in size-tiered compaction.

---

## The Trade-off — More Compaction Work for Faster Reads

Leveled compaction does more background I/O (higher write amplification) in exchange for faster reads (lower read amplification):

```
                     Size-tiered          Leveled
                     ───────────          ───────
Write amplification   ~4-5x               ~10-30x
Read cost per level   Multiple SSTables   Exactly 1 SSTable
Background I/O        Lower               Higher
Best for              Write-heavy          Read-heavy
```

The extra compaction work is a **write cost** — it consumes disk bandwidth in the background. But the payoff is that reads become faster because there are fewer SSTables to check and no overlapping ranges to deal with.

```
Size-tiered:
  Less compaction work  → SSTables pile up with overlapping ranges → slower reads

Leveled:
  More compaction work  → clean, non-overlapping levels           → faster reads
```

---

## What Real Systems Use

```
Cassandra:  size-tiered (default) — write-optimized
RocksDB:    leveled (default)     — balanced
DynamoDB:   proprietary hybrid    — not publicly disclosed
```

Cassandra defaults to size-tiered because most Cassandra workloads are write-heavy (logging, time-series, IoT). It does offer leveled as a configurable option per table, but size-tiered is the default.

RocksDB (used internally by many systems) defaults to leveled because it targets a balance of reads and writes.

DynamoDB uses a custom LSM-based engine — AWS doesn't publicly disclose the exact strategy, but it's believed to be a hybrid approach.

Some systems let you **configure the strategy per table** — write-heavy tables use size-tiered, read-heavy tables use leveled. For a general-purpose KV store like ours, this flexibility is valuable since different services will have different read/write ratios.

> [!tip] Interview framing
> "Leveled compaction organises SSTables into levels where key ranges don't overlap within a level. A read checks exactly one SSTable per level — you know which one because ranges don't overlap. The cost is higher write amplification: pushing data from one level to the next requires merging with every overlapping SSTable in the target level, so the same key might be rewritten 10-30 times across its lifetime. Size-tiered is better for write-heavy workloads (less rewriting), leveled is better for read-heavy workloads (fewer SSTables to check per read). Cassandra defaults to size-tiered, RocksDB defaults to leveled."
