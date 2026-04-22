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
| DB | PostgreSQL for content metadata and watch history, Cassandra for resume positions |
| Peak Traffic | BFF pre-scaling, Redis genre cache, double-checked locking on cache miss |
| Fault Isolation | Circuit breakers + bulkheads on BFF fan-out, load shedding on Redis failure, adaptive bitrate as CDN cascade prevention |
| Search | Dedicated Search Service, Elasticsearch with inverted index + fuzzy matching, CDC sync from PostgreSQL via Debezium |
| Resume Playback | Completion threshold logic in Stream Service, last-write-wins resolution in Cassandra |

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
        APIGW[API Gateway]
        BFF[BFF Service]
        SS[Stream Service]
        SRCH[Search Service]
    end

    subgraph Genre Services
        AS[Action Service]
        CS[Comedy Service]
        CWS[Continue Watching Service]
        NRS[New Releases Service]
        GN[20 genre services]
    end

    subgraph Cache Layer
        REDIS[(Redis — genre rows)]
    end

    subgraph Databases
        PG[(PostgreSQL — content metadata + watch history)]
        CASS[(Cassandra — resume positions)]
    end

    subgraph Search Layer
        ES[(Elasticsearch)]
        DEBEZIUM[CDC — Debezium]
        ESWRK[ES Sync Worker]
    end

    subgraph Content Pipeline
        UPLOAD[Upload Service]
        KAFKA[Kafka]
        TW[Transcoding Workers]
        S3[(S3 — 64 PB video chunks)]
        MANIFEST[Manifest Generator]
    end

    subgraph CDN Layer
        CDN_PUSH[CDN Pre-warm]
        CDN[Global CDN]
    end

    subgraph Observability
        PROM[Prometheus]
        TELEM[Telemetry Service]
        GRAF[Grafana]
        PD[PagerDuty]
    end

    MC --> APIGW
    TC --> APIGW
    WC --> APIGW

    APIGW --> BFF
    APIGW --> SS
    APIGW --> SRCH

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

    SS -->|read resume position| CASS
    CASS -->|position_seconds| SS
    SS -->|manifest URL + resume position| MC
    MC -->|POST /progress every 4s| APIGW

    SRCH -->|query with fuzziness + boost| ES

    MC -->|fetch manifest| CDN
    MC -->|fetch chunks| CDN
    CDN -->|cache miss pull| S3

    PG -->|write-ahead log| DEBEZIUM
    DEBEZIUM -->|metadata-changes topic| KAFKA
    KAFKA --> ESWRK
    ESWRK -->|index document| ES

    UPLOAD --> KAFKA
    KAFKA --> TW
    TW -->|chunks| S3
    TW --> MANIFEST
    MANIFEST -->|hot release push| CDN_PUSH
    CDN_PUSH --> CDN

    BFF --> PROM
    AS --> PROM
    REDIS --> PROM
    MC -->|TTFF + buffering ratio| TELEM
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

### Search

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant S as Search Service
    participant ES as Elasticsearch

    C->>GW: GET /api/v1/search?q=leo&limit=10
    GW->>S: authenticated request
    S->>ES: multi_match query with fuzziness AUTO + boost weights
    ES-->>S: ranked results by relevance score
    S-->>C: { results: [...10 items], next_cursor: "..." }
```

### Stream Start + Resume

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant SS as Stream Service
    participant CASS as Cassandra
    participant CDN as CDN

    C->>GW: GET /api/v1/stream?movie_id=m_123
    GW->>SS: authenticated request
    SS->>CASS: READ position WHERE user_id=X AND movie_id=m_123
    CASS-->>SS: position_seconds: 1847
    Note over SS: 1847 < 95% of duration — in progress
    SS-->>C: { stream_url: "cdn.netflix.com/...", resume_position_seconds: 1847 }
    C->>CDN: fetch manifest
    CDN-->>C: manifest with chunk URLs
    C->>CDN: fetch chunks from position 1847
    CDN-->>C: video chunks
    Note over C: playback starts at 30:47
```

### Progress Write

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant SS as Stream Service
    participant CASS as Cassandra

    Note over C: every 4 seconds while watching
    C->>GW: POST /api/v1/stream/progress { movie_id, position_seconds }
    GW->>SS: authenticated write
    SS->>CASS: WRITE user_id + movie_id + position_seconds + timestamp
    SS-->>C: 204 No Content
