## Phase 1 — Computer Networking & Internet Fundamentals

> HLD relevance: Every case study starts with a client talking to a server over a network.
> This phase gives you the vocabulary and building blocks for every architecture diagram.

### SDE-2 Depth Bar For This Phase
- Know the full request path end to end and explain where latency and failure happen.
- Understand the practical differences between TCP, UDP, HTTP versions, WebSocket, SSE, reverse proxy, API gateway, and CDN.
- Be able to connect networking choices to concrete case studies like chat, streaming, Gmail, and notification systems.
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
- Head-of-line blocking in TCP — why it matters for HTTP/2 vs HTTP/3
- UDP — no handshake, no ordering, why it's faster
- When to use TCP vs UDP — file transfer, video calls, gaming, DNS
- QUIC — reliability built on UDP, basis of HTTP/3

### 1.4 DNS
- What DNS is — domain to IP mapping
- DNS resolution flow — recursive query chain
- Key record types — A, AAAA, CNAME, MX, TXT (skip PTR/SOA)
- TTL — why DNS changes take time to propagate
- DNS load balancing — multiple A records for the same domain
- DNS as a SPOF — how to handle

### 1.5 HTTP & HTTPS
- HTTP request/response structure — method, headers, body, status line
- HTTP methods and idempotency — GET, POST, PUT, PATCH, DELETE
- HTTP status codes — know the key ones in each 2xx/3xx/4xx/5xx group
- HTTPS — TLS handshake, certificates, certificate chain
- HTTP authentication — Bearer tokens, API keys, OAuth (not cookie flags)

### 1.6 HTTP Versions
- HTTP/1.1 — persistent connections, pipelining, head-of-line blocking problem
- HTTP/2 — multiplexing (fixes HOL blocking), header compression, server push
- HTTP/3 — QUIC-based, eliminates TCP-level HOL blocking, 0-RTT reconnect
- When each version matters in system design (streaming, latency-sensitive APIs)

### 1.7 Real-Time Communication
- WebSockets — full duplex, how the upgrade works, use cases (chat, live feeds, auctions)
- Long Polling — simulates real-time, how it works, when still used
- Server-Sent Events (SSE) — server-to-client stream, auto-reconnect (notifications, dashboards)
- Comparing WebSocket vs Long Polling vs SSE — latency, scalability, complexity
- WebRTC — peer-to-peer, STUN/TURN servers, use cases (Google Meet, video calls)

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
- Global Server Load Balancing (GSLB) — routing across data centers
- Load balancer as SPOF — redundant LB setup

### 1.10 CDN (Content Delivery Network)
- What a CDN is — edge servers close to users reduce latency
- Edge servers and Points of Presence (PoPs)
- Static vs dynamic content caching
- Push CDN vs Pull CDN — when to use each
- CDN cache invalidation
- CDN as DDoS shield
- Where CDN fits in architecture — YouTube, Dropbox, news feed, streaming

### 1.11 Email Protocols (SMTP / IMAP / POP3)
> Directly applies to: Gmail case study

- **SMTP (Simple Mail Transfer Protocol)** — the protocol used to *send and relay* email between servers
  - Port 587 (submission from client to mail server), Port 25 (server-to-server relay)
  - Flow: your mail client → your mail server (SMTP submission) → recipient's mail server (SMTP relay) → recipient's inbox
  - SMTP is push-only — it delivers email to the destination server but does not let clients fetch mail
- **IMAP (Internet Message Access Protocol)** — the protocol used by mail clients to *read* email from the server
  - Email stays on the server; client syncs a local view. Multiple devices can all see the same inbox.
  - Supports folders, flags (read/unread/starred), server-side search
  - This is what Gmail, Outlook, and Apple Mail use when you add an account
- **POP3 (Post Office Protocol 3)** — older protocol that *downloads* email to the client and deletes it from the server
  - No sync across devices — once downloaded on your laptop, it's gone from the server
  - Still used in some legacy systems; don't design with it
- **What this means for Gmail's architecture**
  - Inbound email arrives via SMTP → parsed and stored in Gmail's internal storage
  - Client apps access mail via IMAP (or Gmail's proprietary API which abstracts IMAP)
  - Outbound email submitted by client via SMTP submission → Gmail's outbound relay
- **MX records (Mail Exchanger)** — DNS record type that says "email for this domain goes to this mail server." When you send to user@company.com, your mail server looks up the MX record for company.com to find the destination SMTP server.

### 1.12 API Design
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
- **Async API pattern (long-running operations)**
  - Problem: some operations take minutes — video transcoding, report generation, large data export
  - Return `202 Accepted` with a job ID — client doesn't wait
  - Client polls a status endpoint: `GET /jobs/{id}` → `{ status: "processing" }` / `{ status: "complete", result_url: "..." }`
  - Alternative: provide a callback/webhook URL at submission, server calls it when done
  - Use in: YouTube transcoding, Dropbox sync, any async processing pipeline
- **Webhooks**
  - Push-based notification: external service calls YOUR endpoint when an event happens
  - Opposite of polling — instead of asking "any updates?" every 5 seconds, the source tells you immediately
  - Example: Stripe fires `POST /your-server/webhook` with `{ event: "payment.succeeded", data: {...} }` when a charge completes
  - Security: verify webhook signature (HMAC) to ensure it came from the real source, not an attacker
  - Reliability: webhook delivery is at-least-once — your handler must be idempotent (same event delivered twice should not double-process)
  - Retry: if your endpoint returns 5xx, the sender retries with exponential backoff
  - Directly applies to: Payment System, Notification System, any third-party integration
