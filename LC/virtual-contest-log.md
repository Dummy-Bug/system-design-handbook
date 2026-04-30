# Virtual Contest Log

90-min timed sessions. Past contests only (12+ months old). No spoilers before attempt.

## Rules
- Contest must be **12+ months old** — Weekly 420 or earlier, Biweekly 120 or earlier
- 90 min hard cap, full contest simulation
- Log every problem attempted — solved, stuck, or skipped
- Upsolve only failed problems, Mon-Tue after the session
- Do NOT mix with zerotrac pool

---

## How to use

- **Contest:** name + number
- **Date:** when you ran the virtual
- **Problems attempted:** how many out of total
- **Result:** Q1/Q2/Q3/Q4 — Y (AC) / N (stuck) / S (skipped)
- **Stuck on:** what was the missing insight for each N
- **Upsolve due:** date to upsolve failed problems

---

## Log

### VC #1 — Biweekly Contest 152 (pool violation, doesn't count)
**Date:** 2026-04-29
**Q1 — Unique 3-Digit Even Numbers** ([link](https://leetcode.com/problems/unique-3-digit-even-numbers/description/)) — N, 80 min total, solved on hint (three nested loops).

**What I thought:** combinatorics — split first two slots into oe/oo/ee/eo cases, count each. Got tangled in repeated-digit bookkeeping and kept refining the same broken formula across three sessions.

**What I should have thought:** ~30 min in, when math kept failing, that was the signal to **abandon the frame, not patch it**. Re-read the problem and ask "what other shape could this be?" The shape was enumeration (900 candidates, trivial loop). I never asked the question.

**Takeaway:** 10 min stuck with no forward progress = stop and re-frame. Don't refine a dying approach.

---

## Pool reference

| Pool | Range |
|------|-------|
| Zerotrac | Last ~6 months of contests (newest first) |
| Virtual contest | Weekly ≤ 420 / Biweekly ≤ 120 (12+ months old) |

Start from Weekly 420 / Biweekly 120 and walk **backward** one per Wednesday.
