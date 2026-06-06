# Stack Atom 07 — Min/max auxiliary stack · log

| Date | Event | Result |
|---|---|---|
| 2026-06-06 19:05 | Announced — Min Stack (155) | ◐ **recalled** (not cold). Reproduced both forms: two-stack with `<=` push to min-stack (duplicate-min trap), and the cleaner single-stack of `(val, minSoFar=min(val, prevTop.min))` — getMin = top.min, pop needs zero extra logic. Submittable single-stack version written. Min/max stack is **not a blind-spot**, so recall is fine; no cold rep gated |
| 2026-06-06 | Detour — Max Frequency Stack (895) (deferred) | ✓ **conceptual harvest only** (not coded as the rep). Surfaced the load-bearing limit of the lockstep cache: it works **only** when pop removes the **top** and the query is **read-only**. 895's pop removes the **max-frequency** (buried) element and **mutates** freqs → cache goes stale + can't extract a middle node → fix = **bucket-by-frequency** (group: freq→stack, O(1)) or PQ `(freq desc, seq desc)` (O(log n)). PQ + group code drafted in chat |
| — | Disguised — Max Frequency Stack (895) | ⏸ **deferred** — design problem, revisit later; its lesson already captured |

**Atom #7 status:** core installed via Min Stack (recalled). The atom = *carry an aggregate (min/max) in lockstep with the stack*; valid because pop is top-only and getMin is read-only. Bonus boundary lesson from 895: when pop targets a non-top / mutates the aggregate, lockstep breaks → bucket-by-key. **895 deferred** (interview-flavored design problem, low contest value).

**Owned (drill slot, later):** name in <5s cold, mixed-order, 3-day hold.
