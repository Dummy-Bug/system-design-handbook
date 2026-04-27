## Option 3 — Leaderless (Selected)

### How it works

No node is special. There's no primary, no follower, no election. Every node in the cluster is identical. **Nobody is in charge — the quorum math is in charge.**

A client's request hits any node through the load balancer. That node becomes the **coordinator** for this one request — but it's not a leader. It's just a middleman. Next request might be coordinated by a completely different node.

The coordinator's job:
1. Hash the key → find which nodes store this key (determined by consistent hashing)
2. Send the request to those nodes
3. Collect responses based on the quorum setting
4. Respond to the client

```
Write path:
  Client → LB (round-robin, pick any healthy node) → Node A becomes coordinator
    → hashes key → finds Node B, C, D own this key (N=3)
    → sends write to B, C, D simultaneously
    → waits for W acks → responds to client

Read path:
  Client → LB → Node X becomes coordinator
    → hashes key → finds Node B, C, D own this key
    → sends read to 1 node (eventual) or 2+ nodes (strong)
    → responds to client
```

### Why it solves the single-leader problem

Single-leader failed because: **primary dies → writes blocked → no availability-first option.**

In leaderless, there is no primary to die. If the coordinator node dies mid-request, the client retries, the load balancer picks any other healthy node, and that node coordinates instead. No election, no promotion, no downtime window.

If one of the storage nodes (say Node C) is down, the coordinator still sends the write to Node B and Node D. With W=2 and two nodes responding, the write succeeds. The client doesn't even know Node C is down.

```
Single-leader failure:
  Primary dies → writes STOP → election (seconds) → new primary → writes resume
  
Leaderless failure:
  Coordinator dies → client retries → any other node coordinates → no downtime
  Storage node dies → W=2 still met with remaining nodes → write succeeds
  NO election. NO downtime. NO blocked writes.
```

### Why it solves the multi-leader problem

Multi-leader failed because: **independent leaders accept writes without coordinating → conflicts.**

In leaderless, both writes to the same key go to the **same set of nodes** (because hashing the same key always maps to the same ring position). There are no independent leaders making decisions alone.

Conflicts can still happen — two concurrent writes to the same key will arrive at the same nodes in potentially different order. But this is resolved at **read time using quorum math**, not through after-the-fact syncing between independent leaders:

```
Multi-leader conflict:
  Leader A writes "Alice" → acks → syncs to Leader B later
  Leader B writes "Bob"   → acks → syncs to Leader A later
  Conflict discovered during async sync → need LWW or vector clocks

Leaderless conflict:
  Both writes go to same 3 nodes (B, C, D)
  Nodes might end up with different values temporarily
  On read: quorum (R=2) guarantees at least one node has the latest write
  → coordinator picks the value with the highest timestamp
  → read repair fixes the stale node in the background
```

The difference: multi-leader discovers conflicts **after the fact** during async sync between independent leaders. Leaderless resolves disagreements **at read time** using quorum — at least one node in the read set has the latest value, and the coordinator picks it.

### Tunable consistency — both reads AND writes

This is the killer feature that neither single-leader nor multi-leader could offer.

**Writes are tunable:**

```
W=2 (quorum write):  wait for 2 of 3 nodes → durable, slightly slower
W=1 (fast write):    wait for 1 of 3 nodes → less durable, faster
```

A payment service can use W=2. A logging service can use W=1. The client chooses.

**Reads are tunable:**

```
R=2 (quorum read):   ask 2 nodes, pick latest → strong consistency
R=1 (fast read):     ask 1 node → eventual consistency, fastest
```

**The quorum guarantee:** when W + R > N, at least one node in the read set participated in the latest write. That's how strong consistency is achieved — not through a leader, but through overlap.

```
N=3, W=2, R=2:  2 + 2 > 3 → strong consistency (guaranteed overlap)
N=3, W=2, R=1:  2 + 1 = 3 → eventual consistency (might miss latest write)
N=3, W=1, R=1:  1 + 1 < 3 → weak consistency (fastest, least durable)
```

Single-leader couldn't tune writes — they always went through the primary. Leaderless lets the client choose the trade-off on **every request**, for both reads and writes.

### What about conflicts? (Preview — covered in deep dives)

Leaderless doesn't eliminate conflicts — it handles them differently. When two concurrent writes hit the same nodes:

- **Quorum math** ensures reads see the latest write (if W + R > N)
- **Timestamps** resolve which value is newer on a per-node basis
- **Read repair** fixes stale replicas when a quorum read detects disagreement
- **Hinted handoff** handles the case where a node is down during a write
- **Anti-entropy with Merkle trees** catches any remaining inconsistencies in the background

Each of these is a deep dive topic. For architecture selection, the key point is: conflicts exist but are handled by mathematical guarantees and background repair — not by hoping independent leaders sync correctly.

---

## Final Comparison

```
                    Single-Leader        Multi-Leader          Leaderless
                    ─────────────        ────────────          ──────────
Write path          Primary only         Any leader            Any node (coordinator)
Read path           Primary or replica   Any leader/replica    Any node (quorum)
Tunable writes?     No (always primary)  No (always one leader) Yes (W=1 or W=2)
Tunable reads?      Yes                  Yes                   Yes
Node failure         Election needed      Other leaders alive   No election needed
                    (writes blocked)     (conflicts possible)  (quorum still met)
Conflicts           None (single writer) Yes (independent leaders) Rare (same node set)
                                        resolve after-the-fact  resolve at read time
Best for            Smaller clusters     Multi-region           Large single-region
                    Strong consistency   Low-latency geo-writes High availability
Real-world          MongoDB, PostgreSQL  CockroachDB (multi-DC) Cassandra, DynamoDB, Riak
```

```
Our requirements:
  ✓ 1,200 nodes, single region           → leaderless
  ✓ Tunable consistency on reads & writes → leaderless
  ✓ High availability, no write downtime  → leaderless
  ✓ No single point of failure            → leaderless
```

**Leaderless wins.** The deep dives will cover the mechanics: consistent hashing for routing, quorum for correctness, read repair and anti-entropy for convergence.

---

> [!tip] Interview framing
> "Leaderless architecture — no primary, no election, no single point of failure. Any node can coordinate any request. The coordinator hashes the key, sends reads/writes to the owning nodes, and uses quorum math for correctness. Both reads AND writes are tunable: W=2 for durability or W=1 for speed, R=2 for strong consistency or R=1 for eventual. This is what single-leader couldn't offer — when a primary dies there, writes are blocked. Here, any node dies, the quorum still holds with the remaining nodes. This is the Cassandra/DynamoDB model."
