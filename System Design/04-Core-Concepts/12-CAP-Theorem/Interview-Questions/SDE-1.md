# CAP Theorem — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of CAP, why CA doesn't exist, and how to apply CP vs AP to real systems. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is CAP Theorem?

> [!question] State CAP theorem in one sentence. What are the three properties?

> [!success]- Answer
>
> **CAP Theorem:**
> In a distributed system, you can guarantee at most two of three properties: Consistency, Availability, and Partition Tolerance.
>
> **The three properties:**
>
> ```
> Consistency (C):
>   Every read sees the most recent write
>   All nodes return the same value at any point in time
>   Note: this specifically means LINEARIZABILITY — not "data is consistent"
>
> Availability (A):
>   Every request receives a response (not an error)
>   The system is always reachable and responding
>   Note: the response may not reflect the latest write
>
> Partition Tolerance (P):
>   The system continues operating even when network partitions occur
>   Network failures don't cause system failure
> ```
>
> **The practical implication:**
> Partition tolerance is non-negotiable for any distributed system — network partitions will happen. So the real choice is:
>
> ```
> CP → during a partition: stay consistent, may become unavailable
>      "I'd rather return an error than return stale data"
>
> AP → during a partition: stay available, consistency weakens
>      "I'd rather return stale data than return an error"
> ```
>
> > [!important] C in CAP specifically means linearizability — every read sees the globally latest write. AP systems still have consistency (they use eventual consistency) — just not linearizability.
>
> > [!tip] Interview framing
> > *"CAP says: during a partition, choose consistency or availability — you can't have both. P is non-negotiable, so the real choice is CP or AP. CP refuses requests to stay correct. AP serves stale data to stay available."*

---

## Q2 — Why CA Doesn't Exist

> [!question] An interviewer says "design a CA system — consistent and available, sacrifice partition tolerance." How do you respond?

> [!success]- Answer
>
> **The right response: CA doesn't exist as a meaningful distributed system.**
>
> **Why:**
> Partition tolerance means the system continues operating during network failures. If you "sacrifice" partition tolerance, you're saying: "when the network fails, the system can fail."
>
> ```
> What "sacrificing P" actually means:
>   Network partition occurs
>   → system shuts down entirely
>   → no availability ✗
>
> You haven't built a CA system
> You've built a system that fails during network problems
> ```
>
> **Networks fail. This is not optional.**
> ```
> Cloud providers have inter-AZ packet loss
> Network switches reboot
> Cables get cut
> BGP routing changes cause temporary disconnects
>
> Any distributed system WILL experience partitions
> "CA" means "works until the network fails, then completely breaks"
> ```
>
> **The honest answer:**
> CA describes a single-node system — one server, no replication. It's always consistent and always available (until it crashes). But that's not a distributed system.
>
> For truly distributed systems, the choice is always CP or AP during partitions.
>
> > [!important] Saying "I'll sacrifice partition tolerance" is saying "my system will go down when the network fails." That's not a design choice — it's an admission of failure. All distributed systems must be CP or AP.
>
> > [!tip] Interview framing
> > *"CA doesn't exist as a distributed system. Sacrificing P means the system fails during network partitions — which will happen. The real choice is CP or AP. CA only describes single-node systems where there's no replication to partition."*

---

## Q3 — CP vs AP: Payment System

> [!question] You're designing a payment processing system. Should it be CP or AP? Walk me through the reasoning.

