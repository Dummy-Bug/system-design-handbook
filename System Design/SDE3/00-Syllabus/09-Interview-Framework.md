## Phase 9 - System Design Interview Framework

> HLD relevance: at SDE-3, you are being judged on technical judgment, prioritization, and leadership in the room, not just correctness.

### 9.1 Senior-level 45-minute structure

| Time | Step | What to do |
|---|---|---|
| 0-5 min | Requirements | clarify product goals, risks, and scope |
| 5-10 min | Estimation | identify scale and dominant bottlenecks |
| 10-15 min | APIs and data model | define core contracts and entities |
| 15-25 min | High-level architecture | clean baseline design first |
| 25-40 min | Deep dive | correctness, scale, or failure-heavy components |
| 40-45 min | Evolution plan | bottlenecks, migration path, rollback, observability |

### 9.2 Clarifying questions
- what is the critical user journey?
- what failure is unacceptable?
- what consistency is required and where?
- what is the expected scale now and at 10x?
- single region or global?
- what is the latency SLO?
- what is out of scope?

### 9.3 High-level component checklist
- client
- DNS / CDN / edge
- load balancer / API gateway
- stateless services
- cache
- primary data store
- async pipeline / queue
- blob storage
- search / indexing layer if needed
- observability and control plane considerations

### 9.4 NFR to design cheat sheet

| NFR | Likely architecture move |
|---|---|
| very low latency | cache, fewer hops, local reads, async side effects |
| high write throughput | partitioning, batching, async processing |
| high read throughput | caching, replicas, denormalization |
| strict correctness | transactions, idempotency, primary write path |
| high availability | no SPOF, redundancy, graceful degradation |
| geo resilience | multi-region replication and failover strategy |

### 9.5 Tradeoffs to articulate proactively
- consistency vs availability
- latency vs consistency
- read speed vs write complexity
- sync vs async
- precompute vs compute on demand
- SQL vs NoSQL
- queue vs event log

### 9.6 What strong SDE-3 looks like
- drives the conversation
- identifies the real bottleneck early
- gives a sane baseline before reaching for advanced systems
- surfaces failure and rollback plans without being asked
- compares alternatives explicitly
- communicates clearly under ambiguity

### 9.7 Common mistakes
- using advanced tech without proving the need
- ignoring migration and rollout
- missing the hardest failure scenario
- hand-waving multi-region
- diving into one component before finishing the full architecture

### 9.8 Diagram conventions
- separate read and write paths
- label protocols and storage types
- show replication boundaries
- identify the deep-dive component clearly
- keep diagrams causal, not decorative

