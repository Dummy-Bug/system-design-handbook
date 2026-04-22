
> [!info] The core idea
> A leader doesn't always die cleanly — sometimes it just gets temporarily cut off from the network. When it comes back, it still thinks it's the leader. Term numbers are how Raft tells the old leader "you're outdated, step down."

---

## The ghost leader problem

The old leader didn't die. The network between it and the followers broke. Followers stopped receiving heartbeats, assumed the leader was dead, and elected a new one.

Then the network heals. Now you have two nodes both believing they are the leader — **split-brain**.

```
Normal state:
App Servers → Leader (Term 1) → Follower A
                              → Follower B
                              → Follower C

Network partition:
App Servers → Leader (Term 1) [isolated from followers]
              Follower A → times out → starts election → Term 2
              Follower B → votes for Follower A
              Follower C → votes for Follower A
              Follower A → majority → new leader (Term 2)

Network heals:
Leader (Term 1) comes back — still thinks it's in charge
New Leader (Term 2) is already accepting writes
Two leaders simultaneously ✗
```

> [!danger] This is split-brain
> Both leaders accept writes independently. Data diverges silently. This is the worst failure mode in a distributed system.

---

## Term numbers — the single source of truth

Every election increments a **term number** — a monotonically increasing counter that never goes backwards. It is also called an epoch number.

```
Original leader elected → Term 1
Leader unreachable → followers start election → Term 2
New leader elected → Term 2
```

Every single message a leader sends — heartbeat, AppendEntries, commit notification — carries its term number.

When the old leader comes back and sends a heartbeat with Term 1, every node compares it against their current term:

```
Old leader → heartbeat (Term 1) → Follower A
Follower A: "I'm on Term 2 — Term 1 is outdated"
Follower A → rejects heartbeat → sends back Term 2

Old leader receives rejection with Term 2
Old leader: "Term 2 > my Term 1 — a new election happened while I was gone"
Old leader → immediately steps down → becomes a follower
```

The old leader has no choice. Higher term always wins. It cannot fake a higher term because term numbers are determined by elections — not by any single node unilaterally.

> [!important] Term numbers are monotonically increasing
> They never decrease. Each new election bumps the term by 1. This makes ghost leader rejection automatic — the old leader sees a higher term and immediately knows it has been replaced.

---

## What happens to the old leader's writes?

The old leader may have accepted writes during the partition window — from app servers that were still able to reach it. Those writes were never replicated to the majority of followers, so they were never committed.

When the old leader steps down and becomes a follower, the new leader sends it a sync message. The new leader compares logs and force-overwrites the old leader's uncommitted entries to match its own log.

```
Old leader had: [entry1, entry2, entry3-uncommitted]
New leader has: [entry1, entry2]

New leader → force sync old leader → old leader's log becomes [entry1, entry2]
entry3 discarded ✓
```

Uncommitted entries on the old leader are safely discarded — they were never committed, so no client ever received "success" for them. The client will retry, and the new leader will handle the write.

> [!important] Only uncommitted entries are discarded
> Committed entries are never lost. By definition, a committed entry was acknowledged by majority — and the new leader was elected from that majority, so it already has every committed entry.

---

## Term numbers in practice

This is not just a Raft concept. The general idea — a monotonically increasing epoch number that lets nodes reject stale leaders — appears everywhere in distributed systems under different names:

- Raft calls it **term number**
- Other systems call it **epoch**, **generation**, or **fencing token**
- ZooKeeper calls it **zxid**

The pattern is always the same: new leader gets a higher number, old leader's messages carry a lower number and get rejected.
