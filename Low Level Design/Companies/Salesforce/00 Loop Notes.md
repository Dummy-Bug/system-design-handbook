---
company: Salesforce
role: Software Engineering, MTS (Backend + AI)
status: reach-out + resume sent (2026-07-23) — NOT scheduled
---

# Salesforce — MTS (Backend + AI) — Loop & LLD Frequency Map

> [!note] Provenance
> Compiled from public interview experiences (LeetCode discuss, CodingKaro 61+ stories, Medium,
> Substack), Jan 2025 – Jul 2026. Directional, not guaranteed — interviewer-dependent.

## The opportunity
- Recruiter Hrishikesh Misal reached out 2026-07-23; resume sent. Expect reply in a few days.
- Work: LLM tech + **agentic frameworks** (A2A inter-agent protocols, Human-Agent Collaboration),
  structured AI Skills / headless agent workflows, distributed systems, Java/Python/Go.
- **Status = row 1** (reach-out, not a scheduled round). Trunk (core-7) keeps moving; this file is
  the container. Go heavy only when a round is on the calendar.

## The loop (MTS, India, 2025–2026)
- Shape: OA (DSA, LC-medium, ~100 min / 3 Qs) → ~2 DSA rounds → Hiring Manager (behavioral +
  project deep-dive + **Agentforce / AI systems** discussion) → **≥1 LLD/design round**.
- LLD is present at MTS, heavier at SMTS/LMTS. HLD skews senior.
- **Format: discussion / whiteboard / shared doc — Tier B.** Far less "does it compile in 60 min"
  pressure than Flipkart. They grade reasoning, pattern choice, SOLID, extensibility, tradeoffs.

## Salesforce LLD signature — the 3 things that define their round
1. **Requirements are deliberately vague → clarifying questions are GRADED.** A message-queue gets
   asked indirectly as a "connection pool" or "job scheduler." Ask before you model.
2. **Concurrency is THE follow-up.** *"Now make it thread-safe"* is the standard escalation that
   turns easy → hard. Resources are limited (N connections, N workers) and not handed out
   immediately → you discuss locks, blocking queues, semaphores. Then often *"now make it
   distributed with a central DB"* → optimistic/pessimistic locking.
3. **Patterns + extensibility.** Name the right pattern, justify it, SOLID, "how would you extend."

