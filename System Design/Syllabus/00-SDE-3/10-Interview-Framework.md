# Interview Framework

## The 45-Minute Structure

| Time | Step | What to do |
|---|---|---|
| 0–5 min | Requirements | Clarify functional + non-functional, define scope |
| 5–10 min | Estimation | QPS, storage, bandwidth — drive architecture decisions |
| 10–15 min | API Design | Key endpoints, request/response, idempotency |
| 15–25 min | High-Level Design | Core components, data flow, read/write paths |
| 25–40 min | Deep Dive | 2-3 most critical components in detail |
| 40–45 min | Bottlenecks | What breaks at 10x, what you'd improve |

## Requirements Clarification

**Functional**
- What are the core features? (don't assume, ask)
- What's out of scope for this interview?
- Read-heavy or write-heavy?

**Non-Functional**
- How many users? DAU? MAU?
- Expected QPS at peak?
- Consistency model — strong or eventual acceptable?
- Latency requirement?
- Availability — 99.9% vs 99.99%?
- Single region or global?

## High-Level Design Component Checklist
- Client (mobile/web/third-party)
- DNS + CDN (static assets, global routing)
- Load Balancer / API Gateway (entry point, auth, rate limiting)
- Application servers (stateless, horizontally scalable)
- Cache layer (Redis — what do you cache?)
- Primary database (what type, why?)
- Message queue (where is async processing needed?)
- Storage layer (blob storage for media?)
- Search (if full-text needed)
- Notification service (if real-time updates needed)

## NFR → Architecture Decision Cheat Sheet

| NFR | Architecture Response |
|---|---|
| High availability (99.99%+) | Multi-AZ, active-active, redundant LB, no SPOF |
| Low latency (<100ms P99) | Cache + CDN, read replicas, async writes, geo-routing |
| High write throughput | Sharding, async/batching, Cassandra |
| High read throughput | Caching, read replicas, CDN, denormalization |
| Strong consistency | Single-leader, quorum writes (W+R>N), avoid async replication |
| Eventual consistency | Multi-leader, async replication, CRDT |
| Durability (no data loss) | Replication factor 3+, WAL, sync replication, cross-region backup |
| Scalable storage | Sharding, object storage (S3), archival tiers |

## Tradeoffs to Always Articulate
- Consistency vs Availability — CAP, which does this system prioritize?
- Latency vs Consistency — PACELC, are we ok with stale reads for speed?
- Read performance vs Write performance — caching helps reads but adds write complexity
- Fan-out on write vs fan-out on read — precompute feeds or compute on request?
- Push vs Pull — who initiates?
- Sync vs Async — user waits or fire and forget?
- SQL vs NoSQL — what's the access pattern?

## Deep Dive Technique
When interviewer says "tell me more about X":
1. What problem X solves
2. How X works (key components/steps)
3. What can go wrong and how you handle it
4. The tradeoff you accepted

## **What Strong Hire Means at FAANGM (SDE-3 Bar)**
- **Drives the conversation — doesn't wait to be led, proactively covers failure modes**
- **Correctness boundary — identifies exactly where the system can be inconsistent and defends why that's acceptable**
- **Operational ownership — talks about monitoring, alerting, on-call runbooks, not just architecture**
- **Migration path — "how do we get from the current system to this design without downtime?"**
- **Multi-region implications — "what happens if the EU region goes down entirely?"**
- **Disaster recovery — RPO and RTO explicitly called out, backup strategy, failover procedure**
- **Scales reasoning — "at 10x this breaks because X, we'd need to do Y"**
- **Knows when to use what — doesn't use Kafka for everything, doesn't use SQL for everything**

## **SDE-3 Specific Interview Questions**

**Migration and evolution:**
- How do you migrate from this SQL schema to a NoSQL model with zero downtime?
- The system currently handles 10K QPS, how does the design change at 1M QPS?
- How do you re-shard the database if the current shard key causes hotspots?

**Multi-region:**
- How do you handle a full region failure?
- How do you ensure EU user data never leaves the EU?
- How do you resolve write conflicts when both regions accept writes?

**Operational:**
- How would you know if this system is unhealthy at 3am?
- What's the on-call runbook for when the primary DB goes down?
- How do you debug a latency spike that only affects 1% of requests?

**Correctness:**
- How do you guarantee exactly-once payment processing?
- What happens if the Saga compensating transaction fails?
- How do you detect and recover from split-brain?

## What to Say When You Don't Know

At SDE-3, interviewers go so deep that hitting the boundary of your knowledge is guaranteed — not possible, guaranteed. They do this deliberately to see how you handle uncertainty. This is itself a signal.

**The wrong move:** guess confidently and be wrong. At SDE-3 level the interviewer knows the internals. A confident wrong answer is worse than saying you're not sure.

**The right move:** state what you know, name the boundary, and reason from first principles toward an answer.

Template:
> "I know [related concept] well. From that, I'd expect [reasoned inference]. I'm less certain about [specific gap]. The implication for our design is [connect back to the problem]."

**Real SDE-3 examples:**

Interviewer asks about Spanner's exact 2PC coordination across Paxos groups:
> "I know Spanner uses 2PC between Paxos groups for cross-shard transactions and TrueTime to bound timestamp uncertainty. I'm less clear on exactly how it handles coordinator failure mid-commit. But the key implication for our design is that Spanner handles this internally — we get strong consistency without implementing 2PC ourselves. The cost is higher write latency (~10–100ms vs single-region sub-ms), which for financial transactions is acceptable."

Interviewer asks how Kafka exactly-once works across a network partition during a producer retry:
> "I know the idempotent producer uses epoch + sequence numbers to deduplicate retries, and transactional API coordinates atomic writes across partitions. I'm not certain about what happens if the leader fails between the producer sending and receiving an ack — I believe the sequence number prevents duplicates on the new leader, but I'd want to verify that assumption before relying on it for payment systems. In the design I'd pair Kafka exactly-once with idempotency keys at the consumer as a defense-in-depth."

**Three rules:**
1. Never go silent. A reasoned wrong answer shows more than silence.
2. Always connect back to the design impact. "I'm not sure of the internals but here's how it affects the system."
3. Flag it explicitly and move on. "I'd want to verify this before shipping — let me flag it and continue." Interviewers respect intellectual honesty more than bluffing.

## Common Mistakes at SDE-3 Level
- Designing without a failure model — every interviewer will ask "what if X fails"
- Ignoring the migration path — saying "use Cassandra" without explaining how to get there
- Treating consistency as binary — not knowing the full spectrum
- Using Kafka/Redis/Spanner without knowing why — "use Kafka" with no understanding of partitions, ordering, or exactly-once
- Not quantifying tradeoffs — "it's slower" instead of "it adds ~50ms P99 latency because..."
- Skipping observability — a design is not production-ready without monitoring and alerting
- Going silent — think out loud even when uncertain

## Diagram Conventions
- Client → Load Balancer → App Servers → Cache → DB
- Label databases by type: [PostgreSQL], [Redis], [Cassandra], [S3]
- Show read path and write path separately if they differ
- Label arrows with protocol: HTTP, gRPC, WebSocket, async/Kafka
- Show replication: DB Primary → DB Replica
- Circle the component you're about to deep-dive on
- **For SDE-3 — also show: monitoring layer, multi-region topology, data flow for migration**
