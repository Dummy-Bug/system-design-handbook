## Gossip Protocol — How Nodes Share Information

Every few seconds (typically once per second), each node picks a **random** neighbor and exchanges membership information — which nodes exist, which ranges they own, who's alive, who's dead.

Why random? Because it determines how fast information propagates. If nodes always talked to the same neighbors, information would travel in a chain — A → B → C → D — taking O(n) to reach everyone. With random selection, each round roughly **doubles** the number of nodes that know the update:

```
Round 1:  1 node knows   → tells 1 random   → 2 know
Round 2:  2 nodes know   → each tells 1      → 4 know
Round 3:  4 → 8
Round 4:  8 → 16
Round 5:  16 → 32
...
Round 11: 1024 → 2048
```

For 1,200 nodes, that's about **11 rounds** (~11 seconds at 1 round/sec) to reach the entire cluster. That's O(log n) propagation — the same pattern as how rumors spread, which is why it's called "gossip."

---

## What Gets Shared — Heartbeat Counters, Not Timestamps

Each node maintains a **heartbeat counter** that it increments every gossip round. When two nodes gossip, they exchange their view of the entire cluster — for each node, the latest heartbeat counter they've seen.

Why heartbeat counters instead of timestamps? Timestamps require synchronized clocks across all 1,200 nodes. Clock drift between machines would cause nodes to disagree about which information is newer. A heartbeat counter is local to each node — no coordination needed, no drift possible.

```
Node A's membership table:
  Node B: heartbeat 204, status alive
  Node C: heartbeat 187, status alive
  Node D: heartbeat 101, status alive
  Node E: heartbeat 312, status alive
```

When Node A gossips with Node B, they compare their tables entry by entry. For each node, whoever has the **higher heartbeat counter** has the newer information:

```
Node A believes: "Node D, heartbeat 101"
Node B believes: "Node D, heartbeat 98"

101 > 98 → Node A's info is newer → Node B updates its view of Node D
```

After the exchange, both Node A and Node B have the same (latest) view of Node D. In the next round, they'll each gossip with someone else, spreading this updated view further.

---

## Detecting Dead Nodes — Heartbeat Stops Incrementing

If a node is alive, it increments its heartbeat counter every round and gossips it out. The counter keeps going up. If a node **dies**, it stops gossiping — its counter is frozen.

Every node tracks when it last saw each other node's heartbeat counter **increase**. If the counter hasn't changed for a threshold period (say 8-10 seconds), something is wrong:

```
Node A's view of Node D over time:

Time 0s:   heartbeat 99   → counter went up → D is alive
Time 1s:   heartbeat 100  → counter went up → D is alive
Time 2s:   heartbeat 101  → counter went up → D is alive
Time 3s:   heartbeat 101  → same counter...
Time 4s:   heartbeat 101  → still same...
Time 5s:   heartbeat 101  → hasn't changed for 3 seconds
...
Time 10s:  heartbeat 101  → hasn't changed for 8 seconds → D might be down
```

---

## The False Positive Problem — Don't Trust One Node's Opinion

Node A hasn't seen Node D's heartbeat increase for 8 seconds. Is Node D dead? Not necessarily. Maybe the network between Node A and Node D is temporarily broken, but Node D is perfectly healthy and gossiping with other nodes.

Gossip self-corrects this. When Node A gossips with Node C, Node C might have fresher information:

```
Node A believes: "Node D, heartbeat 101" (hasn't changed for 8 seconds)
Node C believes: "Node D, heartbeat 105" (heard from D 2 seconds ago)

105 > 101 → Node C's info is newer → Node A updates its view
→ Node A realizes Node D is alive after all
```

But what if Node A gossips with Node B first, and Node B also hasn't heard from Node D? Both agree Node D seems dead. They start spreading "Node D is down." Then Node C comes along with heartbeat 105 — now conflicting information is propagating through the cluster.

This is why real systems don't go straight from "alive" to "dead." They use an intermediate state:

```
Simple (dangerous):   alive → dead

Real systems:         alive → suspected → dead (only if confirmed)
```

A single node's inability to reach another node isn't proof that the target is dead — it could be a network issue between those two specific nodes. A node is only marked **dead** when enough evidence accumulates from multiple nodes. This suspicion mechanism prevents false positives from cascading through the cluster.
