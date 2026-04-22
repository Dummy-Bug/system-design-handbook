# L4, L7 and API Gateway in Production

> [!question] You now understand L4, L7 and API Gateway separately. How do all three fit together in one real system?
> Each layer has exactly one job. None of them overlap. Together they handle every traffic pattern a production system faces.

---

## The Three Layers — One Job Each

| Layer | Component | Job |
|---|---|---|
| 1 — Edge | L4 NLB | Distribute TCP/UDP connections across API Gateway instances. No intelligence, just speed. |
| 2 — Gateway | API Gateway (L7) | Decrypt HTTPS, validate JWT, rate limit, route to the right service |
| 3 — Internal | L4 Internal LB / PgBouncer | Distribute load across service servers and database connections |

None of these overlap. Each solves a problem the others can't:
- L4 NLB can't validate JWTs — it can't read HTTP content
- API Gateway can't handle UDP game traffic — it only understands HTTP
- PgBouncer can't route by URL — it speaks PostgreSQL protocol

---

## Full Production Architecture

```mermaid
flowchart TD
    subgraph Internet["Internet"]
        Player["Valorant Player<br/>UDP game client"]
        InstaUser["Instagram User<br/>Mobile app / browser"]
    end

    subgraph Edge["Edge — Public Facing"]
        NLB_Game["L4 NLB<br/>UDP port 7777<br/>IP hashing<br/>No content inspection"]
        NLB_HTTP["L4 NLB<br/>TCP port 443<br/>Distributes across<br/>API Gateway instances"]
    end

    subgraph GWCluster["API Gateway Cluster — Private"]
        GW1["API Gateway Instance 1<br/>SSL termination<br/>JWT validation<br/>Rate limiting<br/>URL routing"]
        GW2["API Gateway Instance 2<br/>SSL termination<br/>JWT validation<br/>Rate limiting<br/>URL routing"]
    end

    subgraph GameServers["Game Servers — Private"]
        GS1["Game Server A"]
        GS2["Game Server B"]
        GS3["Game Server C"]
    end

    subgraph AppServices["App Services — Private"]
        ILB_U["Internal L4 LB<br/>User Service pool"]
        ILB_F["Internal L4 LB<br/>Feed Service pool"]
        ILB_P["Internal L4 LB<br/>Payment Service pool"]
        US1["User Server A"]
        US2["User Server B"]
        FS1["Feed Server A"]
        FS2["Feed Server B"]
        PS1["Payment Server A"]
    end

    subgraph DataLayer["Data Layer — Private"]
        PGB["PgBouncer L4<br/>Connection pooling"]
        PG_Primary["Postgres Primary"]
        PG_Replica["Postgres Replica"]
    end

    Player -->|"UDP port 7777 / 128 packets/sec"| NLB_Game
    InstaUser -->|"HTTPS port 443 / JWT token"| NLB_HTTP

    NLB_Game -->|"IP hash → same server per player"| GS1
    NLB_Game --> GS2
    NLB_Game --> GS3

    NLB_HTTP --> GW1
    NLB_HTTP --> GW2

    GW1 -->|"/api/user/* X-User-Id: 98765"| ILB_U
    GW1 -->|"/api/feed/* X-User-Id: 98765"| ILB_F
    GW2 -->|"/api/checkout/* X-User-Id: 98765"| ILB_P

    ILB_U --> US1
    ILB_U --> US2
    ILB_F --> FS1
    ILB_F --> FS2
    ILB_P --> PS1

    US1 -->|"PostgreSQL protocol / TCP port 5432"| PGB
    US2 --> PGB
    FS1 --> PGB
    FS2 --> PGB
    PS1 --> PGB

    PGB --> PG_Primary
    PGB --> PG_Replica
```

---

## Layer by Layer — What Each Does and Why

### Layer 1 — L4 NLB at the Edge

**For HTTP traffic (Instagram):**
```
Instagram app → HTTPS port 443 → L4 NLB
  ✓ Distributes TCP connections across API Gateway instances
  ✗ Cannot read HTTPS content — it's encrypted
  ✗ Cannot validate JWT — doesn't know what a JWT is
```

Why L4 here and not L7? The API Gateway IS the L7 layer. Decrypting HTTPS twice — at the NLB and again at the gateway — would double the CPU overhead and require managing certificates in two places. L4 just forwards TCP at wire speed.

**For UDP game traffic (Valorant):**
```
Valorant client → UDP port 7777 → L4 NLB
  ✓ IP hashing — same player always hits same game server
  ✓ UDP-capable — API Gateway doesn't handle UDP at all
  ✓ No content inspection needed — all packets go to game server pool
```

---

### Layer 2 — API Gateway Cluster

```
L4 NLB forwards TCP connection → API Gateway instance
  ✓ SSL termination — decrypts HTTPS, can now read the request
  ✓ JWT validated — invalid token → 401, request dies here
  ✓ Rate limit checked — 429 if exceeded
  ✓ URL read → /api/user/* → routes to User Service internal LB
  ✓ X-User-Id: 98765 attached — service never needs to decode JWT
```

The gateway is the only component that sees the raw JWT token. Everything behind it sees only `X-User-Id` — already decoded and verified.

---

### Layer 3 — Internal L4 LBs and PgBouncer

**Service-level load balancing:**
```
API Gateway → Internal L4 LB (User Service) → picks User Server A or B
  ✓ Distributes load across service instances
  ✗ No auth needed — private network, already trusted
  ✗ No SSL needed — internal traffic is plain HTTP
```

**Database connection pooling:**
```
Service → PgBouncer (L4) → PostgreSQL
  ✓ Multiplexes hundreds of service connections into small DB connection pool
  ✓ Protocol-agnostic — PostgreSQL binary wire protocol, not HTTP
  ✗ No URL routing — all connections go to same PostgreSQL cluster
```

---

## Decision Framework

| Traffic | Component | Why |
|---|---|---|
| External HTTPS — multiple services | L4 NLB → API Gateway | Need JWT auth, rate limiting, URL routing |
| External UDP — game traffic | L4 NLB directly | Non-HTTP protocol, API Gateway can't handle UDP |
| External HTTPS — single service | L7 LB (no API Gateway needed) | No cross-cutting auth/rate limiting required |
| Internal service → service | Internal L4 LB | Private network, trust exists, no content routing needed |
| Service → PostgreSQL / MySQL | PgBouncer (L4) | Non-HTTP protocol, connection pooling needed |
| Live stream ingestion (RTMP) | L4 NLB directly | Non-HTTP protocol |

---

## The One-Line Summary Per Layer

```
L4 NLB at edge        →  fast TCP/UDP distribution, no intelligence
API Gateway (L7)      →  auth, rate limiting, SSL, routing — all in one place
Internal L4           →  speed, trust already established, no HTTP overhead
```
