
> [!info] The core idea
> Raft is a consensus algorithm designed to be easy to understand. It solves the problem of getting multiple nodes to agree on the same sequence of writes — even when nodes crash, messages are lost, or the network splits.

---

## Why Raft exists

The original consensus algorithm is Paxos. It works, but it's notoriously difficult to understand and even harder to implement correctly. Most engineers who tried to implement Paxos ended up with undocumented, subtly different variants that were hard to reason about.

Raft was designed from scratch with one explicit goal — **understandability**. Same correctness guarantees as Paxos, but structured in a way that's easier to reason about, teach, and implement.

---

## The two problems Raft solves

Raft breaks consensus into two clearly separated problems:

1. **Leader Election** — how nodes pick a single leader, and re-pick when the leader dies
2. **Log Replication** — how the leader safely replicates writes to followers so no committed data is ever lost

Everything in Raft flows from these two mechanisms.

---

## The core guarantee

Raft guarantees **at most one leader per term**. A term is a logical epoch — a numbered period during which one specific node is the leader. Every message in Raft carries a term number. If a node receives a message from a lower term, it rejects it. This single rule is what prevents split-brain.

```
Term 1: Node A is leader
Node A crashes → election → Term 2: Node B is leader
Node A comes back → sees Term 2 > Term 1 → immediately steps down
```

> [!important] Raft is used in production everywhere
> etcd (the backbone of Kubernetes), CockroachDB, TiKV, Kafka KRaft mode — all use Raft. When an interviewer asks "how does your distributed database handle leader failover?" — the answer is Raft.

---

→ See [[02-Leader-Election]] for how Raft picks a leader
→ See [[03-Term-Numbers]] for how term numbers prevent the ghost leader problem
→ See [[05-Log-Replication-Failures]] for how Raft handles crashes during a write
