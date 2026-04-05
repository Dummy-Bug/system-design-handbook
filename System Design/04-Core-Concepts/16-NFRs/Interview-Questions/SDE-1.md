# NFRs — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of non-functional requirements, why they come before design, and how each NFR forces specific architecture decisions. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Are NFRs?

> [!question] What are non-functional requirements? How are they different from functional requirements?

> [!success]- Answer
>
> **Functional requirements — what the system does:**
> ```
> Users can post tweets
> Users can follow other users
> Users can see a feed of posts from people they follow
> Users can search for content
> ```
>
> **Non-functional requirements — how well it does it:**
> ```
> Feed loads in under 200ms (latency)
> System is available 99.99% of the time (availability)
> Data is never lost (durability)
> System handles 500M users (scalability)
> Sensitive data is encrypted (security)
> ```
>
> **Why NFRs come BEFORE design:**
> ```
> "Design a feed system"
>
> Without NFRs:         With NFRs:
> Which DB? No idea.    Availability > consistency → Cassandra
> How many servers?     500M users, 1M writes/sec → sharding + queues
> Cache or not?         Feed must load < 200ms → cache required
> ```
>
> The same feature — a tweet feed — requires completely different architecture depending on the NFRs. Without them, every design decision is a guess.
>
> > [!important] In every design interview: extract NFRs before drawing a single box. Every design decision should reference back to an NFR. "I'm choosing Cassandra here because the NFR is high availability and eventual consistency is acceptable."
>
> > [!tip] Interview framing
> > *"Functional requirements are what the system does. NFRs are how well it does it — availability, latency, durability, security, scalability. I extract NFRs first because they determine the architecture. The same feature needs a completely different design at 100 users vs 500M users."*

---

## Q2 — The Six Core NFRs

> [!question] Name the six core non-functional requirements. For each one, give a one-line description of what it forces architecturally.

> [!success]- Answer
>
> | NFR | What it forces |
> |---|---|
> | **Availability** | Redundancy at every layer, multi-AZ, automatic failover, health checks |
> | **Consistency** | Quorum reads/writes, synchronous replication, CP database (Postgres, Spanner) |
> | **Latency** | Caching (Redis), CDN, read replicas, async processing, denormalization |
> | **Scalability** | Horizontal scaling, DB sharding, message queues (Kafka), auto-scaling |
> | **Durability** | WAL, replication factor 3+, backups (full + incremental), cross-region replication |
> | **Security** | JWT auth, TLS/HTTPS, encryption at rest (AES-256), rate limiting, input validation |
>
> **The three-step move for each NFR:**
> ```
> Step 1: State the NFR
>   "The NFR here is low latency — feed must load under 200ms"
>
> Step 2: State what it forces
>   "That forces caching and read replicas"
>
> Step 3: State the trade-off
>   "I'm accepting eventual consistency — for a feed, slightly stale data is fine"
> ```
>
> > [!important] Never just say "I'll use Redis." Say why — which NFR forces it — and say what you're giving up. NFR → decision → trade-off is the pattern that signals senior-level thinking.
>
> > [!tip] Interview framing
> > *"Six core NFRs: availability, consistency, latency, scalability, durability, security. Each forces specific decisions. Latency → caching + read replicas. Durability → WAL + replication + backups. Always state the NFR, then what it forces, then the trade-off."*

---

## Q3 — NFR Questions During Requirements

> [!question] You're in a system design interview and the interviewer says "design a food delivery platform." What NFR questions do you ask before drawing anything?

> [!success]- Answer
>
> **The goal:** understand the constraints before making architecture decisions.
>
> **Questions to ask:**
>
> **Scale (scalability):**
> ```
> "What's the expected scale — orders per second, number of users?"
> → 100 orders/sec vs 100,000 orders/sec require very different architectures
> → Orders of magnitude matter more than exact numbers
> ```
>
> **Latency:**
> ```
> "Are there latency requirements? Should the app feel real-time?"
> → Map updates for driver location: real-time (websockets, <1s updates)
> → Order history: can be 1-2 seconds, no real-time needed
> ```
>
> **Availability:**
> ```
> "What's the acceptable downtime? Is there an SLO?"
> → 99.9% vs 99.99% require completely different engineering investment
> → Peak hours (dinner time) especially critical
> ```
>
> **Consistency:**
> ```
> "Is it okay for a user to see slightly stale restaurant menu prices?"
> → Menu: eventual consistency fine (a few seconds stale is harmless)
> → Order status: user expects real-time accuracy
> → Payment: must be strongly consistent — no stale balance
> ```
>
> **Durability:**
> ```
> "Is losing an order ever acceptable?"
> → Almost certainly no — orders are financial transactions
> → Forces durable storage, WAL, replication
> ```
>
> > [!tip] Interview framing
> > *"Before drawing anything I'd ask: expected scale (orders per second), latency requirements (is driver location real-time?), SLO for availability, consistency requirements per data type (menu vs order vs payment), and durability requirements. These answers determine the entire architecture."*

