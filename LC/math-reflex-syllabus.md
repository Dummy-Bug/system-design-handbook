# Math Reflex Syllabus for LC (1400 → Guardian)

## Why this exists

You love math but started hating it because you sucked at it. The 20-min derivation on `n(n-1)/2` during Caesar Cipher Pairs is the symptom: facts that should be reflex are being re-derived from scratch every time. This costs 10-30 min per problem and kills contest performance.

This syllabus is the cure. Every topic is tied to a specific LC problem so each fact you learn unlocks a concrete capability — no abstract math for its own sake, ever.

## How to use this

1. **Only learn the band you're currently at — or one stretch above.** No looking ahead. Band 1900 math is useless if you can't solve Band 1500 yet.
2. **Each band = minimum required to start solving at that level.** Not "nice to have" — actually needed.
3. Each topic has: **(a) the fact**, **(b) WHY it matters**, **(c) a concrete LC problem that needs it**.
4. **Socratic drill protocol per topic:**
   - Claude poses a tiny problem that needs the fact
   - You derive (or recognize) the answer
   - Then I show the formula and the LC problem(s)
   - Mark ✓ after 2-3 problems confirm the reflex is installed
5. **Graduate to next band only when all topics in current band are ✓.**

## Personal context

- Current contest rating: ~1500. Sometimes Q1 (1300-1500 rated) is missed.
- 1-year target: 1700 contest rating by Q1 2027.
- Practice zerotrac band on cold re-solve (2026-05-23): backfilling 1600-1650 under tightened rules.
- Math reflex training is the **parallel track** to the zerotrac grind — runs alongside, not instead of.

---

# Band 1400 — Anchor (must have to attempt anything)

**Why this is the floor:** Your contest rating is 1500. Some Q1s slip. Band 1400 = absolute baseline math that even an easy Q1 requires.

## 1.1 — Pair count formula
**Fact:** Number of unordered pairs from n elements = `n(n-1)/2`.
**Why:** "Count pairs (i,j) with i<j and some property" is one of the most common LC patterns.
**LC problems:**
- *Count Number of Pairs With Absolute Difference K* (LC 2006)
- *Number of Pairs of Strings With Concatenation Equal to Target* (LC 2023)
- *Count Equal and Divisible Pairs in an Array* (LC 2176)

## 1.2 — Triangular sum
**Fact:** `1 + 2 + ... + n = n(n+1)/2`.
**Why:** Appears in "minimum operations" problems, "build pyramid" problems, range sum questions.
**LC problems:**
- *Sum of Even Numbers After Queries* (LC 985)
- *Minimum Operations to Make Array Equal* (LC 1551)

## 1.3 — Complexity reflex (1400 baseline)
**Facts:**
- `n ≤ 10⁵` → O(n log n) safe, O(n²) = TLE (10¹⁰ ops > 10⁸ budget)
- `n ≤ 10³` → O(n²) safe
- `n ≤ 10` → O(n!) brute permutation OK
- ~10⁸ simple ops/sec is the typical 1-sec budget on LC

**Why:** Looking at the constraint tells you what algorithm budget you have. Without this, you'll either pick TLE solutions or over-engineer.

## 1.4 — Integer overflow (1400 baseline)
**Fact:** `int` range is ~±2.1×10⁹ (about 2 billion). If any intermediate product or sum could exceed this, cast to `long`.
**Why:** LC routinely has constraints like `nums[i] ≤ 10⁹` and `n ≤ 10⁵`. Multiplying two such values = 10¹⁸ — overflows int silently.
**LC problems:**
- *Maximum Subarray Sum* — if values are 10⁹ and n is 10⁵, sum is 10¹⁴, overflow.
- Any "product of two ints" problem.

## 1.5 — Mod basics
**Fact:** "Output mod 10⁹+7" is everywhere. Why this constant: it's prime, large, and `(prime - 1) × (prime - 1)` fits in long.
**Operations:** `(a+b) % m`, `(a*b) % m` — both distribute. Apply mod at every step to avoid overflow.
**LC problems:**
- *Climbing Stairs IV* and other counting-with-mod problems

