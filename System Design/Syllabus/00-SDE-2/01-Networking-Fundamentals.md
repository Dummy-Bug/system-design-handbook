## Phase 1 — Computer Networking & Internet Fundamentals

> HLD relevance: Every case study starts with a client talking to a server over a network.
> This phase gives you the vocabulary and building blocks for every architecture diagram.

### SDE-2 Depth Bar For This Phase
- Know the full request path end to end and explain where latency and failure happen.
- Understand the practical differences between TCP, UDP, HTTP versions, WebSocket, SSE, reverse proxy, API gateway, and CDN.
- Be able to connect networking choices to concrete case studies like chat, streaming, and notification systems.
- Go beyond definitions: explain when a networking choice changes architecture or operational behavior.

### 1.1 How the Internet Works
- What happens when you type google.com — full end-to-end story
- IP addresses — IPv4 vs IPv6
- Routers and gateways — how packets find their path
- NAT (Network Address Translation) — why private IPs need translation

### 1.2 OSI Model (Know the Layers)
- 7 layers — names, what each does, example technologies
- TCP/IP 4-layer model — how it maps to OSI
- Why it matters — when someone says "L4 load balancer" you know what that means

### 1.3 TCP vs UDP
- TCP — 3-way handshake, reliability, ordering, retransmission, connection pooling
- Head-of-line blocking in TCP — why it matters for HTTP/2
- UDP — no handshake, no ordering, why it's faster
- When to use TCP vs UDP — file transfer, video calls, gaming, DNS

### 1.4 DNS
- What DNS is — domain to IP mapping
- DNS resolution flow — recursive query chain
- Key record types — A, AAAA, CNAME, MX, TXT
- TTL — why DNS changes take time to propagate
- DNS load balancing — multiple A records for the same domain
- DNS as a SPOF — how to handle

### 1.5 HTTP & HTTPS
- HTTP request/response structure — method, headers, body, status line
- HTTP methods and idempotency — GET, POST, PUT, PATCH, DELETE
- HTTP status codes — know the key ones in each 2xx/3xx/4xx/5xx group
- HTTPS — TLS handshake, certificates, certificate chain
- HTTP authentication — Bearer tokens, API keys, OAuth

### 1.6 HTTP Versions
- HTTP/1.1 — persistent connections, pipelining, head-of-line blocking problem
- HTTP/2 — multiplexing (fixes HOL blocking), header compression, server push
- When each version matters in system design (streaming, latency-sensitive APIs)

### 1.7 Real-Time Communication
- WebSockets — full duplex, how the upgrade works, use cases (chat, live feeds, auctions)
- Long Polling — simulates real-time, how it works, when still used
- Server-Sent Events (SSE) — server-to-client stream, auto-reconnect (notifications, dashboards)
- Comparing WebSocket vs Long Polling vs SSE — latency, scalability, complexity

### 1.8 Proxies
- Forward Proxy — client-side, used for caching and access control
- Reverse Proxy — server-side, sits in front of your servers
- What reverse proxies enable — SSL termination, load balancing, caching, routing
- API Gateway as a specialized reverse proxy

### 1.9 Load Balancers
- What problem load balancers solve
- L4 vs L7 load balancers — what the difference means for routing decisions
- Load balancing algorithms — Round Robin, Weighted Round Robin, Least Connections, IP Hash (Sticky Sessions)
- Sticky Sessions — why needed, tradeoffs with horizontal scaling
- Health checks — how LBs detect dead servers and stop sending traffic
- Active-active vs active-passive setup
- Load balancer as SPOF — redundant LB setup

### 1.10 CDN (Content Delivery Network)
- What a CDN is — edge servers close to users reduce latency
- Edge servers and Points of Presence (PoPs)
- Static vs dynamic content caching
- Push CDN vs Pull CDN — when to use each
- CDN cache invalidation
- CDN as DDoS shield
- Where CDN fits in architecture — YouTube, Dropbox, streaming

### 1.11 API Design
- REST — stateless, resource-based, uniform interface
- RESTful best practices
  - Resource naming (nouns not verbs)
  - Versioning — URL-based (/v1/) vs header-based
  - Pagination — offset/limit, cursor-based, keyset (seek method) — know tradeoffs
  - Filtering and sorting
- gRPC — Protocol Buffers, 4 streaming modes, when to prefer over REST (internal services, low latency)
- GraphQL — query language, when it helps (mobile, flexible clients), N+1 problem
- API Gateway — routing, auth, rate limiting, transformation, the entry point for all case studies
- Idempotency keys — essential for reservation, payment, auction APIs
- Async API pattern (long-running operations)
  - Return 202 Accepted with a job ID — client polls GET /jobs/{id} for status
  - Alternative: webhook callback URL at submission
- Webhooks
  - Push-based notification: external service calls YOUR endpoint when an event happens
  - Security: verify webhook signature (HMAC)
  - Reliability: at-least-once delivery — handler must be idempotent
