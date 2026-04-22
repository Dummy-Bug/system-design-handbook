## The Design Philosophy

Cypher is Neo4j's query language. It was designed to look like the graph itself — so you can read a query and immediately visualize the pattern it's matching.

The syntax uses:
- `()` for nodes — shaped like a circle
- `-[:EDGE_TYPE]->` for directed relationships — shaped like an arrow
- `{}` for property filters

---

## Basic Syntax

```cypher
MATCH (a:User {id: 1})-[:FRIENDS_WITH]->(b:User)
RETURN b
```

Read this left to right like a picture:

```
(a: User with id=1)  ──[FRIENDS_WITH]──▶  (b: any User)
      start                                    result
```

Find User with id=1, follow all `FRIENDS_WITH` edges, return whoever is on the other end.

---

## Multi-Hop Queries

**2 hops — friends of friends:**

```cypher
MATCH (u:User {id: 1})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(fof)
RETURN fof
```

```
(User 1) ──▶ (friend) ──▶ (fof)
   hop 1        hop 2
```

**3 hops — one level deeper:**

```cypher
MATCH (u:User {id: 1})-[:FRIENDS_WITH]->(f1)-[:FRIENDS_WITH]->(f2)-[:FRIENDS_WITH]->(f3)
RETURN f3
```

Just add one more arrow. No extra join. No extra table scan.

**Compare to SQL for the same 3-hop query:**

```sql
-- SQL: 3 joins on a billion-row table
SELECT f3.friend_id
FROM friendships f1
JOIN friendships f2 ON f1.friend_id = f2.user_id
JOIN friendships f3 ON f2.friend_id = f3.user_id
WHERE f1.user_id = 1;
```

Same result, but SQL scans the friendships table three times. Cypher follows pointers three times. At billion-row scale, the difference is minutes vs milliseconds.

---

## Variable-Length Paths

Cypher has a shorthand for "follow this relationship type between 1 and N hops":

```cypher
-- Find all users reachable within 3 hops
MATCH (u:User {id: 1})-[:FRIENDS_WITH*1..3]->(other)
RETURN other
```

The `*1..3` means "follow FRIENDS_WITH between 1 and 3 times". This is equivalent to writing out 1-hop, 2-hop, and 3-hop queries and combining the results — but in one line.

---

## Shortest Path

```cypher
-- Find the shortest connection between Alice and a CEO
MATCH path = shortestPath(
  (alice:User {name: "Alice"})-[:FRIENDS_WITH*]-(ceo:User {title: "CEO"})
)
RETURN path
```

This runs BFS under the hood — exactly like the shortest path algorithm from DSA, but on the stored graph. SQL has no equivalent without recursive CTEs that become unusably slow beyond a few hops.

---

## Creating Data

```cypher
-- Create two users and a friendship between them
CREATE (a:User {id: 1, name: "Alice"})
CREATE (b:User {id: 2, name: "Bob"})
CREATE (a)-[:FRIENDS_WITH {since: 2021}]->(b)
```

---

## Deleting Data

```cypher
-- Must delete relationships before deleting a node
MATCH (b:User {id: 2})-[r]-()
DELETE r

MATCH (b:User {id: 2})
DELETE b
```

Neo4j will throw an error if you try to delete a node that still has edges attached. This prevents dangling pointers in the storage layer.
