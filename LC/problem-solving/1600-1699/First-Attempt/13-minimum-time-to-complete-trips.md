# 13 — Minimum Time to Complete Trips

- **Link:** https://leetcode.com/problems/minimum-time-to-complete-trips/
- **Band:** 1600–1699 · sealed queue · blind deal #13 · Q3 (AR 39.8%) · **answer-key bucket = Binary-Search on answer (carried plain-BS)**
- **Bucket (OUR code):** **Binary-Search on answer** — matches the answer-key. Credited by mechanic-in-code [[lc-credit-mechanic-not-label]].
- **Dealt:** 2026-06-13 (walk batch) · solved in-head on the walk, typed after.
- **AC:** 2026-06-15 (**self-derived, no hints**), **first submission clean**, **18 min**.
- **Result:** ✅ **CLEAN — first-submission self-derived AC.** Per rule 6A this is a genuine ownership rep. **Binary-Search debt: 0/2 → 1/2.** First clean rep on the plain-BS debt carried since **1500-1550**. Clean-rate now **9/12 (75%)**.

---

## The problem
`time[i]` = seconds bus `i` takes per trip (each bus runs independently, repeatedly). Find the **minimum total time** such that all buses combined complete at least `totalTrips` trips.

## Approach (self-derived) — binary-search the answer
- **Monotone:** if time budget `T` lets the fleet finish `≥ totalTrips`, any larger `T` also does. → search the smallest feasible `T`.
- **Feasibility `helper(T)`:** in budget `T`, bus `i` completes `⌊T / time[i]⌋` trips. Fleet total = `Σ ⌊T/time[i]⌋`. Feasible iff `≥ totalTrips`. Early-exit once the running sum crosses `totalTrips`.
- **Bounds:** `low = 1`; `high = maxTime · totalTrips` (the slowest single bus alone finishes `totalTrips` in that time → always feasible). Standard lower-bound BS: on feasible, record + shrink right; else move left.

> **The reframe that mattered:** "in budget `T`, how much can each worker independently do? sum it, compare to the target" — the *exact* feasibility shape #12's `helper` needed and couldn't reach 2 days ago. Same template, derived cold this time. The rep did its job.

## Step 2 — worked example (`time=[1,2,3]`, totalTrips=5, expected 3)
| T | ⌊T/1⌋ | ⌊T/2⌋ | ⌊T/3⌋ | Σ | ≥5? |
|---|---|---|---|---|---|
| 2 | 2 | 1 | 0 | 3 | no |
| 3 | 3 | 1 | 1 | 5 | **yes** |
BS lands on `T=3` (T=2 infeasible, T=3 feasible, nothing smaller works). ✅ matches.

## Step 3 — named edge cases
1. **Overflow in `high`** — `maxTime ≤ 1e7`, `totalTrips ≤ 1e7` → `maxTime·totalTrips ≈ 1e14 ≫ int`. Cast `long` before the multiply (`(long)max * totalTrips`). ✅ done.
2. **Overflow in the feasibility sum** — `count` accumulates up to `totalTrips` (1e7), fits int but kept `long` for safety. ✅ done.
3. **Single bus** — `high = time[0]·totalTrips` exact; BS converges to it.
4. **All buses identical** — `Σ = n·⌊T/t⌋`; BS still correct.
5. **totalTrips = 1** — answer = `min(time)`; BS finds it (smallest T with any bus ≥ 1 trip).
6. **Midpoint precedence** — `low + ((high-low)>>1)` written WITH inner parens (the #12 banked trap [[lc-java-shift-precedence-trap]]) — **not tripped this time.**

## As-submitted solution (AC)
```java
class Solution {
    private boolean helper(long budget, int[] time, int totalTrips){
        long count = 0;
        for (int t : time){
            count += budget / t;
            if (count >= totalTrips) return true;
        }
        return count >= totalTrips;
    }
    public long minimumTime(int[] time, int totalTrips) {
        long low = 1;
        int max = time[0];
        for (int t : time) max = Math.max(t, max);
        long high = (long) max * totalTrips;
        long ans = -1;
        while (low <= high){
            long mid = low + ((high - low) >> 1);
            if (helper(mid, time, totalTrips)){ ans = mid; high = mid - 1; }
            else low = mid + 1;
        }
        return ans;
    }
}
```
- Time `O(n · log(maxTime·totalTrips))`.
- **Minor:** `ans = -1` is unreachable — `high` is always feasible, so the loop always assigns `ans`. `ans = high` init would be equally correct; harmless dead defensiveness, not a bug.

## Lesson
- **"Minimize a budget/time so independent agents collectively hit a target" → binary-search the answer; feasibility = `Σ (per-agent capacity in budget T)`.** This is the canonical plain-BS-on-answer template. #12 (mountain) and #13 (trips) are the *same* shape — #12's per-agent capacity needed §3.11 inverse-triangular (harder), #13's is a plain `⌊T/t⌋` (easier). Deriving #13 cold is the reps compounding: the feasibility-reframe is becoming reflexive.
- **Precedence reflex held** — banked yesterday, applied today.

## PENDING
- **No cold re-solve owed** (clean self-derived first-AC). [[lc-cold-resolve-scope]]
- **Day+14 revision (due 2026-06-29):** reproduce cold — re-derive the feasibility `Σ⌊T/t⌋` and the `high` bound from scratch; do NOT re-read. [[lc-retrieval-not-reread]]
- **BS debt now 1/2** — one more clean self-derived BS rep closes it. #12's BS route (inverse-triangular feasibility) is the natural next target.
