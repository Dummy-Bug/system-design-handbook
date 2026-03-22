> **Scalability** is the ability of a system to handle increasing load (users, requests, or data) without significant performance degradation.

A scalable system continues to perform efficiently as demand grows.

---

## What Scalability Means in Practice

- System handles more concurrent users.
    
- System handles higher request throughput.
    
- System handles increasing data volume.
    
- Latency and error rate remain within acceptable limits under growth.
    

---

## Types of Scalability

### 1️⃣ Vertical Scalability (Scale Up)

- Increase resources of a single machine.
    
- Add more CPU, RAM, or storage.
    

Example:

- Upgrading server from 8GB RAM to 64GB RAM.
    

**Limitations:**

- Hardware ceiling.
    
- Expensive.
    
- Single point of failure remains.
    

---

### 2️⃣ Horizontal Scalability (Scale Out)

- Add more machines.
    
- Distribute traffic across instances.
    
- Use load balancers.
    

Example:

- Increasing application servers from 2 to 20 during high traffic.
    

**Advantages:**

- Better fault tolerance.
    
- Higher capacity.
    
- Preferred for distributed systems.
    

---

## Example: Coding Platform During Contest

Normal load:

- 10,000 submissions per hour.
    

Contest load:

- 500,000 submissions per hour.
    

A scalable system:

- Spins up more evaluator workers.
    
- Scales database read replicas.
    
- Uses message queues to buffer spikes.
    
- Maintains acceptable response time.
    

---

## Scalability vs Performance

|Concept|Meaning|
|---|---|
|Performance|How fast the system works under current load|
|Scalability|How the system behaves as load increases|

A system can:

- Perform well but fail under growth (not scalable).
    
- Be moderately fast but scale efficiently (scalable).
    

---

## Scalability vs Availability

|Concept|Meaning|
|---|---|
|Availability|System remains accessible|
|Scalability|System handles increased demand|

Scalability failures often lead to availability issues during traffic spikes.

---

## Techniques to Achieve Scalability

- Stateless application servers
    
- Load balancing
    
- Auto-scaling
    
- Caching (Redis, CDN)
    
- Database sharding
    
- Read replicas
    
- Asynchronous processing using queues
    
- Partitioning large datasets
    

---

> The system should scale horizontally to handle increasing traffic by adding more instances, distributing load effectively, and maintaining stable latency and throughput during peak demand.

---

## Key Mental Model

If traffic doubles:

- Does latency remain stable?
    
- Does throughput increase proportionally?
    
- Does error rate remain low?
    

If yes → system is scalable.

If performance collapses under growth → system is not scalable.
