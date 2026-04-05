# CLAUDE.md — Wiki Knowledge Base

This file gives Claude Code an immediate, complete orientation to this repository so no directory traversal is needed at the start of a conversation.

---

## Active Learning Session — Read This First

### Who the user is
Complete beginner in System Design targeting **Google L4 / SDE-2 strong hire** in the design round. No prior system design knowledge assumed — explain everything from scratch.

### Goal
Work through the syllabus at `System Design/01-Syllabus/` topic by topic, building permanent study notes along the way.

### How each session works — follow this exactly
1. **Study mode first** — user says a topic name or "go". Explain that topic from scratch, beginner-friendly, with real-world analogies and examples. No jargon without explanation.
2. **Notes mode second** — once the user confirms they understood ("got it", "makes sense", "next"), write the notes as a proper `.md` file into the correct folder under `System Design/04-Core-Concepts/` (or whichever phase folder is active).
3. **Never skip ahead** — do not move to the next topic until the user confirms the current one is understood.
4. **Never write notes before the user has confirmed understanding** — explain first, write after.

### How to explain concepts — follow this exactly
- **One concept at a time.** Never dump multiple sub-topics in one message. Explain one thing, ask if it makes sense, wait for confirmation, then continue.
- **Always use scale to justify design decisions.** Don't just say "use Hash instead of String". Show what happens at 10 million users — how much wasted data, how much wasted network traffic, why it matters. Numbers make the trade-off real.
- **Build from the problem, not the solution.** Don't say "Redis has sorted sets, here's what they do." Say "you have a leaderboard problem, here's why a normal list doesn't work, here's what sorted sets give you."
- **Use concrete before abstract.** Real example first, generalisation second. Never the other way around.

### Note file format (use this every time)

Notes are split across **multiple files per topic** (not one big file). Typical structure:

```
00-Overview.md          ← summary + key callouts
01-<Main-Concept>.md    ← deep-dive explanation
02-<Sub-Topic>.md       ← follow-on detail (e.g. when to use, trade-offs)
03-Interview-Cheatsheet.md ← quick-reference for revision
Interview-Questions/
  SDE-1.md              ← 5 foundational questions (definitions, basics)
  SDE-2.md              ← 5 scenario questions (trade-offs, reasoning)
  SDE-3.md              ← 5 architecture questions (open-ended, no single right answer)
```

### How to write notes — follow this exactly

**Notes must be narrative and conversational — not bullet points and definitions.**

The gold standard is the Availability notes at `System Design/04-Core-Concepts/03-Availability/`. Read those before writing any new notes. That is the style to match.

The user reads notes to revise — they must be able to understand the concept completely from the notes alone, without needing to remember the conversation. This means:

- **Narrative and conversational tone throughout.** Notes should read like an explanation, not a reference doc. Write in flowing prose with code blocks to illustrate — not as a list of definitions. A note that just says "2NF — every non-key column depends on the whole PK" is useless without the reasoning behind it.
- **Include the problem first, then the solution.** Don't just state the concept — show why it's needed. Start from the naive approach (e.g. "what if we stored users in a CSV?"), show where it breaks, then introduce the concept as the fix.
- **Keep all the examples from the session.** If Instagram Stories was used to explain schema-on-read, that example goes in the notes. If Kylie Jenner was used to explain write-heavy hotspots, she goes in the notes. Real examples are what make concepts stick.
- **Keep all the reasoning from the session.** If the user asked "so we can afford inconsistency in read-heavy DBs?" and you explained inconsistency windows — that reasoning goes in the notes. The question-and-answer reasoning is exactly what makes the concept click.
- **Keep all the flows and comparisons.** If you drew a before/after, it goes in the notes as a code block.
- **Do not compress or summarise.** A note that says "schema-on-read means structure interpreted at read time" is useless. The note should explain it the way you explained it in the session — with the full reasoning, the full example, the full trade-off discussion.
- **Write for a reader who has forgotten the conversation.** Every concept should be self-contained and fully explained.

**Interview question file format:**
- Each question uses `> [!question]` callout
- Answer is in a **collapsed** `> [!success]-` callout (hidden until clicked in Obsidian)
- Answer contains: detailed explanation of WHY it's correct, followed by `> [!tip] Interview framing` with a concise speakable answer
- All discussed topics must have SDE-1/2/3 files in their `Interview-Questions/` folder
- **Only write interview question files after the interactive Q&A session — never generate them in bulk for topics not yet discussed**

