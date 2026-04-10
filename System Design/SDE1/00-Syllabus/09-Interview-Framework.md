## Phase 9 - System Design Interview Framework

> HLD relevance: this is how you present everything you know in an interview.
> A correct idea explained poorly still performs badly.

### 9.1 The 45-minute structure

| Time | Step | What to do |
|---|---|---|
| 0-5 min | Requirements | clarify scope and constraints |
| 5-10 min | Estimation | QPS, storage, bandwidth |
| 10-15 min | API and data model | define core entities and endpoints |
| 15-25 min | High-level design | draw components and data flow |
| 25-40 min | Deep dive | go into 2 important components |
| 40-45 min | Bottlenecks | what breaks at 10x and how to fix it |

### 9.2 Questions to ask first
- what are the core user actions?
- what is out of scope?
- what scale should I assume?
- what latency target matters?
- do we need strong consistency anywhere?
- single region or global?

### 9.3 Baseline component checklist
- client
- DNS / CDN
- load balancer / API gateway
- stateless application servers
- cache
- primary database
- object storage if files/media exist
- message queue for async work
- background workers

### 9.4 NFR to architecture cheat sheet

| Requirement | Common response |
|---|---|
| high read traffic | cache, CDN, read replicas |
| high write traffic | sharding, queue, batching |
| low latency | cache, fewer hops, async side effects |
| strong consistency | primary write path, transactions, avoid async replica reads |
| eventual consistency acceptable | replicas, async fan-out, background processing |
| high availability | redundancy, no SPOF, graceful degradation |

### 9.5 Tradeoffs to always say out loud
- consistency vs latency
- read performance vs write complexity
- sync vs async
- SQL vs NoSQL
- precompute vs compute on demand

### 9.6 How deep SDE-1 should go
- explain what problem a component solves
- explain how it works at a high level
- explain one failure mode
- explain one tradeoff

### 9.7 What strong hire SDE-1 looks like
- asks good clarifying questions
- structures the conversation clearly
- chooses simple and correct building blocks
- does not misuse buzzwords
- talks about failure and scale without panic

### 9.8 Common mistakes
- starting without clarifying requirements
- saying "use Kafka" or "use Cassandra" without knowing why
- forgetting data model
- ignoring race conditions
- going too deep too early

### 9.9 Diagram conventions
- separate read path and write path when different
- label key components clearly
- show cache, DB, queue, and object store distinctly
- circle the component you will deep dive on

