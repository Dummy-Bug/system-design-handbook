# 15 — Count Number of Bad Pairs

- **Link:** https://leetcode.com/problems/count-number-of-bad-pairs/ (LC 2364)
- **Band:** 1600–1699 · sealed queue · blind deal #14 · Q2 (AR 54.2%) · **answer-key bucket = Hashing ✦ Reframe**
- **Bucket (OUR code):** **Hashing** (counting map keyed by `nums[i]-i`) + complement reframe. [[lc-credit-mechanic-not-label]]
- **Dealt:** 2026-06-15 · **AC:** 2026-06-15 (clock time not captured).
- **Result:** ⚠️ **HINTED — not clean.** Stuck ~20 min (couldn't find a direct bad-pair approach; self-pivoted to counting good pairs), then took LC hint *"Would it be easier to count the number of pairs that are not bad pairs?"* at 20 min (before the 30-min cap). AC after. Per rule 6C a hint disqualifies the rep. **Hashing was already OWNED 2/2 (seed re-audit 2026-06-15) → no ownership rep was at stake.** Clean-rate **10/13 (77%) → 10/14 (~71%)** — this is the 1 hinted-in-batch (rule 6C ≤1/10), now the thin margin.
- **Hint nuance:** the hint was *redundant* — the complement pivot ("count good pairs") was self-stated **before** the hint. The hint did **not** contain the load-bearing insight (the `nums[i]-i` key); that was the real block during the 20 stuck minutes. Logged hinted anyway per anti-optimism (rule 7) — don't upgrade "I basically had it" to clean.

---

## The problem
A pair `(i,j)`, `i<j`, is **bad** iff `j - i != nums[j] - nums[i]`. Count bad pairs. `1 ≤ n ≤ 1e5`, `1 ≤ nums[i] ≤ 1e9`.

## Approach — complement + algebraic rearrangement
- **Complement:** `bad = C(n,2) − good`, where good = pairs with `j - i == nums[j] - nums[i]`.
- **Load-bearing reframe ([[lc-algebraic-rearrangement]] §3.10):** `j - i == nums[j] - nums[i]` ⟺ **`nums[i] - i == nums[j] - j`**. So group indices by the key `nums[i] - i`; every earlier index sharing the key forms a good pair.
- One pass: read `freq = map[key]`, `good += freq`, then `map[key]++`. `bad = total − good`.

## Step 2 — worked example (`nums=[4,1,3,3]`, expected 5)
keys `nums[i]-i`: `4-0=4`, `1-1=0`, `3-2=1`, `3-3=0`.

| i | key | freq before | good += |
|---|---|---|---|
| 0 | 4 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| 2 | 1 | 0 | 0 |
| 3 | 0 | 1 (key 0 seen at i=1) | 1 |

good = 1, total = C(4,2) = 6, bad = 6 − 1 = **5**. ✅

## Step 3 — named edge cases
1. **Overflow in `total`** — `n=1e5` → `n(n-1) ≈ 1e10 ≫ int` → **cast to long before the multiply**: `((long)n*(n-1))/2`. ✅ done. *(perturbation target below)*
2. **Overflow in `good`** — accumulates up to `total ≈ 5e9` → `long`. ✅ done.
3. **Key range** — `nums[i]-i ∈ [1-1e5, 1e9]` → fits `int`; map key stays int. *(perturbation target below)*
4. **All same key** — every pair good → bad = 0.
5. **All distinct keys** — good = 0 → bad = total.

## As-submitted solution (AC)
```java
class Solution {
    public long countBadPairs(int[] nums) {
        int n = nums.length;
        long totalPairs = ((long)n*(n-1)) / 2;
        Map<Integer,Integer> map = new HashMap<>();
        long goodPairs = 0L;
        for (int i = 0; i < n; i++){
            int freq = map.getOrDefault(nums[i] - i , 0);
            map.put(nums[i] - i, freq + 1);
            goodPairs += freq;
        }
        return totalPairs - goodPairs;
    }
}
```
- Time `O(n)`, space `O(n)`.

## Lesson
- **"Count pairs with a positional/value relation" → rearrange to isolate a per-index invariant, then hash-count.** `nums[i]-i` is the invariant; the complement (`bad = total − good`) is the easy half and should be reflexive. The hard half was the rearrangement — that's the rep that matters, not the complement.
- **Hinted because a soft/redundant hint was taken at 20 min instead of pushing the cap.** The carelessness-band signal: reach for the hint before the 30 even when the rep isn't on the line.

## Perturbation — long vs int (worked Socratically 2026-06-15)
The four int/long decision points, each pinned by scale:

| Var | Type | Why (scale) |
|---|---|---|
| `totalPairs` | **long** | `C(n,2) = n(n-1)/2 ≈ 5e9` at `n=1e5` — **multiplication** `n*(n-1) ≈ 1e10` inflates past int (2.15e9) |
| `goodPairs` | **long** | same ceiling `C(n,2)`: when EVERY pair is good (all keys equal, e.g. `nums=[1,2,3,…]`), `freq` runs `0,1,…,n-1` → sum = `C(n,2) ≈ 5e9`. `good = total`, `bad = 0` |
| key `nums[i]-i` | int (→ Long only if `nums[i] > ~2e9`) | range `[1-1e5, 1e9] ⊂ int`. Safe **because** of the suspicious specific `nums[i] ≤ 1e9` |
| `freq` | int | bounded by `n ≤ 1e5` |

**Cast-placement trap (Step-3 #1):** `((long)n*(n-1))/2` casts `n` first → the multiply runs in long. The careless `(long)(n*(n-1))` computes `n*(n-1)` in **int** (overflows at `n≈46341`, since `46341² ≈ 2.15e9`), *then* widens the already-wrong value. Cast must be **before** the multiply.

**Constraint perturbation — raise `nums[i]` to `1e18`:** the key `nums[i]-i` now reaches `~1e18` — exceeds int, fits long → map key must become **`Long`**.

**The load-bearing lesson (why subtraction ≠ multiplication for intermediate overflow):**
- **`a*b` inflates** to ~`a·b`, *bigger than either operand* → overflows even when `a`,`b` individually fit → guard with cast-before-multiply.
- **`a ± b` only overflows when the result GROWS past the type** — subtraction with opposite signs, or addition with same signs. Here `nums[i] ≥ 1` (positive) and `i ≥ 0` (small), so `nums[i] - i` only *shrinks* from `nums[i]`, staying in `[1e18−1e5, 1e18] ⊂ long`. **No intermediate overflow even at the perturbed 1e18** — the key type changes, but the subtraction itself is structurally safe. (Flip a constraint so `nums[i]` could be near `LONG_MIN` with large positive `i` → then `nums[i]-i` underflows; different problem.)
- **Rule banked:** multiplication → always guard the intermediate; `±` → safe iff operands can't push the result to grow past the type. Ties to math-reflex §1.4 (overflow) + §3.4 (cast-to-long-**before**-multiply).

## PENDING
- **Day+14 revision (due 2026-06-29):** re-derive the `nums[i]-i` rearrangement cold (the load-bearing step), not the complement. [[lc-retrieval-not-reread]]
