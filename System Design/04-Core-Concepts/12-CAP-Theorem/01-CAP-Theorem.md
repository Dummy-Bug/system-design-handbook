# CAP Theorem

## What It States

> [!info] During a network partition, a distributed system can only guarantee two of three properties — Consistency, Availability, and Partition Tolerance.

---

## The Three Pillars

### C — Consistency (Linearizability)

Every read sees the latest write. All nodes return the same value at the same time.

> [!important] The C in CAP specifically means **linearizability** — not just any consistency model.
> An AP system sacrificing C during a partition doesn't become fully inconsistent — it just can't guarantee linearizability. It still provides eventual consistency, causal consistency etc. during normal operation.

```
Strong consistency (linearizability):
  Write to Node A → immediately visible on Node B
  Any read anywhere → sees the latest write
```

### A — Availability

Every request receives a response — not an error. The system keeps serving.

```
Availability guarantee:
  Request arrives at any non-failed node
  → must get a response (success or data)
  → never an error or timeout
```

> [!tip] "Available" in CAP means every non-failed node responds. It does NOT mean 100% uptime. A node that's crashed is excluded — CAP talks about nodes that are running but partitioned.

### P — Partition Tolerance

The system keeps operating even when network partitions occur.

```
Partition = nodes alive but cannot communicate
Partition tolerance = system continues despite this
```

---

## Why CA Doesn't Exist

> [!danger] "CA system" is a myth in distributed systems

Sacrificing P means: "our system breaks entirely when a partition happens."

But partitions are not optional — they will happen. Network cables get cut. Routers fail. Cloud providers have outages. A system that breaks entirely during a partition is not a real design choice — it's just a broken system.

```
CA system claim: "we sacrifice partition tolerance"
Reality:         partitions WILL happen → system breaks entirely
                 that's not a choice — that's just poor design

Real options:
  CP → consistent during partition, may be unavailable
  AP → available during partition, may serve stale data
```

> [!tip] Single-node databases (no replication) are technically "CA" — they have no partition to handle. The moment you add a second node, you're in distributed territory and P is non-negotiable.

---

## Normal Operation vs Partition

> [!important] CAP only describes behavior DURING a partition — not normal operation

```
Normal operation (no partition):
  Can have BOTH C and A ✓
  All nodes in sync, every read fresh, system fully available

During a partition:
  Forced to choose — C or A
  Cannot guarantee both simultaneously
```

This is why the choice matters — you're designing for the failure case, not the happy path.

---

## The Real Choice — CP or AP

Since P is non-negotiable, every distributed system is either:

```
CP → during partition: maintain consistency, sacrifice availability
     Nodes stop serving if they can't confirm data is fresh
     "Better to be down than wrong"

AP → during partition: maintain availability, sacrifice consistency  
     Nodes serve potentially stale data rather than refusing
     "Better to be stale than down"
```

Which to choose depends entirely on what's worse for your system — **wrong data or no response.** Covered in the next file.
