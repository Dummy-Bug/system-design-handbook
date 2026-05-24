# Math Reflex — Band 2500+ (Guardian Level)

**143 problems verified** (100% read) · **65 math problems (45.5%)** · Rating range: 2500–3774

---

## Band profile

This is the full Guardian-level pool. 143 problems spanning 2500 to 3774. Math density drops back to 45.5% — above 2500 the non-math problems (advanced graph algorithms, heavy segment-tree DP, string hashing) become harder, not fewer. The math that does appear is the deepest of any band:

- **MOD_ARITH at 27** — by far the highest absolute count of any band. Multinomial combinatorics, Möbius-style GCD counting, generating functions, and large bitmask DP count mod all appear
- **BITMASK at 15** — the largest absolute count since 2200–2299. Guardian-level bitmask DP involves states up to 2×max_value (3181), TSP-style superstrings (3435), and KMP automaton bitmask (1397)
- **MATRIX_EXP at 3** — solidifies as a fixture. String transformation (2851), ball-passing cycle detection (2836), K-multiplication (3266)
- **PERM_COMB at 9** — combinatorics goes deepest here: Catalan-adjacent counting (1977), infection sequences via multinomial (2954), balanced permutations (3343)
- **GCD_LCM at 6** — Möbius inversion (3312), all-GCD subsequences (1819), LCM-graph connectivity (3378)

---

## MOD_ARITH — 27 problems

The full spread of modular arithmetic techniques at Guardian level.

