> [!info] What is a Graph Database?
> A NoSQL database where data is stored as **nodes** (entities) and **edges** (relationships between entities). Optimized for traversing relationships — following connections from one entity to another across multiple hops.

## The Three Building Blocks

A graph database has three things: nodes, edges, and properties. That's it.

### Nodes

A node is an entity. In a social network, every user is a node. In a fraud detection system, every account, phone number, and device is a node. Nodes have a **label** (their type) and **properties** (their data).

```
(User {id: 1, name: "Alice", age: 28})
(User {id: 2, name: "Bob", age: 32})
(Phone {number: "+1-555-1234"})
(Device {id: "iPhone-XYZ-789"})
```

The parentheses `()` represent nodes — this is Cypher notation and it's deliberately shaped like a circle to match the graph diagram convention.

### Edges

An edge is a relationship between two nodes. Edges are **directional** (they point from one node to another) and have a **type** that describes the relationship.

```
(Alice) ──[FRIENDS_WITH]──▶ (Bob)
(Alice) ──[BOUGHT]──▶ (iPhone 15)
(Barack Obama) ──[BORN_IN]──▶ (Honolulu)
```

> [!important] A friend is also a User node
> There is no separate "Friend" node type. Both Alice and Bob are `User` nodes. The friendship is expressed by the `FRIENDS_WITH` edge between them. The relationship lives on the edge, not in a separate table.

### Properties

Both nodes and edges can carry properties — key-value pairs of data:

```
Node property:  (User {name: "Alice", joined: 2019})
Edge property:  (Alice)-[:FRIENDS_WITH {since: 2021}]->(Bob)
```

The edge property `{since: 2021}` tells you when they became friends — data that lives on the relationship itself. In SQL, this would require extra columns in the junction table. In a graph DB, it's a natural part of the edge.

---

## Index-Free Adjacency — Why Traversal Is Fast

This is the core architectural difference from SQL.

In SQL, finding Bob's friends means scanning the friendships table for rows where `user_id = Bob's id`. Even with an index, you're doing a B+Tree lookup every single hop.

In a graph database, each node stores **direct disk pointers** to its edges:

```
Node (Alice) stored at disk block 4821
  data: {name: "Alice", age: 28}
  edge pointer ──▶ Edge (FRIENDS_WITH) at block 7203
                        start: block 4821  (Alice)
                        end:   block 9034  (Bob)
                        ──▶ Node (Bob) at block 9034
                                data: {name: "Bob"}
                                edge pointer ──▶ ...
```

Following Alice's friendship to Bob is just:
1. Read Alice's node — get edge pointer (block 7203)
2. Read that edge — get Bob's node pointer (block 9034)
3. Read Bob's node — done

No table scan. No index lookup. Just reading disk blocks by their stored addresses — like following a linked list.

> [!info] Why "index-free adjacency"?
> In SQL, to find a node's neighbors you need to query an index ("find all rows where user_id = X"). In a graph DB, the node itself already knows where its neighbors are — the adjacency information is stored directly on the node. No index needed.

The cost of each hop is **O(1)** — constant, regardless of how many total nodes exist in the database. A 5-hop traversal on a graph with 1 billion nodes costs the same per hop as on a graph with 1000 nodes.

Compare to SQL: each join's cost grows with the size of the table being joined.

---

## Deletion — The Edge Cleanup Requirement

Because **nodes store pointers to edges, and edges store pointers to nodes**, deleting a node carelessly would leave dangling pointers.

If you delete Bob's node without removing the `FRIENDS_WITH` edge, Alice's edge pointer now points to a block that no longer contains a valid node.

Neo4j prevents this by **refusing to delete a node that still has edges**. You must delete all edges first, then the node:

```cypher
-- Delete all of Bob's relationships first
MATCH (b:User {id: 2})-[r]-()
DELETE r

-- Then delete Bob
MATCH (b:User {id: 2})
DELETE b
```

This makes deletions more expensive than SQL (where `DELETE FROM users WHERE id = 2` with `CASCADE` handles everything). The trade-off is acceptable because graph databases are read-heavy — the fast traversal is worth the slower deletes.