> [!important] The headline finding
> **Salesforce LLD leans concurrency + resource-management far more than pure domain modeling.**
> Their most frequent problems are caches, connection pools, rate limiters, job schedulers — this
> is our **Track B**, not the classic flavor-A core-7. The domain problems they *do* ask (elevator,
> cab booking, notification) are the discussion-friendly kind. So for *this* company, the
> concurrency cluster we deprioritized is actually the higher-value tune. See [[#Plan impact]].

## LLD problems — frequency-ranked (2025–2026), backend + AI weighted

**Tier 1 — concurrency / backend (highest value for this role)**
1. **Thread-safe Cache — LRU / LFU** — most frequent (LRU ×2, LFU ×1). = our **B5**. Thread-safety is the guaranteed follow-up.
2. **Connection Pool** (Sept 2025, LMTS) — BlockingQueue / semaphore, resource-limited, thread-safe. Pure backend, no domain.
3. **API Rate Limiter** (MTS II, 2025) — = our **B1**. Token bucket / sliding window.
4. **Job Scheduler** (Apr 2025, LMTS) — worker threads, thread-safe dispatch, persistence, execution flow.

**Tier 2 — domain / OOD (discussion-friendly)**
5. **Elevator** (MTS II, 2025) — = core-7 **#3**. Scheduling strategy.
6. **Meeting Scheduler / Meeting-Room Reservation** — interval conflict handling, calendar.
7. **Notification System / Library** (SMTS) — email/SMS/push, Observer + Strategy, extensibility.
8. **Cab Booking (Uber-like)** (MTS II, 2025) — matching + ride-lifecycle state machine.

**Tier 3 — classic staples / occasional**
9. **Vending Machine** — State + Singleton. 10. **Parking Lot** — ✅ done. 11. **Chess board** — OOD.
12. **Spotify** — entity modeling. (Plus HLD-leaning: News Feed, Metric Collection, Flash Sale.)

**AI-specific:** no standalone "AI LLD" problem has surfaced in interviews yet — the AI shows up in
the HM/project round and HLD (LLM orchestration). *But* the Tier-1 concurrency primitives (rate
limiter, connection pool, circuit breaker, job scheduler) **are the building blocks of AI-serving
infra** — the same cluster as the Emergent "LLM request router." Backend + AI framing reinforces,
not replaces, the concurrency focus.

## JD → what they'll ask YOU (MTS Backend + AI)
Each JD line maps to an LLD shape — and it points at the *same* cluster the interview data shows
(convergent evidence, not two separate bets):

| JD signal | LLD it points to |
|---|---|
| "scalable **high-performance** systems" + concurrency | thread-safe cache, connection pool |
| "distributed systems, microservices, **APIs**" | rate limiter, API gateway |
| "agentic frameworks, **inter-agent protocols (A2A)**" | pub-sub / message queue, orchestrator |
| "structured AI Skills & **headless agent workflows**, deterministic outcomes" | job/task scheduler, workflow state machine, retry / idempotency, circuit breaker |
| "**real-time** systems" | rate limiter, hit counter, streaming |
| "**Human-Agent Collaboration**" | notification / task-assignment |

→ The AI-serving-infra primitives (limiter, pool, breaker, scheduler, queue) *are* the JD. This is
the same cluster as the Emergent "LLM request router."

## Attack order — tackle one-by-one (JD × frequency × concurrency)

**Tier 1 — concurrency core (start here):**
1. **Thread-safe LRU / LFU cache** — #1 Salesforce frequency + high-perf JD + the *"make it thread-safe"* escalation. Builds straight on Parking Lot's guard-shared-state lesson. `[B5]`
2. **Rate Limiter** — confirmed asked + real-time/API JD. `isAllowed(resourceId)`, per-resource Strategy, fixed-window / token-bucket. `[B1]`
3. **Connection Pool** — confirmed (Sept '25) + resource-mgmt. `requestId` → free conn or queue-and-wait; `BlockingQueue` / `Semaphore`, producer-consumer, release-on-failure. Pure backend.
4. **Job / Task Scheduler** — confirmed (Apr '25) + "headless agent workflows" bullseye. Worker threads, `PriorityQueue`, `ScheduledExecutorService`.

**Tier 2 — orchestration / resilience (JD-aligned):**
5. **Pub-Sub / Message Queue** — A2A inter-agent + event-driven + thread-safe fan-out.
6. **Notification System** — confirmed (SMTS): Template Method (base sender, channel overrides) + Factory + retry queue with exponential backoff.
7. **Circuit Breaker / Retry** — "deterministic production-grade outcomes" + resilience. `[B2/B3]`

**Tier 3 — domain modeling (discussion-friendly, still asked):**
8. Elevator `[#3]` · 9. BookMyShow / Movie Booking `[#4 — seat-lock concurrency]` · 10. Meeting Scheduler · 11. Splitwise `[#5]` · 12. Cab / Bike Rental `[context-status]`.

**Tier 4 — quick staples if time:** Vending Machine (State) · Chess · ~~Parking Lot~~ ✅.

> [!tip] Sequencing
> Tier 1–2 need concurrency primitives installed **one at a time, with motivation** — never dumped
> at once. `synchronized` ✅ (Parking Lot). Next up as each anchor needs it: `BlockingQueue`,
> `Semaphore`, `AtomicInteger`/CAS, `ScheduledExecutorService`.
> **Immediate next build: Thread-safe LRU Cache.**
> Every Salesforce-aimed build: rehearse out-loud narration + the *"now make it thread-safe"* →
> *"now make it distributed"* escalation. That escalation is the actual exam.

## Sources
- [CodingKaro — Salesforce, 61+ interview stories](https://www.codingkaro.in/jobs-internships/leetcode-interview-experience/Salesforce)
- [Salesforce LLD Questions from recent interviews — Prashant Priyadarshi (Jan 2026)](https://medium.com/@prashant558908/salesforce-low-level-design-questions-from-recent-interviews-3009c3a58f78)
- [Salesforce LMTS India, Sept 2025 — connection pool (LeetCode)](https://leetcode.com/discuss/post/7333207/)
- [Salesforce LMTS, Apr 2025 — job scheduler (LeetCode)](https://leetcode.com/discuss/post/6857467/)
- [Salesforce SMTS LLD round — notification system (LeetCode)](https://leetcode.com/discuss/post/7398700/)
- [Salesforce SMTS interview experience (roundz.substack)](https://roundz.substack.com/p/interview-experience-salesforce-smts)
- [Salesforce MTS March 2026 — Flash Sale HLD (interviewexperiences.in)](https://interviewexperiences.in/experience/salesforce/salesforce-mts-march-2026)
- [Salesforce LLD questions (codezym)](https://codezym.com/lld/salesforce)
