## Phase 1 - Computer Networking and Internet Fundamentals

> HLD relevance: every large-scale system still begins with a client request crossing a network.
> SDE-3 depth means you do not stop at naming the boxes. You should be able to explain where latency, control, failure, and routing decisions actually happen.

### SDE-3 depth bar for this phase
- Know the full request path end to end, not just isolated definitions.
- Be able to compare alternative transport and API choices for a workload.
- Be able to explain failure behavior: DNS lag, LB failure, TCP retransmission cost, sticky-session tradeoffs, CDN cache staleness.
- Be able to connect networking choices to concrete system designs like chat, streaming, search, and global APIs.

### 1.1 How the Internet Works
- Full request path: client -> local DNS resolver -> authoritative DNS -> CDN / edge -> load balancer -> API gateway / reverse proxy -> application service -> cache / database / async systems.
- Where latency is introduced: DNS lookup, TLS handshake, cross-region hop, proxy chain, cache miss, downstream fan-out.
- Where failures happen: DNS misconfiguration, packet loss, LB health-check drift, proxy overload, regional routing mistakes.
- Control plane vs data plane intuition: DNS, config, and routing rules are control plane; request serving is data plane.

### 1.2 OSI Model (Know the Layers)
- Enough OSI / TCP-IP knowledge to reason about L4 vs L7 routing and debugging.
- Know which problems belong to transport layer vs application layer.
- Examples: retransmission and HOL blocking are transport concerns; idempotency and pagination are application concerns.
- Interview depth: you do not need textbook recitation, but you should use "L4" and "L7" correctly.

### 1.3 TCP vs UDP
- TCP: handshake, reliability, retransmission, ordering, congestion control, connection reuse.
- Head-of-line blocking and why it matters for latency-sensitive workloads.
- UDP: no built-in ordering or retransmission, lower overhead, useful when low latency matters more than perfect delivery.
- Workload mapping: APIs and payments -> TCP; gaming / live media -> UDP; DNS -> UDP with retries.
- Operational angle: TCP retries and packet loss show up as tail latency, not just as "slow network."

### 1.4 QUIC and HTTP/3
- QUIC gives reliability over UDP and avoids TCP-level HOL blocking.
- 0-RTT reconnect is useful for mobile / flaky networks.
- Why QUIC helps latency-sensitive systems with connection churn.
- What it does not fix: bad application design, slow origin, or overloaded backends.

### 1.5 DNS
- Record types that matter in design conversations: A, AAAA, CNAME, MX, TXT.
- TTL and why DNS is bad for instant failover.
- GeoDNS / latency-based routing as a coarse traffic-steering tool.
- DNS caching at multiple layers means rollback is not instantaneous.
- Gmail / mail-system tie-in: MX records are mandatory knowledge.

### 1.6 HTTP and HTTPS
- Request / response model, headers, bodies, status codes.
- Method semantics and idempotency: GET, PUT, DELETE naturally safer to retry than POST.
- TLS handshake and certificate chain at the practical level.
- Bearer tokens, API keys, cookies, and mTLS at the right abstraction.
- Senior-level expectation: tie API semantics to retry safety and caching behavior.

### 1.7 HTTP Versions
- HTTP/1.1: persistent connections, limited multiplexing, connection-level inefficiency.
- HTTP/2: multiplexing, header compression, better connection reuse.
- HTTP/3: QUIC transport, better recovery under lossy mobile conditions.
- Workload-level tradeoff: what matters for chat, CDN-heavy traffic, search APIs, and browser-heavy clients.

### 1.8 Real-Time Communication
- WebSocket: full duplex, stateful connection management, common for chat and live feeds.
- SSE: simpler server-to-client streaming for dashboards and notifications.
- Long polling: still acceptable when scale is smaller or infra simplicity matters.
- WebRTC awareness for peer-to-peer media systems.
- Senior-level depth: connection stickiness, reconnect storms, and fan-out pressure on real-time services.

### 1.9 Proxies and API Gateways
- Reverse proxy responsibilities: SSL termination, routing, request shaping, compression.
- API gateway responsibilities: auth, rate limiting, quota enforcement, request transformation.
- Gateway as a policy choke point, not just a routing box.
- Failure modes: gateway overload, misconfigured auth policy, centralized bottleneck.

### 1.10 Load Balancers
- L4 vs L7 load balancers and what each can inspect.
- Algorithms: round robin, weighted round robin, least connections, sticky routing.
- Health checks, connection draining, readiness vs liveness.
- Active-active vs active-passive load-balancing setups.
- Senior-level depth: sticky sessions are easy early and painful later because they fight elasticity and failover.

### 1.11 CDN (Content Delivery Network)
- Edge caching for static assets and media delivery.
- Dynamic content caching where safe, and why it is much harder.
- Cache invalidation, signed URLs, private content, and origin shielding.
- CDN as latency reducer, origin protector, and partial DDoS absorber.
- Senior-level depth: explain what should terminate at the edge vs what must reach origin.

### 1.12 Email Protocols (SMTP / IMAP / POP3)
- SMTP for send / relay path.
- IMAP for synchronized mailbox reads.
- POP3 awareness as legacy fetch-and-delete behavior.
- Mail flow: sender -> outbound SMTP -> MX lookup -> recipient server -> mailbox access.
- Why email systems are eventually delivered and retry-heavy by nature.

### 1.13 API Design
- REST as the default external API style.
- gRPC as a strong internal-service choice when low latency and strong contracts matter.
- GraphQL only when client shape flexibility is the real problem.
- Versioning, filtering, sorting, and pagination strategy.
- Async API pattern: 202 + job ID + polling or callback.
- Webhooks: signature verification, retries, idempotent handling.
- Senior-level depth: tie API contract design to retry behavior, latency SLOs, and backward compatibility.
