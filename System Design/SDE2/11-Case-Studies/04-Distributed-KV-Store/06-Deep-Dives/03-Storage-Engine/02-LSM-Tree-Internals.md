## The Core Problem — Fast Writes vs Fast Reads

A write arrives at Node B: `put("user:123", "Alice")`. The node needs to persist this to disk so it survives a crash. The simplest possible approach: open a file, find where `"user:123"` should go in sorted order, shift everything after it, and write it there. This is a **random write** — the disk has to seek to the correct position.

But there's a much faster option: **just append it to the end of the file.** No seeking, no shifting — the disk head (or SSD controller) goes to the end and writes. This is a **sequential write**, and it's dramatically faster:

```
Sequential writes on SSD:  500 MB/s - 3 GB/s
Random writes on SSD:      50 MB/s - 500 MB/s

Sequential writes on HDD:  100 - 200 MB/s
Random writes on HDD:      0.5 - 2 MB/s (100x slower!)
```

So we choose append-only. Every write goes to the end of the file. Fast. Simple. Done.

---

## The Read Problem — Append-Only Files Are Unsorted

After a million writes, the append-only file looks like this:

```
Line 1:        put("user:001", "Alice")
Line 2:        put("user:500", "Bob")
Line 3:        put("user:123", "Charlie")
Line 4:        put("user:001", "Dave")      ← updated user:001
Line 5:        put("user:999", "Eve")
...
Line 1,000,000: put("user:042", "Zara")
```

Now a read comes in: `get("user:123")`. Where is it? Could be anywhere. The file is in **insertion order**, not sorted order. To find it, you'd have to scan the entire file from end to start — O(n). At a million entries, that's a million comparisons per read. Completely impractical.

### Why not keep a pointer index in memory?

One idea: maintain an in-memory hash map that maps every key to its byte offset in the file. Write comes in → append to file → record the offset in the hash map. Read comes in → look up the offset → seek directly to it.

This actually works — it's how **Bitcask** (Riak's storage engine) operates. But the cost is steep: you need to hold **every key's position in memory**. At our scale, each node holds data for multiple shards — potentially hundreds of millions of keys. That index alone could eat up all your RAM. We need a better approach.

### Why not sort the file?

If the file were sorted, we could binary search and find any key in O(log n). For a billion keys, that's ~30 comparisons instead of a billion. But sorting means rearranging the file on disk every time a new write comes in — and that kills the fast sequential writes we just chose.

```
Fast writes  → append to end    → file is unsorted → reads are O(n)

Fast reads   → keep file sorted → every write rearranges data → writes are slow
```

We want both. Fast writes AND fast reads. These seem fundamentally at odds — you can't append (which is unordered) and also maintain a sorted file on disk.

---

## The Memtable — Batching Writes in Memory

The insight: **don't write to disk immediately.** Instead, batch writes in memory first.

Every write goes into an in-memory sorted data structure — usually a red-black tree or a skip list. Inserting into a sorted in-memory structure is O(log n), which is extremely fast (no disk involved at all). This in-memory sorted buffer is called a **memtable**.

```
Write arrives: put("user:123", "Alice")
  → Insert into memtable (in-memory, sorted)
  → Acknowledge to client. Done.

Next write: put("user:001", "Bob")
  → Insert into memtable (in-memory, sorted)

Next write: put("user:500", "Charlie")
  → Insert into memtable (in-memory, sorted)

Memtable now (automatically sorted):
  "user:001" → "Bob"
  "user:123" → "Alice"
  "user:500" → "Charlie"
```

The memtable gives us both properties we wanted:
- **Writes are fast** — inserting into an in-memory tree is O(log n), no disk I/O at all
- **Data is sorted** — the tree maintains sorted order automatically, so when we eventually write it to disk, we get a sorted file for free

---

## The Crash Problem — Write-Ahead Log (WAL)

The memtable is in memory. If the node crashes, everything in the memtable vanishes — all recent writes lost. We need durability before we even touch the memtable.

The fix: before inserting into the memtable, first **append the write to a Write-Ahead Log (WAL)** on disk. The WAL is a simple append-only file — sequential writes, so it's fast. No sorting, no structure, just a raw log of every write in the order it arrived.

```
Write arrives: put("user:123", "Alice")
  Step 1: Append to WAL on disk (sequential write — fast)
  Step 2: Insert into memtable (in-memory — fast)
  Step 3: Ack to client
```

If the node crashes, the memtable is gone — but the WAL is still on disk. On restart, the node replays the WAL entry by entry, re-inserting each write into a fresh memtable. The memtable is rebuilt exactly as it was before the crash. No data lost.

The WAL exists purely for crash recovery. It's never read during normal operation — only on restart after a failure.

---

## Flushing to Disk — SSTables

The memtable can't grow forever — it's in memory, and memory is limited. So when the memtable hits a size threshold (typically 32 MB or 64 MB), it gets **flushed to disk** as a sorted file.

Since the memtable is already sorted (it's a red-black tree or skip list), the flush is just writing entries out in order — one big sequential write. No random I/O, no sorting step needed. The resulting sorted file on disk is called an **SSTable** (Sorted String Table).

```
Memtable (32 MB, sorted, in memory):
  "user:001" → "Bob"
  "user:050" → "Eve"
  "user:123" → "Alice"
  "user:500" → "Charlie"
  "user:999" → "Zara"

  ↓ flush (one sequential write)

SSTable on disk (sorted file):
  "user:001" → "Bob"
  "user:050" → "Eve"
  "user:123" → "Alice"
  "user:500" → "Charlie"
  "user:999" → "Zara"
```

Once the flush is complete, two things happen:
1. The old WAL is **deleted** — the data is now safely on disk in the SSTable, so the WAL is no longer needed for crash recovery
2. A fresh empty memtable and a new WAL are created for incoming writes

This keeps happening. Every time the memtable fills up, it flushes to a **new** SSTable. Over time, multiple SSTables accumulate on disk:

```
SSTable-1 (oldest)
SSTable-2
SSTable-3
SSTable-4 (newest)
+ current memtable (in memory, not yet flushed)
```

Each SSTable is individually sorted, immutable (never modified after creation), and represents a snapshot of whatever was in the memtable at the time of that flush.

---

## The Read Path — Newest to Oldest

A read comes in: `get("user:123")`. The node checks from newest to oldest, because the most recent write for a key is the correct value — an older SSTable might have a stale version of the same key.

```
get("user:123"):
  1. Check memtable           → not found
  2. Check SSTable-4 (newest) → not found
  3. Check SSTable-3          → not found
  4. Check SSTable-2          → FOUND! Return it.
     (stop here — no need to check SSTable-1)
```

Each SSTable is sorted, so the lookup within a single SSTable is a binary search — O(log n). That's fast for one SSTable.

But there's a growing problem. What if the key **doesn't exist at all**? The node has to check the memtable and then every single SSTable on disk before it can confidently say "not found." If there are 100 SSTables, that's 100 binary searches, each potentially hitting disk.

And SSTables keep accumulating — every memtable flush creates a new one. After running for days, there could be hundreds of SSTables. Reads get progressively slower over time:

```
Day 1:    5 SSTables   → max 5 binary searches per read
Day 10:   50 SSTables  → max 50 binary searches per read
Day 100:  500 SSTables → max 500 binary searches per read
```

This is the **read amplification** problem of LSM Trees — a single logical read can turn into many physical disk reads. The more SSTables pile up, the worse it gets.
