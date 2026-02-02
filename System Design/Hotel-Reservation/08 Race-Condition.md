Assume this state at time **t0**:

- `total_rooms = 100`
- `total_reserved_rooms = 99`

Two users check availability at the same time.

Both see **1 room available**.  
Both send a booking request.

Because the database isolation level is **not SERIALIZABLE**, both transactions read the same snapshot and both proceed.

Final result:

- `total_reserved_rooms = 101`
- Same room effectively booked twice.

This is called **race condition** or **lost update problem**.

Root cause:

- Read and write operations were not properly synchronized.
- Database allowed concurrent writes without conflict detection.

---

# Solution Approaches

There are two industry-standard strategies:

1. Pessimistic Locking
2. Optimistic Locking

They solve the same problem differently.

---

## 1) Pessimistic Locking

### Idea

Assume conflicts WILL happen.  
So block others early.

When a user selects a room:

- System immediately locks that row or seat record.
    
- Other users cannot read or modify it until the lock is released.
    

### Example

BookMyShow seat selection:

- You click seat A1.
- Seat becomes temporarily unavailable for others.
- You have a time window to complete payment.

Technically implemented using:

```sql
SELECT * FROM rooms 
WHERE id = 10 
FOR UPDATE;
```

This places a **row-level exclusive lock**.

---

### Advantages

- Guarantees consistency.
    
- No double booking possible.
    
- Simple mental model.
    

---

### Problems

#### 1. Lock holding waste

User may:

- Abandon payment
    
- Close browser
    
- Lose network
    

Result:

- Resource stays locked.
    
- Other users are blocked.
    

Needs timeout logic to clean up stale locks.

---

#### 2. Deadlocks

Example:

- Transaction A locks Room 1 then tries Room 2
    
- Transaction B locks Room 2 then tries Room 1
    

Both wait forever.

Database must detect and kill one transaction.

---

#### 3. Scalability bottleneck

High traffic systems suffer because:

- Threads wait on locks.
    
- Throughput drops.
    
- Latency increases.
    

Not suitable for:

- Flash sales
    
- Ticket booking peaks
    
- High concurrency workloads
    

---

## 2) Optimistic Locking

### Idea

Assume conflicts are RARE.  
Do not lock upfront.

Let everyone try.

At commit time:

- Detect conflict.
    
- Allow only one transaction to succeed.
    
- Reject others.
    

No blocking.

---

### Flow

1. Multiple users read the same data.
    
2. All attempt update.
    
3. Database checks if data changed meanwhile.
    
4. If changed → reject update.
    

Only one wins.

Others retry or show error.

---

### Why This Works Better at Scale

- No long locks.
    
- No waiting.
    
- Better throughput.
    
- Works well when conflicts are infrequent.
    

Used by:

- High-scale APIs
    
- Distributed systems
    
- Microservices
    

---

# How Optimistic Locking Is Implemented

Two common techniques:

---

## Method 1: Timestamp Based

Each row has:

```
last_updated_at
```

### Flow

1. Client reads row with timestamp `T1`
    
2. Client sends update with condition:
    

```sql
UPDATE rooms
SET reserved = true
WHERE id = 10 
AND last_updated_at = T1;
```

If another update happened:

- Timestamp changed
    
- Query affects 0 rows
    
- Update fails
    

---

## Method 2: Version Number (Most Common)

Preferred method.

Add column:

```
version INT
```

Initial value:

```
version = 1
```

---

### Step-by-step Example

Initial state:

```
room_id = 10
reserved = false
version = 5
```

Two users read this.

---

### User A Update

```sql
UPDATE rooms
SET reserved = true,
    version = version + 1
WHERE id = 10
AND version = 5;
```

Success.

Row becomes:

```
reserved = true
version = 6
```

---

### User B Update

Runs same query:

```sql
WHERE version = 5
```

But current version is now 6.

Result:

- 0 rows affected
    
- Update fails
    
- System returns "Booking failed. Try again."
    

---

### Important Property

Database enforces atomicity.

No race possible.

No explicit lock.

---

# Comparison Summary

|Feature|Pessimistic|Optimistic|
|---|---|---|
|Lock upfront|Yes|No|
|Blocking|Yes|No|
|Deadlock risk|Yes|No|
|Throughput|Lower|Higher|
|Failure handling|Rare|Common and expected|
|Best for|High conflict systems|High scale systems|

---

# Real World Usage

### Use Pessimistic Locking When

- Inventory is extremely small
    
- Conflicts are guaranteed
    
- Example: Bank balance transfer
    

---

### Use Optimistic Locking When

- Large inventory
    
- High concurrency
    
- Read heavy systems
    
- Example: Ticket booking, ecommerce carts
    