# LC Training Log — 1600-1650 band — Second Attempt (Cold Re-solve)

**Why this exists:** Per audit on 2026-05-22, the original 1600-1650 run had 2 confirmed clean ACs (#4, #6), 3 WA-then-AC soft fails (#1, #2, #5), 1 hinted (#7), 1 ambiguous (#3), and skip-3 (only 7/10 done). Under tightened graduation rules in `LC/CLAUDE.md`, the band did not pass. This file logs the cold re-solve of all 7 problems plus 3 new ones on untouched patterns (monotonic stack, binary-search-on-answer, interval DP).

**Protocol per cold re-solve:**
- Close notes / the `First-Attempt/` files. Blank file.
- Read problem fresh. Log thinking step by step (no hints from Claude).
- 5-step ritual must be visible in the log: constraint reading, example trace, edge cases, decomposition, code.
- First-submission AC = clean upgrade. WA-then-AC = soft fail (muscle isn't reflex).
- Debrief after AC (or stuck) — bugs, recurring patterns, lessons.

**Strict accounting target:** ≥7/10 first-submission AC, ≤1/10 hinted across the 10 problems logged here.

---
