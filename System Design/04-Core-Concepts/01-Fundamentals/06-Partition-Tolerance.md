> **Partition Tolerance** is the ability of a distributed system to continue operating even when communication between nodes is disrupted due to network failures.

It ensures the system can handle network splits without complete breakdown.

---

## What is a Network Partition?

A network partition occurs when:

- Nodes in a distributed system lose the ability to communicate with each other.
    
- Caused by network failures, latency spikes, firewall issues, or data center outages.
    

Example:

```
Node A   Node B   |   Node C   Node D
```

Group A-B cannot communicate with group C-D.

This is a network partition.

---

## Why Partition Tolerance Is Important

- Network failures are inevitable in distributed systems.
    
- Large systems run across multiple machines and data centers.
    
- Perfect network connectivity cannot be assumed.
    

A system must be designed to handle temporary communication breakdowns.

---

## System Behavior During a Partition

When a partition occurs, the system must decide:

- Continue serving requests (possibly with stale data), or
    
- Stop serving certain requests to prevent inconsistency.
    

The choice depends on system design and requirements.

---

## Example: Coding Platform

If leaderboard service temporarily loses connection to database:

Possible behaviors:

- Serve last known leaderboard data (degraded mode).
    
- Disable leaderboard temporarily until connectivity is restored.
    

Both are examples of partition-tolerant behavior.

---

## Partition Tolerance vs Availability

|Concept|Meaning|
|---|---|
|Partition Tolerance|System handles network splits gracefully|
|Availability|System remains accessible to users|

Partition tolerance focuses on surviving network failures between components.

---

## Partition Tolerance vs Fault Tolerance

|Concept|Meaning|
|---|---|
|Fault Tolerance|Survives component (node/service) failure|
|Partition Tolerance|Survives communication failure between nodes|

A system may tolerate node failure but still struggle with network partitions if not properly designed.

---

> The system should be able to continue operating, possibly in a degraded mode, even if network communication between distributed components is temporarily disrupted.

---

## Key Mental Model

If nodes lose communication and the system completely stops functioning → 
It is NOT partition tolerant.

If the system continues operating (fully or partially) despite the network split → 
It is partition tolerant.

---
