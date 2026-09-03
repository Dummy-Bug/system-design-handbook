# CLAUDE.md — Backend Engineering

Turning the **AlgoCamp Backend Development in Springboot, AI & Micro Services 2026** material into notes in this folder. Read `~/Desktop/Transcribe/PROMPT-FOR-CLAUDE.md` first for how the recording rig works, then `~/Desktop/Transcribe/tracks/backend.md` for what has already come through it.

**Scope: Java and Spring Boot backend engineering, and nothing else.** This folder is self-contained. It does not reference other tracks, other courses, or work outside it.

---

## The source

- **Backend Development in Springboot, AI & Micro Services 2026**, on `courses.algocamp.io` — **306 lessons**, all available at once. There is no weekly release, so lessons can be watched in any order.
- **These are recordings of live cohort sessions**, not a solo studio recording. Expect a chat, student questions answered by name, negotiated breaks, the occasional internet drop and re-share, and sign-offs referring to the next day. The live-session rules in the rig manual therefore apply: **questions are kept, names are stripped.**
- A session arrives as **several recordings**, because OBS is stopped at each break. Parts of one lesson must be read together before any structure is proposed — the second half regularly moves where the note boundaries belong.
- **English**, recorded through OBS at **1.75× or 2×**, transcribed with `--track backend` (`-l en`). A recording runs roughly half its source length; a long silent tail is normal rather than a freeze.
- **Loop damage was negligible for the first several recordings** — confined to the last five to ten seconds of a file, where the capture keeps rolling after the speaking stops. **That no longer holds.** One recording lost **6.5 minutes of speech mid-file** to a single repeated line, so a second pass is now sometimes necessary. Count the top repeated lines before trusting a transcript, and check where the repeats sit: spread through the file means genuine repetition, bunched at one timestamp means a loop.
- **A bunched loop is not proof of silence — measure it.** `ffmpeg -ss <s> -t <n> -i <file> -af volumedetect -f null /dev/null` reports `mean_volume`. Speech on this rig sits at **−24 dB**; a break with background noise reads about **−37 dB**; true silence is −91 dB. A loop measuring at speech level ate content. Recover it by cutting that span to a wav (`-vn -ac 1 -ar 16000`) with a minute of margin either side and transcribing the clip on its own — in isolation the loop does not recur.

### Screen capture

The platform's own notes panel captures fine, and its diagrams are legible. Two things to know:

- **The notes panel is watermarked with the account holder's email and phone, stamped mid-canvas over the diagrams, and it drifts between frames.** Any crop must be read before use, and neighbouring timestamps sampled until the watermark clears the region.
- The canvas often runs **ahead of the audio** — concepts appear drawn on the board well before they are taught. Anything not yet covered by the audio stays out of the notes.

### The code

**There are two repositories on screen, not one, and the second replaces the first.** Both are Spring Boot 4.0.2 on Java 21, Gradle, Lombok, layered as controller → service → repository with the repository behind an interface. Code in notes comes from whichever one the material is currently in, or from official docs, and is run before it goes in.

| Repository | Package | Folders |
|---|---|---|
| `https://github.com/singhsanket143/SpringDemoTodo` | `com.example.demo` | 04 to 07 |
| `https://github.com/singhsanket143/FakeCommerceSpring` | `com.example.FakeCommerce` | 08 onward |

The todo project carries the starter, layering and dependency-injection material. Everything from `08-Building-The-API/` on is the commerce project, and **its commit history is the one the folder numbering follows** — so when a folder's placement is uncertain, that is the history to read.

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

**Not covered:** Kubernetes, Go, Aerospike.

> The list above comes from a syllabus PDF footered **01/04/2025** and describes an earlier cohort. Treat it as indicative only.

### What the platform actually lists

Read off the syllabus panel while recording, so this is observed rather than inferred. Numbering is the platform's own.

| # | Lesson | Notes here |
|---|---|---|
| 07 | Backend Engineering First Principles | `01-Backend-First-Principles/` |
| 08 | Quiz for interactive article reading – APIs | — |
| 09 | Understanding HTTP and REST APIs | `02-Networking-And-HTTP/` |
| 10 | Computer networks, DNS, Torrents, TCP/UDP (24 lessons) | not yet |
| 11 | What is Spring Boot, setting up env variables | not yet |
| 12 | Understanding SOLID principles (9 lessons) | not yet |
| 13 | Homework — working with an HTTP client | not yet |
| 14 | Understanding MVC, repositories, services | not yet |
| 15 | Exploring MVC with Spring Boot | not yet |
| 16 | `@RestController`, `@RequestMapping`, `@Service` | not yet |
| 17 | Understanding the Builder pattern (11 lessons) | not yet |
| 18 | Integrating databases with Spring Boot | not yet |

