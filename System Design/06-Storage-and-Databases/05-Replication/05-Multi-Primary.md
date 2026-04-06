# Multi-Primary Replication

> [!question] Primary-replica removes the SPOF on reads but the primary is still a single point of failure for writes. What if you need multiple nodes accepting writes?

---

## What multi-primary is

Instead of one primary and multiple replicas, **all nodes accept writes simultaneously**. If one node dies, the others keep accepting writes without any failover delay.

```
Multi-Primary:
  Node A ←──── sync ────→ Node B
     ↑                       ↑
  writes                  writes
  from                    from
  region 1               region 2
```

Used for: globally distributed systems where users in different regions need low-latency writes to a nearby node. A user in India writes to an Indian node; a user in the US writes to a US node.

---

## The split-brain problem

Multi-primary sounds ideal — no write SPOF, low latency everywhere. But it introduces the hardest problem in distributed databases: **split-brain**.

The most common trigger is a **network partition** — two nodes lose their connection to each other but both stay operational.

```
Normal:         Node A ←── healthy ──→ Node B

Partition:      Node A ←── ✗ ──→ Node B  (can't reach each other)

Node A: "Node B is dead, I'm the only primary" → keeps accepting writes
Node B: "Node A is dead, I'm the only primary" → keeps accepting writes

User on Node A updates username → "alice_new"
User on Node B updates same username → "alice_123"

Both succeed ✓ — both nodes returned "success"
But both nodes now have different values for the same row ✗

Partition heals:
→ Node A has "alice_new", Node B has "alice_123"
→ which one is correct?
→ last-write-wins? merge? ask the user? → all options are lossy
```

> [!danger] Split-brain is not a theoretical concern
> Network partitions happen in production. Multi-primary without a conflict resolution strategy guarantees you will eventually have conflicting writes. At scale, "eventually" means regularly.

---

## Conflict resolution strategies

When two nodes accept conflicting writes to the same row, something has to give.

**Last Write Wins (LWW)** — the write with the later timestamp wins. Simple, automatic, lossy. One of the two writes is silently discarded. Works for: social feeds, profile updates where losing one concurrent update is tolerable. Fails for: financial data, inventory counts.

**Application-level merge** — the application defines how to merge conflicting versions. Complex but correct. Used in Google Docs (operational transformation), shopping carts (add quantities rather than overwrite), collaborative editors.

**CRDT (Conflict-free Replicated Data Types)** — data structures mathematically designed to merge without conflict. A G-Counter (grow-only counter) can be incremented on two nodes simultaneously and always merged correctly. Used for: distributed counters, sets, registers where the merge semantics can be defined upfront.

---

## Quorum — preventing split-brain

Rather than resolving conflicts after they happen, prevent them by requiring a **quorum** — a node only accepts a write if it can confirm that a majority of nodes are aware of it.

```
3-node cluster, quorum = 2:

Node A is partitioned, can only reach itself (1 node):
→ 1 < quorum of 2
→ Node A refuses writes ← correct behaviour, becomes unavailable

Node B and C can reach each other (2 nodes):
→ 2 ≥ quorum of 2
→ they accept writes ✓

Result: one side is available (B+C), one side is unavailable (A)
        but there is no divergence — impossible to have two conflicting primaries
```

The formula: **quorum = floor(N/2) + 1**

```
3 nodes → quorum = 2
5 nodes → quorum = 3
7 nodes → quorum = 4
```

A minority partition becomes unavailable rather than risk divergence. This is the CP choice in CAP — consistency over availability during a partition.

> [!important] Quorum doesn't eliminate all problems — it eliminates split-brain
> With quorum, you trade availability (the minority partition goes down) for consistency (no diverging writes). Whether that trade is acceptable depends on your system. For financial systems: absolutely. For social feeds: maybe async multi-primary with LWW is fine.

---

## When to use multi-primary

```
Use multi-primary when:
  ✓ Global users need low-latency writes to a nearby node
  ✓ You can define a conflict resolution strategy upfront
  ✓ Your data model tolerates eventual consistency

Avoid multi-primary when:
  ✗ Conflicting writes are unacceptable (financial ledgers, inventory)
  ✗ You need strong consistency across all nodes
  ✗ The complexity of conflict resolution outweighs the availability benefit
```

> [!tip] Interview framing
> "For a global system I'd use multi-primary replication so users write to their nearest region. The risk is conflicting writes — I'd handle that with last-write-wins for user profile data, and route financial operations to a single primary to avoid conflicts entirely."
