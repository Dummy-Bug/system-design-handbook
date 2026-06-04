# 1550–1600 — Phase 2 Sealed Queue (Derivation / Ownership)

> Reshuffled 2026-05-31 (fresh random order; 3 dealt problems retired from the pool → 24 remain).
> Policy: **no vanilla reps — all disguised** ([[lc-no-vanilla-reps]]). Each solve aims to close 2–3 open buckets at once.
>
> **BLIND-DEAL RULE** ([[lc-blind-deal-protocol]]): on "next", take the next un-ticked link from the DEAL LIST only.
> Do NOT scroll to the ANSWER KEY before solving — it is a SPOILER. Reveal buckets only in the debrief.
> Protocol: 30-min cap (derivation clause: self-derived over-cap AC still counts; first submission must be AC), then cold re-solve.

---

## DEAL LIST (blind — links only)

> **TRIMMED 2026-06-03:** dropped problems whose mechanic is an already-OWNED bucket (Greedy, Prefix-Sum,
> Sliding Window, Graph, Math/NT-Combinatorics) and that serve no open bucket — owned-topic reps are wasted.
> Dropped: #11, #16, #22, #24, #27 (marked ✂ below). **Undealt remaining: 14** (#9,10,12,13,14,15,17,18,19,20,21,23,25,26).
> **Borderline kept (your call):** #15 maximize-#-subsequences & #25 ways-to-split-string — mechanic is owned
> (Greedy / Combinatorics) BUT both are `Invariant/Reframe` STRONG members, so they're reframe-muscle reps, not
> bucket reps. Kept for derivation value; say the word to drop them too for a maximal trim.

### ▶ ACTIVE DEAL ORDER (re-shuffled 2026-06-03 — deal top-down, blind; position is NOT a tell)
1. https://leetcode.com/problems/score-of-parentheses/
2. https://leetcode.com/problems/number-of-ways-to-split-a-string/
3. https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/
4. https://leetcode.com/problems/k-th-symbol-in-grammar/
5. https://leetcode.com/problems/time-based-key-value-store/
6. https://leetcode.com/problems/maximize-greatness-of-an-array/
7. https://leetcode.com/problems/encode-number/
8. https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/
9. https://leetcode.com/problems/maximize-number-of-subsequences-in-a-string/
10. https://leetcode.com/problems/properties-graph/
11. https://leetcode.com/problems/iterator-for-combination/
12. https://leetcode.com/problems/search-suggestions-system/
13. https://leetcode.com/problems/before-and-after-puzzle/
14. https://leetcode.com/problems/max-chunks-to-make-sorted/

_(The numbered 1-27 list below is retained ONLY for the spoiler answer-key cross-reference — deal from the
ACTIVE order above, not from it.)_

