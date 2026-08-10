---
track: B — Concurrency & Infra
salesforce: #2 most-likely LLD (see [[00 Loop Notes]], [[01 Problem Lists]])
status: 🚧 in progress — classes + fixed window done, concurrency in progress
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
- **Check-then-act** — two threads both pass a test that only one should have passed. The test result
  is stale by the time you act on it. (`if (count < limit) count++;`)
- **Lost update** — two threads both *write*, but only one write survives, because the second computed
  its value from a base it read before the first wrote. The increment happened and then didn't.
- These two are **different bugs on the same two lines**, and they get conflated because
  `synchronized` fixes both. Check-then-act = a wrong *decision*. Lost update = a wrong *number*.
- **Lost insert** — two threads both find a key absent, both create a value, and the second `put`
  overwrites the first. Loses **a whole object**, not one increment: the loser keeps mutating an
  orphan that is no longer in the map.

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

Bottom-up: the routing key, the request, the per-client counter state, the algorithm interface, the
first algorithm, then the facade that ties them together.

#### `Tier` (enum)

From FR-3 (limits differ per client tier). `FREE`, `ENTERPRISE`. An enum, not a `String`, so the
registry keys are typo-proof and a `switch` over tiers stays exhaustive.

#### `Rule` — the routing key

From FR-2 + FR-3: the limit depends on **which endpoint** and **which tier**, so the thing that
selects a limiter is the pair. It is a value object used as a `Map` key, so it needs `equals`/`hashCode`
— a `record` gives both for free.

```java
record Rule(String endpoint, Tier tier) { }
```

> [!important] Why a map key *must* have `hashCode` and `equals` — and why `record` is the cheap fix
> A `HashMap` finds a value in two steps: **`hashCode()` picks the slot** (narrowing a million keys
> to one short chain), then **`equals()` picks the right node inside that chain** (because unrelated
> keys share slots — see [[90 HashMap Internals]]).
> Without both, `rules.get(new Rule("/login", FREE))` **misses every time**: the freshly built `Rule`
> inherits `Object`'s identity-based versions, hashes to an unrelated slot, and would never `equals`
> the instance you stored even if it landed there. A `record` generates both from its fields, so a
> value object used as a key is correct by construction — that is the actual reason to reach for it
> here, not brevity.

#### `ClientRequest` — what arrives at the facade

```java
record ClientRequest(String clientId, String endpoint, Tier tier) { }
```

> [!warning] `tier` must not be trusted from the caller
> If the tier travels in on the request, a free-tier client sends `tier = ENTERPRISE` and buys itself
> a 100× limit. In a real system the tier is **resolved server-side** from the authenticated identity
> (`clientId` → subscription lookup), and the limiter is handed the result. Keeping it on
> `ClientRequest` is fine *only* because the library sits behind an auth layer that populated it —
> say that out loud rather than letting the interviewer find it.

#### `Window` — one client's counter state

From FR-1 (per-client) plus the need to know when a window has expired. A bare `Map<String, Integer>`
is not enough: a count with no timestamp cannot tell you whether it belongs to the *current* minute.

```java
class Window {
    int count;
    long windowStart;
}
```

> [!tip] Bucketed key vs. one entry per client — this is the real fork
> **Bucketed key** — `counters.get("alice:" + now / windowMillis)`. A new minute is a new key, so
> expiry needs no code at all. This is the *right* answer in **Redis** (`INCR rl:alice:12345` plus an
> `EXPIRE`), because Redis gives you TTL for free.
> 
> **In a JVM `HashMap` it leaks**: nothing ever deletes the old buckets, so entries pile up one per
> client per minute, forever. Fixing that needs a sweeper thread or a cron — a whole moving part.
> So in-process, keep **one entry per client** carrying `(count, windowStart)` and **reset it lazily
> on access**. No sweeper, no growth per minute. (Same lesson as the TTL follow-up in
> [[01 Thread-Safe LRU Cache Design|LRU Cache]].) If the client set is itself unbounded — anonymous
> IPs — cap the map with LRU eviction.

#### `RateLimitStrategy` — the algorithm seam

From FR-5. One method, and it takes **only the `clientId`**.

```java
interface RateLimitStrategy {
    boolean isAllowed(String clientId);
}
```

> [!tip] Each layer's signature carries only what that layer decides on
> The endpoint and the tier are **routing** data — they choose *which* limiter runs. Once that choice
> is made they are dead information; the algorithm counts requests against a key and nothing else.
> Passing them down anyway would let a strategy start branching on endpoint, which is exactly the
> coupling the interface exists to prevent. **Routing data dies at the routing layer.**

#### `FixedWindowStrategy`

FR-5's first algorithm. Config is **constructor state**, and the per-client counters are private to
*this instance* — the `/login`-free limiter and the `/search`-free limiter must not share counts.

```java
class FixedWindowStrategy implements RateLimitStrategy {
    private final int limit;                                        // 10
    private final long windowMillis;                                // 60_000
    private final Map<String, Window> counters = new HashMap<>();   // NOT thread-safe yet

    public boolean isAllowed(String clientId) {
        long now = System.currentTimeMillis();

        Window w = counters.get(clientId);
        if (w == null) {                             // first request from this client
            w = new Window(now);
            counters.put(clientId, w);
        }

        if (now - w.windowStart >= windowMillis) {   // window expired → start a fresh one
            w.windowStart = now;
            w.count = 0;
        }
        if (w.count < limit) {
            w.count++;
            return true;
        }
        return false;
    }
}
```

