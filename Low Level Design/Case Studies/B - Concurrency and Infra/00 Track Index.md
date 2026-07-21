> [!abstract] Track B — Concurrency / Infra
> Flavor B builds: 45-60 min each, interleaved with the flavor-A case studies.
> Where "concurrency answer ready" stops being a talking point and becomes code.

| # | Build | Mechanic payload | Status |
|---|-------|------------------|--------|
| B1 | Rate Limiter | token bucket + sliding window behind one Strategy; atomic refill | ☐ |
| B2 | **Circuit Breaker** | **State flagship** (CLOSED/OPEN/HALF_OPEN), threshold + cooldown | ☐ |
| B3 | Retry / fallback chain | exponential backoff + jitter, fallback ordering, budget cap | ☐ |
| B4 | Health tracker | EWMA over a ring buffer, healthy/degraded/unhealthy transitions | ☐ |
| B5 | Thread-safe LRU cache | map + list under one lock, or striped locks; eviction race | ☐ |

Primitives to reach for cold: `synchronized` vs `ReentrantLock`, `Semaphore`,
`AtomicInteger`/CAS, `ConcurrentHashMap.compute`, `ScheduledExecutorService`.

**Assembly target** once B1-B4 exist: **LLM request router** (registry + limiter + health +
retry/fallback + breaker) — Emergent's own published practice problem.

> [!warning] The line every source grades
> Release a reserved resource on **failure and timeout**, not just on success.

---

## B2 — the reported Emergent variant

> [!note] Provenance: candidate reports + third-party research, **not verified first-hand**
> Treat the exact thresholds as illustrative. The *shape* — sliding-window error rate driving
> state, each state routing traffic by percentage — is what matters and is consistent across
> sources.

An **LLM orchestrator circuit breaker** sitting between clients and two model providers:

| State | Trigger | Routing |
|---|---|---|
| `NORMAL` | error rate < 5% | 100% → Claude |
| `DEGRADED` | error rate ≥ 5% | 95% → OpenAI, 5% → Claude as a probe |
| `TRIPPED` | error rate ≥ 90% | 90% fail fast, 5% → Claude, 5% → OpenAI as probes |

Two mechanics this forces, both worth owning:

**1. Sliding-window error rate** — a timestamped event queue, evicting anything older than the
window on each read. Not a lifetime counter: a service that failed hard an hour ago and has been
healthy since must be allowed back to `NORMAL`.

**2. Stateless percentage routing** — `abs(H(requestId)) % 100`, then map ranges to
destinations. Deterministic, needs no shared counter, and stays consistent across nodes.
The naive answer is `Random` or a global `synchronized` counter; both contend, and the counter
also breaks the moment there's more than one node.

Patterns that fall out: **State** (one class per state, each owning its routing rule) +
**Strategy** (one per provider). The state transition itself is a threshold check on the window
— keep it in one place, not scattered across the state classes.
