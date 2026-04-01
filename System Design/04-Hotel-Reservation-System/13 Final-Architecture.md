## High Level Design

```mermaid
flowchart TD
    User(["👤 User"])
    Admin(["🔧 Admin / Hotel Manager"])

    subgraph Public ["🌐 Public Zone"]
        AG["API Gateway"]
    end

    subgraph Services ["⚙️ Microservices"]
        HS["Hotel Service"]
        RS["Reservation Service"]
        PS["Payment Service"]
    end

    subgraph External ["🏦 External"]
        Stripe["Stripe / Adyen\nPayment Gateway"]
    end

    subgraph Databases ["🗄️ Databases"]
        HDB_P[("Hotel DB Primary")]
        HDB_R[("Hotel DB Read Replica")]
        HC[("Hotel Cache Redis")]
        RDB[("Reservation DB")]
        PDB[("Payment DB")]
    end

    subgraph Background ["⏱️ Background Jobs"]
        CJ["Cleanup Job"]
    end

    subgraph Private ["🔒 Private Zone"]
        HMS["Hotel Management Service"]
    end

    User --> AG
    AG --> HS
    AG --> RS
    AG --> PS

    HS -->|"writes"| HDB_P
    HS -->|"reads"| HDB_R
    HS -->|"cache hit"| HC
    HDB_P -->|"replicates"| HDB_R

    RS --> RDB
    PS --> PDB
    PS --> Stripe

    CJ -->|"expire PENDING"| RDB
    CJ -->|"restore inventory"| HDB_P

    Admin --> HMS
    HMS -->|"Internal APIs"| HDB_P
```

---

## What Each Service Owns

| Service | Responsibility | Database |
|---|---|---|
| **Hotel Service** | Search, hotel detail, availability check | Hotel DB + Redis cache |
| **Reservation Service** | Initiate (PENDING), Confirm (CONFIRMED), Cancel, expiry | Reservation DB |
| **Payment Service** | Charge via Stripe, refund on cancellation/expiry | Payment DB |
| **Hotel Management Service** | Admin-only: add/edit hotels, room types, pricing | Hotel DB (via internal API) |

---

## Request Flow — Full Booking Journey

```mermaid
sequenceDiagram
    actor User
    participant AG as API Gateway
    participant HS as Hotel Service
    participant RS as Reservation Service
    participant PS as Payment Service
    participant Stripe

    User->>AG: GET /hotels?city=NYC&checkin=...
    AG->>HS: forward search request
    HS-->>User: featured hotels + availability

    User->>AG: GET /hotels/{hotel_id}
    AG->>HS: hotel detail + room types
    HS-->>User: hotel detail page

    User->>AG: POST /reservations/initiate
    AG->>RS: deduct inventory + create PENDING
    RS-->>User: reservationToken + expiresAt (15 min)

    Note over User: Page 1 — Personal Details (no API call)
    Note over User: Page 2 — Card Details → Stripe SDK → paymentToken

    User->>AG: POST /reservations/confirm
    AG->>RS: verify PENDING + update to CONFIRMED
    RS->>PS: charge payment
    PS->>Stripe: charge paymentToken
    Stripe-->>PS: success
    PS-->>RS: payment recorded
    RS-->>User: Booking Confirmed ✅
```

---

## Public vs Private Split

```mermaid
flowchart LR
    subgraph Public ["🌐 Public — via API Gateway"]
        A["Hotel Service"]
        B["Reservation Service"]
        C["Payment Service"]
    end

    subgraph Private ["🔒 Private — Internal only"]
        D["Hotel Management Service\n(no API Gateway)"]
    end

    Internet --> Public
    AdminVPN["Admin VPN / Internal Network"] --> Private
```

> [!note] Why separate public and private?
> Hotel managers adding rooms or updating prices should never go through the same public API that customers use.
> The Hotel Management Service is only reachable from an internal network — not exposed to the internet at all.

---

## Read vs Write Path

| Operation | Path | Why |
|---|---|---|
| Search hotels | → Read Replica | High volume, eventual consistency acceptable for metadata |
| Check availability | → Read Replica | High volume — stale by seconds is acceptable at browse time |
| Initiate reservation | → Primary | Must be consistent — deducts inventory |
| Confirm reservation | → Primary | Must be consistent — charges payment |
| Cancel reservation | → Primary | Must be consistent — restores inventory |
| Admin hotel updates | → Primary | Writes always go to primary |

---

## What We Decided NOT to Include (and Why)

| Component | Reason excluded |
|---|---|
| CDN | Hotel thumbnails are not high-frequency enough to justify it at this scale |
| Redis for availability | Availability must be strongly consistent — caching it risks double booking |
| Sharding | 30 QPS writes, 1.1M rooms — fits easily in a single PostgreSQL primary |
| Separate Rate Limiting Service | Rate limiting belongs in the API Gateway, not a downstream microservice |

---

## Key Design Decisions Recap

| Decision | What we chose | Why |
|---|---|---|
| Consistency vs Availability | Consistency | Double booking is worse than showing "sold out" incorrectly |
| Locking strategy | Optimistic (`AND available_count > 0`) | 30 QPS across 1.1M rooms — conflicts are rare, no need to hold locks |
| Last line of defence | `CHECK (available_count >= 0)` | Database physically rejects negative counts even if app logic fails |
| Idempotency | Client UUID in sessionStorage | Retries and refreshes never create duplicate reservations |
| Two-phase booking | PENDING → CONFIRMED | Holds inventory during payment without charging before confirmation |
| Book room type, not room | `room_inventory` tracks types | Specific room assigned at check-in — guest doesn't care which room |
| Denormalization | `hotel_id` in `room_inventory` | Avoids JOIN through `room_types` on every availability search |
