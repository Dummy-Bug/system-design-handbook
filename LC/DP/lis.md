## The problem

Given an integer array `a`, find the **length of the longest strictly increasing subsequence**.

A *subsequence* keeps original order but may drop any elements — it need **not** be contiguous. *Strictly* increasing: each picked element is `>` the previously picked one.

Concrete instance:

```
a = [10, 9, 2, 5, 3, 7, 101, 18]
```

One valid LIS is `[2, 3, 7, 18]`, length 4 — but we derive the length, not eyeball it.

---

## Brute force via include/exclude

Same binary choice as 0/1 knapsack: for each element, **pick it** or **skip it**. The extra constraint LIS adds: you can't pick *unconditionally* — a pick is only legal if it stays strictly larger than the last picked element.

- All include/exclude choices over `n` elements → `2ⁿ` subsequences → **O(2ⁿ)** brute force.

### State — value or index?

The decision needs to remember "what was the last element I picked." How we store that decides everything, because memoization caches on it:

- Store the last picked **value**: values reach `10⁹`, so the cache would be `int[n][10⁹]` → impossible. **Fatal.**
- Store the last picked **index**: ranges over `-1, 0, …, n-1` → only `n+1` values. Cache is `int[n][n]` → **O(n²)**. ✓

> [!important] Store the previous **index**, not the previous **value**. The value domain is unbounded; the index domain is `n`. This single choice is what makes LIS tractable.

```
f(i, prev) = LIS length using indices i..n-1, given the last picked index is `prev`
```

---

## The brute-force recursion

```java
int[] nums;

// f(i, prev) = LIS length over indices i..n-1, last picked index = prev
int f(int i, int prev) {
    if (i == nums.length) return 0;            // no items left

    int skip = f(i + 1, prev);                 // don't pick i

    int pick = 0;
    if (prev == -1 || nums[i] > nums[prev]) {  // nothing picked yet, OR strictly larger
        pick = 1 + f(i + 1, i);                // pick i → it becomes the new prev
    }

    return Math.max(pick, skip);
}
// call: f(0, -1)
```

Reading the pick condition:
- `prev == -1` → nothing picked yet → first element always allowed.
- `nums[i] > nums[prev]` → **strict** increase (`>`, not `>=`).
- On pick, the new `prev` becomes `i`.

**Time = O(2ⁿ)** — include/exclude over `n` elements, broken at scale like knapsack.

---

## Memoization — cache on `(i, prev)`

`prev` ranges over `-1 … n-1`. Arrays can't index `-1`, so **shift by +1**: store at `memo[i][prev + 1]`, where column `0` means `prev = -1`.

```java
int[][] memo;   // sized [n][n+1], filled with -1 (sentinel)

int f(int i, int prev) {
    if (i == nums.length) return 0;

    if (memo[i][prev + 1] != -1) return memo[i][prev + 1];   // shifted key

    int skip = f(i + 1, prev);

    int pick = 0;
    if (prev == -1 || nums[i] > nums[prev]) {
        pick = 1 + f(i + 1, i);
    }

    return memo[i][prev + 1] = Math.max(pick, skip);
}
// caller: memo = new int[n][n + 1]; fill -1; return f(0, -1);
```

### Complexity

```
distinct subproblems = (i values) × (prev values) = n × (n+1)
work per subproblem   = O(1)

Time  = O(n²)
Space = O(n²) table + O(n) stack
```

From **O(2ⁿ)** → **O(n²)**. For `n ≤ 2500` (typical LIS constraint), `n² ≈ 6×10⁶` — fine.

> [!note] This `(i, prev)` form is correct but **clunky** — a 2D table for what is classically a 1D problem. The sharper state below uses one variable, same `O(n²)`, and is the *only* form that opens the door to `O(n log n)`.

---

---

## The sharper state — 1D, "ends exactly at `i`"

The 2D form carried `prev` because it asked a *forward* question ("what comes next, given what I picked?"). Flip the direction and fix the **endpoint**:

```
dp[i] = length of the longest increasing subsequence that ENDS exactly at index i
```

- **One** variable → 1D array, `O(n)` space.
- By forcing `i` to be the *last* element, the increase-constraint is checked **backward** against earlier elements at recurrence time, then forgotten. Nothing needs to be carried as a parameter — the constraint is baked into the state's meaning. That's how the second dimension vanishes.

