# Scalability — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of vertical vs horizontal scaling, statelessness, load balancing, and the bottleneck chain. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is Scalability?

> [!question] What does it mean for a system to be scalable? Give me a one-line definition.

> [!success]- Answer
>
> **Definition:**
> Scalability is the ability of a system to handle increasing load by adding resources, without requiring fundamental redesign.
>
> **Two dimensions:**
> ```
> Vertical scaling  → add more resources to existing machines
>                     bigger CPU, more RAM, faster disk
>                     simple but has a hardware ceiling
>
> Horizontal scaling → add more machines
>                     more servers, more DB nodes
>                     virtually unlimited ceiling
> ```
>
> **A scalable system vs a non-scalable one:**
> ```
> Non-scalable: single server handles everything
>               traffic doubles → server maxes out → requests fail
>               only fix: bigger server (vertical) — has a hard limit
>
> Scalable:     stateless app servers behind a load balancer
>               traffic doubles → add two more servers
>               traffic 10x → add ten more servers
> ```
>
> > [!important] Scalability is not just "can handle more traffic" — it's "can handle more traffic by adding resources without redesign." A system that requires rewriting every time you scale is not scalable.
>
> > [!tip] Interview framing
> > *"Scalability means adding resources handles the load increase, without redesigning the system. Horizontal scaling — more servers — is the target. Vertical scaling — bigger server — is a short-term fix with a hard ceiling."*

---

## Q2 — Vertical vs Horizontal Scaling

> [!question] What is the difference between vertical and horizontal scaling? When would you use each?

> [!success]- Answer
>
> | | Vertical | Horizontal |
> |---|---|---|
> | What | Bigger machine — more CPU, RAM, disk | More machines — more servers |
> | Limit | Hard ceiling — biggest machine exists | Practically unlimited |
> | Cost | Exponentially expensive at the top | Linear cost |
> | Risk | Single point of failure | Redundant by nature |
> | Complexity | Simple — nothing changes in code | Requires stateless services |
>
> **When to use vertical:**
> ```
> Databases early on  → scaling a DB horizontally (sharding) is complex
>                       vertical buys time cheaply
> Stateful systems    → sessions tied to a machine — horizontal requires refactor
> Early stage startup → quick fix, figure out proper scaling later
> ```
>
> **When to use horizontal:**
> ```
> App servers         → stateless, interchangeable — trivial to add more
> Production at scale → vertical has a ceiling; horizontal doesn't
> High availability   → multiple servers = redundancy for free
> ```
>
> **The rule:**
> ```
> Vertical = emergency lever and early-stage fix
> Horizontal = the long-term answer for everything except stateful systems
> ```
>
> > [!tip] Interview framing
> > *"Vertical is a short-term fix — simple but hits a hardware ceiling and creates a SPOF. Horizontal is the answer for app servers — stateless, interchangeable, unlimited scale. I'd use vertical for databases early on since sharding is complex, then move to horizontal sharding as load demands it."*

---

## Q3 — Statelessness

> [!question] You want to horizontally scale your web servers. A colleague says "we can't — user sessions are stored in server memory." What's the problem and how do you fix it?

> [!success]- Answer
>
> **The problem — sticky sessions or session loss:**
> ```
> User logs in → request goes to Server A → session stored in Server A memory
> Next request → load balancer routes to Server B → no session → user logged out
>
> "Fix": sticky sessions — always route user to same server
>        problem: one server holds all sessions for 1M users
>                 that server goes down → all 1M users logged out
>                 can't rebalance load → hot spots
>                 not truly horizontally scalable
> ```
>
> **The correct fix — externalize session state:**
> ```
> Sessions → Redis (centralized, shared, in-memory)
>
> User logs in → Server A → session stored in Redis
> Next request → Server B → reads session from Redis → still logged in ✓
>
> Any server can handle any request
> Servers are interchangeable and disposable
> Add servers, remove servers — no impact on users
> ```
>
> **The principle — stateless servers:**
> ```
> Stateless server = holds no user-specific state in memory
>                    every request carries enough info to be processed by any server
>                    (JWT token, session ID that Redis can look up)
> ```
>
> > [!important] Horizontal scaling requires stateless servers. Sessions in server memory create SPOF and routing dependencies. Move all state to Redis or the database. Servers become disposable.
>
> > [!tip] Interview framing
> > *"Sessions in server memory prevent horizontal scaling — sticky sessions are a band-aid with their own SPOF. The fix is to externalize state: sessions to Redis, all persistent state to the database. Servers become stateless, interchangeable, and truly horizontally scalable."*

