## The Problem — Wasted Reads on Non-Existent Keys

Even with the best compaction strategy, a read for a key that **doesn't exist** is expensive. The node checks the memtable, then one SSTable per level (in leveled compaction) or multiple SSTables per tier (in size-tiered). Every check is a binary search that potentially hits disk. If the key isn't anywhere, you've done all that disk I/O for nothing.

One idea: keep an index of all keys per SSTable in memory, so you can check if a key exists before opening the file. But that's the same problem we rejected earlier — hundreds of millions of keys per node, the index would consume too much RAM.

We need something that uses far less memory and can still tell us whether a key is in an SSTable or not.

---

## Bloom Filters — "Definitely Not Here" vs "Probably Here"

A Bloom filter is a **probabilistic data structure** that answers one question: "Is this key in this SSTable?" It gives two possible answers:

- **"Definitely not here"** — guaranteed correct. Skip this SSTable, no disk read needed.
- **"Probably here"** — might be wrong (false positive), but worth checking with a disk read.

It never says "definitely here" — that's the trade-off for using so little memory. But "definitely not here" is the valuable answer, because it lets you skip entire SSTables without touching disk.

---

## How It Works — A Bit Array and Hash Functions

A Bloom filter is a bit array (all bits start at 0) plus a set of hash functions. When a key is written to an SSTable, it's also inserted into that SSTable's Bloom filter.

### Inserting keys

```
Bit array: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            0  1  2  3  4  5  6  7  8  9

Insert "user:001":
  hash1("user:001") = position 2  → set bit 2 to 1
  hash2("user:001") = position 7  → set bit 7 to 1

Bit array: [0, 0, 1, 0, 0, 0, 0, 1, 0, 0]
            0  1  2  3  4  5  6  7  8  9

Insert "user:002":
  hash1("user:002") = position 4  → set bit 4 to 1
  hash2("user:002") = position 2  → set bit 2 to 1  (already 1, no change)

Bit array: [0, 0, 1, 0, 1, 0, 0, 1, 0, 0]
            0  1  2  3  4  5  6  7  8  9
```

Each key sets a few bits in the array. Multiple keys can set the same bit — that's fine, bits just stay at 1.

---

## Lookups — True Negative vs False Positive

### True negative — key definitely not here

```
Lookup "user:888":
  hash1("user:888") = position 3  → bit is 0 ✗ → STOP

  At least one bit is 0 → "user:888" was DEFINITELY never inserted
  → Skip this SSTable entirely. No disk read. Saved.
```

If **any** of the required bits is 0, the key was never inserted. This is guaranteed — there's no way a bit could be 0 if the key had been inserted, because insertion always sets those bits to 1. This is the powerful case: one quick check in memory saves an entire disk read.

### False positive — bits set by other keys

```
Lookup "user:999" (never inserted):
  hash1("user:999") = position 4  → bit is 1 ✓  (set by "user:002")
  hash2("user:999") = position 7  → bit is 1 ✓  (set by "user:001")

  All bits are 1 → Bloom filter says "probably here"
  → Open the SSTable, binary search... key not found.
  → Wasted disk read. This is the FALSE POSITIVE.
```

Position 4 was set by `"user:002"`. Position 7 was set by `"user:001"`. Neither was set by `"user:999"` — but the Bloom filter can't tell the difference. It just sees that all the required bit positions are 1 and concludes the key might be there.

The key insight: **false positives are possible, but false negatives are not.** If the Bloom filter says "not here," it's 100% correct. If it says "probably here," it might be wrong — but you just do one wasted disk read and move on.

---

## Sizing — How to Keep False Positives Low

The false positive rate depends on three things:
1. **Size of the bit array** — more bits = fewer collisions = fewer false positives
2. **Number of hash functions** — more hash functions = more bits checked per lookup = more precise
3. **Number of keys inserted** — more keys = more bits set to 1 = higher chance of collision

The sweet spot: **10 bits per key with 7 hash functions** gives a false positive rate of roughly **1%**. That means 99% of "not here" lookups are caught and skipped without touching disk. Only 1% of the time does the filter say "probably here" when the key actually isn't — one wasted disk read out of 100 lookups.

The memory cost is tiny. For an SSTable with 10 million keys:

```
10 million keys × 10 bits per key = 100 million bits = ~12 MB
```

12 MB to represent 10 million keys — easily fits in memory. Compare that to storing all 10 million keys themselves, which could take hundreds of megabytes.

---

## Each SSTable Gets Its Own Bloom Filter

Every SSTable has its own Bloom filter, built when the SSTable is created (during memtable flush). The Bloom filter is stored alongside the SSTable on disk but loaded into memory when the node starts. Since each filter is small (~12 MB per SSTable), keeping all of them in memory is practical.

```
Read path with Bloom filters:

get("user:123"):
  1. Check memtable                          → not found
  2. SSTable-4 Bloom filter: "not here"      → SKIP (no disk read)
  3. SSTable-3 Bloom filter: "not here"      → SKIP (no disk read)
  4. SSTable-2 Bloom filter: "probably here"  → binary search SSTable-2 → FOUND!
```

Without Bloom filters, steps 2 and 3 would each be a disk read (binary search the SSTable). With Bloom filters, they're just a few bit checks in memory — essentially free.

The impact is biggest for **non-existent keys**. Without Bloom filters, confirming a key doesn't exist requires checking every SSTable. With Bloom filters, most SSTables are skipped instantly, and you only do a disk read on the rare false positive.

> [!tip] Interview framing
> "Each SSTable has a Bloom filter — a probabilistic bit array that answers 'is this key in this SSTable?' If it says 'not here,' that's guaranteed correct — skip the SSTable, no disk read. If it says 'probably here,' it might be a false positive, so we check the SSTable. At 10 bits per key, false positive rate is about 1%. The filter for 10 million keys is only ~12 MB, so all filters fit in memory. This is critical for non-existent key lookups — without Bloom filters, you'd have to binary search every SSTable before returning 'not found.'"
