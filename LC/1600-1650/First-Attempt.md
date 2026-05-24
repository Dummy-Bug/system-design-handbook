# LC Training Log — 1600-1650 band

Protocol: see `zerotrac.md`. Graduated from 1550-1600 on 2026-05-07 (10/10 first-try AC, derivation-over-speed clause applied — see `CLAUDE.md`).

### #1 — Word Squares II

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/word-squares-ii/description/ |
| Rating | 1606 |
| AC | Y |
| Time | 40min |
| Pattern | brute force / combinatorial search |
| Revision due | 2026-05-22 |
| Remark | Self-derived with WA debugs on sorting. Approach: 4 nested loops over all word combos, check word-square condition (word[i][j] == word[j][i] across all chosen words). Key sorting insight — `String.join("", list).compareTo(...)` cleaner than `toString()`. Complexity: O(n^k) where n is word count, k is grid size. |

---

### #2 — Split Array with Minimum Difference

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/split-array-with-minimum-difference/ |
| Rating | 1649 |
| AC | Y |
| Time | 120min |
| Pattern | two-pointer / greedy validation |
| Revision due | 2026-05-22 |
| Remark | Self-derived with WA edge case debugs. Insight: for each split position i, check if nums[0..i] strictly increasing AND nums[i+1..n-1] strictly decreasing via on-the-fly validation (no extra boolean arrays). Key gotcha — boundary conditions at split point and when entire array is increasing/decreasing. Complexity: O(n^2) time (n positions × O(n) validation per position), O(1) space. |

---

### #3 — House Robber V

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/house-robber-v/description/ |
| Rating | 1619 |
| AC | Y |
| Time | 60min |
| Pattern | DP — state definition + T(C) derivation + space optimization |
| Revision due | 2026-05-22 |
| Remark | First DP in years. Derived state definition `dp[i] = max money from houses 0 to i` from constraints. Calculated T(C): exponential without memo (2^n like Fibonacci tree), O(n) with memo (n states × O(1) work). Top-down → bottom-up → O(1) space via rolling vars (first, second). Integer overflow bug: used int[] instead of long[] for sum up to 10^10. |

---

### #4 — Count Caesar Cipher Pairs

| Field | Value |
|-------|-------|
| Date | 2026-05-11 |
| Link | https://leetcode.com/problems/count-caesar-cipher-pairs/ |
| Rating | 1624 |
| AC | Y |
| Time | 55min |
| Pattern | Caesar cipher / MOD normalization |
| Revision due | 2026-05-25 |
| Remark | Insight — normalize each word relative to first char using `(offset - ref + MOD) % MOD` to detect identical shift patterns. HashMap counts matching normalized forms, pairs increment by prior count. Key gotcha — MOD formula handles wraparound for backward shifts. Complexity: O(n·m) time (n words, m avg length), O(n·m) space (normalized strings in HashMap). |

---

### #5 — Minimum Discards to Balance Inventory

| Field | Value |
|-------|-------|
| Date | 2026-05-12 |
| Link | https://leetcode.com/problems/minimum-discards-to-balance-inventory/description/ |
| Rating | 1639 |
| AC | Y |
| Time | 60min |
| Pattern | Sliding window / frequency threshold |
| Revision due | 2026-05-26 |
| Remark | Self-derived with WA edge case debugs. Insight — slide window over possible frequency thresholds (1 to max freq). For each threshold, count items with frequency > threshold (these must be discarded). Find threshold minimizing total discards. Key gotcha — edge cases around when no discards needed vs all items discarded. Complexity: O(n log n) time (sort frequencies, slide window), O(n) space (frequency map). |

---

### #6 — Sum of Digit Differences of All Pairs

| Field | Value |
|-------|-------|
| Date | 2026-05-12 |
| Link | https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/description/ |
| Rating | 1645 |
| AC | Y |
| Time | 55min |
| Pattern | Digit position iteration / frequency counting |
| Revision due | 2026-05-26 |
| Remark | Self-derived, no gotchas during 15-min coding. 40 min spent deriving O(n·d) approach from first principles. Key insight: iterate each digit position separately. For each number at position j, count how many *previous* numbers (0 to j-1) have same digit — contribution = (j+1) - count. Incremental accumulation avoids formula approach's division-by-2 trap. Complexity: O(n·d) time (n numbers, d digit positions), O(1) space (at most 10 digits per position). |