The platform's numbers are **not** the folder numbers here — folders are numbered by where a subject sits in the teaching order.

---

## Naming comes from the content, never in advance

There is **no fixed viewing order**, and folder names are not assigned ahead of time.

The sequence is: a recording is handed over, it is transcribed, the transcript is read end to end, and **only then** is a folder name and a set of note names proposed — derived from what the material actually covers. Nothing is written until that proposal is approved.

Folders are numbered by **teaching order** — where a subject sits in the sequence a stranger would read it, starting at `01`. A folder is still created only after its material has been watched and read, so in practice new subjects usually land at the end; but when one turns out to belong earlier, **renumbering is allowed.** Reordering means renaming folders in descending order so numbers never collide, and rewriting every reference in the same operation: `[[wiki-links]]` survive a folder move because Obsidian resolves them by filename, but any note **renumbered** inside its folder breaks them, and plain-text paths and absolute `Images/` links break on any rename.

**Keep file names short.** Two to four words. `04-API-Standards.md`, not `04-Standards-For-Writing-APIs.md`.

**Ordering is top-down through the stack, and stays consistent.** Inside `03-Computer-Networks/` the material runs foundations, then the application layer, then `10-Transport-Layer/`, then `11-IP-Addressing/` for the network layer. Within a folder, a note is placed where its prerequisites are already behind it — and **each note's opening line bridges from the note before it**, so moving a note means rewriting that line. A section inside a note follows the same rule: nothing is named before the section that defines it.

---

## Folder layout

What exists right now:

```
Backend Engineering/
├── CLAUDE.md                        ← this file
├── 01-Backend-First-Principles/     ← Remindly, processes, client/server, protocols, APIs, storage, the problem catalogue
├── 02-Networking-And-HTTP/          ← SSH, HTTP anatomy, addressing and ports, DNS, JSON, REST conventions
├── 03-Computer-Networks/            ← foundations, then the application layer: DNS, HTTP and cookies, WebSockets, email, torrents
│   ├── Images/                      ← two Commons diagrams, credited in Images/CREDITS.md
│   ├── 10-Transport-Layer/          ← what transport does, reliable delivery, TCP
│   └── 11-IP-Addressing/            ← why addresses need structure, classes, classless addressing, IPv6
├── 04-Spring-Boot-Starter/          ← what Spring Boot is, the generator, project layout, configuration, first run
├── 05-Layered-Architecture/         ← MVC and where it breaks, controller/service/repository, DTOs, the API layer
├── 06-Spring-Dependency-Injection/  ← dependency injection by hand, dependency inversion, component scan, injection styles, choosing an implementation
├── 07-Databases-With-Spring/        ← JDBC upward, JPA, Hibernate, Spring Data JPA, connection configuration
├── 08-Building-The-API/             ← entity to table, repositories, derived and native queries, request channels
├── 09-Entity-Relationships/         ← Category, @MappedSuperclass, @ManyToOne, lazy loading, the N+1 problem
├── 10-Many-To-Many-And-Soft-Delete/ ← join tables, the join entity, JPA auditing, soft delete, indexes and nulls
├── 11-Database-Migrations/          ← why migrations, Flyway, validate catching drift, failed migrations and repair
├── 12-API-Responses-And-Errors/     ← ResponseEntity, exception advice, the response envelope, adapters and MapStruct
├── 13-Writing-Data-Efficiently/     ← cart as a pending order, N+1 on writes, batching an update
├── 14-Observability/                ← monitoring vs observability, the Java agent, reading traces and percentiles, dashboards and host monitoring, then load testing
├── 15-Operating-In-Production/      ← completing the order API, deleting at scale, incidents and logging
├── 16-Scaling-Reads/                ← monolith vs microservices, EXPLAIN, composite indexes, selectivity, clustered and secondary indexes, choosing a primary key, hash indexes and creating them safely
├── 17-Caching-With-Redis/           ← why cache, where it lives, Redis data structures, TTL locks, when not to cache, caching patterns, eviction, the Spring integration, index vs cache
├── 18-Testing/                      ← where testing sits, unit tests and mocking, the kinds of test, then Mockito service tests, H2 repository tests, MockMvc controller tests, and a full integration test
├── 19-Docker/                       ← what runs your code, virtual machines, images, containers, isolation and limits, Docker Hub and tags, the command layer, Dockerfiles, ports, bind mounts and volumes, networking, Compose, publishing
├── 20-Self-Hosted-Observability/    ← OpenTelemetry, managed vs self-hosted, micrometer, the ELK stack, running it with Compose, wiring Spring logs in, searching in Kibana, then Actuator, Grafana and Prometheus, logs into Loki, building a dashboard, alerts and on-call, and what of it transfers
│   └── Images/                      ← one web diagram, credited in Images/CREDITS.md
├── Cloud-And-AWS/                   ← why cloud, what AWS is and its free tier, regions and availability zones, the service catalogue and how far each reaches
│   └── Images/                      ← one Commons photograph, credited in Images/CREDITS.md
├── Full-Text-Search/                ← prefix/suffix/substring, why substring defeats indexes, Postgres full-text, the inverted index, TF-IDF and BM25
└── MongoDB/                         ← NoSQL families, JSON and BSON, the shell, querying, updating, indexes and explain, aggregation pipelines
```