```

### Content Ingestion + Search Sync

```mermaid
sequenceDiagram
    participant UP as Upload Service
    participant K as Kafka
    participant TW as Transcoding Worker
    participant S3 as S3
    participant MG as Manifest Generator
    participant CDN as CDN
    participant PG as PostgreSQL
    participant DEB as Debezium CDC
    participant ESW as ES Sync Worker
    participant ES as Elasticsearch

    UP->>K: publish transcoding job
    K->>TW: consume job
    TW->>S3: upload chunks at all resolutions
    TW->>MG: trigger manifest generation
    MG->>S3: write manifest with CDN URLs
    MG->>CDN: push chunks for hot releases
    MG->>PG: INSERT title metadata
    PG->>DEB: write-ahead log change event
    DEB->>K: publish to metadata-changes topic
    K->>ESW: consume change event
    ESW->>ES: index document
    Note over ES: title appears in search within seconds
```

---

## Component Summary

| Component | Technology | Purpose |
|---|---|---|
| API Gateway | Kong / AWS API GW | Auth, rate limiting, routing |
| BFF | Node.js / Java | Fan-out to genre services, bulkhead failure isolation |
| Stream Service | Java | Resume position lookup, completion threshold, progress writes |
| Search Service | Java | Translates queries, calls Elasticsearch, returns ranked results |
| Genre Services | Java microservices | Per-genre row fetching |
| Redis | Redis Cluster | Genre row cache, double-checked locking on miss |
| Content DB | PostgreSQL | Titles, metadata, cast, S3 URLs, watch history |
| Resume DB | Cassandra | Resume positions — 7.5M writes/second, partition key: user_id |
| Search Index | Elasticsearch | Inverted index, fuzzy matching, boost-based relevance scoring |
| CDC Pipeline | Debezium + Kafka + ES Sync Worker | Async sync from PostgreSQL to Elasticsearch |
| Object Storage | S3 | 64 PB video chunks |
| CDN | Netflix Open Connect | Global edge, push + pull hybrid, LRU + TTL eviction |
| Transcoding | Kafka + Worker Pool | Parallel encoding to all resolutions and codecs |
| Telemetry | Custom ingest service | Client-side TTFF and buffering ratio |
| Observability | Prometheus + Grafana + PagerDuty | SLI measurement, alerting, dashboards |

---

## Key Design Decisions and Their Justifications

**BFF over client-driven fan-out** — 20+ parallel calls from a mobile client on 3G is brutal. BFF absorbs all fan-out server-side, client makes one call. Bulkheads inside BFF provide the same failure isolation.

**Search Service + Elasticsearch over PostgreSQL LIKE** — `LIKE '%leo%'` is a full table scan across 600,000 rows. At 25,000 search queries per second, this saturates the PostgreSQL instance and degrades every other read on the same DB. Elasticsearch's inverted index makes search a direct lookup, not a scan. Fuzzy matching and boost-based relevance scoring are impossible with LIKE.

**CDC over dual-write for Elasticsearch sync** — writing to PostgreSQL and Elasticsearch simultaneously in the same code path creates distributed failure modes. CDC tails PostgreSQL's write-ahead log passively — the transcoding pipeline writes to one system, Debezium propagates the change asynchronously. A few seconds of search staleness is acceptable.

**Cursor pagination over offset** — Netflix adds content constantly. Offset pagination produces duplicates and gaps under concurrent writes. Cursor is stable regardless of what is added or removed.

**Push + pull hybrid CDN** — pure pull causes cache stampede on hot releases (all CDN nodes cold at 9pm). Pure push wastes 76 TB per CDN server on unpopular content. Hybrid: push for top releases, pull for long tail.

**Double-checked locking on cache miss** — single-check locking allows N waiting requests to all hit DB one by one after the lock is released. Double-check means only the first request ever reaches the DB.

**Adaptive bitrate as load shedding** — when a CDN node fails and users failover to a neighbouring node, that node is at 3× capacity. Dropping all clients to lower quality reduces per-user bandwidth by 5× and stops the cascade.

**PostgreSQL for watch history, Cassandra for resume positions** — watch history is 578 writes/second across 150M DAU, well within PostgreSQL limits. Resume positions are 7.5M writes/second at peak (30M peak streamers each writing every 4 seconds) — 750× PostgreSQL's single-node limit. Same data shape, completely different write frequency, completely different DB choice.

**Completion threshold in Stream Service** — positions ≥ 95% of total duration return 0 instead of the actual position. This logic belongs in the Stream Service, not Cassandra — Cassandra stores raw positions only, business rules live in the service layer.
