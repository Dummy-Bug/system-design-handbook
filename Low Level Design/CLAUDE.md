# LLD Prep — Working Agreement (persists across sessions)

Goal: interview-ready for machine-coding LLD rounds (compiling, running code + driver in
60-90 min). Strategy: 80-20 — a small core set of case studies that covers nearly all
patterns/mechanics first; the long tail comes later as cheap variants.

## Round flavors (researched 2026-07-21 — the round is NOT one thing)
| Flavor | Who runs it | The hard part | Our track |
|---|---|---|---|
| **A. Domain modeling** (classic MC) | Flipkart, Uber, Swiggy, Ola, CRED, Groww, Meesho, Dream11, BrowserStack (120 min) | Clean OOP, patterns, extensibility, working driver | **Core-7** below |
| **B. Concurrency / infra** | **Emergent**, Razorpay/Upstox/fintech, infra startups | Races, resource cleanup on timeout/failure, state machines | **Track B** below |
| **C. AI-assisted mode** | Emergent, Google (2026 code-comprehension round), Meta, Canva | Driving + validating an agent; defending code you didn't type | a *mode*, not a module |
| **D. Contract/schema LLD** | Emergent's separate LLD round, Atlassian, Salesforce | DDL + indexes, API signatures, optimistic concurrency, migrations | parked — overlaps HLD track |

Domain flavor tracks the business: fintech → correctness/idempotency; food-delivery &
ride-hailing → lifecycle modeling; Dream11 → gaming; Flipkart/Amazon → commerce.

**Flavor C detail** — candidates confirm Emergent's MC round has you *generate code with AI* and
grades prompting skill, accuracy of the generated code, and whether you drive the agent or
passively accept it; you still explain entities/patterns yourself. Google scores "AI fluency:
prompt engineering, output validation, debugging"; Meta lets you switch models mid-round and
scores **verification** as its own axis; Canva rewrote problems to be un-one-prompt-able.
Practice rule: **build it cold first, then redo one build by driving an agent under a timer.**
The graded skill is catching the bug in generated code — only reachable if you've built it cold.

## Primary resource
- AlgoMaster LLD course (user has subscription): https://algomaster.io/learn/lld/course-roadmap
- **Trust-but-verify rule**: the course's designs contain modeling flaws. Canonical example:
  BookMyShow puts booking status on `Seat` (physical seat) instead of `ShowSeat` (seat × show)
  — that would block a seat for ALL shows once one show books it. Status/state that depends on
  a context (show, date, rental period) must live on the association class, not the base entity.
  In every case study session: derive our own design first, THEN read the course chapter and
  critique its diffs. Never absorb the course design uncritically.
- Same flaw exists in our own notes: `01-Syllabus/09-LLD-Problems.md` (BookMyShow entry says
  "State pattern on Seat") — fix when we do that case study.

## Pattern scope
11 patterns total, ranked in `00-Pattern-Priority-List.md`: Tier 1 (Strategy, Factory,
Observer, Singleton) produced cold; Tier 2 (**State**, CoR, Composite, Facade, Template Method,
Decorator, Command) installed inside their anchor case studies, no upfront study. The other
12 GoF patterns are recognize-only — never drill them.

- **State moved to Tier 2 (2026-07-20)** — abstractly it teaches nothing (a 3-status seat is
  solved by a 2-line enum, so the pattern looks like pure ceremony) and studying it cold invites
  over-application, which fails bar point 5. Install it inside a real machine, and teach
  enum-transition-table vs state-classes as the judgment call.
- **State's anchor moved Elevator → Circuit Breaker (2026-07-21)** — CLOSED/OPEN/HALF_OPEN is the
  textbook state machine, it is literally what Emergent asked a candidate (LLM orchestrator:
  route Claude → OpenAI once errors cross a threshold), and it carries into flavor B. Elevator
  demotes to a cheap variant of the same skeleton.

Pattern file format (settled): **Trigger → Structure → Component Mapping → Template**, nothing
else. Trigger = one-line rule + what its terms mean + a short code contrast. Template = folder
tree then one code block per file. No prose walkthroughs, no failure-case sections.

## 80-20 core set (do in this order)
7 case studies ≈ 29% of the 24-problem list, but they cover 11 of the 12 interview patterns
and all 5 recurring mechanics (state machine, TTL lock, fan-out notify, dependency graph,
pairwise balance map). Everything after these is a variant.

