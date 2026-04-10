## Phase 1 - Computer Networking and Internet Fundamentals

> HLD relevance: every system starts with a client talking to a server over a network.
> At SDE-1 level, you do not need protocol internals, but you do need to understand the full request path and the practical meaning of common networking terms.

### 1.1 What happens when a user opens your app
- DNS - convert domain name to IP
- CDN - serve static content closer to the user
- load balancer - distribute traffic across servers
- reverse proxy / API gateway - auth, routing, rate limiting
- application server - runs business logic
- cache and database - where data is served from

### 1.2 OSI and TCP/IP - only what matters
- know why L4 vs L7 load balancer is a real distinction
- know that transport layer handles TCP/UDP
- know that application layer is where HTTP, WebSocket, gRPC live

### 1.3 TCP vs UDP
- TCP - reliable, ordered, connection-oriented
- UDP - faster, no ordering, no built-in retransmission
- when to use TCP - APIs, chat messages, payments, file transfer
- when to use UDP - live audio/video, gaming, DNS
- QUIC - reliability built on UDP, foundation of HTTP/3

### 1.4 DNS
- domain to IP mapping
- TTL and why DNS changes do not apply instantly
- common record types - A, AAAA, CNAME, MX, TXT
- DNS load balancing - multiple IPs behind one name

### 1.5 HTTP and HTTPS
- request/response structure - method, headers, body, status code
- HTTP methods - GET, POST, PUT, PATCH, DELETE
- idempotency - why GET and PUT are different from POST
- HTTPS - encryption in transit using TLS
- auth basics - bearer token, API key, session cookie

### 1.6 HTTP versions
- HTTP/1.1 - persistent connections but limited multiplexing
- HTTP/2 - multiplexing and header compression
- HTTP/3 - QUIC-based, useful for mobile and lossy networks
- interview point - know when version choice affects latency-sensitive systems

### 1.7 Real-time communication
- WebSocket - full duplex, good for chat and live updates
- Server-Sent Events - server to client stream, good for dashboards and notifications
- long polling - simpler but less efficient
- know when polling is still acceptable

### 1.8 Reverse proxy and API gateway
- reverse proxy sits in front of your services
- SSL termination
- routing and path-based forwarding
- rate limiting and auth at the edge
- response compression and caching

### 1.9 Load balancers
- why they exist - no traffic should go to one app server directly
- L4 vs L7 balancing
- common algorithms - round robin, least connections, weighted round robin
- health checks
- sticky sessions and why they reduce scalability

### 1.10 CDN
- edge servers close to the user
- static assets are the default CDN use case
- dynamic content is harder but sometimes still cacheable
- cache invalidation basics

### 1.11 API design basics
- REST as the default external API style
- resource naming
- pagination - offset/limit vs cursor
- filtering and sorting
- async API pattern - return 202 with a job ID for slow work
- webhooks - push results back instead of forcing polling

