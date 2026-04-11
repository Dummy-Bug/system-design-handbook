## Phase 9 — Interview Framework (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Interview Framework (Requirements, Estimation, API Design, HLD, Data Model, Deep Dive, Bottlenecks).
> **SDE-3 Focus:** Moving from "how to pass the interview" to "how to demonstrate staff+ engineering maturity, architectural foresight, and operational empathy."

### 9.1 — The "Senior Move": Problem Discovery (Extension of SDE-2 9.1)
*In SDE-2, you gather requirements. In SDE-3, you uncover the "Hard Part."*

- **The "Pre-Design" Inquiry:** Ask about the "Real Constraint" (e.g., "Is this system globally consistent or just regionally?"). Finding the "Edge Case" that breaks the standard design (e.g., "Celebrity Fan-out," "Flash Sale Surge").
- **Constraint-Driven Design:** Explicitly stating that "I am choosing consistency over availability for this specific ledger component because..." and then stating the exact tradeoff.
- **Ambiguity as an Asset:** Identifying when the interviewer's prompt is too broad and proactively "Slicing" it into manageable phases (e.g., "I'll start with the MVP architecture, but I'll design the schema to support sharding later").

### 9.2 — Operational & Observability Empathy (Extension of SDE-2 9.7 & 12)
*In SDE-2, you design for "Success." In SDE-3, you design for "Failure."*

- **The "3 AM Test":** Proactively discussing how to detect and debug the system when it's failing. "I'll add a 'Correlation ID' and 'Distributed Tracing' from the start to avoid a blind spot in this microservice chain."
- **Failure as a First-Class Citizen:** Instead of "I'll add a retry," say "I'll use 'Adaptive Throttling' and 'Load Shedding' to ensure this service doesn't sink the whole fleet if it becomes a bottleneck."
- **Rollback & Migration Logic:** Always addressing how to *deploy* and *roll back* the system safely. "I'll use 'Shadow Reads' to validate the new ranking model against the old one before cutover."

### 9.3 — Business & Economic Alignment (SDE-3 Exclusive)
*Moving from "Technical Correctness" to "Total Value."*

- **Cost-Conscious Architecture:** Discussing "Cloud Spend" as a design constraint. "I'll use 'S3 Tiered Storage' for the old logs to save $500k/year in storage costs."
- **Buy vs. Build Strategies:** Knowing when to use a managed service (e.g., "I'll use Confluent Kafka because managing a 100-node Kafka cluster ourselves isn't our core competency") vs. when to build in-house for extreme scale.
- **Product-Aware Design:** Asking how the system will be used. "If this is a global app, I'll need a 'Home Region' model for latency; if it's a regional app, a single region is enough to avoid complexity."

### 9.4 — Signal Indicators: What the Interviewer is Watching For
*SDE-3 signals are about breadth and depth of experience.*

- **Tradeoff Depth:** Not just naming a tradeoff, but quantifying it. "I'm choosing eventual consistency, which means users might see stale data for up to 5 seconds—this is acceptable for a feed, but not for a payment status."
- **Alternative Design Comparison:** Proactively comparing two viable options. "I could use OT or CRDT; CRDT is better for our 'Offline-First' requirement, even though it has 20% metadata overhead."
- **Future-Proofing:** "I'll design the 'Shard Key' today so that we don't need a migration next year when we grow 10x."
