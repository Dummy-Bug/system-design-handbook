# Minimum Operations to Make Array Non-Decreasing — First Attempt

## Problem

You are given an integer array nums of length n.

In one operation, you may choose any subarray nums[l..r] and increase each element in that subarray by x, where x is any positive integer.

Return the minimum possible sum of the values of x across all operations required to make the array non-decreasing.

An array is non-decreasing if nums[i] <= nums[i + 1] for all 0 <= i < n - 1.

 

Example 1:

Input: nums = [3,3,2,1]

Output: 2

Explanation:

One optimal set of operations:

	Choose subarray [2..3] and add x = 1 resulting in [3, 3, 3, 2]

	Choose subarray [3..3] and add x = 1 resulting in [3, 3, 3, 3]

The array becomes non-decreasing, and the total sum of chosen x values is 1 + 1 = 2.

Example 2:

Input: nums = [5,1,2,3]

Output: 4

Explanation:

One optimal set of operations:

	Choose subarray [1..3] and add x = 4 resulting in [5, 5, 6, 7]

The array becomes non-decreasing, and the total sum of chosen x values is 4.

 

Constraints:

	1 <= n == nums.length <= 10^5

	1 <= nums[i] <= 10^9

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-13 |
| Link | https://leetcode.com/problems/minimum-operations-to-make-array-non-decreasing/description/ |
| Rating | 1662 |
| AC | Y |
| Time | ~1h32min (1h31min brainstorm + <1min code) |
| Pattern | Greedy — fix each drop independently, extend to end |
| Revision due | 2026-05-27 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Constraint reading (done first, correctly)**
- n <= 10^5 → O(n log n) budget max
- nums[i] >= 1 and <= 10^9 → all positive, no zeros, no negatives
- n >= 1 → single element is trivially non-decreasing

*Good: constraint reading was the first move, not the problem statement. This is the correct habit.*

**Step 2 — Hit ambiguity in problem statement**
The line "Return the minimum possible sum of the values of x across all operations" wasn't clear. Instead of guessing, moved to tracing examples to understand what it means concretely.

*Good: when a line is ambiguous, examples are the right tool. Don't proceed on a shaky understanding of the problem.*

**Step 3 — Tracing Example 1: [3,3,2,1] → output 2**
From operation: choose [2..3], add x=1 → [3,3,3,2], then choose [3..3], add x=1 → [3,3,3,3].

Observations made:
- We could have added more than 1 but didn't — x is kept minimum per operation to keep total sum low
- We could have only fixed index 2 (subarray [2..2]) but instead took [2..3] — reasoning: by pre-lifting index 3 along with index 2, the next operation needs smaller x to fix index 3's drop. This reduces total sum.

Still not fully confident in the pattern — went to example 2 to verify.

**Intermediate hypothesis (before example 2)**
When the first decrease (pivot) occurs, it might be optimal to raise all elements in that subarray to be equal (lift to the pivot value). Not proved yet — continuing to example 2 to validate or invalidate.

**Step 4 — Tracing Example 2: [5,1,2,3] → output 4**
First pivot at index 0→1 (5 > 1, drop of 4). Thought: raise everything to 5 — but adding x=4 to [1..3] makes array [5,5,6,7], overshooting elements 2 and 3.

Key unlock: **overshooting does not matter.** The goal is non-decreasing, not equal. The problem only charges the sum of x values — not how far each element was lifted. [5,5,6,7] is non-decreasing and the cost is still just 4.

This invalidates the earlier "make equal" hypothesis. The problem is purely about minimum sum of x, and overshooting is free.

→ Going to re-read the full problem with this corrected understanding before forming an approach.

**Step 5 — First approach attempt (flawed)**

Idea: when a drop is found at i→i+1, start a subarray from i+1, extend it until nums[j] > nums[i] (the array recovers past the original value). Add x = nums[i] - min(subarray) to the whole subarray in one operation. Move i = j.

Traced on [4,2,1,3,1,4,5,2]:
- Drop at 0→1 (4 > 2). Subarray [1..5], min = 1, x = 4-1 = 3.
- After operation: [4, 5, 4, 6, 4, 7, 5, 2]. Move i = 6.

**Caught before submission: [4, 5, 4, 6, 4, 7, 5, 2] is NOT non-decreasing.**
- 5 > 4 at positions 1→2 ✗
- 6 > 4 at positions 3→4 ✗

The flaw: adding the same x to every element in a subarray lifts them all equally but does NOT fix internal violations. [2,1,3,1] + 3 = [5,4,6,4] — internal drops remain. One operation cannot fix a segment with multiple internal violations.

Approach abandoned.

---

**Step 6 — Second approach attempt (closer, still suboptimal)**

Refined idea: fix one drop at a time, extend subarray until the next element >= nums[i]. Add x = nums[i] - nums[i+1] (just the immediate drop). Self-test on [4,2,1,3,1,4,5,2] gave total cost = 9.

When shown that 8 is achievable, identified the flaw: stopping short at index j lifts element j but not element j+1. If element j gets lifted past element j+1 — **a new drop is created at j→j+1 that didn't exist before**. Each new drop costs an extra operation later.

Concrete example: op 3 added +2 to [4..5]. Element at index 5 went from 4 to 6. Element at index 6 stayed at 5. New drop 6→5 created. That extra drop cost +1 in the final sum.

**Step 7 — Correct insight derived**

Always extend operations to the end of the array. When operation covers [i+1..n-1]:
- Drop at i→i+1 is fixed by exactly x
- No right boundary → no new drop can be created
- All elements from i+1 onwards get lifted equally → relative differences within that range don't change

Since every operation extends to the end, the cumulative offset is the same for all elements from any point onwards. The drop between i and i+1 is always exactly nums[i] - nums[i+1] from the original array — offset cancels on both sides.

**Therefore: no array modification needed. Just iterate the original array and sum all positive drops.**

**Step 8 — Edge cases (caught before coding)**
1. n=1 → loop runs 0 times → return 0 ✓
2. Already sorted → no drops → return 0 ✓
3. Overflow → max sum = 10^9 × 10^5 = 10^14 → must use `long` ✓ (individual diff up to 10^9-1, fits in int safely)

---

#### What should have been thought (gaps)

**Gap 1 — Right boundary instinct**
The correct question after seeing the operation structure: *"What happens at the right boundary when I stop short?"* Stopping before the end always risks creating a new drop. Default when minimizing future cost with subarray additions: **extend to the end**.

**Gap 2 — Faster path to formula**
After the "overshooting is free" insight from example 2, the direct question is: *"What's the minimum I must pay per drop?"* Each drop must be paid independently — the offset cancels. This leads straight to the formula without detours through segment extension ideas.

---

#### Complexity

O(n) time, O(1) space.

---
