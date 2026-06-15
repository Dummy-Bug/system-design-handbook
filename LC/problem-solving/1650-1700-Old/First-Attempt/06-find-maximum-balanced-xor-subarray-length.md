# Longest Subarray with XOR Zero and Equal Even/Odd Count — First Attempt

## Problem

Given an integer array nums, return the length of the longest subarray that has a bitwise XOR of zero and contains an equal number of even and odd numbers. If no such subarray exists, return 0.

 

Example 1:

Input: nums = [3,1,3,2,0]

Output: 4

Explanation:

The subarray [1, 3, 2, 0] has bitwise XOR 1 XOR 3 XOR 2 XOR 0 = 0 and contains 2 even and 2 odd numbers.

Example 2:

Input: nums = [3,2,8,5,4,14,9,15]

Output: 8

Explanation:

The whole array has bitwise XOR 0 and contains 4 even and 4 odd numbers.

Example 3:

Input: nums = [0]

Output: 0

Explanation:

No non-empty subarray satisfies both conditions.

 

Constraints:

	1 <= nums.length <= 10^5

	0 <= nums[i] <= 10^9

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-14 |
| Link | TBD |
| Rating | ~1650-1700 |
| AC | — |
| Time | ongoing |
| Pattern | TBD |
| Revision due | TBD |

---

#### Thought process (what was actually going through the mind)

**Step 1 — First observation**
XOR = 0 only if equal odd and even numbers — quickly falsified on [1,2,3] (XOR = 0, but 2 odds and 1 even). These are independent conditions. Need to check count separately.

**Step 2 — Prefix XOR approach**
Use a HashMap storing prefix XOR → first index. When the same prefix XOR appears again at index j, subarray (i+1..j) has XOR = 0. Standard prefix XOR trick.

To check equal odd/even within that range: maintain a `prefixOdd` array counting odds up to index i. For a range (i+1..j), odd count = `prefixOdd[j] - prefixOdd[i]`, even count = range_length - odd count. Equal if odd count = range_length / 2.

**Step 3 — The overwrite problem**
When the same XOR value appears at multiple indices, keeping only the first gives the longest subarray — but that range might not have equal odd/even. Keeping only the latest index might satisfy odd/even but gives a shorter subarray.

Naive fix: store all indices for each XOR value, then for each new occurrence scan all prior indices to find the one giving maximum valid length. Worst case O(n²) for arrays like [1,2,1,2,1].

**Step 4 — Challenge analysis**
Tested [1,2,1,2,1] and [1,1,2,2,1] to find a case where overwriting breaks the answer. Both produced subarray length 4. Could not construct a counterexample to the "keep first index" strategy. Hypothesis: keeping the first index is always sufficient — need to prove or disprove.

**Step 5 — Hypothesis falsified**
[3,1,3,2,0,1,3,2] → prefix XOR array [3,2,1,3,3,2,1,3]. XOR=3 first appears at index 0 with unequal even/odd. Keeping only the oldest (index 0): range (0..n-1) has 4 odd, 3 even — not equal, discarded. But XOR=3 also appears at index 3 with equal even/odd (2+2). Using index 3 as start gives a valid answer. Storing only the oldest fails.

**Step 6 — 2-slot approach considered and rejected**
Thought: keep at most 2 entries per XOR value — oldest and one fallback. Falsified: if 3+ distinct `(xor, diff)` states appear for the same XOR value, a 2-slot cap drops entries still needed later. 2-slot is not sufficient in general.

**Step 7 — Hint taken (1h43min, no editorial before hint)**
Hint: maintain `(pxor, diff)` as combined hashmap key where `diff = evens - odds`. Store first occurrence of each state.

**Step 8 — Key insight after hint**
Same prefix-cancellation trick applied to two conditions simultaneously:
- Same `pxor` at i and j → XOR of range (i+1..j) = 0
- Same `diff` at i and j → diff changed by 0 in that range → equal even and odd

One hashmap, one pass, one key per combined state. First occurrence stored — earliest index gives longest range.

**Step 9 — Bit-packing technique for 2D key**
Encoding `(pxor, diff)` into a single `long`:
```
long key = ((long) pxor << 32) ^ (diff + 100001);
```
- `pxor` shifted into upper 32 bits
- `diff` offset by 100001 (makes it always positive, fits in 18 bits) dropped into lower bits
- XOR combines them without collision since bit ranges don't overlap

Pattern seen in LC-874 and LC-1128 as well. Need more problems using this to internalize — **flag: solve more 2D-state hashmap problems where encoding two ints into one long is the key.**

---
