
> [!info] The core idea
> Paxos works correctly when one proposer finishes before another starts. But under concurrent writes with slow networks, two proposers can keep leapfrogging each other's proposal numbers forever — nobody commits anything. This is livelock, and it's the core reason Raft replaced Paxos in practice.

---

## When Paxos works fine

If DB-1 sends `PREPARE(5)`, gets majority promises, sends `ACCEPT(5, x=100)`, gets majority acks — value committed. Done.

If DB-2 tries to propose after this, it's too late. When DB-2 sends `PREPARE(7)`, acceptors will tell it "I already accepted `x=100` at N=5." DB-2 is forced to use `x=100`. No conflict.

```
DB-1 → PREPARE(5) → majority promises
DB-1 → ACCEPT(5, x=100) → majority acks → committed ✓

DB-2 → PREPARE(7) → acceptors reply "already accepted x=100 at N=5"
DB-2 forced to propose x=100 → same value → no problem
```

---

## The livelock problem

The issue is timing. In a real distributed system with slow networks and high load, you cannot guarantee DB-1 finishes before DB-2 starts.

Say DB-1 sends `PREPARE(5)` and is waiting for acks — network is congested, takes 200ms. In that 200ms window, DB-2 sends `PREPARE(7)`. Acceptors haven't heard back from DB-1. They have no idea DB-1 is mid-flight. They promise N=7 to DB-2 and abandon N=5.

DB-1 finally gets its acks — but they're stale. Acceptors have already moved on to N=7. DB-1's `ACCEPT(5, x=100)` gets rejected.

DB-1 retries with N=9. Acceptors switch to DB-1, reject DB-2.
DB-2 retries with N=11. Acceptors switch back to DB-2, reject DB-1.

```
DB-1 → PREPARE(5)  → acceptors promise 5
DB-2 → PREPARE(7)  → acceptors switch to 7, reject 5
DB-1 → PREPARE(9)  → acceptors switch to 9, reject 7
DB-2 → PREPARE(11) → acceptors switch to 11, reject 9
...forever
```

Nobody ever reaches Phase 2. No value ever gets committed. Both clients are waiting. System is stuck.

> [!danger] Livelock is not deadlock
> In deadlock, processes are frozen waiting for each other. In livelock, processes are actively running — they just keep undoing each other's progress. The system looks busy but nothing gets done.

---

## Fix 1 — Randomized backoff

When a proposer gets rejected, it must wait a **random** amount of time before retrying. This breaks the leapfrog cycle.

```
DB-1 rejected → waits 150ms before retrying
DB-2 rejected → waits 300ms before retrying

DB-1 wakes up first → PREPARE(9) → majority promises
DB-1 → ACCEPT(9, x=100) → committed ✓
DB-2 wakes up → too late → forced to use x=100
```

Same idea as Raft's randomized election timers — randomness breaks symmetry.

But this only reduces the probability of livelock. It doesn't eliminate it. Two proposers could still pick similar backoff times and race again under heavy load.

---

## Fix 2 — Designate a leader

The real fix is to designate one node as the **distinguished proposer** — the only node allowed to propose. No two proposers racing means no livelock, ever.

But now you've just reinvented leadership on top of Paxos. You added all the complexity of Paxos — two phases, proposal numbers, value inheritance rules — and then bolted a leader on top anyway.

```
Paxos without leader → livelock risk → needs randomized backoff
Paxos with leader    → works reliably → but now why not just use Raft?
```

---

## Why Raft replaced Paxos

Raft looked at this situation and said: if you need a leader anyway, why not design the entire algorithm around a single leader from day one?

| | Paxos | Raft |
|---|---|---|
| Leader | Optional, bolted on later | Built in from day one |
| Any node can propose | Yes — causes livelock | No — only leader proposes |
| Understandability | Notoriously hard | Designed to be easy |
| Implementation complexity | High — many subtle edge cases | Lower — clearly separated concerns |
| Correctness | Proven | Proven |
| Used in production | Older systems | etcd, CockroachDB, Kafka KRaft |

Paxos is correct. But correct and understandable are different things. Most engineers who tried to implement Paxos ended up with subtle variants that were hard to reason about and harder to debug.

Raft gives the same correctness guarantees with a design that is deliberately easier to understand, implement, and teach.

> [!tip] Interview framing
> "Paxos works but has no designated leader — any node can propose, which causes livelock under concurrent writes. The fix is to add a leader, but then you've reinvented Raft with more complexity. Raft starts with a single leader by design, gives the same guarantees, and is far easier to implement correctly. That's why etcd, CockroachDB, and Kafka KRaft all use Raft today."
