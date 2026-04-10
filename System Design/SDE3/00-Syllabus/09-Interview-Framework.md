## Phase 9 - System Design Interview Framework

> HLD relevance: at SDE-3, the interviewer is judging whether they would trust you with a large production system.
> That means structure, prioritization, tradeoff clarity, and operational realism all matter.

### SDE-3 depth bar for this phase
- Drive the conversation instead of waiting to be led.
- Identify the dominant risk or bottleneck early.
- Compare alternatives explicitly and pick one for a reason.
- End with migration, observability, and failure handling, not just the happy path.

### 9.1 The 45-Minute Structure

| Time | Step | What to do |
|---|---|---|
| 0-5 min | Requirements | clarify product goals, scope, and sharp edges |
| 5-10 min | Estimation | identify scale and dominant bottleneck |
| 10-15 min | API and data model | define contracts and entities |
| 15-25 min | High-level design | present a clean baseline architecture |
| 25-40 min | Deep dive | correctness, scale, or failure-heavy components |
| 40-45 min | Evolution plan | 10x bottlenecks, migration path, rollback, observability |

### 9.2 Requirements Clarification - Questions to Ask
- What is the critical user flow?
- What is explicitly out of scope?
- What is the scale now and what is the expected growth?
- What latency target matters?
- What consistency is required, and where exactly?
- Single region or global?
- What failure would be unacceptable to the business?

### 9.3 High-Level Design - Component Checklist
- client
- DNS / CDN / edge
- load balancer / API gateway
- stateless services
- cache
- primary data store
- async queue / stream
- object storage
- search / indexing if needed
- observability and control-plane concerns

### 9.4 NFR to Architecture Decision Cheat Sheet

| NFR | Typical architecture response |
|---|---|
| very low latency | cache, fewer hops, async side effects, local reads |
| high write throughput | partitioning, batching, queueing, write-optimized store |
| high read throughput | cache, replicas, CDN, denormalized read path |
| strong correctness | transactional write path, idempotency, stricter consistency |
| high availability | no SPOF, graceful degradation, redundancy |
| geo resilience | multi-region replication and controlled failover |

### 9.5 Tradeoffs to Always Articulate
- consistency vs availability
- latency vs consistency
- read speed vs write complexity
- sync vs async
- precompute vs compute on demand
- SQL vs NoSQL
- queue vs event log
- single-region simplicity vs multi-region resilience

### 9.6 Deep Dive - How to Go Deep at SDE-3
- explain what problem this component solves
- explain the normal write path and read path
- explain one realistic failure mode
- explain the mitigation and what new tradeoff it introduces
- compare at least one alternative design you rejected
- mention migration / rollout if the component is not a day-zero design

### 9.7 What Strong Hire SDE-3 Looks Like
- asks clarifying questions that change the design
- identifies the dominant constraint early
- chooses a sane baseline before using advanced systems
- names tradeoffs proactively
- goes deep on the hardest correctness issue
- talks about rollout, recovery, and observability without being prompted

### 9.8 Common Mistakes to Avoid
- using advanced tech names without explaining why
- skipping estimation
- optimizing the wrong bottleneck
- ignoring migration and rollback
- saying "multi-region" without conflict-resolution or failover detail
- giving only happy-path architecture

### 9.9 Diagram Conventions
- separate read path and write path
- label protocols where useful
- show replication and async boundaries
- identify the component you will deep dive on
- keep the diagram causal and debuggable, not decorative

### 9.10 What Strong SDE-3 Answering Sounds Like
- "My baseline design is X because it keeps correctness simple. If scale forces Y later, here is the migration path."
- "I am choosing eventual consistency only for this surface, not for the whole system."
- "The hardest part of this design is not storage, it is recovery after partial failure."
- "At 10x, the bottleneck moves from API servers to partition hotspots, so my next step is resharding and cache skew control."
