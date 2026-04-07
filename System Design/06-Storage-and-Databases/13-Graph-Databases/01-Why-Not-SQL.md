# Why SQL Breaks for Relationship Queries

## The LinkedIn Problem

You're building LinkedIn's "People You May Know" feature. You have two tables:

```sql
users table              friendships table
id  | name               user_id | friend_id
----|------               --------|----------
1   | Alice              1       | 2
2   | Bob                1       | 3
3   | Charlie            2       | 4
4   | David              3       | 5
```

To find Alice's direct friends — 1 hop — simple:

```sql
SELECT friend_id FROM friendships WHERE user_id = 1;
-- Returns: 2, 3 (Bob, Charlie)
```

To find friends-of-friends — 2 hops — you need a join:

```sql
SELECT f2.friend_id
FROM friendships f1
JOIN friendships f2 ON f1.friend_id = f2.user_id
WHERE f1.user_id = 1;
```

Tracing through this with actual data:

```
Pass 1 (f1) — find Alice's friends:
  user_id=1 → friend_id=2 (Bob)
  user_id=1 → friend_id=3 (Charlie)

Pass 2 (f2) — find friends of Bob and Charlie:
  Bob (id=2)     → friend_id=4 (David)
  Charlie (id=3) → friend_id=5 (someone else)

Result: David and that someone — friends-of-friends of Alice
```

This works fine on a small table. The problem arrives at scale.

---

## The Exponential Join Problem

LinkedIn has 900 million users. The friendships table has **billions of rows**.

Each join reads the entire friendships table again:

```
1 hop  → 1 table scan   (fast)
2 hops → 2 table scans  (manageable)
3 hops → 3 table scans  (slow)
4 hops → 4 table scans  (minutes)
5 hops → 5 table scans  (unusable)
```

And it gets worse — each scan returns more rows than the last, because the fan-out grows with each hop. Alice has 500 friends → each has 500 friends → 250,000 friend-of-friends → each has 500 friends → 125 million nodes at 3 hops.

A 3-hop SQL query on LinkedIn's friendships table could take **minutes** — completely unusable for a real-time feature.

> [!danger] The root cause
> SQL stores relationships as rows. To traverse a relationship, you scan a table. More hops = more scans. The cost grows with both the number of hops AND the size of the table. Neither scales.

---

## Why This Is a Data Model Problem, Not Just a Performance Problem

You could add indexes, partition the friendships table, throw more hardware at it. It helps at 2 hops. It doesn't fundamentally fix 5+ hops.

The problem is that SQL was never designed for relationship traversal. A row in the friendships table has no direct connection to the user it points to — the database has to look it up every single time via an index or scan.

What you actually need is a data model where **relationships are first-class citizens** — stored with direct connections to the nodes they link, so traversal is just following a pointer rather than scanning a table.

That's exactly what a graph database provides.