---

## Q4 — The Bottleneck Chain

> [!question] You've scaled your app servers to 50 instances. Latency is still high. Why, and where do you look next?

> [!success]- Answer
>
> **Scalability is never one fix — it's a bottleneck chain:**
> ```
> 10x traffic →
>   App servers CPU saturated → scale out (50 instances) ✓
>   Latency still high → database is now the bottleneck
>   DB connections maxed → add read replicas + cache
>   Still slow? → cache is cold → preload or TTL issue
>   Still slow? → network bandwidth → CDN for static assets
> ```
>
> **After app servers, the database is almost always next:**
> ```
> 50 app servers × 10 connections each = 500 concurrent DB connections
> DB connection pool: 100 → all saturated → requests queue
> DB query time: 200ms → app server waits → user sees 200ms+ latency
> ```
>
> **Investigation order:**
> ```
> 1. Check DB query time (slow query log)
> 2. Check DB connection pool exhaustion (wait queue length)
> 3. Check cache hit rate (if low → most reads hitting DB)
> 4. Check query plans (missing indexes? full table scans?)
> ```
>
> **Standard fixes in order:**
> ```
> 1. Add Redis cache in front of DB → 80-90% of reads served from memory
> 2. Add read replicas → spread read load across multiple DB nodes
> 3. Add connection pooler (PgBouncer) → multiplex connections
> 4. Shard if write throughput is the problem (last resort)
> ```
>
> > [!tip] Interview framing
> > *"Scaling app servers shifts the bottleneck — it doesn't eliminate it. After 50 servers, the database is almost always next. I'd check DB query latency, connection pool exhaustion, and cache hit rate. Standard fix: Redis cache in front of DB, then read replicas if still needed."*

---

## Q5 — Load Balancer Basics

> [!question] What is a load balancer and what algorithms do you know for distributing traffic?

> [!success]- Answer
>
> **What it does:**
> A load balancer sits in front of multiple servers, distributes incoming requests across them, and routes around unhealthy servers via health checks.
>
> ```
> Without LB: all traffic → single server → overloaded
> With LB:    traffic → LB → Server A (33%)
>                          → Server B (33%)
>                          → Server C (33%)
>             Server B dies → LB detects via health check → routes to A and C only
> ```
>
> **Algorithms:**
>
> | Algorithm | How it works | Use when |
> |---|---|---|
> | Round Robin | Requests go to each server in turn | Servers are identical, requests similar duration |
> | Least Connections | Routes to server with fewest active connections | Request durations vary significantly |
> | IP Hash | Same client IP always goes to same server | When session affinity is needed (workaround) |
> | Weighted Round Robin | Some servers get more traffic based on capacity | Servers have different capacities |
>
> **In practice:**
> ```
> Stateless services → Round Robin or Least Connections
>                      both work well, Least Connections is safer
>
> Never use IP Hash as a substitute for proper session management
> It still creates an availability problem — server dies, those users lose session
> ```
>
> > [!tip] Interview framing
> > *"Load balancer distributes traffic across servers and routes around failures via health checks. Round Robin is simplest — works well when request durations are uniform. Least Connections is safer when durations vary — prevents one server from accumulating slow in-flight requests while others are idle."*
