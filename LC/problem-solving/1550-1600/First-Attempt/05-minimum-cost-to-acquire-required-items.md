# Minimum Cost to Acquire Required Items — First Attempt

## Problem

You are given five integers cost1, cost2, costBoth, need1, and need2. There are three types of items available: An item of type 1 costs cost1 and contributes 1 unit to the type 1 requirement only. An item of type 2 costs cost2 and contributes 1 unit to the type 2 requirement only. An item of type 3 costs costBoth and contributes 1 unit to both type 1 and type 2 requirements. You must collect enough items so that the total contribution toward type 1 is at least need1 and the total contribution toward type 2 is at least need2. Return an integer representing the minimum possible total cost to ach

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-05 |
| Link | https://leetcode.com/problems/minimum-cost-to-acquire-required-items/ |
| Rating | 1580 |
| AC | Y |
| Time | 39min |
| Pattern | greedy + case analysis |
| Revision due | 2026-05-19 |
| Remark | Three item types: type1 (covers need1), type2 (covers need2), type3 (covers both). Core split: if cost1+cost2 < costBoth → buy separately; else use type3 for min(need1, need2) overlap, fill remainder with cheaper of individual vs another type3. Bug: case 3 (cost2 >= costBoth) used `cost2` instead of `cost1` for excess need1 items — classic mirror-case copy-paste. Self-caught before looking at any hint. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