**Numbered folders follow the commit history of `FakeCommerceSpring`** — the record of the sequence the material was actually built in. `12-API-Responses-And-Errors/` precedes `13-Writing-Data-Efficiently/` because the response-and-adapter commits precede the order-API commits; the `Order` entity itself arrived far earlier, with the many-to-many work in folder 10. **When a folder's placement is uncertain, read the commit messages** rather than reasoning about prerequisites — that reasoning has been wrong before.

**A folder with no commits behind it stays unnumbered.** `Full-Text-Search/` and `MongoDB/` are subjects taught with their own tooling and no code in the course project, so the commit history says nothing about where they belong. Numbering them would break the contiguity of the folders that do follow it — testing sits at `18` because its commits come directly after Redis's. They get numbers when the project that uses them appears; until then they sort alphabetically after the numbered run.

**Docker earned its number by being a prerequisite rather than by having commits.** Its own demos live in throwaway repositories, and the project's `docker-compose.yml` arrives later with the ELK commit rather than with the Docker material. It sits at `19` because `20-Self-Hosted-Observability/` cannot be read without it: that folder runs Elasticsearch, Logstash and Kibana as three containers on one network, and every term in that sentence is defined here. Teaching order won over commit order, which is what the numbering scheme is for.

**`19-Docker/01-What-Runs-Your-Code.md` is deliberately long** — around 3,600 words against a folder that otherwise runs 450 to 1,800. It is a single continuous argument, built one rung at a time: a file on disk needs an operating system, Java bytecode needs a JVM, an application needs dependencies a build file only names, a repository carries the list rather than the things, a fat jar freezes the list's result, an artifact can package what it depends on but never what it runs on, an image is the largest package that rule permits, and the kernel is what stays shared. Each rung exists because the one above it could not reach down. Splitting it would break the through-line, so it stays whole.

**Images come before containers, and the four concept notes are one ladder.** `03-Images/` establishes that an image is a root filesystem plus a config, and that a process started from one has that filesystem as its `/`. `04-Containers/` is what happens when one is run — a process with a swapped root, a writable layer, its own namespaces and a lifetime tied to its first process. `05-Kernel/` is what a container is not given: no kernel of its own, so namespaces partition visibility while control groups partition quantity, which is what makes running untrusted code possible and what makes every connection into a container something opened deliberately. `06-Hub-And-Tags/` then supplies the registry vocabulary the command layer needs. **Containers were once explained before images and could only assert isolation rather than derive it; that ordering is fixed and should not be reintroduced.**

**Every folder carrying an `Images/` needs a `CREDITS.md` beside the files** naming source, author and licence for anything taken from the web.

A folder gets a `notes/` subfolder **only when there is code sitting beside it** (`snippets/`, `src/`); otherwise the notes sit flat at the folder root.

**A folder may hold numbered subfolders when one folder's subject grows past what a flat list can carry** — `03-Computer-Networks/10-Transport-Layer/` is inside folder 03 because it is the same subject continued, not a new one. Subfolder numbers carry on from the notes above them, so 01 to 09 are files and 10 onward are folders. **The top-level numbers stay reserved for genuinely new subjects**, in the order they were taken up.

