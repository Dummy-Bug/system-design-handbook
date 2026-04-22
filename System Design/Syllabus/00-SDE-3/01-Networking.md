# Networking

## How the Internet Works
- What happens when you type a URL in the browser — full end-to-end story
- IP addresses — IPv4 vs IPv6
- Routers and gateways — how packets find their path
- NAT (Network Address Translation) — why private IPs need translation

## OSI Model
- 7 layers — names, what each does, example technologies
- TCP/IP 4-layer model — how it maps to OSI
- Why it matters — L4 load balancer vs L7 load balancer, what the difference means

## TCP vs UDP
- TCP — 3-way handshake, reliability, ordering, retransmission, connection pooling
- Head-of-line blocking in TCP — why it matters for HTTP/2 vs HTTP/3
- UDP — no handshake, no ordering, why it's faster
- When to use TCP vs UDP — file transfer, video calls, gaming, DNS
- **QUIC — reliability built on UDP, 0-RTT reconnect, eliminates TCP-level HOL blocking, basis of HTTP/3**
- **TCP congestion control internals — CUBIC (default Linux), BBR (Google), how they differ, why BBR wins on high-latency links**

## DNS
- What DNS is — domain to IP mapping
- DNS resolution flow — recursive query chain
- Key record types — A, AAAA, CNAME, MX, TXT
- TTL — why DNS changes take time to propagate
- DNS load balancing — multiple A records for the same domain
- DNS as a SPOF — how to handle

## HTTP and HTTPS
- HTTP request/response structure — method, headers, body, status line
- HTTP methods and idempotency — GET, POST, PUT, PATCH, DELETE
- HTTP status codes — key ones in each 2xx/3xx/4xx/5xx group
- HTTPS — TLS handshake, certificates, certificate chain
- HTTP authentication — Bearer tokens, API keys, OAuth
- HTTP/1.1 — persistent connections, pipelining, head-of-line blocking problem
- HTTP/2 — multiplexing (fixes HOL blocking at application layer), header compression, server push
- **HTTP/3 — QUIC-based, eliminates TCP-level HOL blocking, 0-RTT reconnect, how it differs from HTTP/2**

## Real-Time Communication
- WebSockets — full duplex, how the upgrade works, use cases (chat, live feeds, auctions)
- Long Polling — simulates real-time, how it works, when still used
- SSE (Server-Sent Events) — server-to-client stream, auto-reconnect
- Comparing WebSocket vs Long Polling vs SSE — latency, scalability, complexity
- **WebRTC — peer-to-peer media, STUN (discover public IP/port), TURN (relay when P2P fails), ICE (negotiation framework), use cases (Google Meet, video calls)**

## Proxies
- Forward proxy — client-side, caching and access control
- Reverse proxy — server-side, SSL termination, load balancing, routing
- API Gateway — routing, auth, rate limiting, transformation, entry point for all case studies

## Load Balancers
- What problem load balancers solve
- L4 vs L7 — what the difference means for routing decisions
- Algorithms — Round Robin, Weighted Round Robin, Least Connections, IP Hash
- Sticky sessions — why needed, tradeoffs with horizontal scaling
- Health checks — how LBs detect dead servers
- Active-active vs active-passive setup
- **GSLB (Global Server Load Balancing) — routing across data centers, Anycast (same IP, nearest node responds)**

## CDN
- What a CDN is — edge servers close to users reduce latency
- Edge servers and Points of Presence (PoPs)
- Static vs dynamic content caching
- Push CDN vs Pull CDN — when to use each
- CDN cache invalidation
- CDN as DDoS shield
- **CDN internals — origin shield (protects origin from cache misses), PoP hierarchy (edge → regional → origin), CDN-to-CDN peering**

## API Design
- REST — stateless, resource-based, uniform interface, RESTful best practices
- Versioning — URL-based vs header-based
- Pagination — offset/limit vs cursor-based vs keyset — tradeoffs
- gRPC — Protocol Buffers, 4 streaming modes, when to prefer over REST
- GraphQL — query language, flexible clients, N+1 problem
- API Gateway — routing, auth, rate limiting, the entry point
- Idempotency keys — essential for reservation, payment, auction APIs
- Async API pattern — 202 Accepted + job ID, polling vs webhook callback
- Webhooks — push-based, HMAC signature verification, idempotent handler

## **mTLS (Mutual TLS)**
- **What mTLS is — both client AND server present certificates, mutual authentication**
- **Why it matters — service-to-service auth without API keys, prevents impersonation**
- **How certificate rotation works — automated via service mesh, no code changes**
- **mTLS vs JWT for service-to-service — mTLS at transport layer, JWT at application layer**

## **Email Protocols**
- **SMTP — protocol used to send and relay email between servers (port 587 submission, port 25 relay)**
- **IMAP — protocol for mail clients to read email from server, email stays on server, multi-device sync**
- **POP3 — downloads email to client and deletes from server, no multi-device sync, legacy**
- **MX records — DNS record that tells senders which mail server handles email for a domain**
- **How Gmail's architecture maps to these protocols — inbound SMTP → storage → client access via IMAP**

## **Multi-Region Networking**
- **Private backbone vs public internet — Google/AWS/Azure own fiber between regions, lower latency and higher reliability than public internet**
- **Latency engineering — choosing region placement to minimize P99 latency for target user geographies**
- **Anycast routing — same IP announced from multiple PoPs, BGP routes request to nearest**
- **Network partitions between regions — what happens, how systems must be designed to tolerate**