### State comparison

| | 2D (clunky) | 1D (sharp) |
|---|---|---|
| State | `f(i, prev)` = LIS from `i` onward, given last picked index `prev` | `dp[i]` = LIS ending exactly at `i` |
| Variables | 2 | 1 |
| View | suffix, forward-looking | "ends here", backward-checked |
| Answer | `f(0, -1)` (one cell) | `max(dp[0..n-1])` (any endpoint) |

### Recurrence

To end at `i`, append `nums[i]` after the best subsequence ending at some earlier `j` that keeps it increasing:

```
dp[i] = 1 + max( dp[j]  for all j < i with nums[j] < nums[i] )
        or just 1 if no such j exists      (the element stands alone)
```

- `nums[j] < nums[i]` → **strict** gate.
- floor `dp[i] = 1` → every element alone is a valid length-1 LIS.

### Code

```java
int lengthOfLIS(int[] nums) {
    int n = nums.length;
    int[] dp = new int[n];
    Arrays.fill(dp, 1);            // floor: every element alone is an LIS of length 1

    int best = 1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < i; j++) {
            if (nums[j] < nums[i]) {                // strict-increase gate
                dp[i] = Math.max(dp[i], 1 + dp[j]); // extend the best run ending at j
            }
        }
        best = Math.max(best, dp[i]);  // answer tracks the max over ALL i
    }
    return best;
}
```

> [!important] Answer is `max(dp[i])`, **not** `dp[n-1]`. `dp[i]` ends *exactly* at `i`, but the true LIS can end anywhere. For `[1,2,3,0]`, `dp[n-1]` reports the run ending at `0` (= 1), missing the real answer 3.

### Trace on `a = [10, 9, 2, 5, 3, 7, 101, 18]`

```
index   0    1   2   3   4   5   6    7
a       10   9   2   5   3   7   101  18
dp      1    1   1   2   2   3   4    4
```

- `dp[3]` (5): only `2 < 5` → `1 + dp[2] = 2`.
- `dp[5]` (7): `2,5,3 < 7` → `1 + dp[3] = 3`.
- `dp[6]` (101): all smaller → `1 + dp[5] = 4`.
- `dp[7]` (18): `2,5,3,7 < 18` → `1 + dp[5] = 4`.

`max(dp) = 4` ✓

### Complexity

```
Time  = O(n²)   — for each i, scan all j < i
Space = O(n)    — single dp array, no recursion
```

Same time as the 2D memo, but `O(n)` space and far cleaner — the default form to write.

---

## O(n log n) — patience / binary search

The `O(n²)` inner loop only does one thing: *"find the longest increasing run I can sit on top of."* To kill the `O(n)` scan we need a **sorted** structure we can binary search. Deriving *what* to keep sorted is the whole trick.

### Insight 1 — keep only the smallest tail per length

Two increasing subsequences of the **same length**, one ending in `9`, one ending in `4`: the one ending in `4` **dominates** — anything that can extend the `9`-tailed one can also extend the `4`-tailed one, and more. So for each length, only the **smallest tail** is worth remembering.

```
tails[k] = smallest possible tail value among all increasing subsequences of length k+1
```

### Insight 2 — `tails` is always strictly increasing

Claim: `tails[0] < tails[1] < tails[2] < …`, always.

**Chop-off proof.** Take the best length-`k` subsequence; its tail is `tails[k-1]`. Drop its last element → a length-`(k-1)` subsequence whose tail is *strictly smaller* (the original was increasing). So a length-`(k-1)` subsequence exists ending below `tails[k-1]`; the best one is `≤` that, hence `tails[k-2] < tails[k-1]`. Holds for every `k` → `tails` is strictly increasing.

That sortedness is exactly what makes binary search legal.

### The update rule — one binary search per element

New element `x` arrives:

1. `x` larger than **everything** in `tails` → **append** → the LIS got longer.
2. otherwise → find the **ceiling** of `x` (smallest tail `≥ x`) and **replace** it with `x`.

Why *replace*, not insert — say the ceiling is at index `k`:
- `x ≤ tails[k]`, so length `k+1` now has an equal-or-smaller tail = strict improvement.
- Sortedness survives: everything left of `k` was `< x`, and `x ≤ tails[k] < tails[k+1]`.
- Inserting would grow the array and falsely claim a longer subsequence exists.

