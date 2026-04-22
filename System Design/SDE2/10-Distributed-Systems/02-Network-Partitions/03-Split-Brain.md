# Split-Brain

## What It Is

> [!info] Split-brain = during a partition, multiple nodes all believe they are the primary and independently accept writes. When the partition heals, you have conflicting versions of the same data.

---

## How It Happens

```
Normal operation — 3 nodes, Node A is primary:
  Node A (Mumbai)    ← primary, accepts writes
  Node B (Singapore) ← replica
  Node C (Tokyo)     ← replica

Partition splits into two groups:
  Group 1: Node A          (Mumbai isolated)
  Group 2: Node B, Node C  (Singapore + Tokyo)

Group 2 thinks Node A is dead → elects Node B as new primary
Node A thinks B and C are dead → keeps acting as primary

Now TWO primaries accepting writes simultaneously:
  Mumbai users  → writing to Node A
  Singapore/Tokyo users → writing to Node B
```

---

## The Problem When Partition Heals

```
During partition:
  Node A: user123 balance = $500  (Mumbai: withdrawal of $200 from $700)
  Node B: user123 balance = $800  (Singapore: deposit of $100 to $700)

Partition heals — which value is correct?
  $500? $800? $1000? ($700 - $200 + $100)

WAL can show you the order of writes on each node
But cannot tell you which node's version should win
Both nodes were "primary" — both writes were "valid"
```

> [!danger] Split-brain creates conflicting writes with no automatic resolution
> Data integrity is compromised. Human intervention or complex merge logic required.

---

## The Solution — Quorum

**The rule:** A node only acts as primary if it can reach a **majority** of nodes (quorum).

```
3 nodes → quorum = 2 (majority of 3)

Partition splits into Group 1 (1 node) and Group 2 (2 nodes):

Group 1 — Node A alone:
  Can reach 1 node → below quorum (need 2)
  → steps down, stops accepting writes

Group 2 — Node B + Node C:
  Can reach 2 nodes → quorum reached ✓
  → elects leader, keeps accepting writes

Only one group has quorum → only one primary → no split-brain
```

**Quorum formula:**
```
Quorum = floor(N/2) + 1

3 nodes → floor(3/2) + 1 = 2
5 nodes → floor(5/2) + 1 = 3
7 nodes → floor(7/2) + 1 = 4
```

---

## Why Odd Numbers of Nodes

> [!important] Always use odd numbers — 3, 5, 7. Never even.

```
3 nodes → quorum = 2
  Partition 1+2 → Group of 2 has quorum ✓, Group of 1 doesn't ✓
  Always one clear winner

4 nodes → quorum = 3
  Partition 2+2 → neither group has quorum ✗
  Both groups stop → entire system unavailable
  Even worse than split-brain

5 nodes → quorum = 3
  Partition 2+3 → Group of 3 has quorum ✓
  Always one clear winner
```

Even numbers can deadlock — neither partition group has quorum, entire system stops. Odd numbers guarantee one group always wins.

---

## Recovery After Partition Heals

```
Partition heals → Node A (isolated, stepped down) rejoins

Node A contacts Group 2 leader (Node B):
  "I stepped down at timestamp T=500"
  "What happened after T=500?"

Node B sends WAL entries from T=500 onwards
Node A replays them → catches up to current state
Node A rejoins as replica

No conflicting writes because Node A stopped accepting writes when isolated
```

---

## How Real Systems Handle This

| System | Split-Brain Prevention |
|---|---|
| ZooKeeper | Quorum-based — leader only valid with majority |
| etcd | Raft consensus — leader steps down without quorum |
| PostgreSQL (Patroni) | External coordinator (etcd/ZooKeeper) grants primary rights |
| Redis Sentinel | Sentinel quorum decides failover |
| Cassandra | Quorum reads/writes configurable per operation |

> [!tip] Interview framing
> *"Split-brain is prevented by quorum — a node only acts as primary if it can reach a majority of nodes. This is why distributed systems use odd numbers of nodes — 3, 5, 7 — so one group always has a clear majority during a partition. Systems like ZooKeeper and etcd implement this via the Raft consensus algorithm."*
