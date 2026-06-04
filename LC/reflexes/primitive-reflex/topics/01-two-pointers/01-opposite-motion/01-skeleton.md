# Atom 01 — Opposite-end two pointers

Tier 1 (Pointers) · prereq: sorting-as-preprocessing
*Derived Socratically 2026-06-03.*

## ① Trigger (the felt signal)

The array is sorted (or affordably sortable), you want a pair/triplet meeting a sum/difference/area condition, and you catch yourself about to write a nested loop over all pairs.

## ② Why naive is broken (with numbers)

Two Sum on sorted `[2,7,11,15]`, target `9`. Naive checks all `C(n,2)` pairs = `O(n²)` → `10¹⁰` at `n=10⁵` → TLE.

The naive loop throws away the sortedness. Sit at both ends, `lo` and `hi`:

- `a[lo]+a[hi] > target` → `a[hi]` is the largest value, and `a[lo]` is the smallest partner it can ever get. If even that smallest sum overshoots, `a[hi]` is in no valid pair → discard it, `hi--`.
- `a[lo]+a[hi] < target` → mirror: `a[lo]` with the largest partner still undershoots → `a[lo]` is dead, `lo++`.

The keystone, in my own words: *with this `lo` we can't reach the target, because `a[hi]` is the largest partner left.* Each comparison kills one element → `O(n)` scan. Monotonicity is what makes discarding a whole end safe.

Trace `[2,7,11,15]`, t=9: `2+15=17>9 → hi--`, `2+11=13>9 → hi--`, `2+7=9 ✓`.

## ③ The move

Converge from both ends; the comparison tells you which end to retract.

## ④ Code skeleton (blank-page this, timed)

```java
int lo = 0, hi = n - 1;
while (lo < hi) {                  // stop when they meet; one item can't pair with itself
    int sum = a[lo] + a[hi];
    if (sum == target) break;      // found a[lo], a[hi]
    else if (sum < target) lo++;   // need bigger
    else hi--;                     // need smaller
}
```

Complexity: `O(n)` scan; `O(n log n)` if you sort it yourself.

## ⑤ Recognition — status: derived for sum-pair only; breadth pending

Self-reported gap (2026-06-03): recalled the mechanic but couldn't name a second disguise beyond Two Sum. Recognition reps queued in ⑦ — this is the stage to drill.

## ⑥ Confusion matrix (the discriminator)

| Confused with | Discriminator |
|---|---|
| #2 same-direction | converge from both ends *vs* both sweep forward building a prefix |
| Sliding window | pick 2 endpoints *vs* maintain a contiguous subarray |
| Binary search | move two bounds at once, `O(n)` *vs* fix one, search its complement, `O(n log n)` |
| Hashset two-sum | opposite-end when sorted / want `O(1)` space / geometry *vs* hashset when unsorted + existence-only |

## ⑦ Practice set — pending (one per distinct facet, no redundant reps)

- [ ] Container With Most Water — the area / `min(height)` invariant (retract the shorter wall; a different proof than the sum case)
- [ ] 3Sum — composition: fix one element, opposite-end the rest
- [ ] Valid Palindrome *or* Squares of a Sorted Array — cold recognition on a surface that never says "two pointers"

## ⑧ Reflex check

Prompt: *sorted array, find a pair hitting a target sum — move, one breath?*
Answer: *two pointers from both ends; `sum<t → lo++`, `sum>t → hi--`; each step kills one end, `O(n)`.*