> [!success]- Answer
>
> **Four-step reasoning:**
>
> **Step 1 — What consistency does payment data need?**
> ```
> Financial data — needs linearizability
> Stale balance → user charges against funds they no longer have → financial loss
> Duplicate charge → user charged twice → legal liability
> ```
>
> **Step 2 — What happens if the system is unavailable?**
> ```
> "Service temporarily unavailable, please try again"
> User retries in 30 seconds → recoverable
> → temporary unavailability is annoying but not catastrophic
> ```
>
> **Step 3 — Which is worse: wrong data or no response?**
> ```
> Wrong data (double charge, incorrect debit) → catastrophic
>   → financial loss
>   → regulatory violation
>   → customer trust destroyed
>
> No response (error page) → recoverable
>   → user retries
>   → support call at worst
> ```
>
> **Step 4 — The choice:**
> ```
> CP ✓ — during a partition, refuse requests rather than risk wrong financial data
>
> DB choice: PostgreSQL (ACID, CP)
>            or Google Spanner (globally consistent, CP)
>            NOT Cassandra (AP, eventual consistency)
> ```
>
> > [!tip] Interview framing
> > *"Payment is CP. Wrong balance or duplicate charge is catastrophic — financial loss and regulatory violation. A failed transaction is recoverable — user retries. I'd use PostgreSQL with SERIALIZABLE isolation or Google Spanner for global payments."*

---

## Q4 — CP vs AP: Social Feed

> [!question] You're designing a social media feed. Should it be CP or AP?

> [!success]- Answer
>
> **Step 1 — What consistency does feed data need?**
> ```
> Feed content — like counts, view counts, new posts
> Stale like count? Off by a few → user doesn't notice
> Post appearing 2 seconds late? → imperceptible
> ```
>
> **Step 2 — What happens if the system is unavailable?**
> ```
> 500M users can't see their feed
> → they leave, engagement drops
> → at Instagram/Twitter scale: millions in ad revenue per minute
> → availability is critically valuable
> ```
>
> **Step 3 — Which is worse: stale data or no response?**
> ```
> Stale data (like count off by a few) → harmless
> No response (error page for 500M users) → catastrophic
> ```
>
> **Step 4 — The choice:**
> ```
> AP ✓ — during a partition, serve stale data rather than go down
>
> DB choice: Cassandra (AP, eventual consistency, massive write throughput)
>            DynamoDB (AP, globally distributed)
>            NOT PostgreSQL with quorum reads (would reduce availability)
> ```
>
> **The additional read-your-writes consideration:**
> Even in an AP system, users should see their own posts immediately. Add a read-your-writes guarantee on top of eventual consistency for user-facing write-then-read patterns.
>
> > [!tip] Interview framing
> > *"Feed is AP. Slightly stale like counts are harmless. 500M users unable to load their feed is catastrophic — massive revenue impact. I'd use Cassandra — AP, eventual consistency, designed for massive write throughput. I'd add read-your-writes on top for user-visible write-then-read patterns."*

---

## Q5 — Tunable Consistency

> [!question] Cassandra is described as "AP". But your colleague says they're using Cassandra with QUORUM reads and writes for their payment service. Are they wrong?

> [!success]- Answer
>
> **Not necessarily — because Cassandra's consistency is tunable per operation.**
>
> **How tunable consistency works in Cassandra:**
> ```
> Write with ONE:    1 node confirms → responds immediately (fast, AP behaviour)
> Write with QUORUM: majority confirms → waits → responds (slower, CP behaviour)
> Write with ALL:    all nodes confirm → slowest, strongest consistency
>
> Read with ONE:    read from 1 node → may be stale (AP)
> Read with QUORUM: read from majority, return most recent → consistent (CP-ish)
> ```
>
> **With QUORUM reads + QUORUM writes:**
> ```
> R + W > N (e.g. R=2, W=2, N=3: 4 > 3) → guaranteed to read latest write
> This gives you strong consistency, just like a CP system
> ```
>
> **But you're still paying the availability cost:**
> ```
> During a partition where the majority is unreachable:
>   QUORUM write fails — can't confirm with majority
>   System becomes unavailable for those writes
>
> By choosing QUORUM, you've opted into CP behaviour
> You're using Cassandra as a CP system in that moment
> ```
>
> **The key insight:**
> ```
> "Cassandra is AP" means: its DEFAULT configuration is AP
> With QUORUM, you're using it in CP mode
> Tunable systems let you make this choice per operation
> ```
>
> > [!tip] Interview framing
> > *"Cassandra defaults to AP but is tunable per operation. With QUORUM reads and writes (R+W>N), you get strong consistency — it behaves like a CP system. The trade-off: during a partition where majority is unreachable, QUORUM operations fail. They've accepted that trade-off for their payment path."*
