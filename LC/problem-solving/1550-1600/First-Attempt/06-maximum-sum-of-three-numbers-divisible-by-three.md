# Maximum Sum of Three Numbers Divisible by Three — First Attempt

## Problem

You are given an integer array nums. Your task is to choose exactly three integers from nums such that their sum is divisible by three. Return the maximum possible sum of such a triplet. If no such triplet exists, return 0. Example 1: Input: nums = [4,2,3,1] Output: 9 Explanation: The valid triplets whose sum is divisible by 3 are: (4, 2, 3) with a sum of 4 + 2 + 3 = 9. (2, 3, 1) with a sum of 2 + 3 + 1 = 6. Thus, the answer is 9. Example 2: Input: nums = [2,1,5] Output: 0 Explanation: No triplet forms a sum divisible by 3, so the answer is 0. Constraints: 3 <= nums.length <= 105 1 <= nums[i]

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-06 |
| Link | https://leetcode.com/problems/maximum-sum-of-three-numbers-divisible-by-three/ |
| Rating | 1585 |
| AC | Y |
| Time | 70min |
| Pattern | mod bucketing + greedy |
| Revision due | 2026-05-20 |
| Remark | Group nums by mod 3 into 3 buckets. Keep top 3 per bucket. Valid combos: (0,0,0), (1,1,1), (2,2,2), (0,1,2). Max across all valid combos. Hinted: "mod 3 → drill it". Two bugs hit: (1) TreeSet silently drops duplicates — [2,8,2] has two 2s, second ignored, bucket size stays 2, sum skipped → WA. Fix: ArrayList. (2) max tracking was inside size==3 block, missing cross-bucket combo when any bucket has <3 elements. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
