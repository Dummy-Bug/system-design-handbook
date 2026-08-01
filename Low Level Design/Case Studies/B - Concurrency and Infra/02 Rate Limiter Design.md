---
track: B — Concurrency & Infra
salesforce: #2 most-likely LLD (see [[00 Loop Notes]], [[01 Problem Lists]])
status: 🚧 in progress — requirements settled, design next
---
> [!abstract] Rate Limiter
> Track B (concurrency) · Salesforce #2-frequency LLD · Patterns: Strategy (algorithm), Factory (later)
> Interviewer prompt was thin on purpose. Everything below was **extracted by asking**, not handed over.

---

## 📖 Jargon (say these by name in the room)

- **Boundary burst / edge burst** — the fixed-window failure mode. Limit 10/min: 10 requests land at
  `11:59:59`, the counter resets at `12:00:00`, 10 more land at `12:00:01`. **20 requests in a
  two-second span** — the *instantaneous* rate is 20× what you promised, which is what actually kills
  the downstream service. Always say it with the timestamps, not as "it's bursty."
- **Capacity vs refill rate** (token bucket's two knobs, and the reason to prefer it) —
  `capacity` bounds the **burst**; `refillRate` bounds the **sustained** rate. They're independent, so
  you can express *"10/sec sustained, but tolerate a spike of 50."* Fixed window cannot express that —
  it has one number doing both jobs.
- **Token bucket does not eliminate bursts — it bounds them.** Wrong sentence: *"token bucket fixes
  bursty traffic."* Right sentence: *"a client can still fire a burst, but never more than `capacity`
  at once, and never more than `refillRate` over the long run."*

---

## 📄 Problem Statement

> Design a **Rate Limiter**. We want to control how frequently our service gets called. Build it as a
> **reusable library** — something another team could drop into their service.

Reusable library, not a service: it is called **in-process, on the request path**, so the answer must be
cheap (µs) and thread-safe. That framing came from the prompt and drives everything.

---

## ✅ Functional Requirements (extracted by clarifying questions)

1. **Limit is per client, not global.** Every request carries a client identifier — a userId or an API
   token. The limiter treats it as an opaque `String key`. Two different keys never affect each other.
2. **Limits are configurable, `N` requests per `T` window.** Different endpoints want different limits,
   so `N` and `T` are parameters, never constants.
3. **Limits differ per client tier.** Free tier = 10 req/min, enterprise = 1000 req/min. So the limit is
   **attached to the key**, not one global setting. A key must resolve to *its own* configuration.
4. **Exceeding the limit rejects immediately.** `isAllowed(key)` → `boolean`. `true` = proceed,
   `false` = caller returns HTTP 429. **No queueing, no waiting** (see judgment call).
5. **Multiple algorithms, selectable.** Fixed Window first, Token Bucket second, behind one interface.
6. **Heavily concurrent.** Many threads call `isAllowed` at once, *including multiple threads on the
   same key*. Thread-safety is a v1 requirement here, not an escalation (unlike [[01 Thread-Safe LRU Cache Design|LRU Cache]]).
7. **Single JVM for v1** — in-memory state is acceptable. The interviewer explicitly flagged that the
   *"now make it work across fifty boxes"* escalation is coming, so the design must not paint itself
   into a corner (see judgment call).

### Out of scope (v1 — announce, don't build)

Queue-and-wait / traffic shaping · distributed shared state (escalation, not v1) · per-endpoint routing
rules · persistence of counters across restart · dynamic config reload · metrics/observability.

---

## 🧠 Judgment Calls

> [!tip] Reject immediately — queueing is a different problem
> A rate limiter exists to protect the service **right now**. Making the caller wait for a free slot
> doesn't shed load — the caller is still holding a connection and a thread, so you've converted a fast
> rejection into a slow one and kept the pressure. Queue-until-a-slot-frees is **traffic shaping**
> (leaky bucket / job scheduler), a different problem. Name it as a variant; don't build it.

> [!tip] Ask "one box or fifty?" — it is an LLD question, not an HLD question
> It looks like an HLD question and it isn't: the answer **changes the object model**. On fifty boxes
> an in-memory counter is simply wrong — each box independently allows `N`, so the real limit is
> `50 × N`, and the state must move to a shared store with an **atomic increment**. Concretely, the
> per-key counter stops being a field and becomes a **store interface** the algorithm talks to.
> Asking this early is what lets you keep the seam; asking it at minute 55 means a rewrite.

> [!tip] Two algorithms is justified, not speculative
> The usual YAGNI rule says build one and extract on the second caller. It doesn't apply here because
> the second algorithm is a **stated requirement with a real driver**: fixed window is cheap but has the
> boundary burst; token bucket costs more state but bounds the burst. Different endpoints genuinely
> want different trade-offs. Build **Fixed Window first** (simplest, and it exposes the flaw that
> motivates the next one), then Token Bucket.

> [!tip] Start with fixed window *because* it's flawed
> Picking the simple-but-flawed algorithm first, **naming its failure mode out loud**, then replacing it
> is the sequence that scores. Picking token bucket immediately without articulating what it fixes reads
> as memorized.

---

## 🧱 Classes

*→ deriving next.*
