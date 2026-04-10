## Phase 1 - Computer Networking and Internet Fundamentals

> HLD relevance: senior designs still start with the same request path as junior ones.
> The difference is that SDE-3 candidates are expected to understand where latency, failure, and control actually live along that path.

### 1.1 What happens when a user hits your system
- full request path: client -> DNS -> CDN / edge -> load balancer -> API gateway / reverse proxy -> application service -> cache / DB / async systems
- where latency is added at each step
- where auth, routing, caching, and rate limiting usually happen

### 1.2 OSI and TCP/IP - practical meaning
- enough layer knowledge to reason about L4 vs L7 load balancers
- enough layer knowledge to reason about transport vs application problems
- know where TCP, QUIC, HTTP, TLS, WebSocket, and gRPC sit

### 1.3 TCP vs UDP vs QUIC
- TCP - reliability, ordering, retransmission, head-of-line blocking
- UDP - lower overhead, no ordering, no retransmission
- QUIC - reliability over UDP, 0-RTT reconnect, HTTP/3 foundation
- interview angle - know how transport choice affects chat, live video, and API traffic

### 1.4 DNS and global request routing
- recursive resolution flow
- TTL and operational consequences during failover
- A, AAAA, CNAME, MX, TXT
- GeoDNS and GSLB at a high level
- DNS as a control-plane tool, not a perfect real-time failover mechanism

### 1.5 HTTP and HTTPS
- methods, status codes, headers, body
- idempotency semantics
- TLS and certificates
- bearer token, cookie, API key, mTLS at the right abstraction level

### 1.6 HTTP versions
- HTTP/1.1 - persistent connections, application-level HOL pain
- HTTP/2 - multiplexing and header compression
- HTTP/3 - QUIC-based transport benefits
- when version choice actually matters in system design

### 1.7 Real-time communication
- WebSocket - full duplex, stateful connection management
- SSE - server-to-client stream, simpler than WebSocket
- long polling - fallback pattern with higher cost
- WebRTC awareness for media systems

### 1.8 Proxies, gateways, and edge control
- reverse proxy
- API gateway
- WAF awareness
- SSL termination
- path-based routing, auth, request shaping, rate limiting

### 1.9 Load balancers
- L4 vs L7
- round robin, weighted round robin, least connections, sticky sessions
- health checks, liveness, readiness
- active-active vs active-passive
- regional traffic steering intuition

### 1.10 CDN
- static vs dynamic caching
- cache invalidation
- origin shielding
- CDN as latency reducer and partial DDoS shield
- where CDN helps and where it does not

### 1.11 API design and service-to-service communication
- REST as the default external interface
- gRPC for internal low-latency service calls
- GraphQL when client flexibility is the actual problem
- pagination, filtering, sorting, versioning
- async API pattern for long-running work
- webhooks and callback-based completion

