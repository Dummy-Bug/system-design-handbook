
> [!info] The core idea
> Instead of every server pinging every other server, each server gossips to just 2-3 random servers per round. Every server maintains a counter table for all nodes in the cluster. If a node's counter stops incrementing, it's assumed dead. Information spreads epidemically — like a rumour — reaching the entire cluster in O(log n) rounds.

---

## The problem with heartbeats at scale

With heartbeats, every server pings every other server directly. At 1000 nodes that's 1 million messages per second — just to check who's alive. Pure overhead, zero actual work.

Gossip solves this by making failure detection **distributed and lazy**. No server is responsible for monitoring everyone. Instead, information spreads naturally through random conversations between servers — exactly like a rumour spreading through an office.

---

## How gossip works

Every server maintains a **counter table** — one row per server in the cluster. It looks exactly like a vector clock, except instead of tracking causality, it tracks "how many gossip rounds have I heard from this server?"

```
Server A's counter table:
A → 42
B → 37
C → 31
D → 29
E → 40
F → 35
G → 33
H → 28   ← H's counter
```

Every second, each server increments its own counter and gossips its entire table to 2-3 randomly chosen servers.

```
Round 1:
A gossips to B and D
B gossips to C and F
C gossips to A and G
...
```

When Server B receives A's table, it merges — taking the max of each position, same as G-Counter merge. This way the highest known counter for every node propagates through the cluster quickly.

---

## How failure detection works — dead node

When H crashes, H stops incrementing its own counter. H's counter freezes at whatever value it was last seen at.

```
Everyone's table starts showing:
H → 28  (round 1)
H → 28  (round 2)
H → 28  (round 3)
...still 28 after 10 seconds
```

Each server independently tracks **when it last saw H's counter move**. After a configured timeout — say 10 seconds — if H's counter has not incremented at all, the server marks H as **SUSPECTED DEAD** in its own table.

```
Server A's updated table:
H → 28 [SUSPECTED DEAD]
```

Now when A gossips to B and C, it includes this status. B and C update their tables. They gossip to more servers. Within a few rounds — everyone in the cluster knows H is dead.

---

## How fast does the information spread?

Say you have 8 servers. Each server gossips to 2 others per round.

```
Round 1: A tells B, C     → 3 servers know H is dead
Round 2: B tells D, E     → 5 servers know
         C tells F, G     → 7 servers know
Round 3: everyone knows
```

3 rounds for 8 servers. For 1000 servers it takes about 10 rounds. This is **O(log n)** — logarithmic growth. Adding more servers barely increases the time to spread information.

> [!important] Compare this to heartbeats
> Heartbeats: O(n²) messages to detect failure
> Gossip: O(log n) rounds to propagate failure detection
> At 1000 nodes — heartbeats generate 1,000,000 messages/sec. Gossip generates roughly 3,000 messages/sec. A 300x reduction in traffic.

---

## How new node detection works

When a new server E comes online, it does not know about anyone else and no one knows about it yet. E contacts one or two **seed nodes** — a small list of well-known servers baked into E's config at startup.

```
New server E starts up
E → introduces itself → Seed node A
A adds E to its counter table with E's initial counter
A includes E in its next gossip round
```

Within a few gossip rounds, every server in the cluster has E in their counter table and starts tracking E's heartbeat counter. E also receives back the full cluster state from the seed nodes — so E quickly learns about all other servers too.

> [!tip] Seed nodes
> Cassandra, Redis Cluster, and most gossip-based systems ship with a `seeds` config. A new node only needs to reach one seed to bootstrap into the full cluster. Seed nodes are not special in any other way — they are just well-known entry points.

---

## The full picture

```
Normal operation:
Every server increments own counter → gossips table to 2-3 random servers → tables merge → everyone stays in sync

Node crashes:
Counter freezes → timeout expires → marked SUSPECTED DEAD → status gossips out → all servers know within O(log n) rounds

Node joins:
Contacts seed node → gets added to tables → status gossips out → all servers know within O(log n) rounds
```

> [!tip] Interview framing
> "Instead of every server pinging every other server — which is O(n²) traffic — gossip has each server share its state with just 2-3 random servers per round. Every server tracks a counter for every other node. If a counter stops moving past the timeout, the node is marked dead. That status propagates through gossip rounds like a rumour — reaching the entire cluster in O(log n) rounds. Cassandra and DynamoDB use this for their membership and failure detection layers."
