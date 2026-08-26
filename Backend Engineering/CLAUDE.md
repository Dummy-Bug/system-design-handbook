# CLAUDE.md — Backend Engineering

Turning the **AlgoCamp Backend Engineering (Spring Boot)** course into notes in this folder. Read `~/Desktop/Transcribe/PROMPT-FOR-CLAUDE.md` first for how the recording rig works, then `~/Desktop/Transcribe/tracks/backend.md` for what has already come through it.

**Scope: Java and Spring Boot backend engineering, and nothing else.** This folder is self-contained. It does not reference other tracks, other courses, or work outside it.

---

## The course

- The **2025 recorded cohort**, so every video is available at once — there is no weekly release, and **modules can be watched out of order**.
- **English**, recorded through OBS at **1.75× or 2×** playback, transcribed with `--track backend` (`-l en`). A recording is therefore roughly **half the source length** — scale before judging whether a capture is complete, and a long silent tail at the end is normal rather than a freeze. English audio on this rig has run ~15× realtime with effectively zero loop damage, but that figure was measured at 1× on a different course, so treat sped-up audio as unproven: check the first transcript for loops before assuming a second pass is unnecessary.
- The syllabus PDF footer is dated **01/04/2025**, so it may describe a previous cohort. Treat the module list below as indicative and correct it against what the videos actually contain.

**Not the same track as `~/Desktop/wiki/Spring Boot/`.** That folder is the Coder Army YouTube series — Hindi, transcripts pasted into chat one video at a time, no rig involved. The two overlap on Spring Framework, Maven, dependency injection, the IoC container and the bean lifecycle, and they will disagree in places. Where they overlap, **link across rather than re-explaining**, and say which course a given treatment came from.

---

## Syllabus

- **Build systems** — Gradle, Maven, fat JARs, JVM memory, AOP
- **LLD** — Singleton, Builder, Strategy, Observer, MapStruct
- **Advanced Databases** — MVCC, WAL, isolation levels, redo logs, B-tree, Hash, GIN and GiST indexes
- **Redis** — Spring Cache, read-through and write-around, Redisson distributed locks, GEO, streams
- **Kafka** — brokers, partitions, `KafkaTemplate`, Streams, the Outbox pattern, Debezium CDC
- **Resilience4J** — circuit breakers, retry, bulkheads, rate limiters
- **REST** — idempotency, status codes, versioning
- **gRPC** and Protobuf
- **Spring Security** — JWT, OAuth2
- **WebSocket** and STOMP
- **Testing** — JUnit 5, Mockito, Testcontainers, REST Assured
- **Ops** — Docker, GitHub Actions, Prometheus, Grafana, Micrometer, ELK, OpenTelemetry, Jaeger
- **Architecture** — CQRS, SAGA in both orchestration and choreography form, Event Sourcing, consistency models, sharding, replication, service discovery via Eureka and Consul, API gateways

**Projects:** Uber Backend · Payment Wallet · Airbnb Booking · Quora Clone · Hotel Management

**Not covered by the course:** Kubernetes, Go, Aerospike.

---

## Viewing order

Modules are being watched in this order rather than syllabus order. Build systems is in progress; the rest follows.

1. Build systems
2. LLD and design patterns
3. Advanced Databases
4. REST
5. Redis and distributed locks
6. Kafka
7. Resilience4J
8. Docker, GitHub Actions, Prometheus and Grafana
9. Payment Wallet project

---

## Folder layout

Module folders are numbered by the **viewing order above**, not the syllabus order. A folder is created when its module starts — a gap in the numbering is a module not yet reached, not a missing file.

```
Backend Engineering/
├── CLAUDE.md                 ← this file
├── 00-Build-Systems/         ← Gradle, fat JARs, JVM memory, AOP
├── 01-LLD-And-Design-Patterns/
├── 02-Advanced-Databases/
├── 03-REST/
├── 04-Redis/
├── 05-Kafka/
├── 06-Resilience4J/
├── 07-Ops-And-Observability/
└── 08-Payment-Wallet/        ← project code, not a notes folder
```

A module gets a `notes/` subfolder **only when there is code sitting beside it** (`snippets/`, `src/`); otherwise the notes sit flat at the module root. Cropped frames go in `<module>/Images/` and are embedded with absolute vault paths — `![[Backend Engineering/<module>/Images/<file>.png]]` — so **any future folder rename has to rewrite those links too**.

---

## How to work here

**Derive before writing.** Never create or edit a note until it is explicitly asked for. Propose the structure for a module and wait. Auto-writing and auto-advancing are the failure mode, and folder economy matters — split into multiple notes only when the content justifies it.

**Full capture, lecture depth only.** Every example, number, distinction, analogy and warning from the lecture goes in. Nothing gets bolted on that the lecture did not cover; anything added beyond it is marked as such and flagged in chat. Read the transcript end to end before claiming a part is done — under-reading has been called out before.

**Problem before solution.** Motivate a tool by showing the simpler thing suffices on the easy case, then breaking it on a harder one. Naive approach first, then break it. Justify with numbers, not adjectives. **Guarantees / does not guarantee** framing where a mechanism has a boundary.

**Plain English, self-contained for a stranger.** These notes are read by people with zero context. Every term is explained at first use and no jargon appears before it is introduced.

**Run it before it goes in a note.** Commands, code and config **never come from the transcript** — dictated code is always garbled, and the typing that produces it is exactly what triggers whisper's silence loops. Take it from the course repo, the official docs, or a legible frame grab, then execute it. Anything that could not be run is labelled as unverified.

**Code blocks carry the file path as a top comment and are line-numbered.**

**No interview-framing callouts.** No `> [!tip] **Interview framing.**` blocks, no "if asked X, the weak answer is…", no viva or exam angles. Write the concept and stop. A point worth making belongs in the body of the note on its own terms. This does not touch material where the lecture itself raises an interview question as its subject — that is the source's content, not framing added on top.

**Visuals both ways.** Recreate flows, architectures, pipelines and comparison tables as mermaid or markdown, leaning on mermaid as heavily as the material allows. Screenshot hand-drawn geometry and annotated diagrams, where recreating loses what made them worth looking at. **Read every crop before embedding it** — the PII-in-a-tooltip, stray-Claude-session and player-chrome hazards in the rig manual all apply here.

**Copyright.** Recordings and raw transcripts are never committed, published, or quoted verbatim at length. The notes are original explanations.

### Formatting

- **Never use italics.** Not `*asterisks*`, not `_underscores_` — not for emphasis, not for a paper or product name, not for a quoted phrase or an aside. **Bold** when something has to stand out, plain text everywhere else. This holds in note bodies, callouts, blockquotes, tables and headings alike.
- **Never hard-wrap a paragraph.** One paragraph is one source line however long it runs, and the same goes for list items, callout lines and blockquote lines. A single newline renders as a line break, so a wrapped paragraph breaks mid-sentence in reading view. Code fences, tables and mermaid blocks keep their own line structure.
- **No H1 as a document title** — Obsidian shows the filename. `#` is for sections inside a note, which is how the Spring Boot and DURGA notes already read.
- **No "Next:" trailer lines.** Each note ends on its own content.