| # | Case study | Pattern payload (new learning) | Status |
|---|-----------|-------------------------------|--------|
| 1 | Parking Lot | Factory, Strategy, Singleton, Observer + last-spot concurrency | ☐ |
| 2 | Snake & Ladder | Template Method (game loop), Dice Strategy — speed rep, Flipkart favorite | ☐ |
| 3 | Elevator | scheduling Strategy (SCAN/LOOK) + PriorityQueue (State now lives in Track B) | ☐ |
| 4 | BookMyShow | Facade, seat-lock TTL, optimistic locking, **ShowSeat fix** | ☐ |
| 5 | Splitwise | Split Strategy + Factory, balance graph simplification | ☐ |
| 6 | Logging Framework | Highest pattern density/hour: Singleton + Chain of Resp + Observer + Strategy + Decorator | ☐ |
| 7 | Spreadsheet | Observer + Composite + dependency graph + cycle detection (Rippling flagship) | ☐ |

Cheap variants unlocked afterwards (30-45 min each, skeleton transfers): Vending Machine &
ATM (from the Circuit Breaker / Elevator state machine), Hotel/Car Rental (from BookMyShow's
context-status idea), Pub-Sub & Notification System (from Logger's fan-out),
Tic-Tac-Toe/Chess/Card Game (from Snake & Ladder's loop; Chess adds Command/undo).

Phase-2 backlog (only after core-7): Chess (Command), Task Scheduler (min-heap), In-Memory
File System (Composite+Iterator), Multi-Tenant RBAC, Calendar, Rule Engine.

## Track B — concurrency / infra builds (flavor B; 45-60 min each)
Smaller than the core-7 and interleaved with them. This is where "concurrency answer ready"
stops being a talking point and becomes code. The recurring grading line across every source:
**release a reserved resource on failure and timeout, not just on success.**

| # | Build | Mechanic payload | Status |
|---|-------|------------------|--------|
| B1 | Rate Limiter | token bucket + sliding window behind one Strategy; atomic refill | ☐ |
| B2 | **Circuit Breaker** | **State flagship** (CLOSED/OPEN/HALF_OPEN), threshold + cooldown timer | ☐ |
| B3 | Retry / fallback chain | exponential backoff + jitter, fallback ordering, budget cap | ☐ |
| B4 | Health tracker | EWMA over a ring buffer, healthy/degraded/unhealthy transitions | ☐ |
| B5 | Thread-safe LRU cache | map + list under one lock, or striped locks; eviction race | ☐ |

Primitives to be able to reach for cold: `synchronized` vs `ReentrantLock`, `Semaphore`,
`AtomicInteger`/CAS, `ConcurrentHashMap.compute`, `ScheduledExecutorService`.
Assembly target once B1-B4 exist: **LLM request router** (registry + limiter + health +
retry/fallback + breaker) — Emergent's own published practice problem.

## The bar (Rippling SDE-2 — every case study graded against all 5)
1. **Timeboxed** — built in 90 min from a blank editor.
2. **Runs** — Main driver prints every core use case working; compiling code is a gate, not a score.
3. **Extension test executed** — actually add one new requirement after finishing; target = 1 new class, 0 modified files.
4. **Concurrency answer ready** — say out loud what breaks with two threads and which line protects it.
   *(Flavor B raises this: name the specific check-then-act race, not "I'd add a lock".)*
5. **No over-engineering** — restraint is part of the bar (no abstract factory for one product).

Rippling-specific problem flavors (Rule Engine, RBAC) stay in phase-2 backlog unless Rippling
becomes a live interview target — the bar is theirs, the problem list is ours.

## Vault layout
```
Low Level Design/
├── CLAUDE.md                          ← this file
├── 00-Pattern-Priority-List.md        ← pattern learning order
├── Behaviorial|Creational Design Pattern/   ← one note per pattern
└── Case Studies/
    ├── A - Domain Modeling/           ← flavor A (core-7)
    └── B - Concurrency and Infra/     ← flavor B (Track B, see its 00 Track Index)
```
Case-study note format (settled 2026-07-21):
**Problem Statement → Functional Requirements (+ explicit *out of scope*) → Judgment Calls
(claims only) → Classes (prose, bottom-up) → Class Diagram (Mermaid) → Build Scope →
Post-Build checklist.**

- **A decision lives at the class it decides**, as a callout inside that class's prose. The
  Judgment Calls section carries the *claims only*, each linking to its class. Reason: a
  decision stated before its subject exists is solution-before-problem, and a decisions section
  written in full duplicates the class prose (it did, three times, before this rule).
- **Class prose, not a table** — one `####` per class, opening with the requirement line it
  comes from, then what it owns and why. Bottom-up: enums → data classes → classes with logic.
- **Diagrams: Mermaid for class structure, Excalidraw only for architecture.** A class diagram
  is a slower duplicate of the code; don't spend build minutes dragging boxes. Excalidraw
  practice belongs to the HLD track, where the diagram is mandatory and separately graded.
- Every disagreement with the AlgoMaster chapter gets recorded inline with its reason — and so
  does every place the chapter was *right* and we were wrong. Both directions, honestly.

## Session protocol
- One case study per session. Derive first (requirements → entities → diagram → patterns →
  code), then compare against the AlgoMaster chapter and log its flaws.
- Interleave the tracks: core-7 for flavor A, Track B for flavor B. Suggested order —
  Parking Lot → B1 Rate Limiter → Snake & Ladder → **B2 Circuit Breaker (installs State)** →
  BookMyShow → B3 → … Do one flavor-C (agent-driven) repeat only after a build exists cold.
- After each study, run the "new requirement" test (add a feature — count files touched).
- Explanations: one concept at a time, plain English, justify with concrete scale/consequence
  ("same seat blocked for all shows"), problem before solution.
- Never write/edit files until explicitly told; discuss and derive in chat first.

## Round execution playbooks
What to *do* in the room, once the problem is on screen. Two different games.

**Deterministic round (flavor A/B — you type every line):**
1. Clarify boundaries in the first ~10 min: inputs, scope, what's explicitly out.
2. Write `Main` **first** — the driver defines the I/O contract and gives you a running
   skeleton to grow. Never leave "does it run" to minute 85.
3. Core features before extensibility. An elegant design that misses a use case scores below
   an ordinary one that works.
4. Enum-heavy, interface-driven — self-documenting and it makes switches exhaustive.
5. State the concurrency model out loud, and point at the line that enforces it.

**AI-assisted round (flavor C — you drive an agent):**
1. **Give the model the design, not the problem.** Hand it the interfaces and the patterns
   you've chosen; never ask for the whole solution in one prompt.
2. Narrow, spec-driven prompts. One component per prompt, with its contract stated.
3. Treat every output as a hypothesis — trace it line by line, run it. Blind acceptance is
   the documented failure mode.
4. You own the integration and any architecture mismatch; the model owns typing.
5. Narrate *why* you're prompting the way you are — the reasoning is what's being graded.

## Concurrency control cheat-sheet (flavors B and D)
| Mechanism | Pattern | Good for | Failure mode |
|---|---|---|---|
| **Optimistic** | version column; `UPDATE … WHERE version = :old` | read-heavy, low contention, distributed | high abort/retry rate under write contention |
| **Pessimistic** | `SELECT … FOR UPDATE`, row locks | high contention, must-not-fail writes | serializes; connection-pool starvation, deadlocks |
| **Distributed** | Redis `SET NX PX` lease | multi-node, offloads the DB | split-brain on partition; lease expiring mid-task |
| **In-process** | `synchronized` / `ReentrantLock` / CAS | single-JVM machine-coding rounds | lock too coarse → serializes everything |

**Stateless percentage routing** (useful in B2/B3, avoids a shared counter entirely):
hash the request id and take `abs(H(id)) % 100`, then map ranges to destinations. Deterministic,
thread-safe, and consistent across nodes with no coordination — a global `synchronized` counter
or `Random` is the naive answer and it contends.

## Companies that go deep on LLD (target awareness)
Tier A — dedicated machine-coding round, compiling code expected (flavor A):
Flipkart, Rippling, Uber, Swiggy, Zomato, PhonePe, Razorpay, CRED, Zepto, Meesho, Ola,
Navi, Myntra, Urban Company, Dream11, Groww, BrowserStack (120 min).

Tier B — deep OOD/class-design discussion (doc/whiteboard, less compile pressure):
Atlassian ("design exercise", more discussion), Salesforce, Walmart Global Tech,
Intuit (craft demo), Amazon, Microsoft, Arcesium, Zeta, ThoughtWorks (pairing round,
clean-code heavy), Grab.

Tier C — infra/concurrency MC, AI-assisted (flavors B + C):
**Emergent** (60-75 min MC + separate 55-65 min contract-level LLD; publishes its own syllabus
at interview-prep-101.emergent.host and asks from it), plus fintech infra teams.
Aspiration only for now — not a scheduled interview (noted 2026-07-21). Comp is real at the
top end but the 6-day/12-hour schedule is ~2x normal hours; price it per hour before
optimizing the whole plan around it.

Google/Meta ask LLD lightly (45-min OOD at most) — do not over-index on them for this track,
but both now run AI-assisted coding rounds, so flavor C practice transfers there.
