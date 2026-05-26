# Final Element After Subarray Deletions — First Attempt

## Problem

You are given an integer array nums. Two players, Alice and Bob, play a game in turns, with Alice playing first. In each turn, the current player chooses any subarray nums[l..r] such that r - l + 1 < m, where m is the current length of the array. The selected subarray is removed, and the remaining elements are concatenated to form the new array. The game continues until only one element remains. Alice aims to maximize the final element, while Bob aims to minimize it. Assuming both play optimally, return the value of the final remaining element. Example 1: Input: nums = [1,5,2] Output: 2 Explan

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-05 |
| Link | https://leetcode.com/problems/final-element-after-subarray-deletions/ |
| Rating | 1591 |
| AC | Y |
| Time | 46min |
| Pattern | game theory / one-move reduction |
| Revision due | 2026-05-19 |
| Remark | Answer = max(nums[0], nums[n-1]). Game theory is a misdirection — Alice picks subarray of length n-1 on turn 1, leaving whichever endpoint is larger, so Bob never plays. Took 46min via longer reasoning (Bob removes max → Alice forces extremes) before realising turn-1 reduction. Cleanup: drop the maxEle for-loop, it's dead code. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
