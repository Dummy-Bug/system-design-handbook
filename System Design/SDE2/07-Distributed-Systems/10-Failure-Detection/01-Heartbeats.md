
> [!info] The core idea
> Every server periodically sends an "I am alive" message to every other server. If a server stops sending for long enough, it's assumed dead. Simple and works well at small scale — but generates O(n²) traffic at large scale, making it unusable for clusters of hundreds or thousands of servers.

---

## How heartbeats work

You have a cluster of servers. Every server needs to know if any other server has crashed so it can stop sending requests to it or trigger a re-election.

The simplest approach — every server sends a periodic **heartbeat** to every other server. Like a pulse. If a server stops sending that pulse for a configured timeout, it is assumed dead.

```
Server A → heartbeat → Server B  (every 1 second)
Server A → heartbeat → Server C  (every 1 second)
Server A → heartbeat → Server D  (every 1 second)
```

If Server B stops receiving heartbeats from Server A for say 5 seconds — it marks Server A as failed and stops routing requests to it.

Simple, easy to implement, works well at small scale.

---

## The O(n²) problem

With 1000 servers, every server sends a heartbeat to every other server every second:

```
Each server sends:  999 heartbeats/sec
Total cluster:      1000 × 999 = ~1,000,000 heartbeats/sec
```

1 million heartbeat messages per second — purely to check if everyone is alive. Zero actual work. Pure overhead.

This is the **O(n²) problem** — as you add more servers, heartbeat traffic grows with the square of the number of servers. A cluster of 10,000 servers would generate 100 million heartbeats per second. Servers would spend more time sending heartbeats than doing real work.

> [!danger] Heartbeats don't scale
> Heartbeats are fine for small clusters of 3-5 nodes (like Raft or ZooKeeper). For large distributed systems with hundreds or thousands of nodes — Cassandra, DynamoDB, Redis Cluster — you need a different approach.

---

## How to detect a dead node

Every server tracks the **last heartbeat timestamp** it received from each other server. There is a configured timeout — say 5 seconds. If no heartbeat arrives within that window, the server is considered dead.

```
Server B received last heartbeat from A at T=100
Current time is T=106
Timeout is 5 seconds

T=106 - T=100 = 6 seconds > 5 second timeout
→ Server A is marked DEAD
```

Once marked dead, the cluster stops routing requests to that server. If it was a leader in a Raft/Paxos cluster, a new election is triggered.

> [!important] Timeout is a trade-off
> Too short a timeout — you get false positives. A slow network spike looks like a crash. You trigger unnecessary re-elections.
> Too long a timeout — real failures go undetected for too long. Clients keep hitting a dead server.
> Typical production timeout: 5–30 seconds depending on how critical fast detection is.

---

## How to detect a new node joining

When a new server comes online, it does the opposite — it announces itself by sending a heartbeat to one or more known servers in the cluster. Those servers register the new node, add it to their member list, and start expecting heartbeats from it.

```
New server E starts up
E → sends heartbeat → Server A
A adds E to its member list
A starts tracking E's heartbeat timestamp
```

In a gossip-based system, E only needs to contact one or two seed nodes. Those nodes spread the news of E's arrival through gossip — within a few rounds, every server in the cluster knows E exists.

> [!tip] Seed nodes
> Most distributed systems (Cassandra, Redis Cluster) have a configured list of "seed nodes" — a small set of well-known addresses a new server contacts on startup. The seed nodes already know the full cluster topology and help the new node bootstrap into the cluster.
