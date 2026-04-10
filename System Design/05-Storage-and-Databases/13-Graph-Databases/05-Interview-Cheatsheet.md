## One-Line Definition

> [!info]
> A NoSQL database where entities are **nodes** and relationships are **edges** stored with direct disk pointers — making multi-hop relationship traversal O(1) per hop instead of O(n) per SQL join.
no 
---

## Why Not SQL?

```
SQL joins on relationships:
  1 hop  → 1 table scan   ✅ fast
  2 hops → 2 table scans  ✅ ok
  3 hops → 3 table scans  ⚠️ slow at scale
  5 hops → 5 table scans  ❌ minutes on billion-row tables
```

Each join scans the entire relationships table again. Cost = hops × table size.

Graph DB: each hop follows a disk pointer. Cost = O(1) per hop, regardless of database size.

---

## Data Model

```
Node  → entity       (User, Product, Account, City)
Edge  → relationship (FRIENDS_WITH, BOUGHT, BORN_IN, USES_PHONE)
Both can have properties {key: value}
```

> [!important]
> A "friend" is not a separate node type — it's a `User` node connected by a `FRIENDS_WITH` edge. Relationships live on edges, not in separate tables.

---

## Cypher Cheatsheet

```cypher
-- 1 hop: direct friends
MATCH (u:User {id:1})-[:FRIENDS_WITH]->(friend)
RETURN friend

-- 2 hops: friends of friends
MATCH (u:User {id:1})-[:FRIENDS_WITH]->(f1)-[:FRIENDS_WITH]->(fof)
RETURN fof

-- Variable length: up to 3 hops
MATCH (u:User {id:1})-[:FRIENDS_WITH*1..3]->(other)
RETURN other

-- Shortest path
MATCH path = shortestPath((a:User {name:"Alice"})-[:FRIENDS_WITH*]-(b:User {name:"Bob"}))
RETURN path
```

---

## Use Cases

| Use case | Why graph? |
|---|---|
| Social graph (LinkedIn, Twitter) | Friends-of-friends, shortest path between users |
| Fraud detection (PayPal, Uber) | Multi-hop shared identifier patterns across accounts |
| Recommendations (Amazon) | Users who bought X also bought Y — edge traversal |
| Knowledge graph (Google) | Entity relationships — Obama → born in → Honolulu |

---

## Deletion Rule

> [!danger] Must delete edges before deleting a node
> Neo4j refuses to delete a node with existing edges — prevents dangling pointers. Always delete relationships first, then the node.

---

## Scale Reality Check

```
Neo4j (off-the-shelf)     → fraud detection, social graphs, recommendations
                            millions to low billions of nodes, supports clustering

Google Knowledge Graph    → custom-built, billions of entities, planet scale
                            not achievable with any off-the-shelf tool
```

---

## When NOT to Use

> [!danger] Graph DB is bad at bulk scans
> "Give me all users over 30" — use SQL. Graph DBs optimize for traversal, not attribute-based filtering across many nodes.

**The signal:**
- Query starts at one node, follows edges → Graph DB
- Query scans a collection by attribute → SQL