Each file uses this style:

- **Obsidian callout blocks** for definitions and warnings:
  ```
  > [!info] Plain-English definition here
  > [!important] Critical nuance to remember
  > [!tip] Interview-specific advice
  > [!danger] Common trap / myth
  ```

- **Code blocks for visual diagrams and flows** (not actual code):
  ```
  Write → Node A → replicates → Node B
  Read  → Node B → stale data returned
  ```

- **Horizontal rules** (`---`) between major sections

- **Concrete real-world examples inline** (e.g. Amazon cart, Instagram, Google Spanner, WhatsApp)

- **"What it guarantees / What it doesn't guarantee"** pattern for each concept

- **Spectrum / comparison diagrams** where a concept exists on a scale

- No rigid section headings required — structure each file around how the concept naturally explains itself

### Current active phase
**Phase 3 — Core System Design Concepts — COMPLETED ✅**
**Phase 4 — Caching — COMPLETED ✅**
**Phase 5 — Storage & Databases — IN PROGRESS**
Syllabus file: `System Design/01-Syllabus/05-Storage-and-Databases.md`
Notes folder: `System Design/06-Storage-and-Databases/`

### Topic order within Phase 3
Work through in this order — tick off as completed:
- [x] 3.1 Performance Metrics → `01-Performance-Metrics/`
- [x] 3.2 SLA / SLO / SLI → `02-Service-Levels/`
- [x] 3.3 Availability → `03-Availability/`
- [x] 3.4 Reliability & Redundancy → `04-Reliability/`
- [x] 3.5 Scalability → `05-Scalability/`
- [x] 3.6 Fault Tolerance → `06-Fault-Tolerance/`
- [x] 3.7 Durability → `07-Durability/`
- [x] 3.8 Concurrency & Locking → `08-Concurrency-Locking/`
- [x] 3.9 Transaction Isolation Levels → `09-Transaction-Isolation/`
- [x] 3.10 Consistency Models → `10-Consistency-Models/`
- [x] 3.11 Network Partitions → `11-Network-Partitions/`
- [x] 3.12 CAP Theorem → `12-CAP-Theorem/`
- [x] 3.13 PACELC Theorem → `13-PACELC/`
- [x] 3.14 Security → `14-Security/`
- [x] 3.15 State Machines → `15-State-Machines/`
- [x] 3.16 NFRs → `16-NFRs/`

### Topic order within Phase 5 — Storage & Databases
Work through in this order — tick off as completed:
- [x] 3.1 DB Fundamentals → `01-DB-Fundamentals.md`
- [x] 3.2 ACID Properties → `02-ACID.md`
- [ ] 3.3 SQL Databases → `03-SQL/` (01-Relational-Model, 02-Joins, 03-Normalisation, 04-Views, 05-Query-Optimisation)
- [ ] 3.4 Database Indexing → `04-Indexing.md`
- [ ] 3.5 Database Replication → `05-Replication.md`
- [ ] 3.6 Database Sharding → `06-Sharding.md`
- [ ] 3.7 MVCC → `07-MVCC.md`
- [ ] 3.8 Change Data Capture → `08-CDC.md`
- [ ] 3.9 Key-Value Stores → `09-Key-Value-Stores.md`
- [ ] 3.10 Document Stores → `10-Document-Stores.md`
- [ ] 3.11 Column-Family Stores → `11-Column-Family.md`
- [ ] 3.12 Search Engines → `12-Search-Engines.md`
- [ ] 3.13 Graph Databases → `13-Graph-Databases.md`
- [ ] 3.14 Blob Storage → `14-Blob-Storage.md`
- [ ] 3.15 NewSQL → `15-NewSQL.md`
- [ ] 3.17 Connection Pooling → `17-Connection-Pooling.md`
- [ ] 3.18 Read/Write Splitting → `18-Read-Write-Splitting.md`
- [ ] 3.19 Cursor Pagination → `19-Cursor-Pagination.md`
- [ ] 3.20 OLTP vs OLAP → `20-OLTP-OLAP.md`
- [ ] 3.21 Choosing the Right DB → `21-Choosing-DB.md`

### How to start a session
User will say something like "let's continue" or "next topic" or a topic name.
- If continuing: check which topics above are not yet completed (no note file exists in their folder), pick up from the first incomplete one, and say "Continuing from [topic name] — ready?"
- If starting fresh on a topic: jump straight into the explanation.

---

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
