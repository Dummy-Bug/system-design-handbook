# Interval Atom 01 — Merge / union · log

| Date | Event | Result |
|---|---|---|
| 2026-06-07 | Announced — Merge Intervals (56), derivation | ☑ **fully self-derived, Socratic, no hints, no wrong attempts.** Produced the by-hand answer, the fuse condition (`next.start ≤ prev.end`), the `max` fused-end (caught the swallow case on `[1,8]`+`[2,5]`), the sort-by-start necessity (from the shuffled-set break), and the start-tie irrelevance (`max` absorbs order) — each on the first Socratic prompt |
| 2026-06-07 | Announced — Merge Intervals (56), code | ☑ AC, **first submission, self-written.** Cleanups noted (not WAs): `remove+re-add` → in-place `cur[1]` mutation; `a[0]-b[0]` → `Integer.compare` overflow habit. Approach was *scaffolded by Socratic questioning* → acquisition-grade install, NOT a cold ownership rep |
| 2026-06-07 | Perturbation | ✓ load-bearing = **closed-interval touch-merge** (`<=` not `<`). `[1,5]`,`[5,10]` is legal and must fuse to `[1,10]`. Generalized: "does endpoint-touch count as overlap?" is a family-wide bit that also sets sweep-line event tie-ordering and scheduling conflict tests |

**Atom #1 status:** ✅ installed. Announced rep self-derived (no hints/WA), scaffolded by Socratic Q&A. **No reserved cold rep** — per policy (2026-06-07) zerotrac supplies plenty of cold interval problems in the normal grind, so recognition gets exercised there rather than via a held-back blind deal.

**Key harvest:** sort-by-start is the *enabler*, not the algorithm — it's what collapses "compare against all previous" to "compare against the running tail." The fused end is `max` (swallowing); `cur.start` is immutable. Merge is the first answer to the family's only question: **which endpoint do I sort by? → start → combine.**

**Born from:** Biweekly 184 Q2 (min-energy bulbs) — interval-union was a decayed reflex (~1 yr since last interval problem), cost ~47 min on a ~12-min problem. This atom closes that decay.

**Owned (drill slot, later):** name the move in <5s cold, mixed-order with sibling atoms, 3-day hold.
