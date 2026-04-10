## Phase 8 - Infrastructure and Reliability Patterns

> HLD relevance: these are the patterns that make real systems survivable in production.
> SDE-1 does not need staff-level platform depth, but you should know the common building blocks and why they exist.

### 8.1 Monolith vs microservices
- monolith is simpler to start with
- microservices bring team isolation and scaling flexibility
- microservices also bring operational complexity
- do not choose microservices by default in interviews

### 8.2 Health checks and readiness
- shallow health check - process is alive
- deep health check - dependencies are healthy
- liveness vs readiness
- load balancers should stop sending traffic to unhealthy instances

### 8.3 Resilience patterns
- timeout
- retry with backoff and jitter
- circuit breaker
- bulkhead
- deadline propagation intuition

### 8.4 Rate limiting
- token bucket
- leaky bucket
- fixed window
- sliding window log
- sliding window counter
- know where to apply rate limiting - gateway, API, per-user, per-IP

### 8.5 Auto-scaling and traffic protection
- horizontal auto-scaling
- queue as a buffer for bursty workloads
- load shedding when downstream cannot keep up
- backpressure intuition

### 8.6 ID generation
- auto-increment
- UUID
- Snowflake
- when sortable IDs are useful

### 8.7 Deployment strategies
- rolling deploy
- blue-green
- canary
- rollback planning

### 8.8 Security essentials
- authentication vs authorization
- RBAC and ACL at a high level
- encryption in transit and at rest
- API keys, tokens, and session-based auth