1. ~~https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/~~ ✅ dealt 2026-06-01 (soft fail) → `First-Attempt/28`
2. ~~https://leetcode.com/problems/find-original-array-from-doubled-array/~~ ✅ dealt 2026-06-01 (clean first-AC, over-cap → derivation clause) → `First-Attempt/29`
3. ~~https://leetcode.com/problems/count-collisions-on-a-road/~~ ❌ dealt 2026-06-01 (3 WA → editorial, **hard fail**) → `First-Attempt/30`
4. ~~https://leetcode.com/problems/count-paths-with-the-given-xor-value/~~ ✅ dealt 2026-06-01 (clean first-AC, 46m over-cap → derivation clause) → `First-Attempt/31`
5. ~~https://leetcode.com/problems/sentence-similarity-iii/~~ ❌→✓ dealt 2026-06-01, AC 2026-06-02 (multi-WA → **soft fail**, over-modeled) → `First-Attempt/32`
6. ~~https://leetcode.com/problems/number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers/~~ ✅ dealt+AC 2026-06-02 (clean first-AC, **22m SUB-CAP**; counts) → `First-Attempt/33`
7. ~~https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/~~ ✅ dealt+AC 2026-06-02 (clean first-AC, 34m over-cap → derivation clause; counts). **First clean DP » LIS-variant rep.** → `First-Attempt/34`
8. ~~https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-i/~~ ◐ dealt 2026-06-02, brute AC same day (trivial, no credit); O(n) two-pointer hard-stuck 120m → **slept → clean 26m cold AC 2026-06-03**. SOFT-HINTED (only a "frame-confirmed, one insight left" signal — user didn't read the skeleton/bug) → Two-Pointers **acquisition, not a clean rep**. Consolidation case study. → `First-Attempt/35`
9. https://leetcode.com/problems/max-chunks-to-make-sorted/
10. https://leetcode.com/problems/before-and-after-puzzle/
11. ~~https://leetcode.com/problems/count-number-of-trapezoids-i/~~ ✂ **DROPPED 2026-06-03 — owned topic** (Combinatorics + Prefix-Sum, both ●). Hashing only incidental.
12. https://leetcode.com/problems/iterator-for-combination/
13. https://leetcode.com/problems/encode-number/
14. https://leetcode.com/problems/score-of-parentheses/
15. https://leetcode.com/problems/maximize-number-of-subsequences-in-a-string/
16. ~~https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-i/~~ ✂ **DROPPED 2026-06-03 — owned topic** (Sliding Window ●).
17. https://leetcode.com/problems/k-th-symbol-in-grammar/
18. https://leetcode.com/problems/time-based-key-value-store/
19. https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/
20. https://leetcode.com/problems/properties-graph/
21. https://leetcode.com/problems/maximize-greatness-of-an-array/
22. ~~https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/~~ ✂ **DROPPED 2026-06-03 — owned topic** (Greedy ●). Hashing only incidental.
23. https://leetcode.com/problems/search-suggestions-system/
24. ~~https://leetcode.com/problems/corporate-flight-bookings/~~ ✂ **DROPPED 2026-06-03 — owned topic** (Prefix-Sum/Diff-Array ●; SegTree/BIT is outlier-class).
25. https://leetcode.com/problems/number-of-ways-to-split-a-string/
26. https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/
27. ~~https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/~~ ✂ **DROPPED 2026-06-03 — owned topic** (Sliding Window ●).

> Reshuffled 2026-06-01 (undealt set + 3 new `Invariant/Reframe` members folded in, genuine perl shuffle — position is NOT a tell).

Mark progress: deal top-down; log each in `First-Attempt/` and tick it here after the cold re-solve.

---

## RETIRED (already dealt — do NOT re-deal)

| Dealt | Problem | Result | File |
|---|---|---|---|
| 2026-05-30 07:30 IST | maximum-points-you-can-obtain-from-cards | ✅ clean, first-AC (24m) | `First-Attempt/25` |
| 2026-05-30 10:34 IST | longest-substring-of-all-vowels-in-order | ✅ clean, first-AC (22m) | `First-Attempt/26` |
| 2026-05-30 | find-mirror-score-of-a-string | ❌→✓ WA-then-AC **soft fail** (44m, over cap; does NOT count toward ownership) | `First-Attempt/27` |
| 2026-06-01 | ways-to-split-array-into-good-subarrays | ❌→✓ WA-then-AC **soft fail** (70m, over cap; does NOT count toward ownership) | `First-Attempt/28` |
| 2026-06-01 | find-original-array-from-doubled-array | ✅ **clean first-AC** (49m, over cap → derivation clause; counts toward ownership) | `First-Attempt/29` |
| 2026-06-01 | count-collisions-on-a-road | ❌ **3 WA → editorial, HARD FAIL** (insight-gated; simulation trap). Seeds new ✦ `Invariant/Reframe` bucket. | `First-Attempt/30` |
| 2026-06-01 | count-paths-with-the-given-xor-value | ✅ **clean first-AC** (46m, over cap → derivation clause; counts). **First clean DP » Grid rep.** | `First-Attempt/31` |
| 2026-06-02 | sentence-similarity-iii | ❌→✓ multi-WA → **soft fail** (~2h/2 days; over-modeled with map+deque vs prefix/suffix two-pointer; does NOT count) | `First-Attempt/32` |
| 2026-06-02 | number-of-ways-square-equal-product | ✅ **clean first-AC, 22m SUB-CAP** (count-map not index-map → over-model reflex self-corrected; counts) | `First-Attempt/33` |
| 2026-06-02 | longest-arith-subseq-of-given-difference | ✅ **clean first-AC, 34m over-cap** (fixed-diff ⇒ unique predecessor ⇒ O(n) hash-DP, not classic LIS; counts) | `First-Attempt/34` |

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

### ✦ Invariant / Reframe membership (non-standard bucket — all 83 band editorials adjudicated 2026-06-01)

> Method: read every editorial's approach prose; keep a problem only if the **optimal solution is a
> reframe to a counted/closed-form invariant** AND a **simulation/brute trap exists**. Tool problems
> (Trie/DSU/BIT/heap/mono-stack/DP-table) were excluded even when hard. Tagged **alongside** each
> problem's real mechanism bucket, never instead. SPOILER — reveal only in debrief.

**STRONG (the reframe IS the solution; sim/brute is the trap):**
| Problem | In queue / status | The invariant/reframe |
|---|---|---|
| max-chunks-to-make-sorted | deal #9 | prefix-max == index ⇒ a cut |
| score-of-parentheses | deal #14 | only `()` scores `2^depth`; depth-count, no stack |
| maximize-number-of-subsequences-in-a-string | deal #15 | running count of `pattern[0]`; insert-one ⇒ max(x,y) |
| k-th-symbol-in-grammar | deal #17 | inversion-parity == popcount(k) |
| number-of-ways-to-split-a-string | deal #25 (added) | multiplication principle over the two gap-ranges |
| maximum-value-of-an-ordered-triplet-ii | deal #26 (added) | maintain prefix-max & prefix-max-diff (kills O(n³)) |
| ways-to-split-array-into-good-subarrays | ✅ solved #28 | product of inter-`1` gaps |
| alice-and-bob-playing-flower-game | ✅ solved #23 | `x+y` odd ⇒ win; count parity pairs |
| final-element-after-subarray-deletions | ✅ solved #03 | answer = max(first, last) |
| count-collisions-on-a-road | ❌ solved #30 (seed) | every car that stops = +1 |

**LIGHTER (reframe-flavored / observation-led but shares a mechanism bucket — count as deck reps, low weight):**
| Problem | In queue / status | Observation |
|---|---|---|
| number-of-ways-where-square-...-product | deal #6 | count value-pairs, not index-pairs (+overflow) |
| count-number-of-trapezoids-i | deal #11 | running prefix-sum of per-`y` pair-counts |
| encode-number | deal #13 | `num+1`, drop leading `1` (bijection) |
| ways-to-make-a-fair-array | ✅ solved #17 | deleting `i` swaps odd/even suffix sums |
| maximum-points-you-can-obtain-from-cards | ✅ solved #25-file | k-from-ends == min middle window of `n−k` |
| smallest-all-ones-multiple | ✅ solved #04 | remainder pigeonhole cycle |
| min-cost-to-equalize-arrays | ✅ solved #02 | cancel common, parity check |
| minimum-swaps-to-make-strings-equal | band (unqueued reserve) | count `xy`/`yx` mismatches, parity gate |
| sum-of-numbers-with-units-digit-k | band (unqueued reserve) | `num − n·k ≡ 0 (mod 10)`, enumerate `n` |
| maximum-number-of-operations-to-move-ones | band (unqueued reserve) | running count of `1`s contributes on each `0` |

**Reps this gives the bucket:** 6 STRONG members are live in the blind queue (4 already there + 2 newly
folded in) → they'll surface as genuine `Invariant/Reframe` reps when dealt cold. 4 STRONG already solved
(#03, #23, #28, #30) are retroactive deck members. 3 lighter band problems held in reserve (unqueued) if
more reps wanted later. Remember: **no clean-rep gate — grow & review, never blocks graduation.**

### Trickiness tiers (editorial cross-check — AR alone misleads)

True difficulty = insight the optimal approach needs, not AR. From editorial approach-count + depth:

- **Insight-gated (the trick IS the problem) — train derivation here:** k-th-symbol-in-grammar (recursive-symmetry brain-teaser), count-collisions-on-a-road (brain-teaser), max-chunks-to-make-sorted (prefix-max/chunk insight), the-earliest-moment-...-friends (Union-Find modeling), search-suggestions-system (Trie), corporate-flight-bookings (diff-array/BIT), count-of-substrings-...-k-consonants (exactly-K = atMost(K)−atMost(K−1)), ways-to-split-array-into-good-subarrays (multiplication principle), number-of-ways-where-square-... (product-pair counting + overflow).
- **AR overstates difficulty (low AR = implementation/edge-case pain, not insight):** ways-to-split-array-into-good-subarrays (35%, off-by-one), find-original-array-from-doubled-array (41%, zero/pairing edge cases), find-mirror-score-of-a-string (36%, stack bookkeeping).
- **AR understates difficulty (high AR only because solvers self-select on knowing the pattern):** the-earliest-moment (66%, DSU), corporate-flight-bookings (67%, BIT), search-suggestions (65%, Trie), max-chunks (64%, mono-stack).
- **Stub editorials — verified by reading the problem directly (2026-05-29):** count-paths-with-the-given-xor-value = **moderate, well-disguised Grid-DP** (gate: realize XOR is a bounded 16-value DP dimension; `dp[i][j][x]`, O(m·n·16)) — keep; minimum-falling-path-sum = **LOW / vanilla** textbook grid-DP (`dp[c]=m[r][c]+min(prev[c-1..c+1])`) — **dropped from queue**; iterator-for-combination = **moderate-low** design wrapper over backtracking pre-generation (chars ≤15 → pre-generate all C(n,k)) — keep as only in-band Backtracking seed.

</details>
