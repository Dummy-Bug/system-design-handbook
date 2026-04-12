
> [!info] The core idea
> In a distributed system, certain tasks must be owned by exactly one node at a time — the leader. Leader election is the process by which nodes collectively agree on who that single owner is, and automatically replace them if they die.

---

## Why a lock isn't enough

Imagine 5 app servers all running the same cron job — every midnight, send birthday emails to users. If all 5 run it simultaneously, every user gets 5 emails.

The obvious fix is a distributed lock — one server grabs the lock in Redis, runs the job, releases it when done. This works for a cron job.

But now think about a **database primary**. The primary is the single node that accepts all writes. If it dies, you need a new primary immediately and automatically, with every other node agreeing on who the new primary is. No two nodes can think they're the primary at the same time — that's split-brain, and it corrupts your data.

A Redis lock with TTL doesn't cut it here. TTL means waiting for the timeout before anyone else can take over. And if the job takes longer than the TTL, two servers run it simultaneously anyway.

What you need is a **permanent designated owner with a proper re-election mechanism** — not a temporary lock.

---

## Heartbeats — how followers know the leader is alive

The leader continuously sends **heartbeats** to all followers — a periodic "I'm alive" signal. As long as followers receive heartbeats, they know the leader is healthy and do nothing.

The moment heartbeats stop, followers know the leader is dead and immediately kick off a new election. No TTL. No waiting. Instant detection.

```
Leader → heartbeat → Follower A ✓
Leader → heartbeat → Follower B ✓
Leader → heartbeat → Follower C ✓

Leader crashes...

Follower A: no heartbeat received → start election
Follower B: no heartbeat received → start election
Follower C: no heartbeat received → start election
```

---

## The election problem — everyone wants to be captain

When the leader dies, all followers notice simultaneously. If every node simply declares itself the new leader, you have split-brain from the start — like the Pirates of the Caribbean scene where every pirate votes for themselves as captain.

Raft solves this with **randomized timers**.

Every node is assigned a random election timeout — say Node 1 gets 150ms, Node 2 gets 300ms, Node 3 gets 450ms. Each node waits for its timer before declaring itself a candidate.

```
Node 1: timer = 150ms → fires first → declares candidacy → requests votes
Node 2: timer = 300ms → still waiting → receives Node 1's vote request → votes for Node 1
Node 3: timer = 450ms → still waiting → receives Node 1's vote request → votes for Node 1

Node 1: 3 votes → majority → elected leader
```

The node with the shortest timer wakes up first. By the time it asks others for votes, they haven't declared themselves candidates yet — so they vote for it. Election done cleanly.

> [!important] Why odd number of nodes?
> With even nodes you can get a perfect split — 2 nodes vote for Node A, 2 vote for Node B, nobody wins. Raft recommends odd numbers (3, 5, 7) so the tie-breaking vote always exists.

---

## What if two nodes get the same timer?

Both wake up simultaneously, both vote for themselves, and ask the remaining nodes for votes. The remaining nodes vote for whichever request arrives first — and with an odd total node count, one candidate always gets majority.

If somehow nobody reaches majority (e.g. even node count with a perfect split), **re-election** kicks in automatically. Every node resets and gets a new randomized timeout. Since the timeouts are random, it's extremely unlikely the same collision happens twice. A leader gets elected on the next round.

---

## The Ghost Leader Problem

A leader doesn't always die cleanly — sometimes it just gets temporarily cut off from the network. Followers stop receiving heartbeats, assume it's dead, and elect a new leader. Then the network heals. Now you have two nodes both believing they are in charge — **split-brain**.

```
Normal state:
App Servers → Leader → Follower A
                     → Follower B

Network partition:
App Servers → Old Leader [isolated from followers]
              Follower A → elects new leader
              Follower B → votes for new leader

Network heals:
Old Leader comes back — still thinks it's in charge
New Leader is already accepting writes
Two leaders simultaneously ✗
```

> [!danger] This is split-brain
> Both leaders accept writes independently. Data diverges silently.