## 1.6 — Parity
**Fact:** Sum of even count of odd numbers = even. Sum/diff of two ints has fixed parity based on inputs.
**Why:** "Can you reach X exactly?" often reduces to a parity check.
**LC problems:**
- *Sum of Two Integers* (LC 371)
- Many "can the operation reach target" problems

## 1.7 — Digit operations
**Facts:**
- Digit count of n: `Long.toString(n).length()` or `(int) Math.log10(n) + 1`
- Sum of digits: `while (n > 0) { sum += n % 10; n /= 10; }`
- Reverse digits: `while (n > 0) { rev = rev*10 + n%10; n /= 10; }`
**LC problems:**
- *Add Digits* (LC 258)
- *Reverse Integer* (LC 7)
- *Sum of Digits of String After Convert* (LC 1945)

---

# Band 1500 — Solve Q1 reliably

**Why this band:** Your contest rating is 1500 — this matches Q2 difficulty. Q1 should be effortless once these facts are reflex.

## 2.1 — Power of 2 anchor
**Fact:** `2^10 = 1024 ≈ 10³`. From this, `2^20 ≈ 10⁶`, `2^30 ≈ 10⁹`, `2^40 ≈ 10¹²`, `2^50 ≈ 10¹⁵`, `2^60 ≈ 10¹⁸`.
**Why:** When you see `n ≤ 20`, you should INSTANTLY think `2^20 = ~10⁶ subsets, brute enumeration OK`. When `n ≤ 60`, you know it fits in a `long` bitmask.
**LC problems:**
- *Subsets* (LC 78) — n ≤ 10, 2^n enumeration
- *Smallest Sufficient Team* (LC 1125) — bitmask DP, recognize n ≤ 16

## 2.2 — Subset count
**Fact:** Subsets of n elements = `2^n`. Subsets of size k = `C(n,k)`.
**Why:** Brute subset enumeration is OK when `n ≤ 20-25`. Above that, need DP or smarter approach.

## 2.3 — Safe negative subtract under mod
**Fact:** `((a - b) % m + m) % m`. Java's `%` preserves sign of dividend, so `-7 % 3 = -1`, not 2.
**Why:** Caesar cipher normalization, mod-based bucket arithmetic, anywhere you compute `a-b` then mod.
**LC problems:**
- *Count Caesar Cipher Pairs* (LC 3146) — your re-solve target