> [!bug] The four bugs in the naive version of this body — all four were made on the first pass
> 1. **The reset didn't reset.** `w.count += 1` on expiry instead of `w.count = 0`. Alice hits her
>    limit at 11:00 (`count = 10`), returns at 11:05, the stale branch bumps her to **11** — and she
>    is then rejected forever, because every later window inherits a count already over the limit.
> 2. **Inverted staleness check.** `w.windowStart - now > windowMillis`. `windowStart` is in the past,
>    so that value is always negative and the window never expires. It is `now - w.windowStart`.
> 3. **Off-by-one.** `w.count + 1 < limit` admits **9** requests when the limit is 10 — at `count = 9`
>    it evaluates `10 < 10` → false. The whole check is `w.count < limit`.
> 4. **No first-request path.** `counters.get(clientId)` returns `null` for a client never seen
>    before, so the very first request from anyone throws `NullPointerException`. Create-and-insert
>    before touching the counter.
>
> Naming: the counter field is a **`count`**, not `tokens`. There are no tokens in fixed window —
> reusing the word signals the two algorithms are blurred together in your head.

#### `RateLimiter` — the facade

Routes a request to its configured limiter. The registry is built once at startup.

```java
class RateLimiter {
    private final Map<Rule, RateLimitStrategy> rules;

    public boolean isAllowed(ClientRequest req) {
        RateLimitStrategy strategy = rules.get(new Rule(req.endpoint(), req.tier()));
        return strategy.isAllowed(req.clientId());
    }
}
```

```java
// wiring — one fully-configured instance per rule
rules.put(new Rule("/login",  FREE),       new FixedWindowStrategy(10,   60_000));
rules.put(new Rule("/login",  ENTERPRISE), new FixedWindowStrategy(1000, 60_000));
rules.put(new Rule("/search", FREE),       new TokenBucketStrategy(50, 10));
```

> [!tip] Config is constructor state, not call state
> The tempting alternative is `isAllowed(key, Config)` — pass the limits in per call. It collapses
> immediately: fixed window needs `(N, T)`, token bucket needs `(capacity, refillRate)`, so `Config`
> becomes a union type with half its fields null, *plus* a second map from rule → config that you
> must keep in sync with the strategy map.
> **The registry lookup already is the config lookup.** The map value isn't "a fixed-window
> algorithm", it is *"the 10-per-minute fixed-window limiter"* — already configured. Sentence for
> the room: **"config is constructor state, not call state — the variety lives in the registry,
> not in the method signature."**

---

## 🔒 Concurrency

FR-6 says heavily concurrent, *including several threads on the same key*. The single-threaded body
above has **three** distinct defects. They are not one bug with three names.

### 1. Lost update

`w.count++` looks like one step and is three — read the field, add one, write it back — and a thread
can be suspended between any two of them. `limit = 10`, Alice at `count = 9`:

| time | T1 | T2 | `w.count` in memory |
|---|---|---|---|
| t0 | reads count → **9** | | 9 |
| t1 | | reads count → **9** | 9 |
| t2 | `9 < 10` ✓ | | 9 |
| t3 | | `9 < 10` ✓ | 9 |
| t4 | writes `9+1` = **10** | | 10 |
| t5 | | writes `9+1` = **10** | **10** |
| t6 | returns `true` | returns `true` | |

**Two requests admitted, the counter advanced by one.** T2 read before T1 wrote, so it computed from a
stale base and stamped over T1's result — T1's increment is *lost*.

The damage compounds rather than being a single leaked request: every interleaved pair costs a tick, so
under sustained parallel load Alice's count crawls upward far slower than her true request rate and she
runs over the limit continuously, not just at a boundary.

Rows t2–t3 are the **check-then-act** half — both threads passed a test only one should have passed.
Rows t4–t5 are the **lost update** half. Number for the room: *"with 50 threads at `count = 9`, all 50
read 9, all 50 see `9 < 10`, and I admit 59 requests against a limit of 10."*

### 2. Lost insert

Same shape as a lost update, but what gets dropped is the **map entry**, not the counter — and it only
fires on a client's *first ever* request. The three steps that race:

```java
Window w = counters.get(clientId);   // read
if (w == null) {
    w = new Window(now);             // construct
    counters.put(clientId, w);       // write
}
```

Alice has never been seen, and two of her requests arrive together:

| time | T1 | T2 | map state |
|---|---|---|---|
| t0 | `get("alice")` → **null** | | `{ }` |
| t1 | | `get("alice")` → **null** | `{ }` |
| t2 | builds `Window A` | | `{ }` |
| t3 | | builds `Window B` | `{ }` |
| t4 | `put` → | | `{ alice: A }` |
| t5 | | `put` → | `{ alice: B }` |
| t6 | `A.count++` → A holds **1** | | `{ alice: B }` |
| t7 | | `B.count++` → B holds **1** | `{ alice: B }` |

Two requests went through. The map holds **`Window B`, whose count is 1.** `Window A` is still
reachable from T1's local variable, so T1 cheerfully increments it — into an object nobody will ever
read again.

> [!important] Why this is worse than a lost update, and worth naming separately
> A lost update loses **a single increment**. A lost insert throws away **an entire counter**, and
> every increment T1 performs for the rest of that call goes into an orphan.

**`computeIfAbsent` is a fix only if the map is right.** The one-line form —

```java
Window w = counters.computeIfAbsent(clientId, k -> new Window(now));
```

— is **atomic on `ConcurrentHashMap`**: the mapping function runs at most once for an absent key and
every thread gets back the same instance. On a plain **`HashMap` it buys nothing** — it is `get` plus
`put` with sugar on top, no locking, exactly the interleaving above. So the method name is not the
fix; the map type is. Which is the bridge to defect 3.

### 3. Corruptible map

*→ next.*
