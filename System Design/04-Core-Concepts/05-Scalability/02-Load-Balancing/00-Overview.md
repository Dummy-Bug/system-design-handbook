# Load Balancing — Overview

> A load balancer is what makes horizontal scaling actually work — without it, adding servers solves nothing.

> [!abstract] Once you have multiple servers, something needs to decide which server handles each request. This folder covers how load balancers work, how they pick servers, and the difference between routing at the network layer (L4) vs the application layer (L7).

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Load-Balancing.md | What it is, health checks, SPOF problem, auto-scaling |
| 02-Algorithms.md | Round robin, least connections, IP hashing, weighted |
| 03-Layer4-Fundamentals.md | OSI model, what L4 sees, port numbers, IANA, why it's fast |
| 04-Layer4-How-It-Works.md | NAT, connection table, TCP walkthrough, UDP walkthrough, Valorant example |
| 05-Layer4-Real-World.md | Real world usage, limitations, how L4 and L7 work together |
| 06-Layer7.md | Routing by request content, SSL termination, API Gateway |
