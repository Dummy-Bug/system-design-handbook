# Empty and single-element inputs

> [!info] The smallest valid inputs (n=0, n=1) are where most bugs hide. Always handle them explicitly OR confirm the constraints rule them out.

---

## When to suspect it

Always — unless the constraints explicitly say `n ≥ 2` or higher.

Trigger conditions:
- `0 ≤ n` in constraints (empty allowed)
- `1 ≤ n` in constraints (single allowed)
- The algorithm assumes at least two elements (pair operations, differences, comparisons)
- Initial accumulator values matter (max/min, product)

---

## Common empty/single bugs

### 1. Empty array — accessing index 0

```java
// BUGGY
int max = nums[0];  // ArrayIndexOutOfBounds if nums is empty
for (int i = 1; i < nums.length; i++) {
    max = Math.max(max, nums[i]);
}

// FIX — handle empty separately, or use Integer.MIN_VALUE
if (nums.length == 0) return /* problem-specific default */;
int max = nums[0];
```

### 2. Single element — pair operations

```java
// Problem: max difference between consecutive elements
// BUGGY
for (int i = 1; i < n; i++) {
    maxDiff = Math.max(maxDiff, nums[i] - nums[i - 1]);
}
return maxDiff;  // Returns 0 (uninitialized) for n=1 — is that correct?

// FIX — check problem semantics, return appropriate value
if (n < 2) return 0;  // or -1, depending on problem
```

### 3. Empty string operations

```java
// BUGGY — String.charAt(0) on empty string throws
char first = s.charAt(0);

// FIX
if (s.isEmpty()) return /* default */;
char first = s.charAt(0);
```

### 4. Accumulator initialization

```java
// BUGGY — product of empty array
int product = 1;  // is 1 the right default? depends on problem

// BUGGY — max of empty
int max = Integer.MIN_VALUE;  // is MIN_VALUE valid output? depends

// SAFER — guard the call
if (nums.length == 0) return /* explicit default */;
```

### 5. Sliding window with k > n

```java
// BUGGY — when k > n.length, no valid window exists
int n = nums.length;
for (int i = 0; i <= n - k; i++) {  // loop never executes if k > n
    // process window
}
return windowMax;  // returns uninitialized

// FIX — explicit guard
if (k > n) return /* default */;
```

### 6. Recursion base cases

```java
// BUGGY — no base case for n=0
int helper(int[] nums, int i) {
    return nums[i] + helper(nums, i + 1);  // infinite recursion
}

// FIX
int helper(int[] nums, int i) {
    if (i >= nums.length) return 0;
    return nums[i] + helper(nums, i + 1);
}
```

---

## Problem-specific defaults

What to return when input is empty or single-element depends on the problem:

| Problem type | Empty | Single |
|--------------|-------|--------|
| Sum | 0 | nums[0] |
| Product | 1 | nums[0] |
| Max/Min | undefined → return -1 / throw | nums[0] |
| Count of pairs | 0 | 0 |
| Max difference | undefined → return 0 or -1 | 0 |
| Number of subarrays | 0 | 1 (the single element itself) |
| Substring count | 0 | 1 (single char is a substring) |
| Length of longest valid X | 0 | 1 (if single qualifies) |

**Always check the problem description for the expected behavior on edge inputs.**

---

## Template for spotting in future problems

Before submitting:

1. **Read constraints**: is `n = 0` or `n = 1` possible? If yes → must handle explicitly.
2. **Manually trace** with `nums = []`, `nums = [x]`:
   - Does any loop body execute zero times?
   - Are accumulators meaningful with their initial value?
   - Are post-loop flushes still needed?
3. **For string problems**, also trace `s = ""`, `s = "x"`.
4. **For tree/linked list**, trace `root = null`, single-node tree.

---

## Test inputs to always run mentally

```
Array: [], [x], [x, x] (duplicates), [x, y] (distinct), max-size
String: "", "x", "xx", "ab", longest valid
Tree: null, single-node, two-node (left + right separately), max depth
LinkedList: null, single-node, two-node, cycle (if relevant)
```

---

## Source problems

Every problem ever. Specifically:

- LC 121 — Best Time to Buy and Sell Stock (n=1 edge)
- LC 53 — Maximum Subarray (n=1 returns nums[0])
- LC 152 — Maximum Product Subarray (single negative element)
- Anything with constraint `0 ≤ n` rather than `1 ≤ n`

---

## Related patterns

- [[07-boundary-first-last-element.md]] — broader boundary handling
- [[09-tie-breaking-rules]] — what to return when "no answer exists"
