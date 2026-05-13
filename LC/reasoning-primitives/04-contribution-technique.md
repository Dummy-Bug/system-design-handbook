# Contribution Technique — Computing Pair Sums Without Iterating Pairs

Some problems ask you to compute a sum over all pairs of elements. The brute force is to iterate every pair — but with n=10^5 elements, that's n*(n-1)/2 ≈ 5*10^9 pairs. Way too slow.

The contribution technique flips the loop: instead of asking "what does each pair contribute?", ask "what does each individual element contribute across all pairs it's involved in?" If you can compute that per-element contribution in O(1), the total is O(n).

---

## The problem

Array `[1, 2, 3, 4, 5]`. Find the sum of absolute differences across all pairs.

Brute force: iterate every pair (i, j), compute |nums[i] - nums[j]|, add to total. O(n²).

---

## Switching the perspective

Pick any element — say `3` at index 2. It appears in pairs with every other element:

```
|3-1| = 2
|3-2| = 1
|3-4| = 1
|3-5| = 2
Total contribution of 3: 6
```

The array is sorted, so elements to the left are smaller and elements to the right are larger. The absolute difference splits cleanly:

- Left elements (smaller): |nums[i] - nums[j]| = nums[i] - nums[j]
- Right elements (larger): |nums[i] - nums[j]| = nums[j] - nums[i]

**Left contribution of element at index i:**

There are `i` elements to the left. nums[i] appears i times, and you subtract the sum of all left elements:

```
left = nums[i] * i - prefixSum[i]
```

For element 3 (index 2): 3*2 - (1+2) = 6 - 3 = 3. ✓

**Right contribution of element at index i:**

There are `n-1-i` elements to the right. You take the sum of all right elements and subtract nums[i] appearing (n-1-i) times:

```
right = suffixSum[i] - nums[i] * (n - 1 - i)
```

For element 3 (index 2, n=5): (4+5) - 3*2 = 9 - 6 = 3. ✓

**Total contribution of element at index i:**

```
contribution[i] = nums[i] * i - prefixSum[i] + suffixSum[i] - nums[i] * (n - 1 - i)
```

Sum contributions across all elements → answer.

---

## Complexity

- Sort: O(n log n)
- Prefix and suffix sums: O(n)
- One pass to sum contributions: O(n)

Total: O(n log n). Down from O(n²) brute force.

---

## The thinking shift

```
Brute force:  for each pair (i,j) → compute something → add to total
Contribution: for each element i → compute its total impact across all pairs → add to total
```

Same answer, completely different loop structure. The key enabler is that once the array is sorted, the contribution of each element splits into a left part and right part — both computable in O(1) using prefix sums.

---

## When to reach for the contribution technique

Trigger: the problem asks for a sum (or count) over all pairs, and n is large enough that O(n²) is too slow.

The question to ask: "Instead of iterating pairs, can I compute how much each individual element contributes to the total?" If the contribution of element i can be expressed using prefix sums or simple arithmetic — O(n²) collapses to O(n log n).
