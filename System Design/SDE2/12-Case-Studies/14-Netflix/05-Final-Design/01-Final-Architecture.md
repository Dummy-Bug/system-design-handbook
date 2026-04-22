# Final Design — Netflix

> [!info] Final Netflix architecture — all deep dive decisions reflected.
> Every component here was justified through an interview session. Nothing is added speculatively.

---

## What Changed from Base Architecture

The base architecture had a single app server returning a manifest URL, with the client fetching chunks directly from S3. That breaks at scale in three ways: S3 cannot serve 500 Tbps of global traffic, a single server is a SPOF, and there is no failure isolation between services.

Every deep dive added one layer of the final design:

| Deep Dive | What it added |
|---|---|
| Transcoding | Kafka-driven pipeline, S3 chunk storage at multiple resolutions |
| Manifest + HLS | Manifest file with CDN URLs, client-side ABR quality switching |
| Caching | CDN edge layer, push for hot releases, pull + LRU/TTL for catalogue |
| DB | PostgreSQL for content metadata, Cassandra for user data and watch history |
| Peak Traffic | BFF pre-scaling, Redis genre cache, double-checked locking on cache miss |
| Fault Isolation | Circuit breakers + bulkheads on BFF fan-out, load shedding on Redis failure, adaptive bitrate as CDN cascade prevention |

---

## Full Architecture Diagram

```mermaid
flowchart TD
    subgraph Clients
        MC[Mobile Client]
        TC[TV Client]
        WC[Web Client]
    end

    subgraph API Layer
        APIGW[API Gateway\nauth · rate limiting · routing]
        BFF[BFF Service\n500 instances on release night\npre-scaled 30min before drop]
    end

    subgraph Genre Services
        AS[Action Service]
        CS[Comedy Service]
        CWS[Continue Watching Service]
        NRS[New Releases Service]
        GN[... 20 genre services]
    end

    subgraph Cache Layer
        REDIS[(Redis\ngenre rows cached\ndouble-checked lock on miss)]
    end

    subgraph Databases
        PG[(PostgreSQL\ncontent metadata\ntitles · cast · genres · S3 URLs)]
        CASS[(Cassandra\nuser data · watch history\nresume positions)]
    end

    subgraph Content Pipeline
        UPLOAD[Upload Service]
        KAFKA[Kafka\ntranscoding-jobs topic]
        TW[Transcoding Workers\nH.264 · H.265 · AV1\n4K · 1080p · 720p · 480p]
        S3[(S3\nvideo chunks\n64 PB total storage)]
        MANIFEST[Manifest Generator\nwrites CDN URLs into manifest]
    end

    subgraph CDN Layer
        CDN_PUSH[CDN Pre-warm\npush hot releases before drop]
        CDN[Global CDN\nedge nodes in 190+ countries\nLRU eviction · 24-48h TTL]
    end

    subgraph Observability
        PROM[Prometheus\nserver-side metrics]
        TELEM[Telemetry Service\nclient TTFF + buffering ratio]
        GRAF[Grafana Dashboards]
        PD[PagerDuty Alerts]
    end

    MC --> APIGW
    TC --> APIGW
    WC --> APIGW

    APIGW --> BFF

    BFF -->|fan-out with bulkheads| AS
    BFF -->|fan-out with bulkheads| CS
    BFF -->|fan-out with bulkheads| CWS
    BFF -->|fan-out with bulkheads| NRS
    BFF -->|fan-out with bulkheads| GN

    AS -->|check cache first| REDIS
    CS --> REDIS
    CWS --> REDIS
    NRS --> REDIS
    REDIS -->|double-checked lock miss only| PG

    BFF -->|GET /api/v1/stream| CASS
    CASS -->|resume_position_seconds| BFF
    BFF -->|manifest URL| MC

    MC -->|fetch manifest| CDN
    MC -->|fetch chunks| CDN
    CDN -->|cache miss pull| S3

    MC -->|POST /api/v1/stream/progress| APIGW
    APIGW -->|save position| CASS

    UPLOAD --> KAFKA
    KAFKA --> TW
    TW -->|chunks| S3
    TW --> MANIFEST
    MANIFEST -->|hot release push| CDN_PUSH
    CDN_PUSH --> CDN

    BFF --> PROM
    AS --> PROM
    REDIS --> PROM
    MC -->|TTFF · buffering ratio| TELEM
    TELEM --> PROM
    PROM --> GRAF
    PROM --> PD
```

