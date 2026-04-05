# PACELC — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of PACELC, how it extends CAP, and how to apply PA/EL vs PC/EC to real systems. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is PACELC?

> [!question] What is PACELC and how does it differ from CAP theorem?

> [!success]- Answer
>
> **CAP theorem says:** during a partition, choose consistency or availability.
>
> **PACELC goes further:** even during normal operation (no partition), there's a trade-off — consistency costs latency.
>
> **PACELC unpacked:**
> ```
> P = Partition
> A = Availability      (during partition)
> C = Consistency       (during partition)
> E = Else (normal ops)
> L = Latency           (normal ops)
> C = Consistency       (normal ops)
>
> If Partition: choose A or C
> Else:         choose L or C
> ```
>
> **The key insight CAP misses:**
> ```
> CAP: "During failures, you choose C or A"
>
> PACELC adds: "Even without failures — every write that waits for replica
>               confirmation to ensure consistency adds latency.
>               Every system trading consistency for speed is making an EL trade-off."
>
> Example: Instagram serves feeds from nearest replica (fast, potentially stale)
>          This is an EL choice — low latency, eventual consistency
>          CAP doesn't describe this — there's no partition happening
> ```
>
> > [!tip] Interview framing
> > *"CAP describes failure behavior. PACELC extends it to normal operation: even without a partition, enforcing consistency requires waiting for replica confirmation — that adds latency. Every system makes both a P trade-off and an E trade-off."*

---

## Q2 — The Four Labels

> [!question] What are the four PACELC labels? Give a real system example for each.

> [!success]- Answer
>
> **PA/EL — Available during partition, Low latency normally:**
> ```
> During partition: serve stale data, stay available
> Normal ops:       respond immediately, don't wait for all replicas
>
> Examples: Cassandra, DynamoDB, CouchDB
> Use case: Instagram feed, shopping cart, DNS, leaderboards
> ```
>
> **PC/EC — Consistent during partition, strongly Consistent normally:**
> ```
> During partition: refuse requests, stay consistent
> Normal ops:       wait for confirmation, ensure freshness
>
> Examples: Zookeeper, Google Spanner, HBase
> Use case: Payment processing, bank transfers, distributed locks, config management
> ```
>
> **PA/EC — Available during partition, strongly Consistent normally:**
> ```
> During partition: serve stale (keep available)
> Normal ops:       wait for confirmation (be consistent)
>
> Examples: MongoDB (default config)
> Use case: General-purpose systems with mixed requirements
> ```
>
> **PC/EL — does NOT exist:**
> ```
> "Consistent during partition, fast normally"
> This is contradictory:
>   If consistency is so important you'd refuse requests during a partition
>   Why would you serve stale data during normal operation?
>   The values conflict — you'd never see this in practice
> ```
>
> > [!important] PC/EL is contradictory and doesn't exist. If you're willing to serve stale data during normal operation, you're not consistency-first — you're availability-first, and you'd choose PA during partitions too.
>
> > [!tip] Interview framing
> > *"PA/EL: social, caches, feeds — speed and availability matter most. PC/EC: financial, coordination, config — correctness is non-negotiable. PA/EC: general purpose (MongoDB). PC/EL: doesn't exist — contradictory values."*

---

## Q3 — Applying PACELC to a Chat System

> [!question] Design WhatsApp's consistency model using PACELC framing.

> [!success]- Answer
>
> **Question 1 — Partition behavior (PA or PC):**
> ```
> WhatsApp has 2 billion users globally
> Many on poor mobile connections — network partitions are common
>
> What's worse: wrong messages or no messages?
>
> "Wrong" messages in chat = slight delivery delay or minor reordering
> No messages = 2 billion users can't communicate
>
> → PA: stay available during partitions, accept slight consistency weakening
> ```
>
> **Question 2 — Normal operation (EL or EC):**
> ```
> Can you afford to wait for all replicas on every message send?
>
> Users expect near-instant delivery
> Waiting for quorum confirmation adds 50-100ms latency per message
> That's noticeable in real-time messaging
>
> → EL: respond fast, replicate in background, accept eventual consistency
> ```
>
> **Result: PA/EL**
>
> **What this means in practice:**
> ```
> Messages may arrive slightly out of order on rare occasions
> Messages may be briefly delayed during partition recovery
> But the system is always available → 2 billion users can always send messages
>
> Additional: add causal consistency on top of eventual
>             replies must appear after their parent messages
>             this is per-conversation ordering, not global
> ```
>
> **DB choice:** Cassandra — designed for PA/EL, massive write throughput, global distribution
>
> > [!tip] Interview framing
> > *"WhatsApp needs PA/EL. 2 billion users going dark during a partition is unacceptable — PA. Waiting for quorum on every message adds noticeable latency — EL. Cassandra is the natural fit. Add causal consistency per-conversation so replies appear after their parent messages."*

