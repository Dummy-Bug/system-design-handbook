> Fault Tolerance is the ability of a system to continue operating correctly even when some of its components fail.

It ensures the system survives partial failures without causing complete breakdown or data loss.

---

## What Fault Tolerance Means in Distributed Systems

A system is fault tolerant if:

- Failure of one node does not crash the system.
    
- Failure of some instances does not stop request processing.
    
- Data is not lost due to partial infrastructure failures.
    
- System can recover automatically.
    

---

## What Fault Tolerance Is NOT

- It does NOT mean the system never fails.
    
- It does NOT guarantee zero downtime.
    
- It does NOT mean it can survive total system collapse.
    

Fault tolerance operates within defined failure boundaries (e.g., single-node or limited multi-node failure).

---

## Common Mechanisms Used to Achieve Fault Tolerance

### 1. Replication

- Multiple copies of data.
    
- If one node fails, another replica takes over.
    

Example: Kafka partition replicas.

---

### 2. Redundancy

- Multiple service instances running.
    
- Load balancer routes traffic to healthy instances.
    

Example: Multiple application servers.

---

### 3. Failover

- Automatic switch from failed node to backup node.
    
- Often involves leader election.
    

Example: Database primary → replica promotion.

---

### 4. Retry Mechanisms

- If processing fails temporarily, system retries.
    
- Common in queue-based architectures.
    

Example: Reprocessing failed submission jobs.

---

### 5. Graceful Degradation

- System continues with reduced functionality.
    
- Non-critical features may be disabled.
    

Example: Hide recommendations if recommendation service fails.

---

## Example: Coding Platform (Submission System)

### Scenario 1: Partial Failure

- 3 out of 10 evaluator machines fail.
    
- Remaining 7 continue processing submissions.
    
- System functions normally (slightly slower).
    

This is fault tolerance.

---

### Scenario 2: Complete Evaluator Failure

- All evaluator machines fail.
    
- Submissions are still accepted.
    
- Submissions are stored in DB or message queue.
    
- Evaluation happens once evaluators recover.
    

System degrades but does not lose data. 
Still considered fault tolerant design.
