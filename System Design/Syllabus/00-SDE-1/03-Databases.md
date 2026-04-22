# Databases

## SQL Fundamentals
- Tables, rows, columns — the mental model
- Primary keys and foreign keys
- Basic queries (SELECT, INSERT, UPDATE, DELETE)
- JOINs (INNER, LEFT — what they return, when to use)
- Aggregations (COUNT, SUM, GROUP BY)
- Views — virtual tables, simplify complex queries
- Indexes — what they are, how they speed up reads, cost on writes

## ACID Properties
- Atomicity — all steps of a transaction succeed or none do
- Consistency — DB moves from one valid state to another
- Isolation — concurrent transactions don't interfere with each other
- Durability — committed data survives crashes
- Why ACID matters — without it, concurrent writes silently corrupt data
- ACID vs BASE — ACID for financial data, BASE (eventually consistent) for scale

## Indexing Basics
- Why indexes exist — O(n) table scan vs O(log n) index lookup
- B+ Tree — what it is conceptually, why databases use it, how range scans work
- Composite index — order of columns matters, leftmost prefix rule
- When NOT to index — low-cardinality columns (e.g. boolean), write-heavy tables
- Covering index — query answered entirely from the index, no table lookup needed

## NoSQL — Introduction
- Why NoSQL exists (limitations of SQL at scale — joins, rigid schema, horizontal scaling)
- Key-value stores — what they are, when to use (Redis, DynamoDB)
- Document stores — what they are, when to use (MongoDB)
- Column-family stores — awareness only (Cassandra — write-heavy, time-series)
- SQL vs NoSQL — how to choose based on access patterns and consistency needs

## Schema Design
- Normalization basics — why duplication is bad, when it's okay to denormalize
- One-to-one, one-to-many, many-to-many relationships
- Junction/join table for many-to-many (e.g. user_roles with user_id + role_id)
- Choosing data types — don't store timestamps as strings, never store money as float
- Soft deletes vs hard deletes — deleted_at column vs DELETE row, tradeoffs
- Modeling for access patterns — design schema around how you'll query it

## Basic Scaling Concepts
- What a read replica is and why you'd use one (read-heavy workloads)
- Replication lag — reads from replica can be slightly stale
- Connection pooling — what it is, why apps need it (raw DB connections are expensive)
- Why you don't shard on day one