## 2.4 — Permutation count
**Fact:** Permutations of n distinct items = `n!`. k-permutations = `n!/(n-k)!`.
**Why:** "How many orderings?" problems. Also `(n-1)!` shows up in "fix one position, permute rest" patterns.
**LC problems:**
- *Count the Number of Computer Unlocking Permutations* (1750 — your 1650-1700 #5)

## 2.5 — Running pair count (delta vs cumulative)
**Fact:** At the k-th occurrence of an element, **NEW pairs added** = `k-1`, **cumulative total** = `C(k,2)`. These are different. Don't mix them while iterating.
**Why:** This is exactly what bit you on Caesar Cipher Pairs today. Whenever you iterate and update a running count, ask: "am I adding the delta this iteration, or the total so far?"
**LC problems:**
- *Count Number of Pairs With Absolute Difference K* (LC 2006)
- *Caesar Cipher Pairs* (LC 3146)
- *Count Equal and Divisible Pairs* (LC 2176)

## 2.6 — Group sum of pairs
**Fact:** For buckets sized `[g1, g2, ..., gk]`, total pairs within all buckets = `Σ gi(gi-1)/2`.
**Why:** "Equivalent pairs" problems — group by some equivalence, count within-group pairs.
**LC problems:**
- *Number of Good Pairs* (LC 1512)
- *Count Number of Bad Pairs* (LC 2364)

## 2.7 — Two-pointer convergence (math intuition)
**Fact:** When checking pairs (i, j) with i < j in a sorted array, two pointers converge in O(n) by exploiting monotonicity.
**Why:** Replaces O(n²) brute force.
**LC problems:**
- *Two Sum II - Input Array Is Sorted* (LC 167)
- *Container With Most Water* (LC 11)

## 2.8 — Simple GCD via Euclidean
**Fact:** `gcd(a, b) = gcd(b, a%b)`, base case `gcd(a, 0) = a`. Runs in O(log min(a,b)).
**Why:** Surprisingly common. LCM formulas, "GCD of array" problems.
**LC problems:**
- *Find Greatest Common Divisor of Array* (LC 1979)
- *GCD of Strings* (LC 1071)

## 2.9 — log₂ values (memorize)
**Fact:** `log₂(10⁶) ≈ 20`, `log₂(10⁹) ≈ 30`. Why: 2^20 ≈ 10⁶.
**Why:** Binary-search problems' complexity claim — `O(n log n)` with n=10⁵ is `~10⁵ × 17 ≈ 1.7×10⁶` ops. Reflex this so you instantly verify the budget.

---

# Band 1600 — Solve Q2 confidently

**Why this band:** Q2 problems are 1500-1700 rated. To solve them WITHOUT WAs, you need the next layer of math reflex.

## 3.1 — Combinations formal
**Fact:** `C(n, k) = n! / (k!(n-k)!)`. Pascal's recurrence: `C(n,k) = C(n-1,k-1) + C(n-1,k)`.
**Why:** Generalization of pair/triple counts. Used in "choose k from n" problems.
**LC problems:**
- *Number of Sets of K Non-Overlapping Line Segments* (LC 1621)
- *Count Number of Texts* (LC 2266)

## 3.2 — Modular exponentiation (binary exp)
**Fact:** Compute `a^n mod m` in O(log n) via repeated squaring:
```
result = 1
while n > 0:
  if n odd: result = (result * a) % m
  a = (a * a) % m
  n /= 2
```
**Why:** Without this, `a^n` is impossible for n in the billions. Used in "count ways mod p" with exponential blowup.
**LC problems:**
- *Count Good Numbers* (LC 1922) — `5^a × 4^b mod p`, classic modexp
- *Knight Dialer* (LC 935)
- *Pow(x, n)* (LC 50) — without mod, but same algorithm

## 3.3 — Inclusion-exclusion (2-3 sets)
**Fact:** `|A ∪ B| = |A| + |B| - |A∩B|`. For three sets: `|A∪B∪C| = |A|+|B|+|C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|`.
**Why:** "Count elements divisible by 2 OR 3 OR 5" type problems.
**LC problems:**
- *Nth Ugly Number III* (LC 1201) — divisible by a OR b OR c, classic 3-set inc-exc
- *Number of Ways to Wear Different Hats* (LC 1434)

## 3.4 — LCM and the cast-to-long trap
**Fact:** `lcm(a,b) = a*b / gcd(a,b)`. **Always cast to long**: `(long) a * b / gcd(a,b)`. For 3 numbers: `lcm(lcm(a,b), c)`.
**Why:** `lcm(10⁵, 10⁵)` can be 10¹⁰, overflows int. Same trap as 1500-1550 #2.

## 3.5 — Float cast trap
**Fact:** `(int) Math.pow(1e9, 1.0/3)` returns `999`, not `1000`. Always `+1` after casting `Math.pow` or `Math.sqrt` to int, then verify with multiplication.
**Why:** Floating-point inexactness. Bit you at 1500-1550 #7 (Find Good Integers).

## 3.6 — Bit operations baseline
**Facts:**
- Set bit `i`: `n |= (1 << i)`
- Unset bit `i`: `n &= ~(1 << i)`
- Toggle bit `i`: `n ^= (1 << i)`
- Check bit `i`: `(n >> i) & 1`
- Lowest set bit: `n & -n`
- Power-of-2 check: `(n & (n-1)) == 0 && n > 0`
- Popcount: `Integer.bitCount(n)`

**Why:** Bitmask DP, XOR problems, parity tricks. Without these, anything bit-related is 3× slower.

## 3.7 — Sieve of Eratosthenes (small range)
**Fact:** Mark composites up to N in O(N log log N). For N=10⁶, ~3×10⁶ ops.
**Why:** Any "primes up to N" problem.
**LC problems:**
- *Count Primes* (LC 204) — the canonical sieve problem
- *Closest Prime Numbers in Range* (LC 2523)

## 3.8 — Prime factorization
**Fact:** Trial-divide by primes up to √n. Each prime p divides n at most log_p(n) times.
**Why:** Used in divisor count, GCD/LCM via prime factorizations.
**LC problems:**
- *Minimum Number of Operations to Make Array XOR Equal to K* (LC 2997)
- *Replace Non-Coprime Numbers in Array* (LC 2197)

## 3.9 — Counting fix-the-middle pattern
**Fact:** For triplets `(i, j, k)` with `i < j < k`, fix `j` as the middle, count `valid_left × valid_right` per j.
**Why:** Reduces O(n³) to O(n²) or O(n log n).
**LC problems:**
- *Special Triplets* (LC 3265 — your 1500-1550 #2)
- *Number of Submatrices That Sum to Target* (LC 1074, harder)

## 3.10 — Algebraic rearrangement
**Fact:** When you see `f(a) ≤ g(b)` or `a + b = c`, rearrange to isolate one variable. "Find b such that..." becomes a hashmap lookup.
**Why:** Many "count pairs with property" problems reduce to a hashmap once rearranged.
**LC problems:**
- *Identify the Largest Outlier in an Array* (LC 2926, 1644 — your hinted #7)
- *Two Sum* (LC 1) — same pattern: `b = target - a`

---

# Band 1700 — Q2 fluency, Q3 attempts

**Why this band:** Q3 problems are 1700-2100 rated. Your contest data shows this is your bottleneck (Q3 rarely solved in 90 min). Band 1700 math = enough to ATTEMPT Q3.

## 4.1 — XOR properties
**Facts:**
- `a ^ a = 0`, `a ^ 0 = a`
- Associative, commutative
- XOR of `[1..n]`: `n` if `n%4==0`, `1` if `n%4==1`, `n+1` if `n%4==2`, `0` if `n%4==3`
**Why:** XOR shows up everywhere in 1700+ — uniqueness checks, "find odd-count element", parity arguments.
**LC problems:**
- *XOR of All Pairings* (LC 2425)
- *Decode XORed Array* (LC 1720)
- *Longest Subarray with XOR Zero* (1650-1700 #6)

## 4.2 — Per-bit independent counting
**Fact:** When operations affect bits independently (XOR, AND, OR), you can solve each bit position separately and combine.
**Why:** Reduces complex bit problems to 30 independent simple problems.
**LC problems:**
- *Sum of All Subset XOR Totals* (LC 1863) — per-bit independence
- *Number of Excellent Pairs* (LC 2354)
- *Unique XOR Triplets I* (1650-1700 #7 — your 3h problem)

## 4.3 — Bit-width / capacity cap on XOR
**Fact:** XOR of values all ≤ M is bounded by next power of 2 ≥ M. Max distinct XOR values = `2^bit_width`.
**Why:** Tells you when counting hits its cap.
**LC problems:**
- *Unique XOR Triplets I/II* (LC 3513, 3514)

## 4.4 — Counting via reframing
**Fact:** Instead of counting outputs of a function, describe the IMAGE set directly. "Distinct outputs of strip0(x) for x in [1,n]" = "no-zero positive integers ≤ n".
**Why:** Collapses problem from "iterate inputs" to "count outputs structurally".
**LC problems:**
- *Count Distinct strip-zero values* (~1800 — yesterday's problem)
- *Numbers At Most N Given Digit Set* (LC 902)

## 4.5 — Digit walk (no memo)
**Fact:** Count integers in `[1, n]` with digit property: do Part A (fewer digits, closed form like `Σ 9^d`) + Part B (walk n's digits left to right, at each position contribute `(d_i - constraint) × 9^(remaining)`).
**Why:** Handles n up to 10^15 in O(log n) without digit DP machinery.
**LC problems:**
- *Count Numbers with Unique Digits* (LC 357)
- *Numbers At Most N Given Digit Set* (LC 902)
- *Count Largest Group* (LC 1399)

## 4.6 — Sum of squares / cubes
**Facts:**
- `1² + 2² + ... + n² = n(n+1)(2n+1)/6`
- `1³ + 2³ + ... + n³ = (n(n+1)/2)²` (square of the triangular sum)
**Why:** Closed-form replacement for O(n) summation in math-derivation problems.

## 4.7 — Geometric series sum
**Fact:** `1 + r + r² + ... + r^(n-1) = (r^n - 1)/(r-1)` for r≠1.
**Why:** Compactly represents "sum of powers". For mod cases, use modular inverse of (r-1).
**LC problems:**
- *Sum of Numbers With Units Digit K* (LC 2310)

## 4.8 — Pigeonhole principle (central skill at 1700+)
**Fact:** n+1 items into n buckets → some bucket has ≥2 items. Used to prove "a repeat must exist" without finding it.
**Why at 1700:** at this band, pigeonhole is the CENTRAL insight — no brute-force escape. (Introduction to pigeonhole on bounded state spaces appears at Band 1300+ already — see `math-band-1100-1399.md` Section 10b — but the problems at 1300+ allow brute-force simulation; at 1700+ they don't.)
**LC problems:**
- *Smallest Integer Divisible by K* (LC 1015) — pigeonhole on mod k states
- *Continuous Subarray Sum* (LC 523)

## 4.9 — Stars and bars
**Fact:** Distribute n identical items into k bins (bins can be empty) = `C(n+k-1, k-1)`.
**Why:** "Count ways to split n into k parts" problems.
**LC problems:**
- *Count Vowels Permutation* (LC 1220, indirect)
- Some DP-counting problems

## 4.10 — Game theory primer
**Facts:**
- Parity arguments — who makes the last move?
- Turn-1 reduction — sometimes one move ends the game
- Optimal play means both players play optimally from each state
**Why:** Game-theory Q3s are common.
**LC problems:**
- *Final Element After Subarray Deletions* (1591 — turn-1 reduction)
- *Stone Game* (LC 877)
- *Predict the Winner* (LC 486)

## 4.11 — Divisor count from prime factorization
**Fact:** If `n = p₁^e₁ × p₂^e₂ × ... × pₖ^eₖ`, number of divisors = `(e₁+1)(e₂+1)...(eₖ+1)`.
**Why:** Used in "how many divisors of n" queries.
**LC problems:**
- *Closest Divisors* (LC 1362)
- *Smallest Value After Replacing With Sum of Prime Factors* (LC 2507)

---

# Band 1800 — Q3 fluency

## 5.1 — Modular inverse via Fermat
**Fact:** For prime p, `a^(p-2) mod p` is the modular inverse of a. So `a/b mod p = a × b^(p-2) mod p`.
**Why:** nCr mod p requires dividing factorials; you can't divide under mod, so multiply by inverse.
**LC problems:**
- *Count of Different Subsequences GCDs* (LC 1819)
- *Number of Ways to Reorder Array to Get Same BST* (LC 1569)

## 5.2 — nCr mod p
**Fact:** Precompute `fact[i]` and `inv_fact[i]` arrays. Then `C(n,k) = fact[n] × inv_fact[k] × inv_fact[n-k] mod p`.
**Why:** O(1) per query after O(n) precompute.
**LC problems:**
- *Number of Different Subsequences GCDs* (LC 1819)
- *Find the Sum of the Power of All Subsequences* (LC 3082)

## 5.3 — Linearity of expectation
**Fact:** `E[X + Y] = E[X] + E[Y]` ALWAYS (even if X, Y dependent).
**Why:** Reduces complex probability problems to sum of simple ones via indicator variables.
**LC problems:**
- *New 21 Game* (LC 837)
- *Knight Probability in Chessboard* (LC 688)
- *Frog Position After T Seconds* (LC 1377)

## 5.4 — Indicator variables
**Fact:** Count of items with property = `Σ P(item_i has property)`.
**Why:** Decomposes counting into individual probabilities.

## 5.5 — Catalan numbers (intro)
**Fact:** `Cₙ = (1/(n+1)) × C(2n, n)`. Counts: balanced parens, BSTs with n nodes, monotonic lattice paths, mountain ranges.
**LC problems:**
- *Unique Binary Search Trees* (LC 96) — direct Catalan
- *Generate Parentheses* (LC 22)
- *Score of Parentheses* (LC 856)

## 5.6 — Subset iteration of mask
**Fact:** `for (int s = m; s > 0; s = (s-1) & m)` enumerates all non-empty submasks of m.
**Why:** Subset DP — Σ over subsets of a mask.
**LC problems:**
- *Smallest Sufficient Team* (LC 1125)
- *Partition to K Equal Sum Subsets* (LC 698)
- *Minimum XOR Sum of Two Arrays* (LC 1879)

## 5.7 — Algebraic bound + tight check
**Fact:** Derive an upper bound from invariants, then test small cases to find where the bound is tight vs slack.
**Why:** This is the "answer-first" framework from 1650-1700 #1 (House Robber V).

## 5.8 — Telescoping sums
**Fact:** `1/(k(k+1)) = 1/k - 1/(k+1)` — sums telescope. `f(k) - f(k-1)` summed gives `f(n) - f(0)`.
**Why:** Collapses summation to two endpoint values.
**LC problems:**
- *Sum of Beauty in the Array* (LC 2012, indirect)

## 5.9 — Multinomial coefficient
**Fact:** Number of arrangements of n items with n₁ of type 1, n₂ of type 2, ..., nₖ of type k = `n!/(n₁!n₂!...nₖ!)`.
**Why:** Counting strings with repeated letters, partitions.

---

# Band 1900 — Q3 hard, Q4 attempts

## 6.1 — Matrix exponentiation
**Fact:** Linear recurrence `f(n) = a×f(n-1) + b×f(n-2) + ...` can be computed in O(k³ log n) via matrix power.
**Setup:** Build transition matrix M, compute `M^n × initial_vector`.
**Why:** Fibonacci-like recurrences with huge n.
**LC problems:**
- *N-th Tribonacci Number* (LC 1137, with extension)
- *Find the Power of K-Size Subarrays I/II* (LC 3254/3255, indirect)
- *Knight Dialer* (LC 935) — direct matrix exp

## 6.2 — Euler's totient
**Fact:** `φ(n) = n × Π(1 - 1/p)` over distinct primes p dividing n. Counts integers in `[1,n]` coprime with n.
**Why:** Used in number-theoretic counting and CRT-related problems.

## 6.3 — Sprague-Grundy (Nim)
**Fact:** Game position has Grundy value = `mex` (minimum excludant) of Grundy values of reachable positions. Sum of games = XOR of Grundy values. Position is losing iff Grundy = 0.
**LC problems:**
- *Stone Game IX* (LC 2029, intro)
- Most LC game-theory problems can be solved without full Grundy, but knowing it expands toolkit.

## 6.4 — Markov chain intro
**Fact:** State transitions with probabilities. Steady-state distribution = eigenvector of transition matrix.
**LC problems:**
- *Frog Position After T Seconds* (LC 1377)
- Random-walk problems

## 6.5 — Chinese Remainder Theorem (intro)
**Fact:** System `x ≡ aᵢ mod mᵢ` with pairwise coprime mᵢ has unique solution mod `Π mᵢ`.
**Why:** Combines multiple mod constraints into one.
**LC problems:** Rare on LC, but appears in advanced number theory.

---

# Band 2000 — Q4 attempts (Knight ~2000 LC contest rating)

## 7.1 — Linear basis over GF(2) (XOR basis)
**Fact:** A set of vectors over GF(2) has a basis of size ≤ 30 (for 30-bit numbers). Insert with Gaussian elimination. Max XOR subset = greedy from MSB on basis.
**Why:** Maximum XOR-subset problems become O(n × 30).
**LC problems:**
- *Maximum XOR With an Element From Array* (LC 1707)
- *Maximum Genetic Difference Query* (LC 1938)

## 7.2 — Polynomial hashing
**Fact:** Hash a string as `Σ s[i] × p^i mod m`. Used for fast substring equality.
**Why:** O(1) substring compare after O(n) precompute.
**LC problems:**
- *Longest Duplicate Substring* (LC 1044) — Rabin-Karp / poly hash

## 7.3 — FFT / NTT (intro only)
**Fact:** Multiply two polynomials of degree n in O(n log n). FFT uses complex numbers; NTT uses modular roots of unity.
**Why:** Very rare on LC but appears in convolution-style counting at the very top end.
**LC problems:**
- Almost none — this is mostly CP territory. Mentioned for completeness.

## 7.4 — Walsh-Hadamard / XOR convolution
**Fact:** For "count pairs (a,b) with a XOR b = c", use Walsh-Hadamard transform.
**Why:** Niche at LC — only top-rated problems need it.

---

# Band 2100 — Q4 occasional, near Guardian

## 8.1 — Lucas theorem
**Fact:** `C(n, k) mod p` for huge n, prime p: write n and k in base p, multiply C(nᵢ, kᵢ) per digit.
**Why:** When n exceeds 10⁶ precompute limit.

## 8.2 — Mobius function / inversion
**Fact:** μ(n) = +1, -1, or 0 based on prime factorization. Used in counting "coprime pairs" or "GCD = d" type problems.

## 8.3 — Burnside's lemma
**Fact:** Number of distinct objects under group actions = average fixed points across actions.
**Why:** Counting necklaces, colorings under rotation. Very rare on LC.

---

# Band 2200+ (Guardian threshold)

## 9.1 — Advanced inclusion-exclusion
Beyond 3 sets — counting via signed sums over all subsets of constraints.

## 9.2 — Stirling numbers (1st and 2nd kind)
Count permutations by cycle structure / partitions of set into nonempty subsets.

## 9.3 — Bell numbers
Number of partitions of an n-element set.

## 9.4 — Generating functions
Encode counting sequences as polynomials.

## 9.5 — Subset sum convolution / SOS DP
Sum over subsets DP. Appears in some very-high-rated LC problems.

---

# Order of attack

You're at contest 1500. **Start at Band 1400, finish it, then 1500, then 1600.** Stretch goal: reach Band 1700 in 2-3 months.

**Do NOT skip ahead.** Band 1900 matrix exponentiation is useless if Band 1500 pair counting still takes you 20 min.

## Per-session protocol

- 30-45 min per session.
- 2-4 sub-topics per session.
- For each: Claude poses a tiny problem → you derive → Claude shows formula and 1-2 LC problems → you solve one for verification.
- Mark ✓ in this file when topic is reflex.

## Parallel to zerotrac grind

- Math reflex track runs PARALLEL to cold re-solve track.
- Suggested: 30 min math reflex in morning, then 60-90 min zerotrac.
- The math reflex topics start unlocking the zerotrac problems within ~2 weeks.

---

# Tracking checklist

(Mark ✓ as topics become reflex.)

## Band 1400
- [ ] 1.1 Pair count
- [ ] 1.2 Triangular sum
- [ ] 1.3 Complexity reflex baseline
- [ ] 1.4 Int overflow
- [ ] 1.5 Mod basics
- [ ] 1.6 Parity
- [ ] 1.7 Digit operations

## Band 1500
- [ ] 2.1 Power of 2 anchor
- [ ] 2.2 Subset count
- [ ] 2.3 Safe negative subtract under mod
- [ ] 2.4 Permutation count
- [ ] 2.5 Running pair count (delta vs cumulative)
- [ ] 2.6 Group sum of pairs
- [ ] 2.7 Two-pointer math intuition
- [ ] 2.8 Simple GCD
- [ ] 2.9 log₂ values

## Band 1600
- [ ] 3.1 Combinations formal
- [ ] 3.2 Modular exponentiation
- [ ] 3.3 Inclusion-exclusion 2-3 sets
- [ ] 3.4 LCM
- [ ] 3.5 Float cast trap
- [ ] 3.6 Bit operations baseline
- [ ] 3.7 Sieve of Eratosthenes
- [ ] 3.8 Prime factorization
- [ ] 3.9 Fix-the-middle counting
- [ ] 3.10 Algebraic rearrangement

## Band 1700
- [ ] 4.1 XOR properties
- [ ] 4.2 Per-bit independent counting
- [ ] 4.3 Bit-width XOR cap
- [ ] 4.4 Counting via reframing
- [ ] 4.5 Digit walk (no memo)
- [ ] 4.6 Sum of squares / cubes
- [ ] 4.7 Geometric series sum
- [ ] 4.8 Pigeonhole
- [ ] 4.9 Stars and bars
- [ ] 4.10 Game theory primer
- [ ] 4.11 Divisor count from factorization

## Band 1800
- [ ] 5.1 Modular inverse via Fermat
- [ ] 5.2 nCr mod p
- [ ] 5.3 Linearity of expectation
- [ ] 5.4 Indicator variables
- [ ] 5.5 Catalan numbers
- [ ] 5.6 Subset iteration of mask
- [ ] 5.7 Algebraic bound + tight check
- [ ] 5.8 Telescoping sums
- [ ] 5.9 Multinomial

## Band 1900
- [ ] 6.1 Matrix exponentiation
- [ ] 6.2 Euler's totient
- [ ] 6.3 Sprague-Grundy
- [ ] 6.4 Markov chain intro
- [ ] 6.5 CRT intro

## Band 2000
- [ ] 7.1 Linear basis over GF(2)
- [ ] 7.2 Polynomial hashing
- [ ] 7.3 FFT/NTT intro
- [ ] 7.4 Walsh-Hadamard

## Band 2100
- [ ] 8.1 Lucas theorem
- [ ] 8.2 Mobius function
- [ ] 8.3 Burnside's lemma

## Band 2200+
- [ ] 9.1 Advanced inclusion-exclusion
- [ ] 9.2 Stirling numbers
- [ ] 9.3 Bell numbers
- [ ] 9.4 Generating functions
- [ ] 9.5 SOS DP / subset sum convolution

---

# Note on ratings

LC ratings cited above are approximate. Exact ratings per zerotrac (https://zerotrac.github.io/leetcode_problem_rating/) may differ by ±50. The band-level math content is what matters — a problem rated 1680 vs 1720 needs the same toolkit.

# Note on what's NOT here

Algorithmic patterns (sliding window, monotonic stack, segment tree, union-find, DP transitions, etc.) are NOT in this file. They live in separate pattern files. **This is math reflex only** — formulas, identities, complexity bounds, mod arithmetic, counting techniques. The actual algorithmic muscle is trained via zerotrac grind.

---

# Existing wiki notes that pair with this syllabus

You already have logged notes that go deeper on several of these topics. When studying a section, also read the relevant wiki note for the worked example:

| Syllabus section | Wiki note | What's in the note |
|---|---|---|
| 1.3 Complexity reflex | `reasoning-primitives/05-tle-mle-budget.md` | TLE/MLE bug families, ops/sec cheat-sheet |
| 1.1, 2.5, 2.6 Pair counting | `reasoning-primitives/04-contribution-technique.md` | Sum over pairs without iterating pairs — full worked example with prefix/suffix sums |
| 3.5 Float cast trap | `contest/weekly-502-q2-count-kth-roots.md` | The Math.pow / Math.sqrt integer trap in a live contest — TLE story + fix |
| 4.10, 5.7 Game theory / algebraic bound | `reasoning-primitives/01-invariants.md` | The Q1-Q4 invariant framework from House Robber V (1650-1700 #1) |
| 5.7 Algebraic bound + tight check | `reasoning-primitives/02-lower-bounds.md` | Full lower-bound reasoning template |
| Greedy correctness proofs (algorithmic, supports many math sections) | `reasoning-primitives/03-exchange-argument.md` | Exchange argument template |
| DP recurrences (math reflex pairs with these) | `DP/1D.md`, `DP/2D.md` | Standard DP transition patterns — pairs with 6.1 matrix exp |

When you study a topic, the suggested order is:
1. Read this syllabus's entry to know the fact and why it matters.
2. Read the linked wiki note (if any) for the worked example and deeper reasoning.
3. Do 1-2 LC problems listed in the syllabus entry.
4. Mark ✓ in the tracking checklist.

If a topic doesn't have a linked wiki note, that's a candidate for a new note once you've worked through 2-3 problems on it.