---

## Q4 — Conflicting NFRs

> [!question] A client says "I want the system to be both highly available AND strongly consistent." How do you respond?

> [!success]- Answer
>
> **Don't say "we can do both." Name the conflict and make the trade-off explicit.**
>
> **The conflict:**
> CAP theorem — during a network partition, you can guarantee availability or consistency, not both. Strong consistency (quorum) means waiting for a majority of nodes — if they can't communicate, the system may refuse requests.
>
> **The three-step response:**
>
> **Step 1 — Name the conflict:**
> ```
> "High availability and strong consistency are in tension.
>  During a network partition, CAP theorem tells us we can only guarantee one.
>  Quorum-based consistency means some partitions cause the system to become unavailable."
> ```
>
> **Step 2 — Ask which matters more, and for what data:**
> ```
> "Let me ask: for which data is consistency most critical, and for which
>  is availability most critical?
>
>  In most systems:
>   Financial data (payments, balances) → consistency wins
>   User-facing content (feeds, profiles) → availability wins"
> ```
>
> **Step 3 — Propose a hybrid:**
> ```
> "I'd apply consistency selectively:
>   Payment path: synchronous replication, quorum reads → CP
>   Feed path: eventual consistency, served from nearest replica → AP
>
>  This gives you strong consistency where it costs money if wrong,
>  and high availability everywhere else."
> ```
>
> > [!tip] Interview framing
> > *"Availability and strong consistency are in tension — CAP theorem. I'd ask: which data absolutely cannot be stale? Apply strong consistency only there. Everything else: eventual consistency for maximum availability. This is the standard hybrid approach."*

---

## Q5 — Translating NFRs to Architecture

> [!question] The NFR is: "P99 latency must be under 100ms for the product search endpoint." Walk me through the architecture decisions this forces.

> [!success]- Answer
>
> **What P99 < 100ms means:**
> ```
> 99 out of 100 requests must complete in under 100ms
> The slowest 1% (tail) is still within budget
> ```
>
> **Trace the latency budget to find what must change:**
>
> **Without any optimization — current state:**
> ```
> Search request → app server → DB full-text search query
> DB query on 10M products: ~300-500ms
> ✗ Way over budget
> ```
>
> **Decision 1 — Cache search results (Redis):**
> ```
> Popular searches: "pizza near me", "wireless headphones"
> Cache these results in Redis with TTL of 5 minutes
>
> Cache hit: Redis read = ~1ms → well within budget ✓
> Cache miss: still must do DB query
> ```
>
> **Decision 2 — Dedicated search infrastructure:**
> ```
> Full-text search on relational DB: slow for complex queries
> Elasticsearch or OpenSearch: optimized for text search
> → inverted index → sub-10ms for most queries
> ```
>
> **Decision 3 — Read replicas + geographic routing:**
> ```
> DB query from EU to US primary: adds ~70ms network latency
> Read replica in EU: DB query stays local → 5-10ms
> → P99 within budget ✓
> ```
>
> **Decision 4 — Async for non-critical work:**
> ```
> Logging the search query for analytics: don't do synchronously
> Async queue → doesn't add to response time
> ```
>
> **The trade-offs accepted:**
> ```
> Redis cache → search results may be 5 minutes stale (acceptable for search)
> Read replica → replica lag means results may not include very recent products
> Elasticsearch → added infrastructure complexity
> ```
>
> > [!tip] Interview framing
> > *"P99 < 100ms forces me to trace the latency budget: DB full-text search is 300ms alone — over budget. Fix: Redis cache for popular searches (1ms hit), Elasticsearch for complex queries (sub-10ms), read replicas geographically close to users (eliminates network latency). Each decision has a trade-off I'd call out explicitly."*
