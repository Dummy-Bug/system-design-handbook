# Layer 7 Load Balancing — Overview

> Layer 7 opens the envelope and reads the letter — routing based on what the request actually says.

> [!abstract] Layer 7 load balancing operates at the Application layer. It decrypts HTTPS, reads the URL, headers, and cookies, then routes to the right service. This makes it intelligent but more expensive than L4. This folder covers SSL termination, content-based routing, canary deployments, full end-to-end request flows, and the API Gateway pattern.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Fundamentals.md | SSL termination, URL/header/cookie routing, canary deployments, L7 cost |
| 02-Request-Flow.md | Instagram profile request — L7 LB flow vs API Gateway flow end to end |
| 03-API-Gateway.md | Auth, rate limiting, transformation, three-layer architecture, Netflix and Uber examples |
