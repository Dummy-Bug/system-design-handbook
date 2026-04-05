# Network Partitions — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of what a partition is, split-brain, quorum, and how to choose between serving stale data vs refusing requests. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is a Network Partition?

> [!question] What is a network partition? Is it a crash? How do you detect one?

> [!success]- Answer
>
> **What it is:**
> A network partition is when nodes are alive and running but cannot communicate with each other. The network link between them has failed.
>
> ```
> Normal:    Node A ←→ Node B  (communicating)
>
> Partition: Node A  ✗  Node B  (nodes alive, network broken)
>            Node A is fine    Node B is fine
>            They just can't talk to each other
> ```
>
> **It is NOT a crash:**
> ```
> Crash:     Node B dies → not responding to anything
>            Detection: health check times out quickly
>
> Partition: Node B is alive → responding to its own clients
>            But Node A can't reach Node B
>            Detection: much harder — is B down or just unreachable from A?
> ```
>
> **Why detection is hard:**
> ```
> Node A sends heartbeat to Node B → no response
>
> Possible explanations:
>   1. Node B crashed
>   2. Network between A and B failed (partition)
>   3. B is overloaded and slow
>   4. One specific link failed — B is reachable from C but not A
>
> Node A cannot tell which scenario it's in
> ```
>
> **Why partitions are inevitable:**
> Any distributed system with a network link will eventually have a partition — network cables fail, switches reboot, cloud AZs have connectivity issues. They are not optional to design for.
>
> > [!important] A partition is not a crash. Both nodes are alive — they just can't reach each other. This makes the situation ambiguous: the node that can't reach others doesn't know if they're down or just unreachable.
>
> > [!tip] Interview framing
> > *"A network partition is nodes alive but unable to communicate — not a crash. Detection is hard because the node can't tell if the other is down or just unreachable. Partitions are inevitable in any distributed system — the design question is what to do during one."*

---

## Q2 — Serve or Refuse During a Partition?

> [!question] During a network partition, an isolated node must choose: serve potentially stale data, or refuse requests entirely. How do you decide?

> [!success]- Answer
>
> **The core trade-off:**
> ```
> Serve stale data → users get a response, but it might be outdated
>                    availability preserved, consistency sacrificed
>
> Refuse requests  → users get an error, but no stale data served
>                    consistency preserved, availability sacrificed
> ```
>
> **The decision depends entirely on the cost of stale data:**
>
> | System | Decision | Reason |
> |---|---|---|
> | Social feed, recommendations | Serve stale | Slightly old content is harmless |
> | Shopping cart | Serve stale | Better to let users browse than show error |
> | Bank balance | Refuse | Wrong balance → user makes financial decision on bad data |
> | Payment processing | Refuse | Could approve a transaction based on stale account state |
> | Hotel/seat booking | Refuse | Stale inventory count → double booking |
> | Inventory management | Refuse | Overselling = unfulfillable orders |
>
> **The rule:**
> ```
> Ask: what does a user DO with this data?
>
> If they consume it passively (read a feed, see a count) → serve stale
> If they make a financial or booking decision based on it → refuse
> ```
>
> > [!tip] Interview framing
> > *"Serve or refuse depends on the cost of showing stale data. Social feed: serve stale — slightly old posts are harmless. Bank balance: refuse — user might spend money they don't have. The question is: what does the user do with this data, and what breaks if it's wrong?"*

---

## Q3 — Split-Brain

> [!question] What is split-brain? Why is it a serious problem and how do you prevent it?

> [!success]- Answer
>
> **Split-brain:**
> When a partition causes two nodes to both believe they are the primary/leader — both accept writes simultaneously, without knowing about each other's writes.
>
> ```
> Normal:    Node A (primary) ←→ Node B (replica)
>
> Partition: Node A  ✗  Node B
>            Node A thinks: "I'm still primary — B must be down"
>            Node B thinks: "A is unreachable — I'll promote myself to primary"
>
>            Now: two primaries, both accepting writes
>            User 1 → writes to Node A
>            User 2 → writes to Node B
>
>            Partition heals:
>            A has data B doesn't have
>            B has data A doesn't have
>            Conflicting writes → which one wins?
> ```
>
> **Why it's serious:**
> ```
> Bank: Node A: balance = $500 (after withdrawal)
>       Node B: balance = $700 (after deposit)
>       Which is correct? → impossible to know automatically
>
> For many systems, there is no safe automated merge strategy
> ```
>
> **Prevention — quorum:**
> A node only acts as primary if it can reach a majority of the cluster.
>
> ```
> 3-node cluster: quorum = 2
>
> Partition: Group of 1 ✗ Group of 2
>
> Group of 1: "I can only reach 1 node (myself) — I don't have quorum"
>             → steps down, refuses writes
>
> Group of 2: "I can reach 2 nodes — I have quorum"
>             → stays primary, continues serving
>
> Only one primary at a time → no split-brain ✓
> ```
>
> > [!important] Split-brain causes conflicting writes that are impossible to merge automatically. Quorum is the standard prevention: a node only leads if it can reach a majority.
>
> > [!tip] Interview framing
> > *"Split-brain is two nodes both thinking they're primary — both accept writes, creating conflicting data that can't be merged. Prevention: quorum. A node only operates as primary if it can reach a majority. With 3 nodes, quorum is 2 — a partitioned single node steps down."*

