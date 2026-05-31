# 1550–1600 — Phase 2 Sealed Queue (Derivation / Ownership)

> Reshuffled 2026-05-31 (fresh random order; 3 dealt problems retired from the pool → 24 remain).
> Policy: **no vanilla reps — all disguised** ([[lc-no-vanilla-reps]]). Each solve aims to close 2–3 open buckets at once.
>
> **BLIND-DEAL RULE** ([[lc-blind-deal-protocol]]): on "next", take the next un-ticked link from the DEAL LIST only.
> Do NOT scroll to the ANSWER KEY before solving — it is a SPOILER. Reveal buckets only in the debrief.
> Protocol: 30-min cap (derivation clause: self-derived over-cap AC still counts; first submission must be AC), then cold re-solve.

---

## DEAL LIST (blind — links only)

1. https://leetcode.com/problems/properties-graph/
2. https://leetcode.com/problems/k-th-symbol-in-grammar/
3. https://leetcode.com/problems/iterator-for-combination/
4. https://leetcode.com/problems/max-chunks-to-make-sorted/
5. https://leetcode.com/problems/count-number-of-trapezoids-i/
6. https://leetcode.com/problems/before-and-after-puzzle/
7. https://leetcode.com/problems/maximize-greatness-of-an-array/
8. https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-i/
9. https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/
10. https://leetcode.com/problems/encode-number/
11. https://leetcode.com/problems/count-collisions-on-a-road/
12. https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-i/
13. https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/
14. https://leetcode.com/problems/sentence-similarity-iii/
15. https://leetcode.com/problems/count-paths-with-the-given-xor-value/
16. https://leetcode.com/problems/find-original-array-from-doubled-array/
17. https://leetcode.com/problems/score-of-parentheses/
18. https://leetcode.com/problems/number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers/
19. https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/
20. https://leetcode.com/problems/time-based-key-value-store/
21. https://leetcode.com/problems/corporate-flight-bookings/
22. https://leetcode.com/problems/search-suggestions-system/
23. https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/
24. https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/

Mark progress: deal top-down; log each in `First-Attempt/` and tick it here after the cold re-solve.

---

## RETIRED (already dealt — do NOT re-deal)

| Dealt | Problem | Result | File |
|---|---|---|---|
| 2026-05-30 07:30 IST | maximum-points-you-can-obtain-from-cards | ✅ clean, first-AC (24m) | `First-Attempt/25` |
| 2026-05-30 10:34 IST | longest-substring-of-all-vowels-in-order | ✅ clean, first-AC (22m) | `First-Attempt/26` |
| 2026-05-30 | find-mirror-score-of-a-string | ❌→✓ WA-then-AC **soft fail** (44m, over cap; does NOT count toward ownership) | `First-Attempt/27` |

---

<details>
<summary>⚠️ SPOILER — ANSWER KEY (do not open before solving)</summary>

### Per-problem buckets (sorted hardest → easiest by AR)

| AR | Q | Problem | Buckets (mechanic to credit by OUR code) |
|---|---|---|---|
| 35.1% | Q3 | ways-to-split-array-into-good-subarrays | DP » Count-ways (Linear) |
| 35.8% | Q2 | find-mirror-score-of-a-string | Stack (with-string) · Hashing |
| 40.7% | Q2 | count-paths-with-the-given-xor-value | DP » Grid (XOR-state) · Bit · Matrix |
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
| 54.3% | Q2 | longest-arithmetic-subsequence-of-given-difference | DP » LIS-variant · Hashing |
| 56.6% | Q1 | count-the-number-of-incremovable-subarrays-i | Binary Search · Two Pointers |
| 57.7% | Q2 | maximum-points-you-can-obtain-from-cards | Sliding Window · Prefix Sum |
| 58.1% | Q2 | count-collisions-on-a-road | Stack |
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
- DP — **tracked by sub-pattern, not as one bucket** (20 sub-patterns; each owns separately):
  - DP » Count-ways (Linear) — 1 (#1 ways-to-split)
  - DP » LIS-variant — 1 (#2 longest-arith-subseq)
  - DP » Grid — 1 (#15 count-paths-xor, disguised) · minimum-falling-path dropped (vanilla); 2 more reps roll cross-band
  - DP » Interval/Minimax — **0 in queue** (only solved Stone Game); rolls cross-band
  - DP » String, Knapsack, LCS, Edit-Distance, Bitmask, Digit, Tree-DP ★, Probability — absent at this band
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

### Trickiness tiers (editorial cross-check — AR alone misleads)

True difficulty = insight the optimal approach needs, not AR. From editorial approach-count + depth:

- **Insight-gated (the trick IS the problem) — train derivation here:** k-th-symbol-in-grammar (recursive-symmetry brain-teaser), count-collisions-on-a-road (brain-teaser), max-chunks-to-make-sorted (prefix-max/chunk insight), the-earliest-moment-...-friends (Union-Find modeling), search-suggestions-system (Trie), corporate-flight-bookings (diff-array/BIT), count-of-substrings-...-k-consonants (exactly-K = atMost(K)−atMost(K−1)), ways-to-split-array-into-good-subarrays (multiplication principle), number-of-ways-where-square-... (product-pair counting + overflow).
- **AR overstates difficulty (low AR = implementation/edge-case pain, not insight):** ways-to-split-array-into-good-subarrays (35%, off-by-one), find-original-array-from-doubled-array (41%, zero/pairing edge cases), find-mirror-score-of-a-string (36%, stack bookkeeping).
- **AR understates difficulty (high AR only because solvers self-select on knowing the pattern):** the-earliest-moment (66%, DSU), corporate-flight-bookings (67%, BIT), search-suggestions (65%, Trie), max-chunks (64%, mono-stack).
- **Stub editorials — verified by reading the problem directly (2026-05-29):** count-paths-with-the-given-xor-value = **moderate, well-disguised Grid-DP** (gate: realize XOR is a bounded 16-value DP dimension; `dp[i][j][x]`, O(m·n·16)) — keep; minimum-falling-path-sum = **LOW / vanilla** textbook grid-DP (`dp[c]=m[r][c]+min(prev[c-1..c+1])`) — **dropped from queue**; iterator-for-combination = **moderate-low** design wrapper over backtracking pre-generation (chars ≤15 → pre-generate all C(n,k)) — keep as only in-band Backtracking seed.

</details>
