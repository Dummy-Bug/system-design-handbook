# CLAUDE.md — Wiki Knowledge Base

This file gives Claude Code an immediate, complete orientation to this repository so no directory traversal is needed at the start of a conversation.

---

## What This Repo Is

A personal backend engineering knowledge base / study wiki built in Obsidian-compatible Markdown. It covers topics from fundamentals through advanced system design and is structured as a progressive learning curriculum aimed at interview prep and practical architecture work.

**~230 Markdown files | 45 Excalidraw diagrams | 19 PDFs**

---

## Top-Level Directory Map

```
wiki/
├── CLAUDE.md                          ← this file
├── README.md                          ← human-facing overview
├── Index.base                         ← skill-progressive 8-phase curriculum index
├── Backend Core/                      ← encoding, ID generation, text representation
├── Computer Networking/               ← internet infrastructure, DNS, cellular
├── Daily Engineering Learning/        ← time-based learning journal (Jan–Feb 2026)
├── Distributed Systems/               ← HLD foundations, caching, CAP, NoSQL
├── Excalidraw/                        ← 45 visual architecture diagrams (.excalidraw.md)
├── Fundamentals/                      ← HTTP status codes, binary/float precision
├── Java/                              ← JVM internals, memory, compilation, perf
├── Low Level Design/                  ← Gang of Four design patterns (all 3 categories)
├── Prompts/                           ← AI prompt notes
└── System Design/                     ← 19 case studies + foundational concepts
```

---

## Section-by-Section Reference

### Fundamentals (`/Fundamentals/`)
- `Binary Number Rounding.md` — IEEE 754 floating point failures, why money needs Decimal
- `HTTP/Status Codes/` — 8 files covering 2xx/3xx/4xx/5xx with debugging guidance

---

### Backend Core (`/Backend Core/`)