> [!warning] The final `tails` array gives the correct **length** but is **not** necessarily a real subsequence of the input — slots get overwritten out of order. Only `tails.length` is meaningful.

### Code (`low <= high` ceiling search)

```java
int lengthOfLIS(int[] nums) {
    int[] tails = new int[nums.length];   // tails[k] = smallest tail of an LIS of length k+1
    int len = 0;

    for (int x : nums) {
        // ceiling search: first index in tails[0..len) with tails[idx] >= x
        int lo = 0, hi = len - 1;
        int idx = len;                    // default = append position (no ceiling found)
        while (lo <= hi) {
            int mid = (lo + hi) >> 1;
            if (tails[mid] >= x) {
                idx = mid;                // candidate ceiling → record, search LEFT for earlier
                hi = mid - 1;
            } else {
                lo = mid + 1;             // tails[mid] too small → search RIGHT
            }
        }
        tails[idx] = x;                   // replace ceiling, or append if idx == len
        if (idx == len) len++;            // appended → LIS grew
    }
    return len;
}
```

The search is a hand-written **lower_bound**: "record on `>=`, then go left" lands `idx` on the *first* index with `tails[idx] >= x`, or leaves it at `len` (append).

> [!tip] Java shortcut: `Arrays.binarySearch` returns `-(insertionPoint) - 1` when the key is absent; decoding `-idx - 1` gives the same ceiling index.

### Contest version — `Arrays.binarySearch` (no hand-rolled loop)

Because `tails` is **strictly increasing — no duplicates** (Insight 2), `Arrays.binarySearch` returns exactly the lower_bound, so you can skip the hand-rolled loop in contests:

```java
public int lengthOfLIS(int[] nums) {
    int n = nums.length;
    int[] tail = new int[n];
    int len = 0;

    for (int i = 0; i < n; i++) {
        int num = nums[i];
        int idx = Arrays.binarySearch(tail, 0, len, num); // search filled prefix [0, len)
        if (idx < 0) idx = -idx - 1;   // not found → decode insertion point (= lower_bound)
        tail[idx] = num;               // found (idx>=0) → overwrite the equal tail
        if (idx == len) len++;         // appended → LIS grew
    }
    return len;
}
```

- The `if (idx < 0)` guard is **mandatory**: a *found* key returns `idx >= 0` (the overwrite-the-equal case), and only the negative branch needs decoding.
- ⚠️ **Strict LIS only.** Non-decreasing LIS needs an upper_bound (`>`); then `tails` carries duplicates and `binarySearch`'s match index is unspecified → hand-roll. The decode contract lives in `02-syntax/03-arrays.md`.

### Trace on `[10, 9, 2, 5, 3, 7, 101, 18]`

```
x=10 → ceil idx 0 == len(0) → append   tails=[10]        len 1
x= 9 → ceil idx 0 <  len(1) → replace  tails=[9]         len 1
x= 2 → ceil idx 0 <  len    → replace  tails=[2]         len 1
x= 5 → ceil idx 1 == len(1) → append   tails=[2,5]       len 2
x= 3 → ceil idx 1 <  len(2) → replace  tails=[2,3]       len 2
x= 7 → ceil idx 2 == len(2) → append   tails=[2,3,7]     len 3
x=101→ ceil idx 3 == len(3) → append   tails=[2,3,7,101] len 4
x=18 → ceil idx 3 <  len(4) → replace  tails=[2,3,7,18]  len 4
```

`len = 4` ✓

### Complexity

```
Time  = O(n log n)   — n elements × one binary search each
Space = O(n)         — the tails array
```

For `n = 10⁵` (where `O(n²) = 10¹⁰` dies), this is `~2×10⁶` — instant.

> [!important] **Strict knob.** `tails[mid] >= x` (record on `>=`) → **strict** LIS. Switch to `tails[mid] > x` → **non-decreasing** LIS. Same code, one operator.

---

## Summary — three forms of LIS

| Form | State | Time | Space | When |
|---|---|---|---|---|
| 2D memo | `f(i, prev)` | O(n²) | O(n²) | first derivation only |
| 1D DP | `dp[i]` ends at `i` | O(n²) | O(n) | default; also when you must reconstruct the subsequence |
| Patience | `tails[k]` = smallest tail of length `k+1` | O(n log n) | O(n) | large `n`; length only |
