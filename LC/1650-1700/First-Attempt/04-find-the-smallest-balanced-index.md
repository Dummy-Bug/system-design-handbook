# Find the Smallest Balanced Index — First Attempt

## Problem

You are given an integer array nums.

An index i is balanced if the sum of elements strictly to the left of i equals the product of elements strictly to the right of i.

If there are no elements to the left, the sum is considered as 0. Similarly, if there are no elements to the right, the product is considered as 1.

Return an integer denoting the smallest balanced index. If no balanced index exists, return -1.

 

Example 1:

Input: nums = [2,1,2]

Output: 1

Explanation:

For index i = 1:

	Left sum = nums[0] = 2

	Right product = nums[2] = 2

	Since the left sum equals the right product, index 1 is balanced.

No smaller index satisfies the condition, so the answer is 1.

Example 2:

Input: nums = [2,8,2,2,5]

Output: 2

Explanation:

For index i = 2:

	Left sum = 2 + 8 = 10

	Right product = 2 * 5 = 10

	Since the left sum equals the right product, index 2 is balanced.

No smaller index satisfies the condition, so the answer is 2.

Example 3:

Input: nums = [1]

Output: -1

For index i = 0:

	The left side is empty, so the left sum is 0.

	The right side is empty, so the right product is 1.

	Since the left sum does not equal the right product, index 0 is not balanced.

Therefore, no balanced index exists and the answer is -1.

 

Constraints:

	1 <= nums.length <= 10^5

	1 <= nums[i] <= 10^9

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-14 |
| Link | https://leetcode.com/problems/find-the-smallest-balanced-index/description/ |
| Rating | 1697 |
| AC | Y |
| Time | 30min (approach fully self-derived, overflow guard syntax fixed with help) |
| Pattern | Prefix sum + suffix product with early stop |
| Revision due | 2026-05-28 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Constraint reading**
- nums[i] >= 1, <= 10^9, n <= 10^5 → all positive, O(n log n) budget
- Immediate red flag: product of right side could blow up

**Step 2 — Naive approach and overflow analysis**
First idea: prefix sum array for left side, suffix product array for right side, iterate and compare. Clean O(n) approach but product overflows — (10^9)^5 = 10^45, nowhere near long range.

Sum is fine: 10^5 × 10^9 = 10^14, well within long (max ~9.2 × 10^18).

**Step 3 — Key insight: monotonicity**
Traversing left to right: sum always increases, product either stays same or decreases (nums[i] >= 1 so multiplying always makes product >= current). Flipped: traversing right to left, sum decreases and product increases.

This means sum and product can cross at most once. As soon as product > sum, they can never be equal again — early stop.

**Step 4 — Overflow guard**
The early stop prevents ever computing a product that exceeds sum. But the multiplication itself could overflow before the check fires. Fix: check before multiplying using rearranged inequality:

```
product * nums[i] > sum  →  product > sum / nums[i]
```

Integer division safe since all values positive. If this holds, break before multiplying.

**Step 5 — Wrong attempts at overflow detection**
- Tried MOD: `(product * nums[i]) % MOD < product` — wrong, mod loses the actual value, comparison against sum becomes meaningless
- Tried: `product < sum / nums[i]` — sign flipped, breaks when it shouldn't and continues when it should stop

---

#### What should have been thought (gaps)

**Gap 1 — MOD reflex**
When overflow appears, the instinct was to reach for mod. Mod only helps when you care about remainders or divisibility — never when you need to compare actual magnitudes. The correct reflex is to rearrange the inequality to avoid the large multiplication entirely.

**Gap 2 — Inequality direction**
`product > sum / nums[i]` means "next product would exceed sum, stop." Wrote it flipped first. Before writing any inequality, state in plain English what the condition means, then translate.

---

#### Key snippet — overflow guard before multiply

```java
if ((sum < product) || (product > sum / nums[i])) break;
product *= nums[i];
```

The rearrangement `product > sum / nums[i]` avoids the multiplication entirely — check before you multiply, not after.

#### Complexity

O(n) time, O(1) space. Early stop guarantees product never overflows long.

---
