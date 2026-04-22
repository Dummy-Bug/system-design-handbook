> [!question] Primary-replica removes the SPOF on reads but the primary is still a single point of failure for writes. What if you need multiple nodes accepting writes?

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

When two nodes accept conflicting writes to the same row, something has to give. You have three options — each with a different trade-off.

---

**Last Write Wins (LWW)**

The write with the later timestamp wins. The other write is silently discarded.

```
Node A at T=10.001s: username → "alice_new"
Node B at T=10.002s: username → "alice_123"

LWW picks Node B's write (later timestamp)
"alice_new" is silently gone ✗
```

Simple and automatic — no extra logic needed. But one of the two writes is just thrown away, and the user who wrote "alice_new" is never told their update was lost. They see "success" and then discover their change disappeared.

Works for: social feed posts, profile picture updates — scenarios where losing one of two near-simultaneous updates is annoying but not catastrophic.

Fails completely for: financial data, inventory counts. If two nodes both process "deduct 100 from account balance" and LWW picks only one, you've lost a transaction silently.

---

**Application-level merge**

Instead of discarding one write, the application defines how to combine both versions into one correct result.

The classic example is a shopping cart. If you add "headphones" on your phone and "keyboard" on your laptop at the same time, and both writes reach different nodes — you don't want LWW to throw one away. You want both items in the cart.

```
Node A: cart = ["headphones"]
Node B: cart = ["keyboard"]

Merge: cart = ["headphones", "keyboard"] ✓
```

Google Docs does something similar — when two users edit the same line simultaneously, it uses **operational transformation** to figure out how to apply both edits without either one overwriting the other.

Complex to implement correctly. You have to define the merge logic upfront for every data type your system has. But it's the only option when data loss is unacceptable and you still need multi-primary.

---

**CRDT (Conflict-free Replicated Data Types)**

A smarter version of application-level merge — but instead of writing custom merge logic, you use **data structures that are mathematically designed to always merge correctly**, no matter what order the updates arrive in.

A simple example: a **G-Counter** (grow-only counter). Say you have a "likes" counter on a post. Two nodes both receive a like at the same time:

```
Node A: likes = 5, increments to 6
Node B: likes = 5, increments to 6

Merge: likes = 7  ✓  (not 6 — both increments are preserved)
```

A regular counter would pick one (LWW gives you 6, losing one like). A G-Counter tracks each node's count separately and adds them all together on merge — so both increments survive.

CRDTs work for counters, sets, registers, and a few other structures where the merge semantics can be defined mathematically. They don't work for arbitrary data — you can't CRDT a username field where two conflicting values genuinely cannot be merged.

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