**Encodings/** (4 files)
- Base62.md, Base64.md, Number-Base-Encoding.md, URL-Encoding.md

**Identifiers/** (4 files)
- Auto-Increment-ID.md, UUID.md, Snowflake-ID.md, ID-Generation-Overview.md

**Text-Representation/** (11 files across 3 sub-modules)
- `01-Unicode/` — Unicode standard, code points, character vs glyph
- `02-Encoding/` — What is encoding, UTF-8 mechanics, UTF-16, comparison, production bugs
- `03-Java/` — Java String internals, length calculations, encoding edge cases

---

### Computer Networking (`/Computer Networking/`)
7 files: networking layers, DNS, ICANN, domain registration, cellular networks (IMSI/IMEI/SIM auth), internet infrastructure, routers/gateways, HTTP.

---

### Distributed Systems (`/Distributed Systems/`)
10 files:
- Architecture overview, load balancing, consistent hashing
- Caching layers + case studies
- CAP theorem, NoSQL types and trade-offs, NoSQL conclusions
- Back-of-the-envelope estimation

---

### Java (`/Java/`)
9 files covering JVM top-to-bottom:
- What is Java, Java features, Java components
- JIT compiler, JVM architecture, JVM memory model, JVM execution pipeline
- Slowness in Java (GC, JIT warm-up, etc.)
- `DURGA/JVM Introduction.md` — introductory JVM material

---

### Low Level Design (`/Low Level Design/`)
16 files — full GoF coverage with real-world examples:

**Behavioral/** (4): Observer, Strategy, Iterator, Chain of Responsibility

**Creational/** (5): Factory, Abstract Factory, Builder, Singleton, Prototype

**Structural/** (7): Adapter, Facade, Decorator, Flyweight, Proxy, Bridge, Composite

---

### System Design (`/System Design/`)
The largest section. Organized in phases:

#### `00-Concepts/` — Foundation knowledge
- **Fundamentals/** (11 files): Failure modes, Performance Metrics (P50/P95/P99), Scalability, Fault Tolerance, Availability, Consistency, Partition Tolerance, Durability, Replication/Failover, Non-Functional Requirements
- **Time/** (5 files): Measuring time, Clock drift, Lamport Clocks, Vector Clocks, CRDT
- **Consensus/** (3 files): Introduction, RAFT, Paxos

#### Case Studies — each folder follows the pattern:
`01-Requirements.md → 02-Estimations.md → 03-API.md → 04-Architecture.md → ...`

| # | Case Study | Key Topics |
|---|-----------|------------|
| 01 | Code-Submission-Platform | Async processing, microservices, Kafka, fault tolerance for live contests |
| 02 | URL-Shortener | ID generation (UUID/Snowflake/Base62), API specs, hashing |
| 03 | Type-Ahead-System | Autocomplete, Tries, Redis, latency optimization |
| 04 | Hotel-Reservation-System | Concurrency, race conditions, idempotent APIs, DB constraints |
| 05 | Key-Value-Store | 100k–1M QPS, Dynamo-style, consistent hashing, replication |
| 06 | Live-News-Feed | Fan-out strategies, personalization ranking, pagination |
| 07 | Taxi-Platform | Geo-spatial indexing, real-time location, ETA |
| 08 | Job-Scheduling-Platform | *(placeholder — no content yet)* |
| 09 | K-Heavy-Hitters | Trending topics from billions of tweets, distributed counting |
| 10 | Online-Auction-System | Bid handling, concurrent updates, auction semantics |
| 11 | Web-Crawler | Distributed crawling, politeness, storage |
| 12 | Dropbox | File sync, metadata vs blob separation, conflict resolution |
| 13 | Movie-Streaming-Platform | *(placeholder)* |
| 14 | Chat-System | Real-time messaging, ordering, presence, offline delivery |
| 15 | Rate-Limiter | *(placeholder)* |
| 16 | Stock-Broker | *(placeholder)* |
| 17 | Ad-Click-Platform | *(placeholder)* |
| 18 | Notification-System | *(placeholder)* |
| 19 | Google-Meet | *(placeholder)* |

---

### Daily Engineering Learning (`/Daily Engineering Learning/`)
Time-based learning journal organized by month/week/day:
- `01 Jan/week-3/` — entries for Jan 19, 20, 21: external API failure classification, HTTP error handling, naming/model mapping, retry architecture, Pydantic model operations
- `02 Feb/week-1/` — Langgraph resume patterns

---

### Excalidraw (`/Excalidraw/`)
45 `.excalidraw.md` files — visual architecture diagrams. Dated from March 2026. Used for system design visualization throughout case studies.

---

## File Format & Naming Conventions

- **Extension**: `.md` everywhere (Obsidian-compatible)
- **Links**: `[[filename]]` internal wiki links, `[[filename.pdf]]` for embedded PDFs
- **System Design folders**: prefixed `NN-Case-Study-Name/` (01–19)
- **Step files within case studies**: `01-Requirements.md`, `02-Estimations.md`, `03-API.md`, etc.
- **Concept modules**: `01-Unicode/`, `02-Encoding/`, `03-Java/` etc.
- **Daily learning**: `MM Mon/week-N/DD/` date hierarchy
- **Images**: stored in `Images/` subdirectory within each case study folder
- **PDFs**: stored in `Pdfs/` subdirectory or co-located; also in `Distributed Systems/Pdfs/`

---

## Key Cross-References

- **ID generation** appears in both `Backend Core/Identifiers/` and `System Design/02-Url-Shortener/`
- **Encoding/Unicode** appears in `Backend Core/Text-Representation/` and underpins chat/crawler systems
- **Consistent hashing** lives in `Distributed Systems/` and is applied in `05-Key-Value-Store/`
- **CAP theorem** is in `Distributed Systems/` and referenced across most stateful case studies
- **LLD patterns** from `Low Level Design/` inform OOP decisions in case study architectures
- **Back-of-envelope** methodology from `Distributed Systems/` is applied in every case study `02-Estimations.md`

## Learning Path (from Index.base)

1. Fundamentals → 2. Computer Networking → 3. HTTP → 4. Distributed Systems → 5. LLD → 6. Java → 7. System Design Concepts → 8. System Design Case Studies (01–14, then placeholders)

---

## Planned But Empty Sections

These directories exist but have no content files yet (as of March 2026):
`08-Job-Scheduling-Platform`, `13-Movie-Streaming-Platform`, `15-Rate-Limiter`, `16-Stock-Broker`, `17-Ad-Click-Platform`, `18-Notification-System`, `19-Google-Meet`
