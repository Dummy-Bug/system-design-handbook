# LLD Prep — Working Agreement (persists across sessions)

Goal: interview-ready for machine-coding LLD rounds (Flipkart/Rippling style: compiling,
running code + driver in 90 min). Strategy: 80-20 — a small core set of case studies that
covers nearly all patterns/mechanics first; the long tail comes later as cheap variants.

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
  over-application, which fails bar point 5. Install it inside **Elevator**, where behaviour
  genuinely differs per state (button press: IDLE starts motor / MOVING queues / DOOR_OPEN
  closes first), and teach enum-transition-table vs state-classes as the judgment call.

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
| 3 | Elevator | **State** flagship + scheduling Strategy (SCAN/LOOK) + PriorityQueue | ☐ |
| 4 | BookMyShow | Facade, seat-lock TTL, optimistic locking, **ShowSeat fix** | ☐ |
| 5 | Splitwise | Split Strategy + Factory, balance graph simplification | ☐ |
| 6 | Logging Framework | Highest pattern density/hour: Singleton + Chain of Resp + Observer + Strategy + Decorator | ☐ |
| 7 | Spreadsheet | Observer + Composite + dependency graph + cycle detection (Rippling flagship) | ☐ |

Cheap variants unlocked afterwards (30-45 min each, skeleton transfers): Vending Machine &
ATM (from Elevator's state machine), Hotel/Car Rental (from BookMyShow's context-status idea),
Pub-Sub & Notification System (from Logger's fan-out), Rate Limiter (Strategy shell),
Tic-Tac-Toe/Chess/Card Game (from Snake & Ladder's loop; Chess adds Command/undo).

Phase-2 backlog (only after core-7): Chess (Command), Task Scheduler (min-heap), In-Memory
File System (Composite+Iterator), Multi-Tenant RBAC, Calendar, Rule Engine.

## The bar (Rippling SDE-2 — every case study graded against all 5)
1. **Timeboxed** — built in 90 min from a blank editor.
2. **Runs** — Main driver prints every core use case working; compiling code is a gate, not a score.
3. **Extension test executed** — actually add one new requirement after finishing; target = 1 new class, 0 modified files.
4. **Concurrency answer ready** — say out loud what breaks with two threads and which line protects it.
5. **No over-engineering** — restraint is part of the bar (no abstract factory for one product).

Rippling-specific problem flavors (Rule Engine, RBAC) stay in phase-2 backlog unless Rippling
becomes a live interview target — the bar is theirs, the problem list is ours.

## Session protocol
- One case study per session. Derive first (requirements → entities → diagram → patterns →
  code), then compare against the AlgoMaster chapter and log its flaws.
- After each study, run the "new requirement" test (add a feature — count files touched).
- Explanations: one concept at a time, plain English, justify with concrete scale/consequence
  ("same seat blocked for all shows"), problem before solution.
- Never write/edit files until explicitly told; discuss and derive in chat first.

## Companies that go deep on LLD (target awareness)
Tier A — dedicated machine-coding round, compiling code expected:
Flipkart, Rippling, Uber, Swiggy, Zomato, PhonePe, Razorpay, CRED, Zepto, Meesho, Ola,
Navi, Myntra, Urban Company, Dream11, Groww.

Tier B — deep OOD/class-design discussion (doc/whiteboard, less compile pressure):
Atlassian, Salesforce, Walmart Global Tech, Intuit (craft demo), Amazon, Microsoft,
Arcesium, Zeta, ThoughtWorks (pairing round, clean-code heavy), Grab.

Google/Meta ask LLD lightly (45-min OOD at most) — do not over-index on them for this track.
