
> [!info] The core idea
> Paxos is the original consensus algorithm — predates Raft. It solves the same problem (all nodes agree on the same value) but with no designated leader. Any node can propose a value at any time.

---

## Why Paxos exists

Before Raft, Paxos was the go-to algorithm for consensus. It is mathematically proven to be correct — if a majority of nodes are alive and communicating, Paxos will eventually reach agreement.

The problem is not correctness. The problem is complexity. Paxos is notoriously hard to understand and even harder to implement correctly. Most engineers who tried ended up with subtle variants that were difficult to reason about. Raft was designed specifically to replace it with something more understandable.

---

## The three roles

Unlike Raft which has a fixed leader and fixed followers, Paxos has three roles that any node can play:

**Proposer** — the node that received a client request and wants to get the cluster to agree on a value. Any node can become a proposer the moment a client write hits it.

**Acceptor** — the voter. Receives proposals and votes to accept them based on rules. Also ensures that once a decision is made, it is not violated.

**Learner** — learns the final agreed value once majority has committed. In practice, all nodes are both acceptors and learners.

---

## Proposal numbers

Since any node can propose at any time, you need a way to distinguish between old and new proposals. Paxos uses **proposal numbers** — monotonically increasing integers, unique across all nodes.

Each node generates its proposal number using a combination of a local counter and its node ID:

```
Node 1: counter = 2, node ID = 1 → proposal number = 21
Node 2: counter = 2, node ID = 3 → proposal number = 23
```

This guarantees uniqueness without any central coordinator. The higher the number, the more recent the proposal.

Acceptors always side with the higher proposal number. If a new proposal comes in with a higher number, the acceptor abandons its promise to the old proposer and switches to the new one.

---

## Quorum

Just like Raft, Paxos requires majority. With `2F+1` acceptors, you can tolerate up to `F` failures.

```
5 nodes → tolerate 2 failures (still have majority of 3)
11 nodes → tolerate 5 failures (still have majority of 6)
```

A proposer only needs majority to proceed — not all nodes.

---

