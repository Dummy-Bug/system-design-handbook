## Phase 9 — System Design Interview Framework

> HLD relevance: This is HOW you present everything you've learned.
> Knowing the theory is not enough — you need to communicate it in 45 minutes under pressure.

### 9.1 The 45-Minute Structure

| Time | Step | What to do |
|---|---|---|
| 0–5 min | Requirements | Clarify functional + non-functional, define scope |
| 5–10 min | Estimation | QPS, storage, bandwidth — drive architecture decisions |
| 10–15 min | API Design | Key endpoints, request/response, idempotency |
| 15–25 min | High-Level Design | Core components, data flow, read/write paths |
| 25–40 min | Deep Dive | 2-3 most critical components in detail |
| 40–45 min | Bottlenecks | What breaks at 10x, what you'd improve |

### 9.2 Requirements Clarification — Questions to Ask

**Functional**
- What are the core features? (don't assume, ask)
- What's out of scope for this interview?
- Are we designing for read-heavy or write-heavy workload?

**Non-Functional**
- How many users? DAU? MAU?
- What's the expected QPS at peak?
- What consistency model is acceptable?
- What's the latency requirement?
- What availability do we need (99.9% vs 99.99%)?
- Single region or global?
- Is strong consistency required or is eventual OK?

### 9.3 High-Level Design — Component Checklist
Every design should consider:
- [ ] Client (mobile/web/third-party)
- [ ] DNS + CDN (static assets, global routing)
- [ ] Load Balancer / API Gateway (entry point, auth, rate limiting)
- [ ] Application servers (stateless, horizontally scalable)
- [ ] Cache layer (Redis — what do you cache?)
- [ ] Primary database (what type, why?)
- [ ] Message queue (where is async processing needed?)
- [ ] Storage layer (blob storage for media?)
- [ ] Search (if full-text search needed)
- [ ] Notification service (if real-time updates needed)

### 9.4 NFR → Architecture Decision Cheat Sheet

| NFR | Architecture Response |
|---|---|
| High availability (99.99%+) | Multi-AZ, active-active, redundant LB, no SPOF |
| Low latency (<100ms p99) | Cache + CDN, read replicas, async writes, geo-routing |
| High write throughput | Sharding, async/batching, write-optimized DB (Cassandra) |
| High read throughput | Caching, read replicas, CDN, denormalization |
| Strong consistency | Single-leader, quorum writes (W+R>N), avoid async replication |
| Eventual consistency | Multi-leader, async replication, CRDT |
| Durability (no data loss) | Replication factor 3+, WAL, sync replication, cross-region backup |
| Scalable storage | Sharding, object storage (S3), archival tiers |

### 9.5 Tradeoffs to Always Articulate
The interviewer wants to hear you say these:
- Consistency vs Availability — CAP theorem, which does this system prioritize?
- Latency vs Consistency — PACELC, are we ok with stale reads for speed?
- Read performance vs Write performance — caching helps reads but adds write complexity
- Fan-out on write vs fan-out on read — precompute feeds or compute on request?
- Push vs Pull — notifications, feeds — who initiates?
- Sync vs Async — user waits for result vs fire and forget
- SQL vs NoSQL — what's the access pattern?
- Strong typing (Protobuf) vs flexibility (JSON) — internal vs external APIs

### 9.6 Deep Dive — How to Go Deep
When the interviewer says "tell me more about X":
- Explain what problem X solves
- Explain how X works (key components/steps)
- Explain what can go wrong and how you handle it
- Mention the tradeoff you accepted

Example: "Tell me more about your caching layer"
→ "I'm using Redis with cache-aside. On a cache miss, the app reads from DB and populates the cache with a 5-minute TTL. The tradeoff is stale data for up to 5 minutes, which is acceptable here because [reason]. The risk I'm handling is cache stampede by using a mutex on the first miss."

### 9.7 What Google Strong Hire Looks Like
- Drives the conversation — doesn't wait to be led
- Asks the right clarifying questions before designing
- States tradeoffs proactively — "I chose X, the downside is Y, which is acceptable because Z"
- Goes deep when pushed — not just "use Kafka" but knows partitioning, ordering, at-least-once
- Identifies failure modes — "what if this node goes down?"
- Scales reasoning — "at 100x this breaks because..."
- Communicates clearly — interviewer can follow your thinking

### 9.8 Common Mistakes to Avoid
- Starting to design without clarifying requirements
- Saying a technology name without knowing why ("use Kafka" → interviewer asks why → blank stare)
- Ignoring failure scenarios — every interviewer will ask "what happens when X fails"
- Forgetting the data model — schema design matters and reveals your thinking
- Not considering scale — "add more servers" is not an answer
- Going too deep too early — cover the full picture first, then drill down
- Going silent — think out loud even when you're not sure

### 9.9 Diagram Conventions
- Client → Load Balancer → App Servers → Cache → DB
- Label databases by type: [PostgreSQL], [Redis], [Cassandra], [S3]
- Show read path and write path separately if they differ
- Label arrows with protocol: HTTP, gRPC, WebSocket, async/Kafka
- Show replication: DB Primary → DB Replica
- Circle the component you're about to deep-dive on
