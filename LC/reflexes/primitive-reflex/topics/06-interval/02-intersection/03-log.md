# Interval Atom 02 — Intersection (two lists) · log

| Date | Event | Result |
|---|---|---|
| 2026-06-07 | Announced — Interval List Intersections (986), derivation | ☑ **approach self-derived, Socratic.** Pair-intersection formula `[max(starts), min(ends)]` (self-corrected an initial `min`→`max` on the start, via the `A=[1,8]`,`B=[5,12]`→`[5,8]` pair); the "advance the pointer with the smaller end" rule derived correctly from "can a passed interval be reached again?" |
| 2026-06-07 | Announced — Interval List Intersections (986), code | ☑ AC. **Code written by Claude on request** (two-pointer, `lo<=hi` overlap test, explicit list→array copy by preference), submitted by user. Install grade — code not self-written, so not a cold ownership rep |

**Atom #2 status:** ✅ installed. Approach self-derived, code provided. **No reserved cold rep** — per policy (2026-06-07) zerotrac supplies cold interval problems in the normal grind.

**Key harvest:** the overlap test `lo <= hi` is algebraically *identical* to the symmetric two-interval check `a1<=b2 && b1<=a2`, which is atom #1's `start ≤ end` test generalized to two independent (unsorted-relative-to-each-other) intervals. Computing `[max(starts), min(ends)]` and testing `lo<=hi` does the overlap check and the answer-bounds in one shot. Linear walk works because both lists are sorted → the smaller-end interval is provably finished. Same closed-interval `<=` boundary as merge (point-touches like `[5,5]` count).

**Owned (drill slot, later):** name the move in <5s cold, mixed-order with sibling atoms, 3-day hold.
