# 1550–1600 — Phase 2 Sealed Queue (Derivation / Ownership)

> Rebuilt 2026-05-29. 28 unsolved band problems, biased to **hard (low AR) + multi-bucket**.
> Policy: **no vanilla reps — all disguised** ([[lc-no-vanilla-reps]]). Each solve aims to close 2–3 open buckets at once.
>
> **BLIND-DEAL RULE** ([[lc-blind-deal-protocol]]): on "next", take the next bare link from the DEAL LIST only.
> Do NOT scroll to the ANSWER KEY before solving — it is a SPOILER. Reveal buckets only in the debrief.
> Protocol: 30-min cap (derivation clause: self-derived over-cap AC still counts; first submission must be AC), then cold re-solve.

---

## DEAL LIST (blind — links only)

1. https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/
2. https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/
3. https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-i/
4. https://leetcode.com/problems/encode-number/
5. https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-i/
6. https://leetcode.com/problems/search-suggestions-system/
7. https://leetcode.com/problems/max-chunks-to-make-sorted/
8. https://leetcode.com/problems/sentence-similarity-iii/
9. https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/
10. https://leetcode.com/problems/time-based-key-value-store/
11. https://leetcode.com/problems/count-collisions-on-a-road/
12. https://leetcode.com/problems/longest-substring-of-all-vowels-in-order/
13. https://leetcode.com/problems/properties-graph/
14. https://leetcode.com/problems/score-of-parentheses/
15. https://leetcode.com/problems/count-paths-with-the-given-xor-value/
16. https://leetcode.com/problems/corporate-flight-bookings/
17. https://leetcode.com/problems/k-th-symbol-in-grammar/
18. https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/
19. https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/
20. https://leetcode.com/problems/before-and-after-puzzle/
21. https://leetcode.com/problems/maximize-greatness-of-an-array/
22. https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/
23. https://leetcode.com/problems/find-original-array-from-doubled-array/
24. https://leetcode.com/problems/find-mirror-score-of-a-string/
25. https://leetcode.com/problems/iterator-for-combination/
26. https://leetcode.com/problems/count-number-of-trapezoids-i/
27. https://leetcode.com/problems/number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers/
28. https://leetcode.com/problems/minimum-falling-path-sum/

Mark progress: deal order is fixed (seed 1550); log each in `First-Attempt/` and tick it here after the cold re-solve.

---

<details>
<summary>⚠️ SPOILER — ANSWER KEY (do not open before solving)</summary>

### Per-problem buckets (sorted hardest → easiest by AR)

| AR | Q | Problem | Buckets (mechanic to credit by OUR code) |
|---|---|---|---|
| 35.1% | Q3 | ways-to-split-array-into-good-subarrays | DP (Linear) |
| 35.8% | Q2 | find-mirror-score-of-a-string | Stack (with-string) · Hashing |
| 40.7% | Q2 | count-paths-with-the-given-xor-value | DP (Grid) · Bit · Matrix |
| 40.8% | Q2 | find-original-array-from-doubled-array | Hashing (canonical) · Greedy · Sorting |
| 41.9% | Q2 | count-of-substrings-...-k-consonants-i | Sliding Window · Hashing |
| 43.0% | Q2 | maximum-sum-of-distinct-subarrays-with-length-k | Sliding Window · Hashing |
| 43.5% | Q2 | number-of-ways-where-square-...-product | Two Pointers · Hashing · Math |
| 48.1% | Q2 | count-number-of-trapezoids-i | Combinatorics · Hashing |
| 48.3% | Q1 | k-th-symbol-in-grammar | Bit |
| 48.4% | Q2 | sentence-similarity-iii | Two Pointers (string) |
| 48.8% | Q2 | properties-graph | Union-Find ★ · Graph · Hashing |
| 49.9% | Q2 | time-based-key-value-store | Binary Search · Hashing |
| 51.9% | Q3 | longest-substring-of-all-vowels-in-order | Sliding Window · Two Pointers |
| 51.9% | Q2 | before-and-after-puzzle | Hashing · Sorting |
| 53.5% | Q3 | longest-palindrome-by-concatenating-two-letter-words | Greedy · Hashing |
| 54.3% | Q2 | longest-arithmetic-subsequence-of-given-difference | DP (Linear) · Hashing |
| 56.6% | Q1 | count-the-number-of-incremovable-subarrays-i | Binary Search · Two Pointers |
| 57.7% | Q2 | maximum-points-you-can-obtain-from-cards | Sliding Window · Prefix Sum |
| 58.1% | Q2 | count-collisions-on-a-road | Stack |
| 60.8% | Q3 | minimum-falling-path-sum | DP (Grid) · Matrix |
| 61.7% | Q2 | maximize-greatness-of-an-array | Two Pointers · Greedy · Sorting |
| 63.6% | Q2 | score-of-parentheses | Stack (with-string) |
| 64.2% | Q3 | max-chunks-to-make-sorted | Monotonic Stack ★ · Greedy |
| 65.2% | Q3 | search-suggestions-system | Trie ★ · Heap · Binary Search |
| 66.1% | Q3 | the-earliest-moment-when-everyone-become-friends | Union-Find ★ · Sorting |
| 67.3% | Q2 | corporate-flight-bookings | Segment Tree/BIT · Prefix Sum |
| 70.3% | Q1 | encode-number | Bit |
| 72.7% | Q3 | iterator-for-combination | Backtracking |

### Bucket coverage this queue provides

**Closable in-band (≥3 reps available here):**
- Two Pointers — 5 (#8,12,21,27,5)
- Sliding Window — 4 (#3,9,12,19)
- Stack (plain/string) — 4 (#7,11,14,24)
- Binary Search — 3 (#5,6,10)
- Bit — 3 (#4,15,17)
- DP (Linear/Grid) — 4 (#1,2,15,28) — *note: interval-DP specifically is NOT in this queue; that rep rolls cross-band*
- Hashing (canonical/counting) — many (#3,19,20,22,23,24,26,…)

**Acquire-only here (1–2 reps; ownership completes cross-band):**
- Monotonic Stack ★ — 1 (#7)
- Heap — 1 (#6)
- Trie ★ — 1 (#6)
- Union-Find ★ — 2 (#13,18)
- Backtracking — 1 (#25)
- Combinatorics — 2 (#26,27)
- Segment Tree/BIT — 1 (#16, likely above-level)
- Graph traversal — partial (#13 graph-rep)

</details>
