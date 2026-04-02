> **Durability** guarantees that once data is successfully written and acknowledged, it will not be lost — even if the system crashes immediately afterward.

In simple terms , If the system says:
> “Submission received”

Then that submission must survive:

- Server crash
    
- Power failure
    
- Process restart
    
- Machine reboot
    

---

# Example — Coding Platform

User submits code.

System responds:

> “Submission Successful”

Immediately after that:

- App server crashes
    
- Database node restarts
    

If submission is still stored → durable  
If submission is lost → not durable

---

# What Durability Protects Against

- Server crashes
    
- Power outages
    
- OS restarts
    
- Unexpected shutdowns
    
- Process failures
    

---

# What Durability Is NOT

- It does not guarantee availability.
    
- It does not guarantee replication.
    
- It does not guarantee scalability.
    

It strictly guarantees:

> A committed write is permanent.

---

# How Systems Achieve Durability

1️⃣ Write-Ahead Logging (WAL)  
2️⃣ Flushing to disk before acknowledgment  
3️⃣ Replication to multiple nodes  
4️⃣ Persistent storage (not in-memory only)  
5️⃣ Quorum-based commits

---

# Durability vs Fault Tolerance

|Concept|Meaning|
|---|---|
|Durability|Data is not lost after acknowledgment|
|Fault Tolerance|System continues operating during failures|

System may:

- Be fault tolerant but lose recent data (low durability)
    
- Be durable but temporarily unavailable
    

They are different guarantees.

---

# Durability vs Availability

- Availability = system responds
    
- Durability = response means data is safe
    

System can respond “success” but lose data → high availability, low durability.

That is catastrophic for systems like coding platforms.

---

# In Your Coding Platform Context

Durability is critical for:

- Submissions
    
- Contest results
    
- Ratings
    
- Plagiarism records
    

You cannot afford losing this data.

Leaderboard UI delay is fine.  
Submission loss is not fine.

---

# Interview-Ready One-Liner

> Durability ensures that once a write operation is acknowledged as successful, the data will not be lost even if the system crashes immediately afterward.

---

Now I’ll give you clean Obsidian-ready notes.

---

# Durability

## Definition

> Durability guarantees that once data is successfully written and acknowledged, it will persist permanently and will not be lost even in case of system crashes or failures.

---

## What Durability Means in Practice

- Once a submission is confirmed, it must survive crashes.
    
- System restarts must not erase committed data.
    
- Data must be stored on persistent storage.
    

---

## Example: Coding Platform

User submits code:

System responds:

> “Submission Successful”

Even if:

- Application server crashes
    
- Database restarts
    
- Machine reboots
    

The submission must still exist.

---

## How Durability Is Achieved

- Write-Ahead Logging (WAL)
    
- Flushing writes to disk before acknowledgment
    
- Replication across multiple nodes
    
- Quorum-based write commits
    
- Persistent storage (SSD/HDD)
    

---

## Durability vs Other Concepts

|Concept|Meaning|
|---|---|
|Durability|Data is permanently stored|
|Availability|System is accessible|
|Fault Tolerance|System survives component failures|
|Consistency|All reads reflect correct data|

---

> The system must ensure that once a submission is acknowledged as successful, it is permanently stored and cannot be lost due to crashes or failures.

---

## Key Mental Model

If the system says “success” 
and data disappears after crash → 
Durability is broken.
