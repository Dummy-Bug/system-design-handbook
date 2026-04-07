# Graph Databases — Overview

> [!info] What is a Graph Database?
> A NoSQL database where data is stored as **nodes** (entities) and **edges** (relationships between entities). Optimized for traversing relationships — following connections from one entity to another across multiple hops.

---

## Where It Sits in the NoSQL Landscape

```
NoSQL
├── Key-Value      → Redis, DynamoDB       (ultra-fast simple lookups)
├── Document       → MongoDB               (flexible nested JSON)
├── Column-Family  → Cassandra, Bigtable   (write-heavy, time-series)
├── Graph          → Neo4j                 (relationship traversal)
└── Search         → Elasticsearch         (full-text ranked search)
```

Each NoSQL type sacrifices generality to be exceptional at one specific thing. Graph DB sacrifices bulk scanning to be exceptional at multi-hop relationship traversal.

---

## The Core Problem It Solves

SQL represents relationships as rows in a junction table. To traverse a relationship, you join tables. Each additional hop requires another join on a potentially billion-row table — cost grows exponentially with depth.

Graph databases store relationships as **first-class citizens** with direct disk pointers between nodes. Traversing a relationship is just following a pointer — O(1) per hop, regardless of total database size.

---

## Key Concepts

| Concept | What it is |
|---|---|
| Node | An entity (User, Product, City, Account) |
| Edge | A relationship between two nodes (FRIENDS_WITH, BOUGHT, BORN_IN) |
| Property | Data attached to a node or edge ({name: "Alice"}, {since: 2020}) |
| Index-free adjacency | Each node stores direct pointers to its edges — no index scan needed |
| Cypher | Neo4j's query language — reads like a picture of the graph |

---

## When to Use a Graph DB

- Relationships are the **primary thing being queried**, not the data itself
- Queries involve **3+ hops** through relationships
- The relationship pattern itself is meaningful (fraud rings, social connections)

## When NOT to Use

- Bulk scans on node data ("give me all users over 30") — SQL is better
- Simple key lookups — Key-Value store is better
- The data is relational but queries rarely traverse more than 1-2 hops — SQL with indexes is fine
