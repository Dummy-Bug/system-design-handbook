
> [!info] The core idea
> Raft needs exactly one leader at all times — the single node that accepts writes. Leader election is how nodes collectively pick that leader at startup, and automatically replace it when it dies.

---

## The chicken-and-egg problem

At startup, 5 nodes are all identical followers. No node is special. No central authority exists to assign a leader. You could say "randomly pick one" — but who does the picking? There's no coordinator.

You need consensus to elect a leader, but you need a leader to have consensus.

Raft breaks this with **randomized timers**.

---

## How election works

Each node is assigned a random election timeout — a value between 150ms and 300ms (configurable). When the timer fires and the node hasn't heard from a leader, it assumes no leader exists, nominates itself as a candidate, and asks every other node for a vote.

```
Node 1: timer = 150ms → fires first → nominates itself → requests votes
Node 2: timer = 210ms → still waiting → receives Node 1's request → votes for Node 1
Node 3: timer = 240ms → still waiting → receives Node 1's request → votes for Node 1
Node 4: timer = 270ms → still waiting → receives Node 1's request → votes for Node 1
Node 5: timer = 300ms → still waiting → receives Node 1's request → votes for Node 1

Node 1: 5/5 votes → elected leader
```

Because timers are random, one node almost always fires first. By the time the others wake up, they've already received a vote request — so they vote for the first candidate instead of nominating themselves. Election done cleanly.

> [!important] Why odd number of nodes?
> With even nodes you can get a perfect split — 2 votes each with 4 nodes, nobody wins. With odd nodes (3, 5, 7), majority is always achievable. Raft recommends odd numbers for exactly this reason.

---

## Heartbeats — how followers know the leader is alive

Once elected, the leader continuously sends **heartbeats** to all followers — a periodic "I'm still here" signal. As long as followers receive heartbeats, they reset their election timer and stay idle.

```
Leader → heartbeat → Follower A ✓ (timer reset)
Leader → heartbeat → Follower B ✓ (timer reset)
Leader → heartbeat → Follower C ✓ (timer reset)
```

The moment heartbeats stop arriving, the timer fires. The follower assumes the leader is dead and immediately starts a new election.

---

## Re-election

Re-election is triggered automatically — no coordinator needed. If a follower's timer fires without receiving a heartbeat, it nominates itself and asks for votes. The process is identical to the initial election.

```
Leader crashes...

Follower A: no heartbeat → timer fires → nominates itself
Follower B: no heartbeat → timer fires → receives A's request → votes for A
Follower C: no heartbeat → timer fires → receives A's request → votes for A

Follower A: majority → new leader elected
```

If two candidates emerge simultaneously and split the votes, no majority is reached. Every node resets with a new random timer and a fresh election round begins. Because timers are random, the same collision is extremely unlikely to happen twice — a leader is elected within a round or two.

---

## What if the network partially fails?

Say the leader can reach Node 4 but not Nodes 2 and 3. Nodes 2 and 3 stop receiving heartbeats, assume the leader is dead, and start an election.

But to win, a candidate needs **majority** — 3 out of 5 nodes. Nodes 2 and 3 can only get 2 votes between them. Node 4 still hears from the leader and won't vote. No majority reached — the election fails.

Meanwhile, the original leader is still alive and still sending heartbeats to Node 4. But can it commit writes?

Raft requires majority acknowledgment before committing. With only 2 nodes (leader + Node 4), it cannot reach majority out of 5. So writes stall — the leader stops making progress.

```
Normal state (5 nodes):
Leader → Node 2 ✓
       → Node 3 ✓
       → Node 4 ✓
       → Node 5 ✓
Majority = 3 acks needed → easy

Partial partition (leader isolated from 2 and 3):
Leader → Node 4 ✓
       → Node 5 ✓
Only 2 acks reachable (+ itself = 3) → depends on whether Node 5 is reachable
If only Node 4 reachable → 2 acks total → cannot reach majority → writes stall
```

Two outcomes:
1. **Network heals** — Nodes 2 and 3 start receiving heartbeats again, cancel their election, go back to being followers. Cluster resumes normally.
2. **Network stays broken** — Nodes 2 and 3 keep re-electing with no majority. Leader keeps running but cannot commit writes. Cluster is effectively frozen until the partition heals.

> [!important] This is Raft being safe over available
> Raft will never allow a split-brain write. It would rather stall writes entirely than risk two leaders committing conflicting data. This is a deliberate CP trade-off (Consistency over Availability in CAP terms).

---

## Election safety — only the most up-to-date node can win

This is one of the most critical rules in Raft and it's what guarantees committed data is never lost.

A follower will **refuse to vote** for a candidate whose log is behind its own. The candidate must have a log that is at least as up-to-date as the voter's log. If the candidate is behind, the vote is rejected.

Why does this matter? Say the leader committed entry 5 and then died permanently. Majority of followers already have entry 5 in their WAL (that's why the leader was allowed to commit it). Now an election starts.

```
Follower A: log = [1, 2, 3, 4, 5] ← has committed entry
Follower B: log = [1, 2, 3, 4, 5] ← has committed entry
Follower C: log = [1, 2, 3, 4]    ← was slow
Follower D: log = [1, 2, 3, 4]    ← was slow

C nominates itself → asks A for vote
A: "my log has index 5, yours has index 4 — you're behind" → rejects vote

Only A or B can win the election — they are the only ones with the complete log.
```

The new leader (A or B) sees entry 5 as uncommitted on its log, recognizes majority has it, and auto-commits it. Same value, same index — committed properly under the new leader. The client already got "success" from the old leader and never knew the difference.

> [!important] Election safety rule
> The candidate with the most up-to-date log always wins. This single rule guarantees that a newly elected leader always has every entry that was ever committed — so committed data survives even permanent leader failure.

The only scenario where data is truly lost is if more than ⌊N/2⌋ nodes die permanently at the same time — meaning quorum is gone entirely. At that point Raft cannot make progress and there is nothing to be done.

---

→ See [[03-Term-Numbers]] for how Raft handles the ghost leader — an old leader that comes back after a partition thinking it's still in charge

