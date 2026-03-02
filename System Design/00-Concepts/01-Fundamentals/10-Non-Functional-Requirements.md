## 1️⃣ Availability

> The system should remain accessible and responsive to users under normal and peak load conditions.

- Define target uptime (e.g., 99.9% / 99.99%).
    
- Critical APIs must have minimal downtime.
    
- Graceful degradation is acceptable for non-critical features.
    
- Multi-instance deployment with load balancing.
    
- Health checks and automatic failover mechanisms.
    

**Questions to Clarify:**

- Is downtime acceptable?
    
- Is availability more critical during certain events (e.g., contests, sales)?
    

---

## 2️⃣ Scalability

> The system must handle increasing traffic, users, and data volume without significant performance degradation.

- Support horizontal scaling of stateless services.
    
- Auto-scaling during traffic spikes.
    
- Caching for high read load.
    
- Partitioning/sharding for large datasets.
    
- Queue-based buffering for burst traffic.
    

**Questions to Clarify:**

- Expected QPS?
    
- Peak vs average traffic?
    
- Growth rate over time?
    

---

## 3️⃣ Fault Tolerance

> The system must continue operating correctly despite failure of individual components.

- No single point of failure.
    
- Replication of critical services and data.
    
- Automatic retries for transient failures.
    
- Failover mechanisms for critical components.
    
- Circuit breakers and timeouts.
    

**Questions to Clarify:**

- Should system tolerate single-node failure?
    
- Multi-node failure?
    
- Region-level failure?
    

---

## 4️⃣ Durability

> Once data is acknowledged as successfully written, it must not be lost.

- Persistent storage (not in-memory only).
    
- Write-ahead logging.
    
- Replication before acknowledgment (if required).
    
- Quorum-based writes (if strong durability required).
    

**Questions to Clarify:**

- Is data loss acceptable?
    
- For which operations is durability critical?
    

---

## 5️⃣ Consistency

> The system must define how fresh and synchronized data must be across components.

- Strong consistency for critical operations.
    
- Eventual consistency for non-critical features.
    
- Clear read/write consistency model.
    

**Questions to Clarify:**

- Is stale data acceptable?
    
- Where is strong consistency mandatory?
    

---

## 6️⃣ Partition Tolerance

> The system should continue operating during network communication failures between distributed components.

- Handle network splits gracefully.
    
- Allow degraded operation during partitions.
    
- Ensure data convergence after recovery.
    

**Questions to Clarify:**

- How should system behave during network partition?
    
- Should availability or consistency be prioritized?
    

---

## 7️⃣ Performance

> The system must meet latency and throughput requirements.

- Define acceptable latency (e.g., <200ms API response).
    
- Define throughput expectations.
    
- Optimize critical paths.
    
- Use caching and indexing appropriately.
    

**Questions to Clarify:**

- Real-time vs batch?
    
- Latency SLAs?
    

---

## 8️⃣ Security

> The system must protect user data and prevent unauthorized access.

- Authentication & authorization.
    
- Encryption in transit (TLS).
    
- Encryption at rest (if required).
    
- Rate limiting and abuse prevention.
    

**Questions to Clarify:**

- Sensitive data involved?
    
- Compliance requirements?
    

---

## 9️⃣ Observability

> The system must be monitorable and debuggable in production.

- Centralized logging.
    
- Metrics and alerting.
    
- Distributed tracing.
    
- Health monitoring.
    

---

# How to Use This Template in Interviews

1. Start with Availability, Scalability, and Fault Tolerance.
    
2. Add Durability and Consistency based on system type.
    
3. Mention Partition Tolerance only if distributed.
    
4. Add Performance and Security briefly.
    
5. Don’t over-explain unless asked.
    

---

# Minimal Version (If Interview Time Is Limited)

If short on time, always cover:

- Availability
    
- Scalability
    
- Fault Tolerance
    
- Consistency
    

Everything else is secondary unless problem demands it.