# Log-Structured Merge Tree — Write Path

You're building a system that tracks every location ping from Uber drivers. 1 million drivers, each sending GPS coordinates every 5 seconds. That's 200,000 writes per second, constantly, forever.

With a B+ Tree index, every single write must go to the **exact right position** in the tree to keep it sorted:

```
New ping arrives → find correct leaf node → insert in sorted position
                → maybe split → update parent → maybe split again
```

That correct leaf node could be **anywhere on disk**. Every write is a **random disk I/O** — jumping to a different location on disk each time.

And this isn't just a write problem. The B+ Tree itself — every node, every pointer, every level — is **stored on disk**. The tree is too large to keep in memory. A table with 100 million rows has a tree 27 levels deep. To find a single row, you start at the root and walk down level by level:

```
Root node        → disk read 1   (random)
  Child node     → disk read 2   (random, somewhere else on disk)
    Grandchild   → disk read 3   (random)
      ...
        Leaf     → disk read 27  (random) → row pointer found
          Actual row → disk read 28 (random) → data returned
```

27 random disk reads just to traverse the tree, then one more to fetch the actual row. Each read is a jump to a completely different location on disk. That's what "random I/O" means — not one sequential scan, but dozens of scattered jumps per query.

That "one more read" to fetch the actual row happens because B+ Tree leaf nodes store **row pointers**, not the row itself. The pointer says "this row lives at block 4821, offset 12." The actual row — all the columns, all the data — lives in a separate file called the **heap file**. Two separate things on disk:

```
Disk
└── database_files/
    ├── users.index   ← B+ Tree lives here (pointers only)
    └── users.heap    ← heap file lives here (actual rows, unsorted)
```

The heap file is just a flat file where rows are written one after another as they arrived — no sorting, no structure. Think of it like a notebook where every new row just gets added to the next page in order of arrival. The B+ Tree is the organized index on top of this messy notebook — it tells you exactly which page to jump to.

LSM Tree works differently. The SSTables store the **actual data directly** — there is no separate heap file. The SSTable IS the data. So LSM Tree is more of a storage engine than a pure index — data and index merged into one structure.

Random disk I/O is slow. Even on SSDs, random writes are significantly slower than sequential writes. At 200,000 writes per second, you're doing 200,000 random disk jumps per second. That's the bottleneck.

The opposite of random writes is **sequential writes** — writing to disk one after another in order, no jumping around. Sequential writes are dramatically faster — on SSDs, up to 10x. On spinning disks, the difference is even more extreme.

The question: can you design an index where **every write is sequential**, no matter what key you're inserting? That's exactly what LSM Tree does.

---

## The Core Idea — Write to Memory First

Instead of writing to disk immediately, every write first goes into **memory**. Fast, no disk I/O. You only flush to disk periodically in one big sequential batch.

```
200,000 writes/sec → all go to memory first
                   → accumulate
                   → flush to disk in one sequential write
                   → repeat
```

But memory is volatile — a power cut loses everything.

---

## Step 1 — WAL (Write-Ahead Log) for Durability

Before going into memory, every write is **appended to a log file on disk**. Appending is always sequential — you never jump around, you just add to the end.

```
Write arrives:
→ Step 1: append to WAL on disk   ← sequential write, very fast, durable
→ Step 2: insert into MemTable    ← memory, instant
→ done ✓
```

Power cuts:
```
Memory lost   ✗
WAL on disk   ✓ → on restart, replay WAL → memory restored ✓
```

Durability without random I/O. This is the **Log-Structured** part of the name.

---

## Step 2 — MemTable (In-Memory Buffer)

The **MemTable** is the in-memory data structure that holds all incoming writes. It keeps entries sorted in memory — sorting in memory is cheap, no disk involved.

```
Writes accumulating in MemTable:
  ping: driver_99,  13:00:05
  ping: driver_1,   13:00:03
  ping: driver_450, 13:00:04
```

When the MemTable fills up, it's time to flush to disk.

---

## Step 3 — SSTable (Sorted String Table)

When the MemTable is full, sort it and flush the entire thing to disk in one sequential write. This creates an **SSTable** — an immutable, sorted file on disk.

The sorting is always by **key** — whatever you define as the key for this table. In the Uber example, the key is `driver_id`, so the SSTable is sorted by driver_id. The timestamp is just part of the value being stored alongside it. If your key were `email`, the SSTable would sort by email instead:

```
SSTable (email as key):
  john@gmail.com  → { name: John, age: 28 }
  mike@gmail.com  → { name: Mike, age: 25 }
  sara@gmail.com  → { name: Sara, age: 31 }
```

Because each SSTable is sorted by key, you don't need to scan the whole file to find an entry — you can binary search it, O(log n), just like B+ Tree.

```
Sort MemTable → flush to disk as one sequential write:

SSTable 1:
  driver_1,   13:00:03  → location A
  driver_1,   13:00:05  → location B
  driver_450, 13:00:04  → location X
  driver_99,  13:00:05  → location Y

→ clear MemTable → start filling again
```

One big sequential write. No random I/O. Fast.

Over time, multiple SSTables accumulate:

```
SSTable 1: driver_1→A, driver_1→B, driver_450→X
SSTable 2: driver_1→C, driver_2→Z           ← driver_1 appears again
SSTable 3: driver_1→D, driver_99→Y          ← and again
```

Driver_1 is sending pings every 5 seconds. Each MemTable flush captures whatever writes happened during that window — so driver_1's data ends up spread across multiple SSTables over time.