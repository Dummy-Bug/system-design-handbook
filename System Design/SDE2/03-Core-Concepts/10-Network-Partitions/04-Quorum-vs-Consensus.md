# Quorum vs Consensus

## The Distinction

> [!info] Quorum is a **number** — the minimum nodes that must agree.
> Consensus is a **process** — how nodes actually reach agreement.

They are related but different. Consensus algorithms use quorum internally.

---

## Quorum

A threshold. Nothing more.

```
3 node cluster → quorum = 2
"At least 2 nodes must confirm before this operation is valid"

Write request:
  Node A confirms ✓
  Node B confirms ✓  ← quorum reached → write successful
  Node C hasn't responded → doesn't matter

Read request (quorum read):
  Must read from at least 2 nodes
  Compare values → take the latest
  Guarantees you see the most recent write
```

**R + W > N formula:**
```
N = total nodes
W = nodes that must confirm a write
R = nodes that must confirm a read

R + W > N → guaranteed to see latest write

Example: N=3, W=2, R=2
  2 + 2 > 3 ✓ → strong consistency guaranteed
  At least one node in the read set saw the write
```

**Quorum is just the number** — it doesn't say anything about how nodes communicate, how leaders are elected, or how conflicts are resolved.

---

## Consensus

The full protocol for nodes to agree on a value — including leader election, handling failures, and guaranteeing no split-brain.

```
Consensus answers:
  Who is the leader?
  How is a new leader elected when the current one fails?
  How do nodes agree on the order of operations?
  What happens when nodes disagree?
  How is split-brain prevented?
```

**Famous consensus algorithms:**

| Algorithm | Used In | Key Idea |
|---|---|---|
| **Raft** | etcd, CockroachDB, TiDB | Leader-based, easier to understand |
| **Paxos** | Google Chubby, Zookeeper (ZAB) | Original, mathematically proven, complex |

---

## How They Relate

Consensus algorithms use quorum internally:

```
Raft consensus:
  Leader election → candidate needs quorum of votes to become leader
  Write commit    → leader needs quorum of followers to confirm before committing
  Leader validity → leader steps down if it can't reach quorum

Quorum is a tool INSIDE consensus — not the same thing
```

**Analogy:**
```
Quorum    → "we need 6 out of 10 board members to vote yes"
            just the threshold

Consensus → the entire board meeting:
            agenda, discussion, handling absent members,
            what if two people claim to be chairperson,
            how to record decisions, how to replay them
            
Consensus uses quorum as one of its rules
```

---

## When to Mention Each in Interviews

```
Mention QUORUM when talking about:
  → Read/write safety (R + W > N)
  → How many nodes must confirm a write
  → Why you need majority for split-brain prevention

Mention CONSENSUS when talking about:
  → Leader election
  → Distributed coordination
  → ZooKeeper, etcd, Raft
  → How distributed databases maintain consistency
```

> [!tip] Interview framing
> *"For write safety I'd use quorum — R + W > N ensures any read sees the latest write. For leader election and coordination I'd use a consensus-based system like etcd which implements Raft — nodes only become leader with quorum of votes, preventing split-brain automatically."*