---

## Request Flows

### Home Feed

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant B as BFF
    participant R as Redis
    participant G as Genre Services
    participant DB as PostgreSQL

    C->>GW: GET /api/v1/home?limit=10
    GW->>B: authenticated request
    par fan-out with bulkheads
        B->>R: GET action_row
        B->>R: GET comedy_row
        B->>R: GET continue_watching
    end
    R-->>B: cache hits (most rows)
    B->>G: fetch rows not in cache
    G->>DB: query (double-checked lock)
    DB-->>G: rows
    G-->>R: populate cache
    G-->>B: rows
    B-->>C: { rows: [...], next_cursor: "..." }
```

### Stream Start

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant B as BFF
    participant CASS as Cassandra
    participant CDN as CDN

    C->>GW: GET /api/v1/stream?movie_id=m_123
    GW->>B: authenticated request
    B->>CASS: get resume position for user + movie
    CASS-->>B: position_seconds: 1847
    B-->>C: { stream_url: "cdn.netflix.com/...", resume_position_seconds: 1847 }
    C->>CDN: fetch manifest
    CDN-->>C: manifest with chunk URLs
    C->>CDN: fetch chunks (ABR quality selection)
    CDN-->>C: video chunks
    Note over C: playback starts at 30:47
```

### Content Ingestion

```mermaid
sequenceDiagram
    participant UP as Upload Service
    participant K as Kafka
    participant TW as Transcoding Worker
    participant S3 as S3
    participant MG as Manifest Generator
    participant CDN as CDN

    UP->>K: publish transcoding job
    K->>TW: consume job
    TW->>TW: transcode to 4K, 1080p, 720p, 480p
    TW->>TW: split into 4-second chunks
    TW->>S3: upload all chunks
    TW->>MG: trigger manifest generation
    MG->>S3: write manifest with CDN URLs
    MG->>CDN: push chunks (hot release pre-warm)
    Note over CDN: CDN edge nodes pre-populated before release
```

---

## Component Summary

| Component | Technology | Purpose |
|---|---|---|
| API Gateway | Kong / AWS API GW | Auth, rate limiting, routing |
| BFF | Node.js / Java | Fan-out to genre services, failure isolation |
| Genre Services | Java microservices | Per-genre row fetching |
| Redis | Redis Cluster | Genre row cache, double-checked locking |
| Content DB | PostgreSQL | Titles, metadata, S3 URLs |
| User DB | Cassandra | Watch history, resume positions, user profiles |
| Object Storage | S3 | 64 PB video chunks |
| CDN | Netflix Open Connect | Global edge, push + pull hybrid, LRU + TTL |
| Transcoding | Kafka + Worker Pool | Parallel encoding to all resolutions and codecs |
| Telemetry | Custom ingest service | Client-side TTFF and buffering ratio |
| Observability | Prometheus + Grafana + PagerDuty | SLI measurement, alerting, dashboards |

---

## Key Design Decisions and Their Justifications

**BFF over client-driven fan-out** — 20+ parallel calls from a mobile client on 3G is brutal. BFF absorbs all fan-out server-side, client makes one call. Bulkheads inside BFF provide the same failure isolation.

**Cursor pagination over offset** — Netflix adds content constantly. Offset pagination produces duplicates and gaps under concurrent writes. Cursor is stable regardless of what is added or removed.

**Push + pull hybrid CDN** — pure pull causes cache stampede on hot releases (all CDN nodes cold at 9pm). Pure push wastes 76 TB per CDN server on unpopular content. Hybrid: push for top releases, pull for long tail.

**Double-checked locking on cache miss** — single-check locking allows N waiting requests to all hit DB one by one after the lock is released. Double-check means only the first request ever reaches the DB.

**Adaptive bitrate as load shedding** — when a CDN node fails and users failover to a neighbouring node, that node's bandwidth is 3× its capacity. Dropping all clients to lower quality reduces bandwidth by 5× and prevents cascade failure.

**Cassandra for user data** — watch history and resume positions are write-heavy (every 10 seconds per active viewer) and keyed by user. Cassandra's LSM tree is optimised for write throughput. PostgreSQL would struggle under 20M concurrent streams writing position updates every 10 seconds.
