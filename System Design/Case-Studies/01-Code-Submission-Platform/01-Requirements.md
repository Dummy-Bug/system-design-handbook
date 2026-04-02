### Functional Requirements

* Users can register and authenticate.
* Users can view list of questions.
* Users can submit a code solution in the available set of language and get the code evaluated on custom or internal test cases.

---

# Non-Functional Requirements

### **1️⃣ Fault Tolerance**

The system must tolerate failure of individual components (e.g., application servers, evaluator workers, database nodes, or message brokers) without causing system-wide failure or loss of user submissions.

- Submissions must be reliably persisted.
- Failed processing should be retried automatically.
- Replication and failover mechanisms should ensure continuity.
- Partial failures should not impact overall system correctness.

---

### **2️⃣ High Availability (Especially During Contests)**

The system must remain accessible and responsive to users, particularly during live contests where downtime directly impacts user rankings.

- Submission APIs must have minimal downtime.
- Critical services (submission intake, evaluation, leaderboard updates) should be highly available.
- Temporary degradation is acceptable for non-critical features (e.g., recommendations).
- Higher availability guarantees are required during contest windows.

---

### **3️⃣ Consistency (Eventual Consistency for Leaderboard)**

Strong consistency is required for critical operations such as submission recording and evaluation results.

However, leaderboard updates and rating calculations can follow eventual consistency:

- Slight delays in ranking updates during contests are acceptable.
- Final contest results must be correct.
- Plagiarism detection and rating recalculation can be processed asynchronously after contest completion.

This allows scalability without sacrificing correctness.

---

### **4️⃣ Scalability (Contest Traffic Spikes)**

The system must handle significant traffic spikes during contests.

- Auto-scaling of evaluator workers.
- Load balancing across stateless application servers.
- Queue-based buffering of submissions.
- Database sharding or read replicas for high read throughput.

Latency and error rates must remain stable under peak load.
