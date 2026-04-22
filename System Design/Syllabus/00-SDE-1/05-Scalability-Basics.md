# Scalability Basics

## Vertical vs Horizontal Scaling
- What vertical scaling is (bigger machine — more CPU, RAM)
- What horizontal scaling is (more machines)
- Tradeoffs — vertical has a hard ceiling, horizontal adds operational complexity
- When to use which — vertical first, horizontal when vertical limits hit or cost is too high

## Stateless Services
- What stateless means (server holds no session state between requests)
- Why stateless enables horizontal scaling (any server can handle any request)
- How to handle sessions in a stateless world (JWT tokens, or session store in Redis)
- Common mistake — storing state in-process (in-memory variables, local files)

## Auto-Scaling
- What auto-scaling is — automatically add/remove servers based on load
- Reactive auto-scaling — scale up when CPU/memory crosses threshold
- Predictive auto-scaling — scale up before expected traffic (scheduled events, Black Friday)
- Cold start problem — new instances take time to boot, traffic spikes can overwhelm before scale completes
- Why it doesn't replace caching — scaling servers doesn't fix a DB bottleneck

## Load Balancing
- What a load balancer does — distributes traffic across multiple servers
- Common algorithms — round-robin, least connections, IP hash
- Health checks — how load balancers detect dead servers and stop sending traffic
- Layer 4 vs Layer 7 — L4 routes by IP/TCP, L7 routes by HTTP headers/URL/cookies
- Sticky sessions — what they are (same user always to same server), why they break horizontal scaling
- Active-active vs active-passive — both serving traffic vs one on standby

## Single Points of Failure (SPOF)
- What a SPOF is — one component whose failure takes down the whole system
- Common SPOFs — single DB, single load balancer, single cache node
- How to eliminate SPOFs — redundancy at every layer (N+1 rule)
- Awareness: even your load balancer needs redundancy

## API Gateway
- What an API gateway is — single entry point for all client requests
- What it handles — routing, authentication, rate limiting, SSL termination
- Why it simplifies client code — clients talk to one endpoint, not dozens of services
- API gateway vs load balancer — gateway understands HTTP/API semantics, LB just distributes connections

## Replication Basics
- Primary-replica concept (one writer, many readers)
- Read scaling via replicas — route read traffic to replicas
- Replication lag — replica data can be slightly behind primary
- Read-your-own-writes problem — user writes something, immediately reads it back from a lagged replica
- Not a replacement for caching

## Rate Limiting
- What rate limiting is — controlling how many requests a client can make in a time window
- Why it exists — protect servers from abuse, prevent one client from starving others, cost control

**Token Bucket**
- Bucket holds up to C tokens, refills at rate R tokens/sec
- Each request consumes one token. If bucket is empty, request is rejected.
- Allows burst up to C requests, then enforces sustained rate R
- Most common algorithm — used by AWS, Stripe, most APIs

**Fixed Window Counter**
- Divide time into fixed windows (e.g. 1 min). Count requests in current window.
- Reset counter when window resets.
- Problem: a client can send 2× the limit by sending max requests at the end of one window and max again at the start of the next

**Leaky Bucket (awareness)**
- Requests enter a queue, processed at a constant rate. Excess requests are dropped.
- Smooths out bursts — no spikes ever reach the server

**Sliding Window (awareness)**
- More accurate than fixed window — no boundary spike problem
- Higher memory cost — store timestamp of every request

**Distributed Rate Limiting**
- Single server rate limiting doesn't work when you have 10 app servers
- Solution — Redis `INCR` + `EXPIRE` as a shared atomic counter
- All servers talk to the same Redis, so the limit is enforced globally

**Rate Limit Headers**
- `X-RateLimit-Limit` — max requests allowed in the window
- `X-RateLimit-Remaining` — how many requests left
- `Retry-After` — how many seconds until the window resets (returned with 429)
