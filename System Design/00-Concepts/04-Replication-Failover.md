
> **Replication** is the process of maintaining multiple synchronized copies of data across different nodes in a distributed system.

It ensures that data exists in more than one place to prevent data loss.

---

## Purpose of Replication

- Prevent data loss
    
- Improve durability
    
- Enable fault tolerance
    
- Improve read scalability (in some systems)
    

---

## How Replication Works

- One node acts as the **leader/primary**.
    
- Other nodes act as **followers/replicas**.
    
- Data written to the leader is copied to replicas.
    
- Replication may be:
    
    - **Synchronous** (wait for replica acknowledgment)
        
    - **Asynchronous** (replica updates later)
        

---

## Example

Database with:

- Primary node
    
- 2 replica nodes
    

When data is written:

- Primary stores it
    
- Replicas copy it
    

If primary crashes, data still exists on replicas.

---

## Important

Replication:

- Happens continuously
    
- Is a data protection mechanism
    
- Does NOT automatically switch traffic during failure
    

---

# Failover

> Failover is the process of automatically switching from a failed primary component to a healthy backup component.

It ensures system availability during failures.

---

## Purpose of Failover

- Maintain service availability
    
- Minimize downtime
    
- Automatically recover from component failure
    

---

## How Failover Works

1. Failure is detected.
    
2. A healthy replica is promoted to primary.
    
3. Traffic is redirected to the new primary.
    
4. System continues operating.
    

---

## Example

Primary DB crashes:

- Replica promoted to primary.
    
- Application traffic redirected.
    
- System continues functioning.
    

---

## Important

Failover:

- Happens only during failure.
    
- Is a control/traffic-switching mechanism.
    
- Requires replication or redundancy to work.
    

---

# Replication vs Failover

|Aspect|Replication|Failover|
|---|---|---|
|Purpose|Protect data|Protect availability|
|Function|Create multiple data copies|Switch to backup during failure|
|Timing|Continuous|Triggered by failure|
|Nature|Data mechanism|Control/role-switching mechanism|
|Works Alone?|Yes|No (needs replicas/backups)|

---

## Relationship Between Them

- Replication enables failover.
    
- Without replication, failover cannot occur.
    
- Replication ensures data exists.
    
- Failover ensures service continues.
    

---

> Replication maintains multiple copies of data for durability, while failover is the mechanism that promotes a backup and redirects traffic when a primary component fails.

---
