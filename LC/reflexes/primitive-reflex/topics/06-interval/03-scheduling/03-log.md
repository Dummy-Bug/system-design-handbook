# Interval Atom 03 — Greedy scheduling (sort by end) · log

| Date | Event | Result |
|---|---|---|
| 2026-06-07 | Announced — Non-overlapping Intervals (435), derivation | ☑ **fully self-derived, Socratic.** By-hand answer on `[[1,3],[2,4],[3,5]]`; derived "keep the earlier-finishing interval" as the rule; initially leaned on a merge-style approach (atom #1 carryover) and "start would be sorted anyway", then **ran the `[[1,10],[2,3],[4,5],[6,7]]` trap and saw start-sort-take-first keeps only 1 vs optimal 3** → corrected to sort-by-end; got the `start ≥ lastEnd` touching boundary right |
| 2026-06-07 | Announced — Non-overlapping Intervals (435), code | ☑ AC. **Code provided by Claude on request** (sort by `a[1]` with `Integer.compare`; `lastEnd=MIN_VALUE` seed; count removals), submitted by user. Install grade — code not self-written |

**Atom #3 status:** ✅ installed. Approach self-derived, code provided. No reserved cold rep (zerotrac supplies them).

**Key harvest:** this is the family's first **sort-by-END** atom — the "which endpoint?" question flips. The decision criterion (keep earlier end) and the sort key are the *same* key, which is the whole lesson: the naive start-sort breaks precisely because it sorts by a different key than the one the greedy rule uses. Earliest-finisher greedy is optimal by an exchange argument (no DP needed). `>=` boundary because LC 435 allows touching; Min Arrows (452) is the `>` sibling.

**Carryover caught:** first reached for atom #1's merge reflex on a *selection* problem — corrected by doing the instance by hand. The discriminator (cover→merge / select-max→schedule) is now logged in notes.

**Owned (drill slot, later):** name the move in <5s cold, mixed-order with sibling atoms, 3-day hold.
