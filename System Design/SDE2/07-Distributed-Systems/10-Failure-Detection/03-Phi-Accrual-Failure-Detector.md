
> [!info] The core idea
> Instead of a fixed timeout that gives a binary alive/dead decision, Phi Accrual gives you a suspicion score — phi (φ) — that keeps growing the longer you don't hear from a server. You set your own threshold. The score is calculated based on the server's own historical heartbeat patterns, so a normally flaky server doesn't trigger false alarms.

---

## The problem with fixed timeouts

Heartbeats and gossip both rely on a fixed timeout — say 10 seconds of silence means dead. That works fine on a stable network. But networks are not always stable.

Imagine your network is having a bad day. High latency, packets arriving late. A heartbeat that normally arrives every 1 second is now arriving every 4 seconds due to congestion.

With a 5-second fixed timeout — you mark that server dead. But it's not dead. It's just slow. That's a **false positive** — you triggered an unnecessary re-election or failover.

Flip it — set the timeout to 30 seconds to avoid false positives. Now when a server actually crashes, you wait 30 seconds before detecting it. That's 30 seconds of routing requests to a dead server.

**Fixed timeout is a binary decision — alive or dead. No in-between. No adaptation.**

---

## The fix — a suspicion score

Phi Accrual replaces the binary decision with a **continuously growing suspicion score** called phi (φ).

```
φ = 0.5  → probably fine, heartbeat just a little late
φ = 1    → getting suspicious
φ = 5    → very likely dead
φ = 10   → almost certainly dead
```

You set your own threshold based on how much risk your system can tolerate:

- If false positives are expensive (unnecessary re-elections) — set threshold high, like φ = 10
- If missing a real failure is catastrophic — set threshold low, like φ = 3

The key difference from fixed timeout: **phi grows based on how late the heartbeat is compared to that server's own historical patterns** — not a hardcoded number.

---

## How it learns normal behavior — the sliding window

Every server keeps a **sliding window of the last N heartbeat arrival intervals** from each other server. Typically the last 200 heartbeats.

```
Last 10 heartbeat intervals from Server H:
1.1s, 0.9s, 1.0s, 1.2s, 0.8s, 1.1s, 1.0s, 0.9s, 1.1s, 1.0s
```

From this window it calculates:
- **Mean** — average interval (here ~1.0s)
- **Variance** — how much it fluctuates around the mean

A stable server has low variance. A flaky server has high variance.

When a heartbeat is late, the detector asks — given this server's history, how likely is it that a heartbeat this late is just a delay vs an actual crash? That probability is what phi is derived from.

```
Rock-solid server (low variance, always 1s):
→ 3 seconds late = extremely unusual
→ phi shoots up fast → crosses threshold quickly

Flaky server (high variance, anywhere from 1s to 4s):
→ 3 seconds late = totally within normal range
→ phi stays low → no false alarm triggered
```

The same 3-second delay means something completely different depending on the server's history. Fixed timeout treats both cases identically. Phi Accrual does not.

---

## Cassandra combines both

Cassandra does not choose between gossip and Phi Accrual — it uses both together, and they serve different purposes.

```
Gossip       → spreads cluster state (who joined, who left, current counters)
Phi Accrual  → decides when to actually mark a node as DEAD
```

Gossip is the information highway. Phi Accrual is the decision engine sitting on top of it. When gossip delivers counter updates, Phi Accrual evaluates those updates against the server's historical pattern and outputs a phi score. When phi crosses the threshold — the node is marked dead and gossip spreads that status to the rest of the cluster.

Cassandra's default phi threshold is **8**.

---

## The three failure detectors — when to use which

```
Heartbeats     → fixed ping, fixed timeout, binary alive/dead
                 best for: small clusters (Raft, ZooKeeper, 3–5 nodes)

Gossip         → counter table, O(log n) spread, scales to thousands
                 best for: large clusters (Cassandra, DynamoDB, Redis Cluster)

Phi Accrual    → suspicion score, learns per-server behavior, adaptive
                 best for: flaky networks, when false positives are expensive
                 (Cassandra uses gossip + phi accrual together)
```

> [!tip] Interview framing
> "Fixed timeouts are binary — alive or dead — and either cause false positives on slow networks or slow detection on long timeouts. Phi Accrual replaces this with a suspicion score that grows based on how late a heartbeat is relative to that server's own historical pattern. A flaky server that's always slow won't trigger a false alarm. A rock-solid server going silent for 3 seconds will. Cassandra uses gossip to spread state and Phi Accrual on top to make the actual dead/alive call, with a default threshold of phi = 8."