| Problem | Rating | Subtype |
|---------|--------|---------|
| [Count Beautiful Numbers](https://leetcode.com/problems/count-beautiful-numbers/) | 2502 | digit DP, count mod |
| [Final Array State After K Multiplication Operations II](https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-ii/) | 2509 | matrix exp mod — track which element is multiplied at each step |
| [Number of Effective Subsequences](https://leetcode.com/problems/number-of-effective-subsequences/) | 2519 | DP count mod |
| [Minimum Cost to Connect Two Groups of Points](https://leetcode.com/problems/minimum-cost-to-connect-two-groups-of-points/) | 2538 | bitmask DP count mod |
| [Maximum Number of Groups Getting Fresh Donuts](https://leetcode.com/problems/maximum-number-of-groups-getting-fresh-donuts/) | 2559 | bitmask DP on remainder classes mod batch_size |
| [Score of Students Solving Math Expression](https://leetcode.com/problems/the-score-of-students-solving-math-expression/) | 2584 | interval DP with possible result bitmask (set of values ≤ 10×target), mod scoring |
| [Least Operators to Express Number](https://leetcode.com/problems/least-operators-to-express-number/) | 2594 | base-x representation — cost via digit analysis |
| [Minimum Changes to Make K Semi-palindromes](https://leetcode.com/problems/minimum-changes-to-make-k-semi-palindromes/) | 2608 | DP over palindrome cost matrix, mod |
| [Count the Number of Ideal Arrays](https://leetcode.com/problems/count-the-number-of-ideal-arrays/) | 2615 | for each divisor chain of length k, C(n+k-2, k-1) arrangements mod |
| [Count Number of Balanced Permutations](https://leetcode.com/problems/count-number-of-balanced-permutations/) | 2615 | split digits into even/odd positions — C(n,k) × permutations mod (prime factorization of n!) |
| [Minimum Number of Operations to Make String Sorted](https://leetcode.com/problems/minimum-number-of-operations-to-make-string-sorted/) | 2620 | count inversions; each op = leftward shift counted via C(remaining, rank) mod |
| [Sum of Total Strength of Wizards](https://leetcode.com/problems/sum-of-total-strength-of-wizards/) | 2621 | contribution via prefix sum of prefix sums, mod |
| [Count the Number of Infection Sequences](https://leetcode.com/problems/count-the-number-of-infection-sequences/) | 2645 | multinomial: 2^(total_uninfected - gaps) × product of gap-start terms, mod |
| [Find X Value of Array II](https://leetcode.com/problems/find-x-value-of-array-ii/) | 2645 | DP tracking prefix product residues mod x |
| [Sum of Beautiful Subsequences](https://leetcode.com/problems/sum-of-beautiful-subsequences/) | 2647 | DP count mod |
| [Find All Good Strings](https://leetcode.com/problems/find-all-good-strings/) | 2667 | digit DP + KMP automaton + bitmask, mod |
| [Maximum Total Reward Using Operations II](https://leetcode.com/problems/maximum-total-reward-using-operations-ii/) | 2688 | bitmask DP up to 2×max_value; use bitset for O(n²/64) mod |
| [Find Sum of Array Product of Magical Sequences](https://leetcode.com/problems/find-sum-of-array-product-of-magical-sequences/) | 2694 | generating function / DP with multinomial weights mod |
| [Count of Sub-Multisets With Bounded Sum](https://leetcode.com/problems/count-of-sub-multisets-with-bounded-sum/) | 2759 | generating function per distinct value; multiply polynomials with sliding window, mod |
| [Maximize Value of Function in a Ball Passing Game](https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/) | 2769 | matrix exp: follow cycle + tail — binary lifting for 2^k steps, mod |
| [Subsequences with a Unique Middle Mode I](https://leetcode.com/problems/subsequences-with-a-unique-middle-mode-i/) | 2800 | combinatorial formula via prefix counts, mod |
| [Subarrays Distinct Element Sum of Squares II](https://leetcode.com/problems/subarrays-distinct-element-sum-of-squares-ii/) | 2816 | contribution: each element's new-contribution to sum of distinct counts², mod |
| [Number of Ways to Separate Numbers](https://leetcode.com/problems/number-of-ways-to-separate-numbers/) | 2817 | DP with string comparison via LCP array — count valid splits mod |
| [Find All Possible Stable Binary Arrays II](https://leetcode.com/problems/find-all-possible-stable-binary-arrays-ii/) | 2825 | DP mod (harder stable arrays — larger constraints) |
| [String Transformation](https://leetcode.com/problems/string-transformation/) | 2858 | matrix exp: letter-transition count after k transformations mod |
| [Find Products of Elements of Big Array](https://leetcode.com/problems/find-products-of-elements-of-big-array/) | 2859 | bit position counting + prefix products mod — how many times bit i is set across all "powerful arrays" |
| [Maximize the Number of Partitions After Operations](https://leetcode.com/problems/maximize-the-number-of-partitions-after-operations/) | 3039 | bitmask DP over distinct char set, mod |

**2338 (Count Ideal Arrays):** An ideal array has each element dividing the next. For each ending value v, count divisor chains of length ≤ k ending at v. If a chain visits d distinct values, it can be arranged in C(n−1, d−1) ways (choosing where transitions happen among n positions). Sum over all chains: enumerate by factorization depth. This is a stars-and-bars over prime exponent distributions.

**2954 (Infection Sequences):** Between infected segments, uninfected nodes can be infected in any order — but the first uninfected node of each gap must be infected before others. Total free choices = 2^(total_uninfected − number_of_gaps). Then multiply by multinomial for interleaving gap orders. Mod 1e9+7.

**2902 (Sub-Multisets Bounded Sum):** Generating function per distinct element: `(1 + x^v + x^(2v) + ... + x^(cnt·v))`. Multiply all polynomials together — but multiplying naively is O(n×sum). Use the sliding window trick: the geometric series `(1−x^((cnt+1)v)) / (1−x^v)` allows O(sum) per element. GCD of all frequencies guides the structure.

---

## BITMASK — 15 problems

Guardian-level bitmask DP goes beyond 2^15 — several problems here require 2^20 or bitset optimisation.

| Problem | Rating | Angle |
|---------|--------|-------|
| [Minimum Cost to Connect Two Groups of Points](https://leetcode.com/problems/minimum-cost-to-connect-two-groups-of-points/) | 2538 | dp[i][mask] = min cost connecting first i left-points, mask of right-points covered |
| [Find the Maximum Sequence Value of Array](https://leetcode.com/problems/find-the-maximum-sequence-value-of-array/) | 2545 | prefix OR bitmask left, suffix OR bitmask right — find max (left OR) XOR (right OR) |
| [Maximum Number of Groups Getting Fresh Donuts](https://leetcode.com/problems/maximum-number-of-groups-getting-fresh-donuts/) | 2559 | dp[remainder_mask] — remainder classes mod batch_size; groups summing to 0 mod b are happy |
| [Score of Students Solving Math Expression](https://leetcode.com/problems/the-score-of-students-solving-math-expression/) | 2584 | dp[i][j] = set of values students might compute for expr[i..j] — interval DP with value bitmask |
| [Minimum Time to Transport All Individuals](https://leetcode.com/problems/minimum-time-to-transport-all-individuals/) | 2604 | bitmask DP over individual states |
| [Number of Valid Move Combinations On Chessboard](https://leetcode.com/problems/number-of-valid-move-combinations-on-chessboard/) | 2611 | enumerate bitmask of piece-destination pairs; check all non-colliding paths |
| [Make the XOR of All Segments Equal to Zero](https://leetcode.com/problems/make-the-xor-of-all-segments-equal-to-zero/) | 2640 | XOR constraint → period-k positions must share same value; dp[i][xor_so_far] |
| [Find the Minimum Cost Array Permutation](https://leetcode.com/problems/find-the-minimum-cost-array-permutation/) | 2642 | bitmask DP over visited set, track last element |
| [Maximize Grid Happiness](https://leetcode.com/problems/maximize-grid-happiness/) | 2655 | dp[row][introverts_placed_mask][extroverts_placed_mask] — bitmask over last two rows |
| [Find All Good Strings](https://leetcode.com/problems/find-all-good-strings/) | 2667 | digit DP with KMP automaton state + tight constraint |
| [Count Paths That Can Form a Palindrome in a Tree](https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/) | 2677 | XOR of char-count bitmask on root-to-node path; pairs with same or 1-bit-diff bitmask |
| [Maximum Total Reward Using Operations II](https://leetcode.com/problems/maximum-total-reward-using-operations-ii/) | 2688 | dp as a bitset of size 2×max; shift and OR operations on the bitset |
| [Palindrome Rearrangement Queries](https://leetcode.com/problems/palindrome-rearrangement-queries/) | 2780 | bitmask of unmatched chars in query range + LCP for boundary matching |
| [Frequencies of Shortest Supersequences](https://leetcode.com/problems/frequencies-of-shortest-supersequences/) | 3028 | bitmask DP over string overlaps (SCS-style TSP) — find all minimum-length supersequences |
| [Maximize the Number of Partitions After Operations](https://leetcode.com/problems/maximize-the-number-of-partitions-after-operations/) | 3039 | dp[i][char_changed?][current_distinct_mask] — bitmask of chars in current window |

**3181 (Maximum Total Reward):** dp[v] = can we achieve reward v. Process values in sorted order; for each value x, you can add x to any current total < x. This is a bitset shift: new_reachable |= (reachable << shift) & mask. The bitset has size 2×max_value ≈ 10^5, so O(n × max_val / 64) via Java/C++ bitset. The mod constraint on 1e9+7 requires careful handling.

---

## PERM_COMB — 9 problems

Combinatorics at this level involves non-standard identities: Catalan adjacency, multinomial infections, divisor-chain arrangements.

| Problem | Rating | Angle |
|---------|--------|-------|
| [Longest Subsequence Repeated k Times](https://leetcode.com/problems/longest-subsequence-repeated-k-times/) | 2558 | enumerate candidates: only chars appearing ≥ k times matter; check via greedy |
| [Count the Number of Ideal Arrays](https://leetcode.com/problems/count-the-number-of-ideal-arrays/) | 2615 | for each divisor chain of depth d: C(n−1, d−1) ways to stretch over n positions |
| [Count Number of Balanced Permutations](https://leetcode.com/problems/count-number-of-balanced-permutations/) | 2615 | split by even/odd index sums; count via C(count, half_count) × factorial arrangements |
| [Minimum Operations to Make String Sorted](https://leetcode.com/problems/minimum-number-of-operations-to-make-string-sorted/) | 2620 | inversion counting: each op removes one inversion; count via C(remaining_pos, rank) |
| [Count the Number of Infection Sequences](https://leetcode.com/problems/count-the-number-of-infection-sequences/) | 2645 | multinomial: 2^(free_days) × product of (gap_choices), mod |
| [Find Sum of Array Product of Magical Sequences](https://leetcode.com/problems/find-sum-of-array-product-of-magical-sequences/) | 2694 | weighted sum over sequences — generating function approach |
| [Subsequences with a Unique Middle Mode I](https://leetcode.com/problems/subsequences-with-a-unique-middle-mode-i/) | 2800 | for each candidate middle value, count valid configurations via prefix counts + C(n,k) |
| [Number of Ways to Separate Numbers](https://leetcode.com/problems/number-of-ways-to-separate-numbers/) | 2817 | DP counting valid integer sequences; LCP preprocessing ensures O(1) comparison |
| [Frequencies of Shortest Supersequences](https://leetcode.com/problems/frequencies-of-shortest-supersequences/) | 3028 | count all minimum-length supersequences — bitmask + frequency counting |

**2338 (Ideal Arrays):** The deep insight — every ideal array of length n with max value ≤ m corresponds to a weakly-increasing divisor chain (a₁ \| a₂ \| ... \| aₗ). The chain of l distinct divisors can be stretched into an n-length sequence in C(n−1, l−1) ways (choose where each new distinct value starts). Enumerate all chains: factorize each v ≤ m, the number of chains ending at v with l values = number of multiplicative chains of length l to v. Sum over all v and l with C(n−1, l−1).

---

## GCD_LCM — 6 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Minimum Edge Weight Equilibrium Queries in a Tree](https://leetcode.com/problems/minimum-edge-weight-equilibrium-queries-in-a-tree/) | 2508 | LCA + prefix GCD counts on path — find which weight appears most frequently |
| [Count Connected Components in LCM Graph](https://leetcode.com/problems/count-connected-components-in-lcm-graph/) | 2532 | union-find: connect numbers sharing a prime factor (LCM = product/GCD → share prime) |
| [Sorted GCD Pair Queries](https://leetcode.com/problems/sorted-gcd-pair-queries/) | 2533 | Möbius: count pairs with GCD = g using f(g) = #elements divisible by g → C(f(g),2) − inclusion-exclusion |
| [Number of Different Subsequences GCDs](https://leetcode.com/problems/number-of-different-subsequences-gcds/) | 2540 | for each g, check if any subset has GCD = g — O(max × log(max)) sieve |
| [Count the Number of Houses at a Certain Distance II](https://leetcode.com/problems/count-the-number-of-houses-at-a-certain-distance-ii/) | 2709 | sum of distances in circular + linear graph — contribution per distance value |
| [Count of Sub-Multisets With Bounded Sum](https://leetcode.com/problems/count-of-sub-multisets-with-bounded-sum/) | 2759 | GCD of frequencies determines period of generating function |

**3312 (Sorted GCD Pair Queries):** Count pairs (i,j) with GCD = g for each g. Let cnt[g] = number of array elements divisible by g. Pairs with GCD divisible by g: C(cnt[g], 2). By Möbius inversion: pairs with GCD exactly g = C(cnt[g], 2) − Σ pairs_with_GCD_exactly(kg) for k ≥ 2. Precompute all cnt[] in O(n + max log max) via sieve, then invert in O(max log max). Sort all (count_for_g, g) pairs to answer rank queries.

**1819 (Different Subsequences GCDs):** For each possible GCD value g from 1 to max, check if there exists a subsequence with GCD = g. This is true iff the GCD of all multiples of g in the array equals g. Sieve: for each g, find GCD of all a[i] that are multiples of g. O(max log max).

---

## TRICK — 6 problems

| Problem | Rating | The Trick |
|---------|--------|-----------|
| [Substring With Largest Variance](https://leetcode.com/problems/substring-with-largest-variance/) | 2516 | fix which two chars are max/min; run Kadane's variant: track (count_a − count_b) with constraint b appeared ≥ 1 |
| [Maximum Elegance of a K-Length Subsequence](https://leetcode.com/problems/maximum-elegance-of-a-k-length-subsequence/) | 2582 | greedy swap: take top-k by profit; swap lowest repeated-category for a new category — only swap increases elegance |
| [Stamping The Sequence](https://leetcode.com/problems/stamping-the-sequence/) | 2583 | reverse simulation: find a position where the target matches the stamp ignoring "?" cells; stamp backwards |
| [Least Operators to Express Number](https://leetcode.com/problems/least-operators-to-express-number/) | 2594 | write target in base x; cost to form each "digit" block greedily — alternating between multiply-right or sum |
| [Find the K-Sum of an Array](https://leetcode.com/problems/find-the-k-sum-of-an-array/) | 2648 | max sum − (k-th smallest subset sum of absolute values) — min-heap on sorted absolute values |
| [Minimum Cost to Equalize Array](https://leetcode.com/problems/minimum-cost-to-equalize-array/) | 2666 | make all elements equal to max; if cost1 ≤ 2×cost2, just use op1; else use op2 to reduce — parity check on remaining |

**2272 (Substring Largest Variance):** Variance = (count of max char − count of min char). Fix the pair (a, b). Run modified Kadane: track `score = count_a − count_b`, reset when score goes negative AND at least one b has appeared (otherwise we can keep extending). O(26² × n) total.

**2386 (Find K-Sum):** Max subset sum = sum of all positive numbers. The k-th largest subset sum = max_sum − (k-th smallest subset sum formed from absolute values). Sort absolute values ascending. Use a min-heap: start with (smallest_val, index). At each step, pop minimum, push (current + next_val, next_idx) and (current − prev_val + next_val, next_idx). Exactly the "k-th smallest" problem on sorted differences.

---

## PRIME — 6 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Count Connected Components in LCM Graph](https://leetcode.com/problems/count-connected-components-in-lcm-graph/) | 2532 | edges exist between numbers sharing a prime factor — union via prime sieve |
| [Number of Different Subsequences GCDs](https://leetcode.com/problems/number-of-different-subsequences-gcds/) | 2540 | sieve multiples, take GCD over all multiples of g in array |
| [Count Number of Balanced Permutations](https://leetcode.com/problems/count-number-of-balanced-permutations/) | 2615 | factorial mod requires prime factorization of n! for modular inverse |
| [Count the Number of Infection Sequences](https://leetcode.com/problems/count-the-number-of-infection-sequences/) | 2645 | 2^k mod via fast exp; prime structure of gap counts |
| [Maximize Count of Distinct Primes After Split](https://leetcode.com/problems/maximize-count-of-distinct-primes-after-split/) | 2697 | sieve + greedy split point selection |
| [Smallest Divisible Digit Product II](https://leetcode.com/problems/smallest-divisible-digit-product-ii/) | 3101 | digit product divisible by n — factorize n into digits 2–9, greedily extend number |

**3348 (Smallest Divisible Digit Product II):** The product of digits must be divisible by n. Factorize n — if n has a prime factor > 7, it's impossible (no single digit covers primes > 7). Otherwise decompose n into digits from {2,3,4,5,6,7,8,9} (prefer larger digits to minimize digit count). Greedily build the smallest number with at least as many digits as required, and the right digit product.

---

## GEOM — 6 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Find the Minimum Area to Cover All Ones II](https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-ii/) | 2541 | try all 6 ways to partition 3 non-overlapping rectangles; brute force corners |
| [Count Number of Trapezoids II](https://leetcode.com/problems/count-number-of-trapezoids-ii/) | 2643 | count pairs of collinear points with same slope — C(k,2) contribution per slope group |
| [Separate Squares II](https://leetcode.com/problems/separate-squares-ii/) | 2671 | binary search on line position; prefix area computation |
| [Maximum Area Rectangle With Point Constraints II](https://leetcode.com/problems/maximum-area-rectangle-with-point-constraints-ii/) | 2723 | sweep line + BIT: for each right edge, find left edge with no interior points |
| [Maximize the Distance Between Points on a Square](https://leetcode.com/problems/maximize-the-distance-between-points-on-a-square/) | 2806 | binary search on min distance; greedy placement on square perimeter |
| [Check if the Rectangle Corner Is Reachable](https://leetcode.com/problems/check-if-the-rectangle-corner-is-reachable/) | 3774 | circles block path iff they form a connected chain from top/left wall to bottom/right wall — union-find on circle intersections |

---

## CONTRIBUTION — 6 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Maximum Elegance of a K-Length Subsequence](https://leetcode.com/problems/maximum-elegance-of-a-k-length-subsequence/) | 2582 | each distinct category contributes its "novelty bonus" once — contribution of adding a new category |
| [Sum of Total Strength of Wizards](https://leetcode.com/problems/sum-of-total-strength-of-wizards/) | 2621 | each element as min: contribution = (sum of prefix sums in range) × element — prefix-of-prefix sum |
| [Maximum and Minimum Sums of at Most Size K Subarrays](https://leetcode.com/problems/maximum-and-minimum-sums-of-at-most-size-k-subarrays/) | 2645 | monotonic stack: each element contributes as max/min for subarrays of size ≤ k |
| [Minimum Moves to Pick K Ones](https://leetcode.com/problems/minimum-moves-to-pick-k-ones/) | 2673 | median minimises total cost; contribution per 1-position to cost of gathering k ones |
| [Count the Number of Houses at a Certain Distance II](https://leetcode.com/problems/count-the-number-of-houses-at-a-certain-distance-ii/) | 2709 | contribution per distance: linear + shortcut path analysis |
| [Subarrays Distinct Element Sum of Squares II](https://leetcode.com/problems/subarrays-distinct-element-sum-of-squares-ii/) | 2816 | when element x enters window, it contributes 2×(running_distinct_count)−1 squared terms — monotonic stack |

**2281 (Sum of Total Strength):** For each element as the minimum of its range: strength contribution = sum × min, where sum is over all subarrays it's the min of. Using monotonic stack gives left/right bounds. Key: Σ prefix_sum[l..r] over all subarrays with min=A[i] = (prefix_of_prefix[R+1] − prefix_of_prefix[L]) × something. The prefix-of-prefix sum trick reduces O(n²) to O(n).

---

## MATRIX_EXP — 3 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Final Array State After K Multiplication Operations II](https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-ii/) | 2509 | simulate until all elements cycle; detect the cycle position via modular arithmetic |
| [Maximize Value of Function in a Ball Passing Game](https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/) | 2769 | binary lifting: jump[node][k] = node after 2^k passes; answer = sum scores over 2^k hops |
| [String Transformation](https://leetcode.com/problems/string-transformation/) | 2858 | KMP on patterns; transition matrix of letter → letter after one transformation; raise to power k |

**2836 (Ball Passing Game):** Each node has a fixed successor (functional graph). To count score after exactly k passes starting at each node: binary lifting precomputes ancestor[node][j] = node reached after 2^j steps, and sum[node][j] = total score accumulated over 2^j steps from node. Decompose k in binary and combine. O(n log k) precomputation, O(n log k) query.

---

## XOR — 5 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Maximum Genetic Difference Query](https://leetcode.com/problems/maximum-genetic-difference-query/) | 2503 | offline XOR trie: process queries in DFS order, add/remove nodes on path |
| [Make the XOR of All Segments Equal to Zero](https://leetcode.com/problems/make-the-xor-of-all-segments-equal-to-zero/) | 2640 | period-k constraint → elements at same position mod k must share value; dp[i][xor] |
| [Kth Smallest Path XOR Sum](https://leetcode.com/problems/kth-smallest-path-xor-sum/) | 2646 | linear basis on tree path XORs; k-th smallest via basis search |
| [Maximum XOR Score Subarray Queries](https://leetcode.com/problems/maximum-xor-score-subarray-queries/) | 2693 | XOR score of subarray = XOR of all its subarrays' XORs; offline queries + XOR basis |
| [Partition Array for Maximum XOR and AND](https://leetcode.com/problems/partition-array-for-maximum-xor-and-and/) | 2744 | XOR and AND properties on partition — bit-by-bit greedy |

---

## PALINDROME — 4 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Minimum Changes to Make K Semi-palindromes](https://leetcode.com/problems/minimum-changes-to-make-k-semi-palindromes/) | 2608 | precompute cost(i,j,d) = min changes to make s[i..j] d-palindrome; then DP over k parts |
| [Count Paths That Can Form a Palindrome in a Tree](https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/) | 2677 | XOR bitmask of char counts on root-to-node; pair paths with same bitmask or 1-bit difference |
| [Maximum Product of the Length of Two Palindromic Substrings](https://leetcode.com/problems/maximum-product-of-the-length-of-two-palindromic-substrings/) | 2691 | Manacher for palindrome radii; segment tree for max palindrome length up to each position |
| [Palindrome Rearrangement Queries](https://leetcode.com/problems/palindrome-rearrangement-queries/) | 2780 | for each query range, check if unmatched chars (bitmask) can be fixed within the range using rearrangement |

---

## BIT_OPS — 3 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Partition Array for Maximum XOR and AND](https://leetcode.com/problems/partition-array-for-maximum-xor-and-and/) | 2744 | bit-by-bit: greedily maximise XOR then AND |
| [Find Products of Elements of Big Array](https://leetcode.com/problems/find-products-of-elements-of-big-array/) | 2859 | count how many "powerful" numbers have bit i set across all numbers up to X — prefix counting per bit |
| [Minimize OR of Remaining Elements Using Operations](https://leetcode.com/problems/minimize-or-of-remaining-elements-using-operations/) | 2918 | greedy from highest bit: can we zero out bit b? If yes, do it and move to next |

---

## GAME_THEORY — 2 problems

| Problem | Rating | Angle |
|---------|--------|-------|
| [Cat and Mouse](https://leetcode.com/problems/cat-and-mouse/) | 2567 | BFS game DP from terminal states backwards — mouse wins if it reaches node 0, cat wins if it catches mouse |
| [Cat and Mouse II](https://leetcode.com/problems/cat-and-mouse-ii/) | 2849 | minimax DP on (mouse_pos, cat_pos, turn, moves_remaining) — harder variant |

---

## One-offs

| Topic | Problem | Rating | Insight |
|-------|---------|--------|---------|
| DIGIT_OPS | [Count Beautiful Numbers](https://leetcode.com/problems/count-beautiful-numbers/) | 2502 | digit DP with divisibility tracking |
| DIGIT_OPS | [Find Products of Elements of Big Array](https://leetcode.com/problems/find-products-of-elements-of-big-array/) | 2859 | bit counting across huge number ranges |
| AP_SUM | [Minimum Cost to Equalize Array](https://leetcode.com/problems/minimum-cost-to-equalize-array/) | 2666 | target = max element; arithmetic formula for ops |
| AP_SUM | [Minimum Moves to Pick K Ones](https://leetcode.com/problems/minimum-moves-to-pick-k-ones/) | 2673 | sliding window median + prefix sum of positions |
| TRIPLE_COUNT | [Count Number of Trapezoids II](https://leetcode.com/problems/count-number-of-trapezoids-ii/) | 2643 | pairs of parallel sides = pairs of collinear point-pairs with same slope |
| STARS_BARS | [Count of Sub-Multisets With Bounded Sum](https://leetcode.com/problems/count-of-sub-multisets-with-bounded-sum/) | 2759 | generating function = product of geometric series per element value |

---

## Complete cross-band summary (all bands)

| Band | Problems | Math % | Top topic | Key new technique |
|------|----------|--------|-----------|-------------------|
| 1100–1399 | 724 | 39% | SUM_ARITH | Parity, digit ops basics |
| 1400–1499 | 214 | 38% | MOD_ARITH | Contribution, prime factorization |
| 1500–1599 | 195 | 40% | GEOM | Geometry rises, XOR prefix |
| 1600–1699 | 187 | 35% | GEOM | Pair count, GCD rises |
| 1700–1799 | 186 | 38% | GEOM | Bitmask emerges |
| 1800–1899 | 165 | 47% | MOD_ARITH | Bitmask consolidates, Matrix exp hinted |
| 1900–1999 | 134 | 46% | MOD_ARITH | Catalan, AP_SUM in binary search |
| 2000–2099 | 160 | 53% | MOD_ARITH | Contribution explodes, Stone Games cluster |
| 2100–2199 | 102 | 47% | MOD_ARITH | Prime cluster, Stars-and-bars |
| 2200–2299 | 107 | 67% | MOD_ARITH | Bitmask peak, GCD connectivity |
| 2300–2399 | 93 | 59% | MOD_ARITH | XOR linear basis, Stirling numbers |
| 2400–2499 | 78 | 55% | MOD_ARITH | Matrix exp debut, Square-free bitmask |
| 2500+ | 143 | 46% | MOD_ARITH | Generating functions, Möbius inversion, Bitset DP |

---

## Drill plan for Guardian level

**What actually differentiates Guardian from 2200:**

1. **Generating functions / polynomial multiplication** (2902) — geometric series per element, sliding window on polynomial coefficients. Not a standard template; requires deriving the approach from scratch.

2. **Möbius inversion** (3312, 1819) — counting exact-GCD pairs via inclusion-exclusion over multiples. The key formula: `exact(g) = C(cnt[g], 2) − Σ exact(k×g)`. Implement once, applies to all GCD-counting problems.

3. **Binary lifting with values** (2836, 1483) — not just ancestor[node][k] but also sum[node][k] accumulated over 2^k hops. One derivation covers ball-passing (2836) and all ancestor-query problems.

4. **Bitset-optimised bitmask DP** (3181) — when bitmask size exceeds 30 bits, use Java BitSet. Shift + OR instead of explicit iteration. The maximum-reward problem (3181) has masks of size 2×max_val = 2×10^5 — only bitset makes this feasible.

5. **Divisor chain counting** (2338) — the "ideal arrays" pattern: multiplicative chains of divisors arranged via C(n−1, d−1). This requires enumerating chains by factorization depth, not just iterating over divisors.

**Skip entirely (implementation-only at Guardian level):** 936 (stamping sequence — 100% simulation), 770 (calculator IV — polynomial expression parsing), 1982 (find array from subset sums — divide and conquer, rare).
