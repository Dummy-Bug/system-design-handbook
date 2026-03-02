
> **Availability** is the ability of a system to remain operational and accessible when users attempt to use it.

A system is considered available if it successfully responds to user requests.

---

## What Availability Means in Practice

- When a user sends a request, the system responds.
    
- The system remains reachable and usable.
    
- Temporary internal failures do not prevent request handling.
    

Availability focuses on **service accessibility**, not internal correctness.

---

## What Availability Is NOT

- It does NOT guarantee data will never be lost.
    
- It does NOT guarantee perfect consistency.
    
- It does NOT mean zero failures.
    
- It does NOT mean zero downtime.
    

It simply ensures the system remains usable from the user's perspective.

---

## Example: Coding Platform

### Normal Scenario

- User submits solution.
    
- System accepts submission.
    
- Returns confirmation.
    

System is available.

---

### Contest Scenario

- During contest, users cannot submit for 5 minutes.
    
- Website returns errors or times out.
    

This is an availability failure.

Even if no data is lost.

---

## Availability vs Fault Tolerance

|Concept|Meaning|
|---|---|
|Fault Tolerance|System survives internal component failures|
|Availability|System remains accessible to users|

Fault tolerance helps achieve availability, but they are not identical.

---

## Availability vs Durability

|Concept|Meaning|
|---|---|
|Durability|Data is not lost once written|
|Availability|System responds to requests|

A system can be:

- Highly available but lose data (low durability)
    
- Durable but temporarily unavailable
    

---

## Measuring Availability

Availability is typically measured as uptime percentage.

Examples:

- 99% → ~3.65 days downtime per year
    
- 99.9% → ~8.76 hours downtime per year
    
- 99.99% → ~52 minutes downtime per year
    
- 99.999% → ~5 minutes downtime per year
    

Higher availability requires more redundancy and engineering effort.

---

## How to Improve Availability

Common techniques:

- Multiple service instances
    
- Load balancers
    
- Health checks
    
- Automatic failover
    
- Auto-scaling
    
- Multi-region deployment
    

---
> The system should remain accessible and responsive to user requests even during partial failures or traffic spikes, ensuring minimal downtime.
---

## Key Mental Model

If users cannot access the system → 
Availability has failed.

If users can access the system but some internal components failed → 
Availability is preserved.

---
