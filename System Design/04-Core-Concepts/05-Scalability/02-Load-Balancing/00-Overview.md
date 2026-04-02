# Load Balancing — Overview

> A load balancer is what makes horizontal scaling actually work — without it, adding servers solves nothing.

> [!abstract] Once you have multiple servers, something needs to decide which server handles each request. This folder covers how load balancers work, how they pick servers, and the difference between routing at the network layer (L4) vs the application layer (L7) — with full end-to-end walkthroughs for both.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Load-Balancing.md | What it is, health checks, SPOF problem, auto-scaling |
| 02-Algorithms.md | Round robin, least connections, IP hashing, weighted |
| 03-L4/ | Layer 4 — OSI model, NAT, connection tables, real world examples |
| 04-L7/ | Layer 7 — SSL termination, URL routing, API Gateway, Instagram walkthrough |
| 05-L4-L7-APIGateway-In-Production.md | How all three work together — full production architecture |
| 06-Interview-Cheatsheet.md | Algorithm choice, L4 vs L7, SPOF fix, API Gateway decision, three-layer architecture |
