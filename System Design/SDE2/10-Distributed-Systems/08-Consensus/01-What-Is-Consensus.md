
> [!info] The core idea
> Consensus means all non-faulty nodes in a distributed system agree on the same value, in the same order. Not "most nodes." Not "eventually maybe." All of them. On the same value. At the same time.

---

## The problem with "everyone accepts writes"

Imagine 5 database nodes, all accepting writes independently. Client A writes `x = 10` to Node 1. Client B writes `x = 99` to Node 3 at the exact same millisecond. Now Node 1 thinks x is 10, Node 3 thinks x is 99.

You have a conflict. Someone has to win.

The obvious fix is timestamps — Last Write Wins. The write with the later timestamp is the real one. But clocks drift across machines. Node 1's clock might be 50ms ahead of Node 3's clock. So Client A's write gets timestamp `12:00:00.050` and Client B's write gets `12:00:00.000` — even though Client B's write happened later in real time. Last Write Wins silently discards Client B's write. No error. No warning. Data just disappears.

So you can't trust clocks. You need a different way to agree on which write is the real one.

---

## Why consensus is hard

To agree on a value, nodes need to communicate. But any message between them can be lost, delayed, or arrive out of order — the Two Generals Problem. You can never be 100% certain the other side received your message.

So how do you get 5 nodes to agree on something when the very messages they use to agree might not arrive?

This is why consensus is considered one of the hardest problems in distributed systems. And it's why you need a proper algorithm — not just "nodes talk to each other and figure it out."

---

## Consensus algorithms

Two algorithms solve this problem in practice:

- **Raft** — designed to be understandable. Single leader, randomized timeouts, explicit log replication. Used in etcd, CockroachDB, Kafka KRaft.
- **Paxos** — the original consensus algorithm. More complex, harder to implement correctly. Raft was literally designed as a simpler alternative to Paxos.

→ See [[02-Leader-Election]] for Raft
→ See [[03-Paxos]] for Paxos
