# Weekly Contest Log

Real LC contests. Every Sunday 8:00-9:30 AM.

## Rules
- 90 min hard cap, full contest simulation
- Log every problem — solved, stuck, or skipped
- Upsolve only failed problems, Mon-Tue after the contest
- Do NOT mix with zerotrac pool

---

## How to use

- **Contest:** name + number
- **Date:** when you ran it
- **Result:** Q1/Q2/Q3/Q4 — Y (AC) / N (stuck) / S (skipped)
- **Stuck on:** missing insight for each N
- **Upsolve due:** date to upsolve failed problems

---

## Log

### Weekly Contest 500
**Date:** 2026-05-04
**Q1 —** [Count Indices With Opposite Parity](https://leetcode.com/problems/count-indices-with-opposite-parity/description/) — Y (suffix count arrays, O(n))
**Q2 —** [Sum of Primes Between Number and Its Reverse](https://leetcode.com/problems/sum-of-primes-between-number-and-its-reverse/description/) — Y (prefix prime sum, static precompute)
**Q3 —** — S (internet lost mid-contest)
**Q4 —** — S (internet lost mid-contest)

**Upsolve due:** —

---

### Weekly Contest 501
**Date:** 2026-05-10
**Q1 —** (not mentioned) — ? 
**Q2 —** [Count Valid Word Occurrences](https://leetcode.com/contest/weekly-contest-501/problems/count-valid-word-occurrences/) — Y (split regex, got lucky — regex only matches space/`--`, doesn't catch all invalid hyphens)
- **Upsolve:** 2026-05-10 (AC) — derived correct character-by-character parsing approach, extracted `isSeparator` predicate, applied 5-step ritual (comprehend → edge cases → decompose → code bottom-up). Key learning: ~1.5 hours total including refactor → need to enumerate edge cases and decompose *before* coding, not after. Accepted.
**Q3 —** [Minimize Array Sum Using Divisible Replacements](https://leetcode.com/contest/weekly-contest-501/problems/minimize-array-sum-using-divisible-replacements/) — N, TLE (initial)
- **Upsolve:** 2026-05-10 (AC) — approach: iterate factors up to √num, add complementary factor num/f. Find smallest factor in array. O(n·√max_val). **Revision approach: sieve — precompute minDivisor[i] for all i ≤ max, O(max·log(max))**.
**Q4 —** — S (didn't attempt)

**Upsolve due:** 2026-05-24

---

### Weekly Contest 502
**Date:** 2026-05-17
**Q1 —** Y (in-contest AC)
**Q2 —** [Count K-th Roots in a Range](https://leetcode.com/problems/count-k-th-roots-in-a-range/) — N, TLE during contest (also MLE on an earlier attempt). 13k+ users AC'd it. Eventually AC'd post-contest.
- **Stuck on:** Did NOT see that final loop `for (int i = l; i <= r; i++) if (set.contains(i)) count++` was the TLE source — l=0, r=10⁹ → 1 billion iterations. Had the right candidates generated in the set (only ~31623 entries for k=2) but didn't trust them — scanned the full [l, r] range to "verify." Patched local bugs (broken `getPower`, then `Math.pow` cast) without ever questioning whether the final scan should exist at all.
- **Misconception that caused it:** Thought 10⁹ Java iterations would AC. Actual Java ceiling is ~10⁸ ops/sec.
- **Upsolve:** 2026-05-17 (AC) — fix is architectural: merge counting INTO the generation loop. No set, no re-scan. Loop bounded by `r^(1/k)` ≤ 31623. Also: never use `Math.pow` for integer powers — floating-point error gives `999999999` instead of `10⁹`. Use long integer multiplication with early-break on overflow.
**Q3 —** S (didn't attempt — Q2 ate the time)
**Q4 —** S (didn't attempt)

**Upsolve due:** 2026-05-31

**Lessons logged separately:**
- `contest/weekly-502-q2-count-kth-roots.md` — full deep dive on the bug pattern + 10⁸ ceiling cheat-sheet + n → complexity table

---
