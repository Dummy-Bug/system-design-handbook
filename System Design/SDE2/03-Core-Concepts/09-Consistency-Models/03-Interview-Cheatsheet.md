# Interview Cheatsheet — Consistency Models

> [!question] When does consistency come up in an interview?
> Every time you add replication or multiple nodes. The interviewer will ask "what consistency model does your system need?" — this is your answer.

---

## The Spectrum — Memorize This

```
Strictest ──────────────────────────────────────── Loosest

Linearizable → Strong → Causal → Monotonic → Read-Your-Writes → Eventual

Each level includes all guarantees of the levels to its right.
```

---

## One Line Per Model

```
Eventual          → replicas converge eventually, no ordering guarantee
Read-Your-Writes  → you always see your own writes
Monotonic Reads   → time never goes backwards for a user
Causal            → causally related operations seen in correct order by everyone
Strong            → every read sees the latest write (quorum)
Linearizable      → strong + real wall-clock time ordering (atomic clocks)
```

---

## The Decision Question

> *"What is the cost of showing stale data?"*

```
Nothing          → Eventual
Jarring for user → Read-Your-Writes / Monotonic
Breaks logic     → Causal
Costs money      → Strong
Legal impact     → Linearizable
```

---

## Moment 1 — "What consistency model does your system need?"

Pick the model, justify the cost of staleness, mention the availability tradeoff:

*"For the feed I'd use eventual consistency — like counts being off by a few is acceptable, and we need maximum throughput at scale. For user's own profile I'd add read-your-writes — you must see your own posts immediately or it feels broken. For messages I'd use causal consistency — replies must appear after originals, but full strong consistency would hurt availability for users on poor networks."*

---

## Moment 2 — "Why not just use strong consistency everywhere?"

*"Strong consistency requires quorum — every write waits for a majority of replicas to confirm before returning success. At Instagram's scale — billions of likes per day — that latency cost is unacceptable. For the feed, eventual consistency gives us maximum throughput with acceptable staleness. Strong consistency is reserved for operations where staleness has real cost — bank transfers, payments."*

---

## Moment 3 — "What's the difference between strong consistency and linearizability?"

*"Strong consistency means every read sees the latest write — all nodes agree on the same value. Linearizability adds real wall-clock time ordering — the system's internal ordering must match actual real time. This matters when multiple systems need to agree on the exact moment something happened. Google Spanner achieves this with atomic clocks and GPS receivers. Most systems don't need linearizability — strong consistency is sufficient."*

---

## System → Model Quick Reference

| System | Model |
|---|---|
| Social feed, like counts | Eventual |
| Shopping cart | Eventual |
| Your own profile/posts | Read-Your-Writes |
| Timeline, news feed ordering | Monotonic Reads |
| Chat messages, comments | Causal |
| Bank balance, payments | Strong |
| Global financial systems | Linearizable |

---

## The Availability Connection

> [!important] Always mention the availability tradeoff when choosing consistency

```
Eventual      → maximum availability, works during partition
Causal        → available, partition only affects ordering
Strong        → may be unavailable during partition (waits for quorum)
Linearizable  → strictest availability requirements
```

*"I'd use causal for WhatsApp — replies appear after originals, but system stays available for 2 billion users even on poor networks. Linearizability would mean going down during any network partition, which is unacceptable."*

---

## Full Checklist

- [ ] Named the specific consistency model — not just "consistent" or "eventually consistent"
- [ ] Justified the choice — what does staleness cost in this system?
- [ ] Mentioned the availability tradeoff — stricter = less available
- [ ] Used read-your-writes for user-facing write-then-read scenarios
- [ ] Used causal for messaging/comment systems
- [ ] Used strong for financial operations
- [ ] Did NOT say "strong consistency everywhere" without justification

---

## Quick Reference

```
The spectrum (strictest → loosest):
  Linearizable → Strong → Causal → Monotonic → Read-Your-Writes → Eventual

Real world mapping:
  Amazon cart      → Eventual
  Instagram feed   → Eventual
  Own Instagram    → Read-Your-Writes
  Twitter timeline → Monotonic Reads
  WhatsApp chat    → Causal
  Bank balance     → Strong
  Google Spanner   → Linearizable

Availability tradeoff:
  Looser model  → higher availability, works during partition
  Stricter model → lower availability, may block during partition

The interview trap:
  Don't say strong consistency everywhere
  Always justify based on cost of staleness
```
