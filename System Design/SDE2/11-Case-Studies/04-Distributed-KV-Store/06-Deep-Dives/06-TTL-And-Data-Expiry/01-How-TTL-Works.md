## The Problem — Auto-Deleting Data in an Immutable Storage Engine

In our FRs, we said users can set a TTL on a key: "delete this key automatically after 24 hours." The user doesn't call delete — the system handles it silently.

Simple enough in concept. But our storage engine is an LSM Tree, where data lives in the **memtable** (in memory) and **SSTables** (immutable files on disk). SSTables are never modified after creation. You can't open an SSTable and erase one entry — the whole file is frozen.

So two questions need answering:
1. How does the system know a key has expired?
2. How does the expired data actually get removed from disk?

---

## Storing the Expiry — Metadata Alongside the Entry

When a client writes a key with a TTL, the expiry time is calculated and stored as **metadata** alongside the key-value pair. It's not stored in some external system or a separate table — it lives right next to the data.

```
Client calls: put("session:abc", "token123", TTL=24h)

Current time: 1713400000 (Unix timestamp)
TTL: 24 hours = 86400 seconds

What gets written:
  Key:       "session:abc"
  Value:     "token123" (opaque bytes)
  Timestamp: 1713400000
  Expiry:    1713486400  (1713400000 + 86400)
```

This entry flows through the entire LSM Tree pipeline with its expiry field intact:

```
Write arrives
  → Append to WAL (key + value + timestamp + expiry)
  → Insert into memtable (key + value + timestamp + expiry)
  → Ack to client

Later, memtable flushes to SSTable:
  → SSTable entry: key + value + timestamp + expiry

The expiry field travels with the data everywhere it goes.
```

For keys without a TTL, the expiry field is simply empty or set to "never" — they live forever (or until explicitly deleted).

---

## Read-Time Check — Expired Keys Return "Not Found"

When a read comes in, the node finds the entry (memtable or SSTable) and checks the expiry field against the current time. If the key has expired, the node returns "not found" — as if the key doesn't exist. The data is still physically sitting on disk, but logically it's dead.

### Example — reading an expired session token

A session token was written with a 24-hour TTL. 25 hours later, someone reads it:

```
get("session:abc"):

  Step 1: Check memtable → not found
  Step 2: Bloom filter for SSTable-3 → "probably here"
  Step 3: Binary search SSTable-3 → FOUND!

    Key:       "session:abc"
    Value:     "token123"
    Timestamp: 1713400000
    Expiry:    1713486400

  Step 4: Check expiry
    Current time: 1713500000
    1713500000 > 1713486400 → EXPIRED

  Step 5: Return "not found" to client
```

The entry was found on disk, but the expiry check catches it. The client gets the same response as if the key never existed. No delete call was made, no tombstone was written — the expiry field alone is enough to make the key logically invisible.

### Example — reading a still-valid session token

Same key, but only 2 hours after it was written:

```
get("session:abc"):

  Step 1: Check memtable → not found
  Step 2: Bloom filter for SSTable-3 → "probably here"
  Step 3: Binary search SSTable-3 → FOUND!

    Key:       "session:abc"
    Value:     "token123"
    Timestamp: 1713400000
    Expiry:    1713486400

  Step 4: Check expiry
    Current time: 1713407200  (2 hours later)
    1713407200 < 1713486400 → NOT EXPIRED

  Step 5: Return "token123" to client
```

The only difference is the current time. Same data, same lookup path — the expiry check is just one extra comparison at the end.

---

## Disk Cleanup — Compaction Drops Expired Entries

The read-time check makes expired keys invisible to clients, but the data is still physically on disk taking up space. A 24-hour session token that expired a month ago is still sitting in an SSTable — wasting storage.

The cleanup happens during **compaction**. When the compaction process reads through SSTables and merges them, it checks the expiry field of every entry. If the expiry is in the past, the entry is simply **dropped** — not written to the new merged SSTable.

