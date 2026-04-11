> [!info] Each failure case in 2PC has a specific mitigation. None of them fully eliminate the blocking problem — they reduce it.


## Solution 1 — Write-Ahead Log (WAL) on every participant

Every participant writes its vote and the coordinator's decision to its WAL **before** applying anything. This makes crash recovery deterministic.

```
Phase 1 — participant receives PREPARE:
  1. Write "PREPARED for txn XYZ" to WAL
  2. Lock resources
  3. Send YES to coordinator

Phase 2 — participant receives COMMIT:
  1. Write "COMMIT for txn XYZ" to WAL
  2. Apply the change
  3. Release locks
  4. Send ACK
```

On recovery, the participant reads its WAL:
- WAL says PREPARED but no COMMIT/ABORT → contact coordinator, ask for decision
- WAL says COMMIT → replay and finish the commit
- WAL says ABORT → rollback and release locks

**What this fixes:** Failures 4 and 5 — participant crashes mid-commit or before receiving the Phase 2 message. Self-healing on recovery.

**What this doesn't fix:** The coordinator crash mid-Phase 2. The participant still needs to contact the coordinator to find out the decision.

---

## Solution 2 — Coordinator WAL + recovery

The coordinator also writes to WAL before doing anything:

```
Before sending COMMIT:
  1. Write "DECIDED COMMIT for txn XYZ" to WAL
  2. Send COMMIT to all participants

On coordinator recovery:
  1. Read WAL
  2. Find all in-doubt transactions
  3. Re-send the decision to any participant that hasn't ACKed yet
```

**What this fixes:** Coordinator crash mid-Phase 2. When the coordinator recovers, it reads its WAL, finds that it decided COMMIT for transaction XYZ, and re-sends COMMIT to any participant that missed it.

**What this doesn't fix:** The window between the coordinator crash and its recovery. Participants are still blocked holding locks during that window.

---

## Solution 3 — Coordinator timeout with ABORT

If the coordinator crashes after Phase 1 but hasn't written a COMMIT decision to WAL yet — on recovery it can safely ABORT.

```
Coordinator WAL has:
  "PREPARED — all participants voted YES — txn XYZ"
  (no COMMIT decision written yet)

→ Coordinator recovers, sees no COMMIT decision
→ Sends ABORT to all participants
→ Clean rollback
```

This works because: if the coordinator hadn't written COMMIT to WAL, no participant could have received a COMMIT message. So no participant committed anything. Safe to abort.

**What this fixes:** Coordinator crash after Phase 1 before deciding. Participants get unblocked quickly on coordinator recovery.

---

## Solution 4 — Participant cooperative termination (limited)

When a participant is in-doubt and the coordinator is unavailable, can participants talk to each other to figure out the outcome?

Partially. The rules are:

```
If ANY participant has already committed   →  everyone must commit
If ANY participant has already aborted     →  everyone must abort
If ALL participants are still in PREPARED  →  cannot decide — must wait for coordinator
```

The problem: **if all participants are in PREPARED state** (no one has committed or aborted yet), **they still cannot decide on their own**. They need the coordinator's decision. This is the fundamental blocking case that cooperative termination cannot solve.

**What this fixes:** Cases where at least one participant already knows the outcome — it can inform the others.

**What this doesn't fix:** The pure in-doubt case where all participants voted YES but none have received the coordinator's decision.

---

## Solution 5 — Replicated coordinator (eliminates SPOF)

The coordinator being a single point of failure is itself a problem. The fix: run the coordinator as a replicated service using consensus (Raft or Paxos).

```
Primary Coordinator  ──→  Replica 1
                     ──→  Replica 2
                     ──→  Replica 3
```

The coordinator writes its COMMIT/ABORT decision to a replicated log before sending it out. If the primary coordinator crashes, a replica takes over and has the full decision log — it can immediately continue sending COMMIT/ABORT to participants that haven't received it yet.

**What this fixes:** The coordinator SPOF. Recovery time drops from "wait for the crashed coordinator to restart" to "replica takeover in seconds."

**What this doesn't fix:** The fundamental latency of 2PC — two network round trips are still required regardless of coordinator redundancy.

This is what **Google Spanner** does — uses Paxos groups to replicate the coordinator, reducing the blocking window to the Paxos election time (typically milliseconds).

---

## Solution 6 — 3PC (Three-Phase Commit) — theoretical

3PC adds a third phase called "pre-commit" between PREPARE and COMMIT to eliminate the blocking problem.

```
Phase 1 — PREPARE     (same as 2PC)
Phase 2 — PRE-COMMIT  (coordinator tells everyone "I'm about to commit")
Phase 3 — COMMIT      (actual commit)
```

The idea: if the coordinator crashes after PRE-COMMIT, participants know the coordinator intended to commit. They can safely commit on their own without waiting.

**Why it's not used in practice:** 3PC only works in a network where messages are either delivered or timed out — no partitions. In real networks, a partition can make it impossible to distinguish "coordinator crashed" from "message lost." Under a partition, 3PC can still lead to split-brain. The added complexity isn't worth it.

---

## The honest answer — 2PC's blocking is inherent

No solution fully eliminates the blocking problem in 2PC. The fundamental issue is:

> A participant that voted YES cannot safely decide on its own. It needs external information (the coordinator's decision). If that information is unavailable, it must wait.

This is a proven theoretical result — you cannot have both safety (no inconsistency) and liveness (always makes progress) in a distributed system under all failure scenarios. **2PC chooses safety over liveness**. It will block rather than risk inconsistency.

---

## Where 2PC is actually used

2PC isn't dead — it's just narrow. It works in controlled environments where you own all the participants, the network is reliable, and throughput is manageable.

```
Google Spanner     →  2PC across shards internally, but coordinator is
                       Paxos-replicated so blocking window is milliseconds

CockroachDB        →  same — 2PC across nodes, Raft-replicated coordinator

XA Transactions    →  MySQL/Postgres distributed transactions across two
                       internal databases in the same company's infrastructure
                       e.g. two internal DBs that both need to commit together
```

The pattern is clear — 2PC only works when:

```
✓  you control ALL participants (same company, same infra)
✓  coordinator is replicated (not a SPOF)
✓  number of participants is small (2-3, not 20 microservices)
✓  throughput is low enough that locking is acceptable
✓  network is reliable (internal network, not public internet)
```

It breaks the moment you cross organisational or service boundaries — other banks, third-party APIs, independent microservices with their own databases.

---

## What to use instead at scale

For high-throughput systems or cross-service boundaries where 2PC's blocking and latency are unacceptable:

```
Use Saga instead:
→  No locks held across services
→  Each service commits locally and immediately
→  Failures handled by compensating transactions (undo actions)
→  Eventually consistent — but never blocking
```

The tradeoff: Saga gives up atomicity for availability. 2PC gives up availability for atomicity. Choose based on what your business can tolerate.

> [!tip] Interview framing
> "2PC's core problem is that it's a blocking protocol — a coordinator crash mid-Phase 2 leaves participants holding locks indefinitely. You mitigate this with WAL on both coordinator and participants for crash recovery, and a replicated coordinator to reduce the unavailability window. But you can't fully eliminate the blocking. 2PC only makes sense inside a controlled distributed DB like Spanner or CockroachDB where the coordinator is Paxos-replicated. For microservices or cross-organisational flows, use Saga instead."
