## Cluster vs Shard vs Replica Set — Getting the Words Right

Before we touch the hash ring, we need to be precise about terminology. These words get thrown around loosely, and confusing them leads to confused designs.

### Cluster

The **entire system**. All 1,200 nodes together — that's the cluster. When we say "the KV store," we mean the cluster. Every node, every piece of data, every connection — it's all one cluster.

### Shard (aka Partition)

A shard is a **range of keys** — not a group of nodes. Think of it as a slice of the total key space. If the hash ring goes from 0 to 1,000,000, then:

```
Shard 1: keys that hash to range 0 - 999
Shard 2: keys that hash to range 1000 - 1999
Shard 3: keys that hash to range 2000 - 2999
...and so on
```

When `put("user:123", value)` comes in, we hash `"user:123"` and get a number — say 1500. That falls in Shard 2's range. So the data belongs to Shard 2.

A shard is **just a key range**. It's not a machine. It's not a group of machines. It's a logical division of the data.

### Replica Set (for a shard)

Each shard's data is replicated across N nodes for durability (in our case N=3). The 3 nodes that hold copies of Shard 2's data are Shard 2's **replica set**.

```
Shard 2 (key range 1000-1999):
  → Node B has a copy
  → Node C has a copy  
  → Node D has a copy
  
  These 3 nodes are Shard 2's replica set.
```

### The key insight — nodes hold MULTIPLE shards

This is the part that surprises people. A single node doesn't just hold one shard's data — it holds data for **multiple shards**. And different shards overlap on different nodes.

```
Shard 1 (range 0-999):      stored on Node A, Node B, Node C
Shard 2 (range 1000-1999):  stored on Node B, Node C, Node D
Shard 3 (range 2000-2999):  stored on Node C, Node D, Node E
```

Look at Node B — it's in the replica set for both Shard 1 and Shard 2. Node C holds data for all three shards. Every node participates in multiple shards.

This happens naturally because of how the consistent hashing ring works. Each node owns a position on the ring, and a shard's replicas are the next N nodes clockwise from the shard's range. Since nodes are spread around the ring, the replica sets for adjacent shards overlap.

```
Ring position:    0 -------- 1000 -------- 2000 -------- 3000
                  |           |             |             |
Nodes on ring:   A           B             C             D, E
                  
Shard 1 (0-999):     primary=A, replicas=B,C  (next 2 nodes clockwise)
Shard 2 (1000-1999): primary=B, replicas=C,D
Shard 3 (2000-2999): primary=C, replicas=D,E
```

> [!important] A shard is NOT "3 nodes holding the same data"
> A shard is a key range. That key range's data is replicated across 3 nodes (the replica set). But each of those nodes also holds data for other shards. Don't think of a shard as a group of machines — think of it as a slice of the key space that happens to be stored on multiple machines.

---

## Why This Matters

This overlap is what makes the system efficient. If each shard had its own dedicated group of 3 machines that did nothing else:

```
Bad: 1,200 nodes ÷ 3 nodes per shard = 400 shards
     Each node only serves 1 shard's traffic
     If that shard is cold (no one reading those keys), the node sits idle
```

With overlapping replica sets:

```
Good: Each node serves multiple shards
      Traffic is spread more evenly
      If one shard is hot, the load is shared across nodes that also serve other shards
      No node sits idle — everyone participates in multiple shards
```

This is a direct consequence of the consistent hashing ring. The ring doesn't divide nodes into isolated groups — it creates a continuous, overlapping assignment where every node is a neighbor to multiple shards.


## Cluster — The Bigger Picture

Everything above describes what happens inside **one cluster** — one set of 1,200 nodes in one region. But the word "cluster" itself can be confusing, because there are different reasons you might have multiple clusters.

### One cluster = one region, one set of nodes

Our system right now is one cluster: 1,200 nodes in a single datacenter, holding all the data, serving all the traffic. Simple.

### Two clusters, same data (multi-region replication)

If you replicate all the data to another region — say US-East and EU-West — each region has its own cluster. Both clusters hold **the same data**. This is done for:

- **Disaster recovery** — if the US-East datacenter burns down, EU-West still has everything
- **Low-latency reads** — EU users read from the EU cluster instead of crossing the ocean

```
US-East cluster (1,200 nodes):  has ALL keys → serves US users
EU-West cluster (1,200 nodes):  has ALL keys → serves EU users

Data replicates between them — both clusters have the same data.
If US-East dies, EU-West still serves everyone.
```

### Two clusters, different data (data partitioning by region)

Alternatively, each region's cluster holds **only that region's data**. EU users' data lives exclusively in the EU cluster, NA users' data lives exclusively in the NA cluster. They don't replicate to each other.

This is often driven by **data residency laws** — GDPR requires that EU citizens' personal data stays within the EU. You can't replicate it to a US datacenter.

```
EU cluster (600 nodes):  has only EU users' keys → serves EU users
NA cluster (600 nodes):  has only NA users' keys → serves NA users

No replication between them — completely independent systems.
EU data never leaves EU. NA data never leaves NA.
```

### Both setups are called "clusters"

The word "cluster" just means "a group of nodes that work together as one system." Whether two clusters hold the same data or different data depends on the use case. The distinction matters for interviews:

- Interviewer says "make it multi-region for disaster recovery" → same data, two clusters
- Interviewer says "handle GDPR compliance" → different data, two clusters
- Interviewer says "both" → different data per region, but each region's cluster replicates to a backup region
