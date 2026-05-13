# Distinct indices → frequency map, not set

> [!info] When the problem requires distinct indices but allows shared values, a `Set` is insufficient — you need a frequency map to verify multiple occurrences.

---

## When to suspect it

Trigger keywords/phrases in the problem statement:

- "**distinct indices, but may share the same value**"
- "**must have distinct indices**"
- "indices `i ≠ j` such that `nums[i] == X` and `nums[j] == Y`"
- "the same element cannot be used twice"
- Any "two-sum-style" problem where the target value could equal `nums[i]` itself

If you see any of these, **you cannot use a plain `Set`** — you need frequency tracking.

---

## The bug — concrete failing example

**Problem:** [Identify the Largest Outlier in an Array](https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/) (LC 1644)

For each candidate outlier `nums[i]`, compute target `(tSum - nums[i]) / 2`. Check if target exists in the array (at a *different* index than `i`).

**Failing test:** `nums = [1, 2, 4, 5]`, tSum = 12

| i | nums[i] | target = (12 − nums[i])/2 | set.contains(target)? | Verdict |
|---|---------|---------------------------|-----------------------|---------|
| 0 | 1       | 5.5                       | skip (parity)         | —       |
| 1 | 2       | 5                         | YES ✓                 | maxOutlier = 2 ✓ |
| 2 | **4**   | **4**                     | **YES (itself!)** ✗   | **maxOutlier = 4** ✗ |
| 3 | 5       | 3.5                       | skip (parity)         | —       |

`Set` returns **4**, but 4 is NOT a valid outlier — the only element with value 4 is the outlier candidate itself; there's no separate sum_element with value 4.

Expected output: **2** (specials = [1, 4], sum_element = 5).

---

## The fix

Use a frequency map. When `target == nums[i]`, require **frequency ≥ 2**:

```java
Map<Integer, Integer> freq = new HashMap<>();
for (int x : nums) {
    freq.put(x, freq.getOrDefault(x, 0) + 1);
}

for (int i = 0; i < n; i++) {
    int target = (tSum - nums[i]) / 2;
    int required = (target == nums[i]) ? 2 : 1;
    if (freq.getOrDefault(target, 0) >= required) {
        maxOutlier = Math.max(maxOutlier, nums[i]);
    }
}
```

---

## Why it works

- If `target != nums[i]`: one occurrence is enough — the two values are at different indices by definition.
- If `target == nums[i]`: the lookup is asking for *another* index with the same value, so we need at least 2 occurrences total (one for the outlier slot, one for the sum_element slot).

The Set can't distinguish these two cases — it only tracks existence, not multiplicity.

---

## Source problems

- LC 3289 — [Identify the Largest Outlier in an Array](https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/) (1644)
- LC 1 — [Two Sum](https://leetcode.com/problems/two-sum/) — same trigger when `nums[i] * 2 == target`
- LC 167 — Two Sum II — sorted variant, same trap

---

## Template for spotting in future problems

When you read the problem statement:

1. Search for the word "**distinct**". If found near "indices" or "elements" → flag.
2. Ask: "Does the lookup value depend on `nums[i]` itself?" → if yes, can it equal `nums[i]`?
3. Default to frequency map. Only downgrade to Set after explicitly proving duplicates can't matter.

**Algebraic check (most reliable):** Set up the equation for when `target = nums[i]`. If a valid input satisfies that equation, you need a frequency map.

For the outlier problem: `target = nums[i]` → `nums[i] = tSum / 3` → any array where one element equals tSum/3 will trigger the bug.

---

## Related patterns

- [[02-self-reference-in-lookup]] — the broader category this falls under
- [[06-adversarial-test-construction]] — how to construct the failing test case yourself
