## The Problem — Concurrent Writes to the Same Key

Two clients write to the same key at the exact same time:

```
Client 1: put("user:123", "Alice")  → goes to Node B, Node C, Node D
Client 2: put("user:123", "Bob")    → goes to Node B, Node C, Node D
```

Both writes get W=2 acks. Both succeed. But the order each node receives them is **not guaranteed** — network latency is unpredictable. Client 1's request might reach Node B first but reach Node C second.

```
Node B receives: Alice first, then Bob  → stores "Bob"
Node C receives: Bob first, then Alice  → stores "Alice"
Node D receives: Alice first, then Bob  → stores "Bob"

Final state:
  Node B: "Bob"
  Node C: "Alice"
  Node D: "Bob"
```

The replicas disagree. A quorum read (R=2) that hits Node B and Node C gets two different values. We need a **deterministic rule** that every node agrees on, regardless of network timing — so that no matter which nodes a read hits, the same value wins.

---

## Last Writer Wins (LWW) — The Simple Solution

Every write carries a timestamp. When two values exist for the same key, the one with the **higher timestamp wins**. We've been using this throughout the system already — read repair compares timestamps, anti-entropy compares timestamps, compaction keeps the higher timestamp.

```
Client 1: put("user:123", "Alice", timestamp=1001)
Client 2: put("user:123", "Bob",   timestamp=1002)

Node B: has both → keeps "Bob" (1002 > 1001)
Node C: has both → keeps "Bob" (1002 > 1001)
Node D: has both → keeps "Bob" (1002 > 1001)
```

Every node independently picks the same winner. No coordination needed. Deterministic. This is what Cassandra and DynamoDB use as their default conflict resolution strategy.

---

## The Clock Drift Problem

LWW relies on timestamps, but **who assigns the timestamp?** Two options:

1. **Client assigns it** — each client stamps its own write. But clients run on different machines with different clocks.
2. **Coordinator assigns it** — the coordinator node stamps the write when it receives it. But two different coordinators also have different clocks.

Either way, clocks across machines **drift**. A machine's clock might be milliseconds or even seconds ahead of another. This means LWW doesn't guarantee "the actually-last write wins" — it guarantees "the write with the higher timestamp wins." There's a difference:

```
Real time:    Client 1 writes at 3:00:00.000
              Client 2 writes at 3:00:00.001  ← actually later

Client 1's clock: 3:00:00.500  ← clock is 500ms ahead
Client 2's clock: 3:00:00.001  ← clock is accurate

LWW picks Client 1 (timestamp 500 > 001)
  → Client 1 wins even though Client 2 was actually later
  → Client 2's write is silently dropped
```

The user behind Client 2 thinks their update succeeded — they got W=2 acks. But the value was quietly overwritten by Client 1's stale write because Client 1's clock was ahead. The write is **silently lost**.

---

## Is Silent Data Loss Acceptable?

For most KV store use cases, LWW is **acceptable**. If two clients are writing to the same key at the exact same millisecond, there's no meaningful "correct" ordering — it's a race condition in the application logic. Either value is equally valid. LWW just picks one deterministically.

But there are use cases where losing a concurrent write is **not acceptable**. Consider a shopping cart on Amazon:

```
Phone:  put("cart:user123", ["shoes"])      timestamp=1001
Laptop: put("cart:user123", ["shirt"])      timestamp=1002

LWW picks ["shirt"] (1002 > 1001)
  → "shoes" is silently dropped
  → User expects both items in cart, but only "shirt" is there
```

The user didn't intend to overwrite shoes with shirt — they intended to **add** shirt to the cart. Both writes are valid and should be **merged**, not overwritten. LWW can't do this — it always picks one winner and discards the other.

This is where the question becomes: should our KV store solve this, or is it the application's problem?
