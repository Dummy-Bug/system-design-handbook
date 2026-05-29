# Boats to Save People — First Attempt (Phase 1 acquisition: Two-Pointer on Arrays)

## Problem

You are given an integer array `people` where `people[i]` is the weight of the `i`-th person, and an infinite number of boats where each boat can carry a maximum weight of `limit`. **Each boat carries at most two people** at the same time, provided the sum of the weight of those people is at most `limit`. Return the minimum number of boats to carry every given person.

Example: `people = [3,2,2,1], limit = 3` → `3` (boats: `(1,2)`, `(2)`, `(3)`).

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-28 |
| Link | https://leetcode.com/problems/boats-to-save-people/ |
| Rating | ~1500-1549 (Phase 1 acquisition) |
| AC | Y (after 2 WA) |
| Time | — (derivation-clause phase) |
| Pattern | sort + two-pointer (pair extremes) |
| Outcome | **SOFT FAIL** — 2 WA-then-AC |
| Revision due | 2026-06-11 |

---

## Verbatim thinking (the derivation path)

1. **First model (wrong):** start from left, keep a running sum, reset + `count++` when it exceeds `limit`. Step-2 trace on the richest example `[3,2,2,1], limit=3` reproduced the stated answer `3` — but **by coincidence**: those weights never allow >2 people in a boat anyway, so the missing constraint stayed masked.
2. **WA #1** on `[3,8,7,1,4], limit=9` → realized input must be **sorted** first (else a small element gets paired with a big one, splitting one boat into two).
3. **WA #2** on `[5,1,4,2], limit=6` even after sorting → the running-sum model is still fundamentally wrong.
4. **The missed rule:** *each boat carries at most TWO people.* The running-sum approach assumed unlimited people per boat.
5. **Correct approach:** sort, then two pointers — `i` at lightest, `j` at heaviest. The heaviest person must sail regardless, so pair them with the lightest person that still fits. If `people[i]+people[j] <= limit` → both board (`i++`). Always `count++; j--`. Loop while `i <= j`.

## Solution (AC)

```java
class Solution {
    public int numRescueBoats(int[] people, int limit) {
        int count = 0;
        int n = people.length;
        Arrays.sort(people);
        int i = 0, j = n - 1;
        while (i <= j) {
            if (people[i] + people[j] <= limit) i++;
            count++;
            j--;
        }
        return count;
    }
}
```

**Complexity:** O(n log n) time (sort dominates), O(1) extra space.

---

## WA-cause

**WA-cause [read-error]:** missed the "each boat carries at most two people" constraint — built an unlimited-capacity running-sum model. The richest worked example masked it (its weights never permitted >2 per boat), so the Step-2 trace falsely confirmed a wrong model.

**WA-cause [untraced-submit]:** Step 3 (edge cases) was deliberately skipped on this problem. An all-light multi-person case (e.g. `[1,1,1], limit=5`) would have forced the question "does one boat hold all three?" and surfaced the at-most-2 rule before coding. Cost: 2 WA submissions vs ~5 min of edge cases.

## Lesson

Step 2 alone can **confirm a wrong model** when the richest example happens not to exercise the binding constraint. Step 3 (named edge cases that stress each rule) is the independent check that breaks it. Skipping Step 3 here cost exactly the 2 iterations the ritual is designed to prevent.