---

## Q4 — Why Odd Number of Nodes?

> [!question] Why do distributed systems use an odd number of nodes (3, 5, 7) rather than even numbers?

> [!success]- Answer
>
> **The problem with even numbers:**
>
> ```
> 4-node cluster, quorum = 3 (floor(4/2) + 1)
>
> Partition: 2-2 split
>            Group A: 2 nodes — does NOT have quorum (needs 3)
>            Group B: 2 nodes — does NOT have quorum (needs 3)
>
>            Both groups step down
>            System is completely unavailable ✗
>            No writes, no reads (with quorum reads)
> ```
>
> **With odd numbers, one group always has majority:**
>
> ```
> 3-node cluster, quorum = 2
>
> Any partition: 1-2 or 0-3 (only options)
>
>   1 vs 2: Group of 2 has quorum → keeps serving ✓
>   0 vs 3: Group of 3 has quorum → keeps serving ✓
>
> One group ALWAYS has majority → system stays available
> ```
>
> ```
> 5-node cluster, quorum = 3
>
> Possible partitions: 1-4, 2-3
>
>   2 vs 3: Group of 3 has quorum → keeps serving ✓
>   1 vs 4: Group of 4 has quorum → keeps serving ✓
> ```
>
> **Practical values:**
> ```
> 3 nodes → tolerates 1 failure, quorum = 2
> 5 nodes → tolerates 2 failures, quorum = 3
> 7 nodes → tolerates 3 failures, quorum = 4
> ```
>
> > [!tip] Interview framing
> > *"Even numbers create symmetric partitions where neither group has majority — both step down, system fully unavailable. Odd numbers guarantee one group always has clear majority. 3 nodes tolerates 1 failure. 5 nodes tolerates 2. More nodes = more fault tolerance, more write overhead."*

---

## Q5 — Quorum Reads and Writes

> [!question] What is a quorum read and write? What formula ensures you always read the latest write?

> [!success]- Answer
>
> **Setup:**
> ```
> N = total number of replicas
> W = number of replicas that must confirm a write
> R = number of replicas that must respond to a read
> ```
>
> **The formula:**
> ```
> R + W > N → guaranteed to read the latest write
> ```
>
> **Why it works:**
> If W nodes confirmed the write and R nodes must respond to the read, then at least one node in your read set must have participated in the write. You're guaranteed to see the latest value.
>
> **Common configurations:**
>
> ```
> N=3, W=2, R=2: R + W = 4 > 3 → strong consistency ✓
>   Write: 2 of 3 nodes confirm
>   Read:  2 of 3 nodes respond
>   Overlap guaranteed: at least 1 node in common
>
> N=3, W=1, R=1: R + W = 2 < 3 → eventual consistency (fast, may be stale)
>   Write: only 1 node confirms (fast)
>   Read:  only 1 node responds (may be behind)
>   No overlap guaranteed
>
> N=3, W=3, R=1: strong consistency (write is slow — all 3 must confirm)
>   Write: all 3 nodes confirm (slow)
>   Read:  any 1 node responds → guaranteed to have latest write ✓
> ```
>
> **Practical use:**
> ```
> Cassandra: configurable per operation
>   ONE   → fastest, no consistency guarantee
>   QUORUM → R+W>N, strong consistency
>   ALL   → strongest, slowest
> ```
>
> > [!tip] Interview framing
> > *"R + W > N guarantees you read the latest write — the read set and write set must overlap. With N=3: W=2, R=2 gives strong consistency. W=1, R=1 gives eventual consistency — fast but potentially stale. Cassandra lets you tune this per operation."*