---

### #7 — Identify the Largest Outlier in an Array

| Field | Value |
|-------|-------|
| Date | 2026-05-13 |
| Link | https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/ |
| Rating | 1644 |
| AC | Y (hinted) |
| Time | 135min (2h 15m) |
| Pattern | HashMap lookup / algebraic rearrangement |
| Revision due | 2026-05-27 |
| Remark | **First hinted pass in this band.** Spent 60+ min stuck on wrong approach (tracking max/second-max with absolute values). Hint received — "convert O(n²) brute force to O(n) lookup via algebra." Self-derived the math: tSum = 2·sum_element + outlier → sum_element = (tSum - outlier)/2. So for each outlier candidate, target value is determined; just check existence. Key bug — used Set, but when target == outlier_value, need frequency ≥ 2 (distinct indices required). Failing test: `[1,2,4,5]` returns 4 (fake) instead of 2 (real) because 4 = tSum/3 appears once. Fix: frequency map. Complexity: O(n) time, O(n) space. |

---

## Lessons learned from #7 (2026-05-13)

**Diagnosed gap:** edge cases are the #1 reason for WA on 1600+ problems. Not because I don't know how to handle them — because I don't *flag* them while reading the problem. The outlier problem statement literally said "distinct indices, but may share the same value" — and I read past it without registering it as a Set-vs-Map flag.

**Habit to install: decide the approach BEFORE coding, including edge cases.** Don't start writing the orchestrator and discover edge cases via WA on submit. The 5-step ritual in `CLAUDE.md` exists for this — actually use it.

### Edge case detection checklist (apply during step 3 of the 5-step ritual)

Run this on every problem before touching the keyboard:

1. **"Distinct indices" trigger.** If the problem says "distinct indices, may share values" (or variant) → **frequency map, NOT set**. The author is screaming the bug exists.
2. **Self-reference check.** When iterating `i` and looking up `f(nums[i])`, ask: "Can the lookup return `nums[i]` itself?" → edge case branch.
3. **Cardinality check.** Before using a Set, ask: "Do I care *whether* X exists, or *how many times*?" Default to frequency map unless duplicates explicitly ruled out.
4. **Algebraic collision check.** For derived values (target, complement, sum-minus-X), ask: "Can computed `target` accidentally equal `nums[i]`?" → distinct-index check required.
5. **Constraint keyword scan.** Search problem statement for: "distinct", "unique", "may be equal", "may share", "at least one". Each is a loaded flag.
6. **Adversarial test construction.** Before submitting, spend 5 min constructing the test most likely to break your solution. Derive backwards from the bug condition algebraically — don't guess arrays, *solve* for them.

### Pre-submit ritual

Answer two questions out loud before clicking submit:
1. "Where could my lookup return the same element I'm iterating on?"
2. "What's the most adversarial valid input I can construct that satisfies my bug condition?"

### Post-problem ritual (after AC)

Write one line: *"What pattern did this problem test, and what was the trigger keyword in the problem statement?"*

For #7: *"Distinct indices, may share values → frequency map, not set. Trigger: 'distinct indices, but may share the same value.'"*

**Goal:** build a trigger → pattern dictionary across 30+ problems so edge cases become reflexive, not learned-by-WA.

### Algebraic-thinking principle (also from #7)

When constructing failing test cases or spotting edge cases, **don't guess inputs and check** — **solve for inputs that satisfy the constraint**. Strong solvers do this naturally:

> "I want X to happen. What constraint does X impose? Solve for inputs that satisfy it."

Example from this problem: "I want target == nums[i]. Constraint: nums[i] = tSum/3. Pick valid array with one element = tSum/3 appearing once → `[1, 4, 5, 2]` (tSum=12, value 4 = 12/3)."

---
