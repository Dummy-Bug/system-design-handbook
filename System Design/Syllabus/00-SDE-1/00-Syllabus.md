# SDE-1 System Design Syllabus (0–2 YOE)

## Concepts

1. Networking
2. APIs
3. Databases
4. Caching
5. Scalability Basics (includes Rate Limiting)
6. Storage
7. Security Basics
8. Back-of-Envelope Estimation
9. Message Queues
10. Interview Framework
11. Basic Observability (bonus strong hire signal)

## Case Studies

1. URL Shortener
2. Pastebin
3. Leaderboard
4. Simple Social Feed

---

## Required vs Stretch

> **Required** — must know to pass an SDE-1 system design interview.
> **Stretch** — not required to pass, but knowing it puts you at the top of the SDE-1 pool and signals early SDE-2 readiness.

### Concepts

| Topic | Area | Level |
|---|---|---|
| How the internet works (DNS, HTTP, TCP/UDP) | Networking | Required |
| HTTP/1.1 vs HTTP/2 | Networking | Required |
| WebSocket vs SSE vs Long Polling | Networking | Required |
| CDN — what it is and when to use it | Networking | Required |
| L4 vs L7 Load Balancer | Networking | Required |
| REST fundamentals, HTTP methods, status codes | APIs | Required |
| URL versioning and pagination (offset vs cursor) | APIs | Required |
| Idempotency — what it means and why it matters | APIs | Required |
| JWT basics — access token + refresh token pattern | APIs | Required |
| SQL basics — ACID, joins, indexes, schema design | Databases | Required |
| B+ Tree — what it is, how range scans work | Databases | Required |
| NoSQL intro — key-value, document, column-family | Databases | Required |
| Read replicas and replication lag | Databases | Required |
| Cache-aside, write-through, write-back | Caching | Required |
| LRU vs LFU eviction | Caching | Required |
| Redis data structures and use cases | Caching | Required |
| Cache stampede, avalanche, penetration | Caching | Required |
| Vertical vs horizontal scaling | Scalability | Required |
| Stateless services — why they enable horizontal scaling | Scalability | Required |
| Load balancing algorithms (round-robin, least connections) | Scalability | Required |
| SPOF — what it is and how to eliminate it | Scalability | Required |
| API Gateway vs Load Balancer | Scalability | Required |
| Object storage — S3, pre-signed URLs, multipart upload | Storage | Required |
| Storage tiers — hot, warm, cold | Storage | Required |
| Auth vs Authz, JWT, RBAC vs ACL | Security | Required |
| TLS everywhere, AES-256 at rest | Security | Required |
| Estimation framework — QPS, storage, bandwidth | Estimation | Required |
| When estimation changes your architecture | Estimation | Required |
| Producer/consumer model, at-least-once delivery | Message Queues | Required |
| Dead Letter Queue, visibility timeout | Message Queues | Required |
| 45-minute interview structure | Interview Framework | Required |
| NFR → Architecture decision cheat sheet | Interview Framework | Required |
| Rate Limiting — Token Bucket, Fixed Window | Scalability | **Stretch → SDE-2** |
| Distributed rate limiting with Redis | Scalability | **Stretch → SDE-2** |
| Basic observability — logging, metrics, what to say | Observability | **Stretch → SDE-2** |
| gRPC — what it is, when to prefer over REST | APIs | **Stretch → SDE-2** |
| Async API pattern — 202 Accepted + job ID | APIs | **Stretch → SDE-2** |
| Cursor-based pagination — why it wins at scale | Databases | **Stretch → SDE-2** |

### Case Studies

| Case Study | Level |
|---|---|
| URL Shortener | Required |
| Leaderboard | Required |
| Simple Social Feed | Required |
| Pastebin | Required |
