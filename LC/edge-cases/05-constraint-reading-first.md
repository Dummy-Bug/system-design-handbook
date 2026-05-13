# Constraint reading first

> [!info] Read the constraints section BEFORE the problem description. Constraints frame the entire problem — they tell you the algorithm budget, the data type, and what edge cases the problem creator deliberately enabled.

---

## Why this is a meta-skill

Most people read constraints **last**, treating them as fine print. Top coders read them **first**. This single habit catches more bugs and saves more time than any other technique.

Three things constraints tell you in 30 seconds:

1. **Algorithm budget** — what time complexity is allowed
2. **Data type** — int vs long
3. **Declared edge cases** — what extreme inputs the test suite contains

By the time you read the problem description, you already know what's coming.

---

## Algorithm budget by constraint size

| Constraint | Allowed complexity | Likely algorithm family |
|------------|--------------------|-------------------------|
| `n ≤ 10` | O(n!) | Brute force, permutations |
| `n ≤ 20` | O(2^n) | Bitmask DP, subset enumeration |
| `n ≤ 100` | O(n³) or O(n² · log n) | DP, Floyd-Warshall, matrix |
| `n ≤ 1000` | O(n²) or O(n² · log n) | DP, double loops, all-pairs |
| `n ≤ 10^4` | O(n²) or O(n · sqrt(n)) | Two pointers, segment tree borderline |
| `n ≤ 10^5` | O(n log n) or O(n) | Sort, hashing, sliding window, BIT/segment tree |
| `n ≤ 10^6` | O(n) or O(n log log n) | Linear sieve, hashing, single pass |
| `n ≤ 10^7` | O(n) — strict | Linear only, avoid hashmap overhead |
| `n ≤ 10^9` | O(log n) or O(sqrt(n)) | Math, binary search on answer |

**Calibration:** modern judges accept ~10⁸ basic operations per second. So `n=10^5` with O(n²) = `10^10` ops = TLE.

---

## Value range → data type

| Value range | Data type | Note |
|-------------|-----------|------|
| `\|nums[i]\| ≤ 10^4` | int | sum up to ~10⁹, borderline |
| `\|nums[i]\| ≤ 10^9` | int for individual, **long** for sum/product | classic overflow trap |
| `\|nums[i]\| ≤ 10^18` | long | sum needs BigInteger or careful overflow handling |
| Strings of length up to 10^5 | String, but careful with substring (O(n) copy) | Use indices, not slices |

---

## Declared edge cases — what to look for

| Constraint | What it tells you |
|------------|-------------------|
| `1 ≤ n` | n ≥ 1, no empty input (skip empty-check) |
| `0 ≤ n` | n could be 0 — handle empty explicitly |
| `2 ≤ n` | at least 2 elements — pair operations safe |
| `n ≥ 3` | degenerate cases (single/double) ruled out |
| `nums[i] ≥ 0` | no negatives — simpler sign handling |
| `nums[i] ≥ 1` | no zeros and no negatives — even simpler |
| `-10^9 ≤ nums[i] ≤ 10^9` | both signs possible — modular arithmetic risk |
| `nums[i]` distinct | no duplicates — Set might work where Map usually needed |
| `nums[i]` may repeat | duplicates exist — Map preferred over Set |
| "The input is generated such that..." | hidden invariant — read carefully, may simplify or complicate |

---

## Concrete example: outlier problem

> Constraints:
> - `3 <= nums.length <= 10^5`
> - `-1000 <= nums[i] <= 1000`
> - The input is generated such that at least one potential outlier exists in nums.

What this tells you BEFORE reading the problem:

1. **`n ≤ 10^5`** → need O(n) or O(n log n). Brute force O(n²) won't pass.
2. **`-1000 ≤ nums[i] ≤ 1000`** → sums up to `10^5 * 1000 = 10^8`, int is safe. But negatives exist → modular caution.
3. **`n ≥ 3`** → no degenerate cases, special numbers always have ≥ 1 element.
4. **"input generated such that at least one outlier exists"** → don't worry about returning -1 / null for no-outlier case; one always exists.

Already, before reading the problem, you know: linear-time algorithm, signed arithmetic, guaranteed answer.

---

## Template for spotting in future problems

**Workflow on every problem:**

1. Skip to the **Constraints** section first.
2. In ~30 seconds, note:
   - Max `n` → what's the algorithm budget?
   - Max `|nums[i]|` → do I need long?
   - Any "must be distinct" / "may share" / "at least" hints?
   - Any "input guaranteed" clauses?
3. Write the algorithm budget at the top of your scratch:
   ```
   n=10^5, O(n log n) budget, int safe, has negatives
   ```
4. NOW read the problem with that framing.

This habit takes 30 seconds and saves hours.

---

## Source problems

Every problem ever — but the constraint-driven pivot was especially useful in:

- LC 3289 — Identify Largest Outlier (1644) — constraint `-1000 ≤ nums[i] ≤ 1000` flagged negative arithmetic
- LC 1639 — House Robber V — constraint flagged 10¹⁰ sum → long required
- LC ??? — Count Caesar Cipher Pairs — constraint of fixed alphabet size 26 flagged MOD math

---

## Related patterns

- [[03-integer-overflow-use-long]] — overflow detection starts here
- [[10-category-checklists]] — applies category-specific knowledge after constraint reading