```
Compaction reads SSTable-2:

  "session:abc"  expiry=1713486400  → now > expiry → DROP (expired)
  "user:123"     expiry=none        → no TTL       → KEEP
  "session:def"  expiry=1713600000  → now < expiry → KEEP (still valid)
  "cache:xyz"    expiry=1713400000  → now > expiry → DROP (expired)

New SSTable after compaction:
  "user:123"     expiry=none
  "session:def"  expiry=1713600000
```

Two expired entries consumed disk space until compaction ran and cleaned them up. This is **lazy deletion** — expired keys aren't immediately removed, they're cleaned up whenever compaction gets around to processing their SSTable.

### How long does expired data sit on disk?

It depends on how frequently compaction runs and how many SSTables are involved. In the worst case, an expired entry in the oldest SSTable could sit on disk for days or weeks until compaction reaches it. This is a trade-off:

```
Aggressive compaction → expired data cleaned up quickly → more background I/O
Lazy compaction       → expired data lingers on disk   → less background I/O
```

For most use cases, this delay doesn't matter — the read-time check already makes expired keys invisible. The disk space is the only cost, and compaction will eventually reclaim it.

---

## Why No Tombstone? — TTL Expiry vs Explicit Delete

In the anti-entropy deep dive, we learned that explicit deletes need **tombstones** to prevent resurrection. If you just erase the data and anti-entropy copies it back from another replica, the deleted data comes back to life.

TTL expiry doesn't need tombstones. Here's why:

### Explicit delete — no self-describing death

```
delete("user:123") on Node B and Node C. Node D was down and missed it.

Without tombstone:
  Node B: "user:123" → (erased, nothing)
  Node D: "user:123" → "Alice", expiry=none (still has the data)

  Anti-entropy: Node D has data, Node B doesn't
    → Copies "Alice" back to Node B
    → Node B has no way to know this key was deleted
    → Resurrection! The deleted data is back.
```

The entry has no expiry field — it was meant to live forever. Once it's erased, there's no record that it was ever deleted. That's why we need a tombstone — it's the record that says "this key was deleted at time X."

### TTL expiry — self-describing death

```
"session:abc" expires on Node B and Node C. Compaction drops it.
Node D was down during compaction — still has the entry.

  Node B: "session:abc" → (dropped by compaction, nothing)
  Node D: "session:abc" → "token123", expiry=1713486400

  Anti-entropy: Node D has data, Node B doesn't
    → Copies "token123" with expiry=1713486400 back to Node B
    → Node B now has the entry again...
    → But any read checks: now > 1713486400 → EXPIRED
    → Returns "not found" anyway
```

The expired entry gets copied back, but it doesn't matter. The expiry timestamp is **baked into the entry itself** — it's a death certificate that travels with the data wherever it goes. No matter how many times anti-entropy copies it around, every node that reads it will check the expiry and return "not found."

```
Explicit delete:
  → No built-in "I am dead" marker
  → Tombstone needed to carry that information
  → Without tombstone → resurrection

TTL expiry:
  → Expiry timestamp IS the "I am dead" marker
  → Baked into the entry, travels with it everywhere
  → Even if resurrected, reads still return "not found"
  → No tombstone needed
```

The expired entry will eventually get cleaned up by compaction on Node B again. It's a bit of wasted disk space in the meantime, but logically the key stays dead regardless.

---

> [!tip] Interview framing
> "TTL is stored as an expiry timestamp in the entry's metadata — right alongside the key, value, and write timestamp. It travels through the entire LSM pipeline: WAL, memtable, SSTable. On reads, the node checks the expiry against the current time — if expired, it returns 'not found' without any actual deletion. The physical cleanup happens lazily during compaction, which drops expired entries when it encounters them. Unlike explicit deletes, TTL expiry doesn't need tombstones — the expiry timestamp is baked into the entry itself, so even if anti-entropy copies an expired entry back to a node, every read will still check the expiry and return 'not found.' The entry carries its own death certificate."
