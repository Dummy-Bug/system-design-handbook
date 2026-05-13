# Self-reference in lookup

> [!info] When iterating index `i` and looking up some `f(nums[i])` in the array, the lookup may accidentally return `nums[i]` itself — which usually violates the problem's distinct-index requirement.

---

## When to suspect it

This pattern triggers in **almost any problem** with the following structure:

```
for each i in 0..n-1:
    target = some_function_of(nums[i])  // computed value derived from current element
    if (lookup(target)):                  // does this value exist in the array?
        do_something()
```

The lookup says "yes, target exists" — but the only occurrence of `target` may BE `nums[i]` itself, which usually violates "distinct indices" or "different elements" requirements.

**Common derivations that trigger this:**

- `target = sum - nums[i]` (two-sum, complement lookup)
- `target = nums[i] * 2` (find half / double)
- `target = (totalSum - nums[i]) / 2` (outlier-style)
- `target = nums[i] - k` or `nums[i] + k` (pair difference)
- `target = some_hash(nums[i])` (normalized lookup)

---

## The bug — concrete failing example

**Two Sum-style problem:** find indices `i ≠ j` where `nums[i] + nums[j] == target`.

```java
// BUGGY
Set<Integer> seen = new HashSet<>();
for (int x : nums) seen.add(x);

for (int i = 0; i < n; i++) {
    int complement = target - nums[i];
    if (seen.contains(complement)) {  // BUG: could be nums[i] itself
        return new int[]{i, indexOf(complement)};
    }
}
```

**Failing test:** `nums = [3, 5]`, `target = 6` (complement of 3 is 3, but only one 3 in array — `seen.contains(3)` returns true, falsely claiming a pair exists).

---

## The fix — three options

### Option 1: Build map AFTER current index
```java
Map<Integer, Integer> seen = new HashMap<>();
for (int i = 0; i < n; i++) {
    int complement = target - nums[i];
    if (seen.containsKey(complement)) {
        return new int[]{seen.get(complement), i};
    }
    seen.put(nums[i], i);  // add AFTER checking
}
```
This works because at the time of check, `seen` contains only `nums[0..i-1]` — never `nums[i]` itself.

### Option 2: Frequency map with multiplicity check
```java
Map<Integer, Integer> freq = ...;  // pre-built
for (int i = 0; i < n; i++) {
    int complement = target - nums[i];
    int required = (complement == nums[i]) ? 2 : 1;
    if (freq.getOrDefault(complement, 0) >= required) {
        // valid pair exists
    }
}
```

### Option 3: Check index inequality explicitly
```java
Map<Integer, Integer> indexOf = ...;
for (int i = 0; i < n; i++) {
    int complement = target - nums[i];
    if (indexOf.containsKey(complement) && indexOf.get(complement) != i) {
        // valid
    }
}
```
(Fragile if duplicates exist — only stores one index per value.)

---

## When to use which fix

| Scenario | Use |
|----------|-----|
| Need to return indices, single pair | Option 1 (build-as-you-go) |
| Need to count or maximize over all valid pairs | Option 2 (frequency map) |
| Need ordered pairs (i, j) with i < j | Option 1 |
| Duplicates can't exist | Plain Set works — but verify first |

---

## Template for spotting in future problems

Before writing any "for each element, look up derived value" loop, run these two checks:

1. **Compute the derivation symbolically.** What is `target` in terms of `nums[i]`?
2. **Ask: can `target` equal `nums[i]`?** Algebraically solve. If yes → self-reference branch required.

Example for outlier problem: `target = (tSum - nums[i]) / 2`. Setting `target = nums[i]` gives `nums[i] = tSum/3`. So any element equal to `tSum/3` triggers the bug.

---

## Source problems

- LC 1 — Two Sum (the classic example)
- LC 3289 — Identify the Largest Outlier in an Array (1644)
- LC 532 — K-diff Pairs in an Array (when `k == 0`)
- LC 454 — 4Sum II

---

## Related patterns

- [[01-distinct-indices-frequency-map]] — the specific Set-vs-Map fallout
- [[06-adversarial-test-construction]] — solve for the failing input algebraically
