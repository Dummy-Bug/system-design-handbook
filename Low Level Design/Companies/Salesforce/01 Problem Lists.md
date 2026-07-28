---
company: Salesforce
purpose: two orderings of Salesforce-confirmed LLD problems — by likelihood, and by learning difficulty
---

# Salesforce LLD — Two Lists

> [!note] Scope rule
> Every problem below was reported in a **public Salesforce interview experience, 2024–2026**
> (LeetCode discuss, CodingKaro 61+ stories, Medium, Substack). Nothing invented. Confidence tag:
> **H** = specific report with role + year · **M** = company-tagged aggregator (codezym "Salesforce=Yes").
> See [[00 Loop Notes]] for sources and the JD analysis.

---

## LIST 1 — Most likely → least likely (what to prioritize)

Ranked by: frequency of report × recency × MTS-level match × JD alignment (Backend + AI).

| # | Problem | Evidence | Conf | Our track |
|---|---------|----------|------|-----------|
| 1 | **Thread-safe LRU / LFU Cache** | LRU: MTS-I 2026 (×2+); LFU: MTS-II 2025 | **H** | B5 |
| 2 | **Rate Limiter** (per-resource `isAllowed`) | MTS-II 2025; fixed-window / token-bucket | **H** | B1 |
| 3 | **Elevator** | MTS-II 2025 | **H** | core #3 |
| 4 | **Connection Pool** | LMTS Sept 2025; queue-and-wait | **H** | (new) |
| 5 | **Job / Task Scheduler** | LMTS Apr 2025; worker threads | **H** | (new) |
| 6 | **Meeting Scheduler / Room Reservation** | 2025; codezym Salesforce=Yes | **H/M** | (new) |
| 7 | **Notification System** | SMTS; Template Method + retry | **H** | Logger-adj |
| 8 | **Movie Ticket Booking (BookMyShow)** | codezym Salesforce=Yes | **M** | core #4 |
| 9 | **Cab Booking / Bike Rental** | Cab: MTS-II 2025 · Bike: SMTS 2024-25 | **H** | (new) |
| 10 | **Parking Lot** ✅ | codezym Salesforce=Yes | **H** | core #1 ✅ |
| 11 | **Splitwise (Expense Sharing)** | codezym Salesforce=Yes | **M** | core #5 |
| 12 | **Pub-Sub / Message Queue** | often *disguised* as #4/#5 | **M** | Logger-adj |
| 13 | **Chess** | codezym Salesforce=Yes | **M** | phase-2 |

*Footnotes:* **Spotify** (MTS-II 2026, one report) and **Vending Machine** (generic staple, not pinned
to a 2024-26 report) are real-but-weak — parked, not in the main list.

---

## LIST 2 — Learning order, easy → tough (what to actually build, in sequence)

Ordered so each build adds **one** new thing on the last. Concurrency primitives install in a chain:
one-lock → atomic → semaphore/blocking-queue → scheduled-executor. Domain modeling ramps in parallel.

| Step | Problem | Difficulty | What's new / why here | Likelihood |
|------|---------|-----------|------------------------|-----------|
| 0 | Parking Lot ✅ | — | baseline: enums, Strategy, Singleton, one-lock | #10 |
| **1** | **Thread-safe LRU Cache** | Easy | 2 classes; **one lock** around HashMap+DLL — the *same* guard-shared-state lesson as Parking Lot | **#1** |
| 2 | LFU Cache | Easy–Med | LRU + frequency buckets (cheap once LRU exists) | #1 |
| 3 | Rate Limiter | Easy–Med | **new primitive:** `AtomicInteger`/CAS, token-bucket vs sliding-window behind a Strategy | **#2** |
| 4 | Meeting Scheduler | Med | interval overlap + conflict detection; low concurrency | #6 |
| 5 | Elevator | Med | domain step-up: more entities + scheduling Strategy + `PriorityQueue` | **#3** |
| 6 | Notification System | Med | Template Method + Factory + retry queue w/ exponential backoff | #7 |
| 7 | Connection Pool | Med–Hard | **new primitive:** `Semaphore` / `BlockingQueue`, producer-consumer, release-on-failure | **#4** |
| 8 | Splitwise | Med–Hard | graph / balance simplification (algorithmic) | #11 |
| 9 | Pub-Sub / Message Queue | Med–Hard | thread-safe fan-out + backpressure (Observer under a lock) | #12 |
| 10 | Cab Booking / Bike Rental | Med–Hard | matching + ride/rental lifecycle + `searchBikes(filters, location)` | #9 |
| 11 | Job / Task Scheduler | Hard | **new primitive:** `ScheduledExecutorService` + priority + worker pool (combines several) | #5 |
| 12 | Movie Booking (BookMyShow) | Hard | seat-lock TTL + optimistic locking + **ShowSeat** — concurrency-in-domain | #8 |
| 13 | Chess | Hard | richest rules + Command/undo | #13 |

---

## How to use the two lists

- **Follow LIST 2 (learning order) as your build sequence** — it compounds; each problem makes the
  next easier. Don't jump around by likelihood, or you'll hit a concurrency primitive you haven't
  installed yet.
- **Use LIST 1 to know what you cannot skip.** If the loop gets scheduled and time is short, make
  sure everything in LIST 1 rows 1–7 is *at least* built once. Rows 1–5 of both lists overlap
  heavily — that overlap is your must-do core.
- **The two lists agree on the starting point: Thread-safe LRU Cache is both #1-likely and the
  gentlest next step.** Strong signal. That's the next build.
- Every build ends with the Salesforce escalation drill: *"now make it thread-safe" → "now make it
  distributed with a central DB."*
