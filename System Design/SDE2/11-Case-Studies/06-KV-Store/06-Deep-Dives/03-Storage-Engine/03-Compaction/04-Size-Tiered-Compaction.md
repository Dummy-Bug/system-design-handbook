
The idea is simple: group SSTables by size. When you accumulate enough SSTables of roughly the same size (typically 4), merge them into one bigger SSTable.

```
4 × 32 MB SSTables   → merge → 1 × 128 MB SSTable
4 × 128 MB SSTables  → merge → 1 × 512 MB SSTable
4 × 512 MB SSTables  → merge → 1 × 2 GB SSTable
```

Fresh memtable flushes produce small SSTables (~32 MB each). When 4 of them accumulate, they merge into a ~128 MB SSTable. When 4 of those accumulate, they merge into a ~512 MB SSTable. And so on. SSTables naturally grow through tiers over time.

Each time an SSTable participates in a merge, the old SSTables are deleted — you're not endlessly duplicating data. A key gets rewritten once per tier it passes through (roughly 4-5 times total across its lifetime).

---

## What the Tiers Look Like at Any Point in Time

At any moment, you might have SSTables at various tiers, waiting for enough to accumulate to trigger the next merge:

```
Tier 0: [32MB] [32MB] [32MB]      ← 3 fresh flushes, waiting for 4th to trigger merge
Tier 1: [128MB] [128MB]           ← 2 merged SSTables, waiting for more
Tier 2: [512MB]                   ← 1 large SSTable
```

---

## The Read Path in Size-Tiered Compaction

A read checks from newest to oldest — memtable first, then the newest tier, then older tiers. The moment you find the key, you stop. If it's in Tier 0, that's guaranteed to be the latest value because newer writes always land in newer tiers.

```
get("user:123"):
  1. Check memtable        → not found
  2. Check Tier 0 SSTables → not found
  3. Check Tier 1 SSTables → FOUND! Return it.
     (stop here — this is the latest value for this key)
```

If a newer version of the key existed, it would be in a newer tier. So the first tier where you find the key is always correct.

---

## The Read Problem — Overlapping Key Ranges Within a Tier

The problem isn't across tiers — it's **within** a tier. Each SSTable in a tier was flushed from a separate memtable at a different point in time. They each cover whatever keys happened to arrive during that memtable's lifetime, which means their key ranges overlap:

```
Tier 1:
  SSTable-A [128MB]: contains keys from "aardvark" to "zebra"
  SSTable-B [128MB]: contains keys from "apple" to "zoo"
  SSTable-C [128MB]: contains keys from "banana" to "yak"
```

All three cover most of the key space. When you're looking for `"user:123"` in Tier 1, it could be in any of these three SSTables — their ranges all include it. You can't skip any of them. You have to binary search **all three** before you can conclude whether the key is in this tier or not.

```
Looking for "user:123" in Tier 1:
  Binary search SSTable-A → not found
  Binary search SSTable-B → not found
  Binary search SSTable-C → FOUND!
  
  Had to check all 3 SSTables before finding it (or before concluding "not in this tier")
```

If a tier has 4 SSTables with overlapping ranges, that's 4 binary searches. This is manageable at small tiers, but it adds up — especially for keys that don't exist at all, where you have to check every SSTable in every tier before returning "not found."

---

## Why Size-Tiered Is Good for Write-Heavy Workloads

Despite the read cost, size-tiered compaction has a significant advantage: **low write amplification**. A key only gets rewritten when its SSTable participates in a merge, which happens once per tier — roughly 4-5 times total across its lifetime. Compaction triggers less frequently (only when enough same-size SSTables accumulate), so less background disk I/O is consumed by merging.

Less background I/O means more disk bandwidth available for WAL writes and memtable flushes — exactly what a write-heavy workload needs.

```
Size-tiered compaction:
  ✓ Low write amplification (data rewritten ~4-5 times)
  ✓ Less background disk I/O from compaction
  ✗ Overlapping key ranges within tiers → more SSTables to check per read
  Best for: write-heavy workloads
```

> [!tip] Interview framing
> "Size-tiered compaction groups SSTables by size and merges them when enough accumulate at the same tier. It's great for write-heavy workloads because write amplification is low — a key only gets rewritten once per tier. The trade-off is read performance: within each tier, SSTables have overlapping key ranges, so a read might have to check multiple SSTables per tier before finding the key or confirming it doesn't exist."
