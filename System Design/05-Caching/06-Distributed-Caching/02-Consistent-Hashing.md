# Consistent Hashing

> [!info] Hash keys to nodes on a ring. Adding or removing a node only remaps ~1/N of keys — not the entire keyspace.

---

## Why naive hashing fails

The obvious approach — modulo hashing:

```
node = hash("user:123") % 4   → node 2

Add a 5th cache node:
node = hash("user:123") % 5   → node 3  ← different node!
```

Adding one node causes approximately 80% of all keys to map to different nodes. Every remapped key is a cache miss until it gets repopulated. A cache miss at the moment of scaling means the DB absorbs the traffic that was previously served from cache.

```
Before scaling: DB handles 5% of traffic (cache absorbs 95%)
After adding node: ~80% of keys remap → mass cache miss
→ DB suddenly handles 80%+ of traffic → DB collapses
```

---

## How consistent hashing works

Place both nodes and keys on a conceptual ring (0 to 2³²). Each key is assigned to the first node clockwise from its hash position.

```
Ring with 4 nodes:
          Node A (hash: 50)
         /
0 ──────────────────── Node B (hash: 150)
         \
          Node D (hash: 350) ── Node C (hash: 250)

Key with hash 80  → first node clockwise → Node B
Key with hash 200 → first node clockwise → Node C
Key with hash 300 → first node clockwise → Node D
```

Add a 5th node (Node E, hash: 200) between Node B and Node C:

```
Before: ... Node B → Node C ...
After:  ... Node B → Node E → Node C ...

Only keys that were in the Node B → Node C slice (hash 150–250)
and now fall between Node B → Node E (hash 150–200) need to move.
Everything else → completely untouched ✓

~1/N of keys remapped instead of ~80% ✓
```

---

## Virtual nodes — even distribution

With few physical nodes, the arc sizes between them are uneven. One node might own 40% of the ring, another only 5%.

The fix: each physical node gets multiple positions on the ring (150-200 virtual nodes per physical node). Each physical node owns many small arcs scattered around the ring instead of one large arc.

```
Physical Node A → virtual positions at hash: 23, 87, 156, 234, 312, ...
Physical Node B → virtual positions at hash: 45, 112, 189, 267, 389, ...
```

When Node A is removed, its keys are distributed across all remaining nodes proportionally — no single node absorbs the full load.

> [!tip] Interview answer
> "I'd use consistent hashing so adding or removing cache nodes only remaps ~1/N of keys instead of causing a mass cache miss that hammers the DB."