**`Images/` holds anything mermaid cannot carry** — a hand-drawn curve, a plotted shape, an annotated trace, or a good diagram found on the web. Boxes, arrows, bullet lists and comparison tables are recreated as mermaid, which renders in both themes and stays searchable. When an image is used, it goes in `<folder>/Images/` and is embedded by absolute vault path — `![[Backend Engineering/<folder>/Images/<file>.png]]` — so **any future folder rename has to rewrite those links in the same operation.**

---

## How to work here

**Derive before writing.** Never create or edit a note until it is explicitly asked for. Propose the structure for a module and wait. Auto-writing and auto-advancing are the failure mode, and folder economy matters — split into multiple notes only when the content justifies it.

**Full capture, lecture depth only.** Every example, number, distinction, analogy and warning from the lecture goes in. Nothing gets bolted on that the lecture did not cover; anything added beyond it is marked as such and flagged in chat. Read the transcript end to end before claiming a part is done — under-reading has been called out before.

**Problem before solution.** Motivate a tool by showing the simpler thing suffices on the easy case, then breaking it on a harder one. Naive approach first, then break it. Justify with numbers, not adjectives. **Guarantees / does not guarantee** framing where a mechanism has a boundary.

**Plain English, self-contained for a stranger.** These notes are read by people with zero context. Every term is explained at first use and no jargon appears before it is introduced.

**Run it before it goes in a note.** Commands, code and config **never come from the transcript** — dictated code is always garbled, and the typing that produces it is exactly what triggers whisper's silence loops. Take it from the course repo, the official docs, or a legible frame grab, then execute it. Anything that could not be run is labelled as unverified.

**Code blocks carry the file path as a top comment and are line-numbered.**

**No interview-framing callouts.** No `> [!tip] **Interview framing.**` blocks, no "if asked X, the weak answer is…", no viva or exam angles. Write the concept and stop. A point worth making belongs in the body of the note on its own terms. This does not touch material where the lecture itself raises an interview question as its subject — that is the source's content, not framing added on top.

**Visuals, mermaid first — but not mermaid only.** Recreate flows, architectures, pipelines and comparison tables as mermaid or markdown, leaning on mermaid as heavily as the material allows — it renders in both themes and stays searchable and copyable. **Every conceptual section gets a visual unless the concept is genuinely one sentence long.** Where a picture would carry the meaning better than mermaid can — physical layout, real hardware, wire-level geometry, a shape or curve, a widely recognised standard illustration — **search the web for one and embed it.** Screenshot only what recreating would destroy: hand-drawn geometry, curves, annotated traces. Avoid self-referencing mermaid edges (`B -. label .- B`); they render as dangling arcs. Put the label on the edge between two nodes instead.

**Web images are downloaded, never hot-linked.** Fetch the file into `<folder>/Images/`, give it a descriptive name, **open and read it before embedding** — the wrong diagram, a watermark, or an unrelated logo all look identical to a URL — then embed by vault path. A remote URL in a note breaks the moment the host rotates it or the vault is opened offline. Prefer sources whose licence permits reuse, and say in chat where each image came from. The same reading rule covers screen crops — the watermark noted above, plus the stray-Claude-session and player-chrome hazards in the rig manual, all apply.

**Never mention the source inside a note.** No course, lecture, instructor, session, student, syllabus, recording, homework or dashboard. A note is a standalone piece of writing about the subject, not a record of someone teaching it. Write the concept and stop. Provenance worth knowing — a capture gap, something added beyond what was covered, a number that was measured rather than stated — is reported **in chat**, never left in the file.

**Copyright.** Recordings and raw transcripts are never committed, published, or quoted verbatim at length. The notes are original explanations.

### Formatting

- **Never use italics.** Not `*asterisks*`, not `_underscores_` — not for emphasis, not for a paper or product name, not for a quoted phrase or an aside. **Bold** when something has to stand out, plain text everywhere else. This holds in note bodies, callouts, blockquotes, tables and headings alike.
- **Never hard-wrap a paragraph.** One paragraph is one source line however long it runs, and the same goes for list items, callout lines and blockquote lines. A single newline renders as a line break, so a wrapped paragraph breaks mid-sentence in reading view. Code fences, tables and mermaid blocks keep their own line structure.
- **No H1 as a document title** — Obsidian shows the filename. `#` is for sections inside a note, which is how the Spring Boot and DURGA notes already read.
- **No "Next:" trailer lines.** Each note ends on its own content.
