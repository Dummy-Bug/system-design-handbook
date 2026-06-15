# 14 — Minimum Time to Repair Cars

- **Link:** https://leetcode.com/problems/minimum-time-to-repair-cars/ (LC 2594)
- **Band:** 1600–1699 · **user-chosen** (not a sealed-queue deal) · **bucket = Binary-Search on answer**
- **Bucket (OUR code):** **Binary-Search on answer** — feasibility = "how many cars can the fleet repair within budget `T`?" Credited by mechanic-in-code [[lc-credit-mechanic-not-label]].
- **Dealt:** 2026-06-15 (self-picked)
- **AC:** 2026-06-15 (**self-derived, no hints**), **first submission clean** (exact clock time not captured).
- **Result:** ✅ **CLEAN — first-submission self-derived AC.** Per rule 6A a genuine ownership rep. **Binary-Search debt: 1/2 → 2/2 → ● OWNED.** This is the second clean rep (after #13) → **closes the plain-BS debt carried since 1500-1550**, and closes Binary-Search for the band.

---

## The problem
`ranks[i]` = rank of mechanic `i`. A mechanic of rank `r` repairs `n` cars in `r·n²` minutes. All mechanics work in parallel. Given `cars` total cars to repair, find the **minimum time** in which the fleet repairs all of them.

## Approach (self-derived) — binary-search the answer
- **Monotone:** if budget `T` lets the fleet repair `≥ cars`, any larger `T` also does → search the smallest feasible `T`.
- **Feasibility `helper(T)`:** in budget `T`, a mechanic of rank `r` can repair `n` cars where `r·n² ≤ T` → `n = ⌊√(T/r)⌋`. Sum over mechanics, feasible iff `≥ cars`. Early-exit once the running sum crosses `cars`.
- **Bounds:** `low = 1`; `high = cars²·100` — the **single slowest possible mechanic** (max rank = 100) repairing **all** cars alone takes `100·cars²`, always feasible. Standard lower-bound BS: on feasible, record + shrink right; else move left.

> Same template as #13 (trips), derived cold again. The only new wrinkle vs #13: the per-mechanic capacity is `⌊√(T/r)⌋` (a square-root inversion) instead of `⌊T/t⌋` (a plain division) — and that √ is where the only real subtlety lives (see the float-precision debrief).

## Step 2 — worked example (`ranks=[4,2,3,1]`, cars=10, expected 16)
Per-mechanic cars at budget `T`: `⌊√(T/r)⌋`.

| T | r=4 | r=2 | r=3 | r=1 | Σ | ≥10? |
|---|---|---|---|---|---|---|
| 15 | ⌊√3.75⌋=1 | ⌊√7.5⌋=2 | ⌊√5⌋=2 | ⌊√15⌋=3 | 8 | no |
| 16 | ⌊√4⌋=2 | ⌊√8⌋=2 | ⌊√5.33⌋=2 | ⌊√16⌋=4 | 10 | **yes** |

BS lands on `T=16` (15 infeasible, 16 feasible). ✅ matches. **Note the `r=1` column at T=16: `√16 = 4` exactly — a perfect square — which is precisely the case the float guard has to get right.**

## Step 3 — named edge cases
1. **Overflow in `high`** — `cars ≤ 1e6` → `cars²·100 ≈ 1e14 ≫ int`. Cast `long` before the multiply (`(long)cars*cars*100`). ✅ done.
2. **Float precision on `√`** — `(long)Math.sqrt(x)` can in principle return `k−ε` for a perfect square `x=k²`, undercounting by 1 → feasibility falsely fails → answer drifts **high**. **Safe here** because `x = budget/r ≤ 1e14 ≪ 2⁵³` (double is exact + Java's `sqrt` is correctly rounded). See the full debrief below. (Defensive isqrt guard added in the canonical form.)
3. **Single mechanic** — `high = 100·cars²` covers it; BS converges. With one rank-`r` mechanic the answer is exactly `r·cars²`.
4. **All ranks equal** — `Σ = n·⌊√(T/r)⌋`; BS still correct.
5. **cars = 1** — answer = `min(ranks)` (the fastest mechanic does the one car in `r·1²`).
6. **Midpoint precedence** — `low + ((high-low)>>1)` with inner parens (the banked trap [[lc-java-shift-precedence-trap]]) — not tripped.

## As-submitted solution (AC)
```java
class Solution {
    private boolean helper(long budget, int[] ranks, long cars){
        long repaired = 0;
        for (int r : ranks){
            repaired += (long)Math.sqrt((double)budget/r);
            if (repaired >= cars) return true;
        }
        return repaired >= cars;
    }
    public long repairCars(int[] ranks, int cars) {
        long low = 1L;
        long high = (long)cars*cars*100;
        long ans = high;
        while(low <= high){
            long mid = low + ((high-low)>>1);
            if (helper(mid,ranks,cars)){ ans = mid; high = mid - 1; }
            else low = mid + 1;
        }
        return ans;
    }
}
```
- Time `O(n · log(cars²·100))`.
- ACed because `budget/r ≤ 1e14 < 2⁵³` keeps the float round-trip exact — **right answer for the right constraints**, not because "longs never become doubles."

## Canonical form (defensive isqrt guard — for reuse at larger constraints)
Work the capacity in **integers** so no float can betray it. `x = budget/r` (integer division is exact here: `⌊√⌊y⌋⌋ = ⌊√y⌋`), then correct the float estimate to the exact `⌊√x⌋`:
```java
class Solution {
    private boolean helper(long budget, int[] ranks, long cars){
        long repaired = 0;
        for (int r : ranks){
            long x = budget / r;
            long k = (long)Math.sqrt((double)x);
            while ((k+1)*(k+1) <= x) k++;   // estimate too small -> bump up
            while (k*k > x) k--;            // estimate too big   -> bump down
            repaired += k;
            if (repaired >= cars) return true;
        }
        return repaired >= cars;
    }
    public long repairCars(int[] ranks, int cars) {
        long low = 1L, high = (long)cars*cars*100, ans = high;
        while(low <= high){
            long mid = low + ((high-low)>>1);
            if (helper(mid,ranks,cars)){ ans = mid; high = mid - 1; }
            else low = mid + 1;
        }
        return ans;
    }
}
```
- The two `while`s exit only when `k² ≤ x < (k+1)²` — the **definition** of `⌊√x⌋`. Correctness no longer depends on any precision argument.
- **Overflow watch:** `(k+1)*(k+1)` here ≤ `~1e14` (safe). At larger constraints where `x ~ 1e18` (so `k ~ 1e9`), `(k+1)²` flirts with the `long` ceiling → compare as `k+1 <= x/(k+1)` instead.

## The float-precision debrief (the real lesson of this problem)
**The misconception corrected:** `budget` is a `long`, but `Math.sqrt` *takes and returns a `double`* — `budget/r` is widened to double on the way in. A double **is** involved; "it's a long so it stays exact" is false reasoning.

**When the bug actually fires** — `(long)` *truncates* (drops the fraction, never rounds up), so a perfect square `x=k²` whose `sqrt` returns `k−ε` (e.g. `4.9999999`) casts to `k−1`. That undercounts repaired cars → feasibility falsely fails → BS hunts a bigger budget → **answer returned > true answer.** A silent +drift, not a crash/TLE.

**Why it's safe at *these* constraints (the two-fact chain):**
1. **`x` goes in exact** — `x ≤ 1e14 < 2⁵³ ≈ 9·10¹⁵`, and a double holds every integer below `2⁵³` exactly (52-bit mantissa).
2. **`sqrt` comes out correctly rounded** — Java's `Math.sqrt` is IEEE-754 correctly rounded → for a perfect square `k²` it returns the *nearest* double to `k`, which is `k` itself. No `k−ε`, ever, below `2⁵³`.

**Where it breaks (file for future):**
- **`x > 2⁵³`** (budgets up to `1e18` in harder BS-on-answer problems) → fact 1 dies, `x` is pre-rounded, perfect squares *can* come back low → the isqrt guard earns its keep.
- **`Math.pow(x, 0.5)`** is **not** correctly rounded (unlike `sqrt`) → loses fact 2 even below `2⁵³`. Use `sqrt`, never `pow`-to-the-half.

**Why the guard uses `while`, not `if`/`else`:** with a correctly-rounded `sqrt` the error across the whole `long` range is `< 1` (worst case `≈ √x·2⁻⁵³ ≈ 3·10⁻⁷` at `x~9·10¹⁸`), so a single bump *would* suffice — the user was right. But `while` is **strictly dominant at identical cost** (the body runs 0–2 times): it's correct *unconditionally* (no precision proof to get wrong), and it survives a sloppy `sqrt`/`pow`. `while` turns "correct because I proved the error is small" into "correct because the loop can't exit until `k²≤x<(k+1)²` holds."

→ **Promoted to a math-reflex card: §3.12 Exact integer sqrt (isqrt).**

## Lesson
- **"Minimize a budget so independent agents collectively hit a target" → binary-search the answer; feasibility = `Σ (per-agent capacity in budget T)`.** #13 capacity = `⌊T/t⌋` (division); #14 capacity = `⌊√(T/r)⌋` (sqrt inversion). Same template, the per-agent capacity is the only moving part.
- **The √ is the trap, not the BS.** Got the answer for the right *reason* only after the debrief: it's "values stay under `2⁵³` where the double round-trip is exact," not "longs can't be doubles." Bank the isqrt guard as the default whenever a BS feasibility check needs `⌊√x⌋`.

## PENDING
- **No cold re-solve owed** (clean self-derived first-AC). [[lc-cold-resolve-scope]]
- **Day+14 revision (due 2026-06-29):** re-derive cold — the `⌊√(T/r)⌋` capacity, the `high = 100·cars²` bound, AND reproduce the isqrt guard + the `2⁵³` exactness argument from scratch; do NOT re-read. [[lc-retrieval-not-reread]]
- **Binary-Search now ● OWNED 2/2 (#13, #14)** — plain-BS debt carried from 1500-1550 is **closed**.