---

## Q4 — The EL vs EC Decision

> [!question] During normal operation (no partition), what are you trading when you choose EL over EC?

> [!success]- Answer
>
> **EL — Else choose Latency:**
> Respond immediately, replicate asynchronously. The write is acknowledged before all replicas have confirmed it.
>
> ```
> Client writes → Primary confirms → responds to client
>                                  → replicates to replicas in background
>
> Read immediately after: may hit a replica that hasn't synced yet → stale read
>
> Latency: low (just primary write)
> Consistency: eventual (replicas catch up within milliseconds to seconds)
> ```
>
> **EC — Else choose Consistency:**
> Wait for replica confirmation before responding.
>
> ```
> Client writes → Primary writes → waits for replica confirm → responds
>
> Read after: all replicas have the write → always see latest
>
> Latency: higher (primary write + network round trip to replica)
> Consistency: strong (every read sees latest write)
> ```
>
> **The concrete numbers:**
> ```
> EL: primary write latency = 5ms → respond to client in 5ms
> EC: primary write + replica confirm = 5ms + 70ms (EU→US) = 75ms
>
> For a service with P99 SLO of 100ms:
>   EL: 5ms write → budget left for other operations
>   EC: 75ms write → nearly entire latency budget consumed
> ```
>
> **When EL is fine:** feed posts, like counts, activity logs, recommendations
> **When EC is required:** financial data, booking inventory, distributed locks
>
> > [!tip] Interview framing
> > *"EL responds immediately, replicates later — stale reads possible but fast. EC waits for replicas to confirm — always fresh but adds network round-trip latency. For cross-region, that's 70-200ms extra per write. Only pay that cost when stale data has real consequences."*

---

## Q5 — PACELC vs CAP: When to Use Which

> [!question] An interviewer asks about your consistency model. Do you use CAP or PACELC framing? Why?

> [!success]- Answer
>
> **Use CAP when:**
> The question is specifically about failure behavior — what happens during a partition.
>
> ```
> "What happens when two of your nodes can't communicate?"
> "How do you handle a network failure in your distributed DB?"
> → CAP framing: "This is a CP system — during partition, we refuse writes 
>                rather than risk inconsistency"
> ```
>
> **Use PACELC when:**
> The question covers both normal operation and failure behavior — why you chose a specific database or architecture.
>
> ```
> "Why did you choose Cassandra over PostgreSQL?"
> "How does your consistency model affect latency?"
> → PACELC framing: "This system needs PA/EL — availability and low latency 
>                   at all times. Cassandra is designed for exactly this."
> ```
>
> **PACELC is a superset of CAP:**
> ```
> PACELC includes the P/A and P/C choice (same as CAP)
> Plus the E/L and E/C choice (normal operation — CAP doesn't cover this)
>
> PACELC is the more complete model
> CAP is still widely understood — don't dismiss it, use whichever fits the question
> ```
>
> **What impresses interviewers:**
> Mentioning PACELC when discussing a database choice shows you understand that consistency trade-offs exist during normal operation, not just during failures. Most candidates only know CAP.
>
> > [!tip] Interview framing
> > *"CAP for failure questions. PACELC for architecture questions. PACELC extends CAP — it includes the partition trade-off plus the latency-vs-consistency trade-off in normal operation. Bringing up PACELC unprompted when justifying a DB choice signals you understand consistency is a continuous trade-off, not just a failure-mode decision."*
