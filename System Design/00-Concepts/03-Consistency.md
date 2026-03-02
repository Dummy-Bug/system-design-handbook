> **Consistency** means that all users see the same, correct, and most recent data after a successful write operation.

It ensures data correctness across reads and writes in a system.

---

## What Consistency Means in Practice

- After a write is committed, subsequent reads return the updated value.
    
- Different users reading the same data do not see conflicting values.
    
- Replicas remain synchronized with the latest committed state.
    

Consistency focuses on **data correctness and freshness**.

---

## Types of Consistency

### 1️⃣ Strong Consistency

- After a successful write, every read returns the latest value.
    
- No stale data is served.
    
- Common in single-node databases or tightly coordinated systems.
    

**Trade-offs:**

- Higher latency.
    
- Harder to maintain in distributed environments.
    

---

### 2️⃣ Eventual Consistency

- After a write, some reads may temporarily return stale data.
    
- Over time, all replicas converge to the same value.
    
- Common in large-scale distributed systems.
    

**Advantages:**

- Better scalability.
    
- Better availability.
    

---

## Example: Coding Platform

### Submission Status

User submits code:

- Status changes from "Pending" → "Accepted".
    

Consistency ensures:

- User sees correct final evaluation result.
    
- No conflicting statuses across devices.
    

---

### Contest Leaderboard

During contest:

- Slight delay in ranking updates may be acceptable.
    

After contest:

- Final leaderboard must be correct.
    

This is eventual consistency.

---

## Consistency vs Availability

|Concept|Meaning|
|---|---|
|Consistency|All users see correct and latest data|
|Availability|System remains accessible to users|

A system may:

- Be available but temporarily inconsistent.
    
- Be consistent but unavailable during coordination.
    

---

## Consistency vs Durability

|Concept|Meaning|
|---|---|
|Consistency|Correctness of reads after writes|
|Durability|Data is not lost after being written|

Durability ensures data is stored safely.  
Consistency ensures data is read correctly.

---

## Techniques to Achieve Strong Consistency

- Synchronous replication
    
- Quorum-based writes
    
- Single-leader architecture
    
- Distributed locking
    

---

> The system should ensure that once a write operation is successfully completed, subsequent reads return the correct and consistent value across all nodes.

---

## Key Mental Model

If a user updates data:

- And all users immediately see the updated value → strong consistency.
    
- If some users see old value temporarily but it eventually updates → eventual consistency.
    