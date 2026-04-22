# Networking

## How the Internet Works
- What happens when you type a URL in the browser (end-to-end story)
- IP addresses — what they are, IPv4 vs IPv6 (awareness)
- Packets — how data travels in chunks, not one stream
- Routers — how packets find their path across the internet
- NAT — why your home device has a private IP but talks to the internet

## OSI Model
- 7 layers — names and what each is responsible for
- TCP/IP 4-layer model — how it maps to OSI
- Why it matters practically — when someone says "L4 load balancer" vs "L7 load balancer"
- Which layers matter most for system design (Transport and Application)

## TCP vs UDP
- TCP — guarantees delivery, ordering, retransmission. How the 3-way handshake works.
- UDP — no guarantees, no handshake, faster
- When to use TCP vs UDP — file transfers, API calls vs video calls, gaming, DNS
- Connection pooling — why reusing TCP connections matters (cost of new connections)

## HTTP and HTTPS
- HTTP request/response structure — method, headers, body, status line
- HTTP methods and idempotency — GET/PUT/DELETE are idempotent, POST is not
- HTTP status codes — key ones in each 2xx / 3xx / 4xx / 5xx group
- HTTP/1.1 vs HTTP/2 — persistent connections, multiplexing (what it fixes)
- HTTPS — what TLS does, why HTTP alone is not safe
- Common headers (Content-Type, Authorization, Cache-Control)

## DNS
- What DNS is and why it exists
- DNS resolution flow (browser → resolver → root → TLD → authoritative)
- Common DNS record types — A, CNAME, MX, TTL
- TTL — why DNS changes take time to propagate
- DNS as a potential SPOF — awareness only

## CDN
- What a CDN is and why it exists (edge servers close to users)
- How CDN caching works (cache-control headers, edge TTL)
- Static vs dynamic content on CDN
- When to use a CDN vs when it doesn't help

## Proxies
- Forward proxy — sits in front of clients (access control, anonymity)
- Reverse proxy — sits in front of servers (SSL termination, load balancing, routing)
- API Gateway as a specialized reverse proxy — auth, rate limiting, routing in one place
- Why reverse proxies appear in almost every system design

## WebSockets and Real-Time Communication
- Why HTTP request/response is not enough for real-time
- What WebSockets are — full-duplex, persistent connection
- How WebSocket upgrade works (starts as HTTP, switches protocol)
- Long polling — what it is, why it's a workaround
- SSE (Server-Sent Events) — server pushes to client, simpler than WebSocket
- When to use WebSocket vs SSE vs polling
