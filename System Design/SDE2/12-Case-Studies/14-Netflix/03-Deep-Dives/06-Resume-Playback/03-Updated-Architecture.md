# Resume Playback — Flow Architecture

## The Two Paths

Resume playback has two distinct flows — the write path (continuous position saving during playback) and the read path (position lookup when a new stream starts). They are independent and hit different endpoints.

---

## Write Path — Saving Position During Playback

Every 4 seconds while a user is watching, the client fires a progress update. This goes through the API Gateway for auth and lands at the Stream Service, which writes directly to Cassandra.

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant SS as Stream Service
    participant CASS as Cassandra

    Note over C: User watching — every 4 seconds
    C->>GW: POST /api/v1/stream/progress { movie_id, position_seconds }
    GW->>SS: authenticated write
    SS->>CASS: WRITE user_id + movie_id + position_seconds + timestamp
    CASS-->>SS: acknowledged
    SS-->>GW: 204 No Content
    GW-->>C: 204 No Content
```

The response is `204 No Content` — there is nothing meaningful to return. The client fires and forgets, continuing playback without waiting.

---

## Read Path — Resuming on Stream Start

When a user clicks Play, the Stream Service reads the last saved position from Cassandra, applies the completion threshold, and returns the position alongside the stream URL.

```mermaid
sequenceDiagram
    participant C as Client
    participant GW as API Gateway
    participant SS as Stream Service
    participant CASS as Cassandra
    participant CDN as CDN

    C->>GW: GET /api/v1/stream?movie_id=inception
    GW->>SS: authenticated request
    SS->>CASS: READ position WHERE user_id=X AND movie_id=inception
    CASS-->>SS: position_seconds: 2843

    Note over SS: Apply completion threshold
    Note over SS: 2843 < 95% of 7800 → in progress

    SS-->>GW: { stream_url: "cdn.netflix.com/...", resume_position_seconds: 2843 }
    GW-->>C: response

    C->>CDN: fetch manifest → fetch chunks from position 2843
    Note over C: Playback starts at 47:23
```

---

## How the Two Paths Fit Together

```mermaid
flowchart TD
    subgraph Write Path
        WC[Client — watching] -->|POST /progress every 4s| WGW[API Gateway]
        WGW --> SS1[Stream Service]
        SS1 -->|WRITE position + timestamp| CASS[(Cassandra)]
    end

    subgraph Read Path
        RC[Client — press Play] -->|GET /stream| RGW[API Gateway]
        RGW --> SS2[Stream Service]
        SS2 -->|READ last position| CASS
        SS2 -->|apply 95% threshold| SS2
        SS2 -->|resume_position_seconds| RC
        RC -->|fetch chunks from that position| CDN[CDN]
    end
```

---

## Component Responsibilities

| Component | Role in Resume Playback |
|---|---|
| Client | Fires progress write every 4 seconds during playback |
| API Gateway | Auth on both read and write paths |
| Stream Service | Writes position to Cassandra, reads position on stream start, applies completion threshold |
| Cassandra | Stores raw position — last-write-wins by timestamp, no business logic |
| CDN | Serves video chunks from the resumed position — no knowledge of Cassandra |

The CDN has no involvement in resume logic. Once the client knows the position, it uses it to seek to the right chunk in the manifest and start fetching from there. Resume playback and chunk delivery are fully independent concerns.
