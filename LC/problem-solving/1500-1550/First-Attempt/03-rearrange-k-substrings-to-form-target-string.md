# Rearrange K Substrings to Form Target String — First Attempt

## Problem

You are given two strings s and t, both of which are anagrams of each other, and an integer k. Your task is to determine whether it is possible to split the string s into k equal-sized substrings, rearrange the substrings, and concatenate them in any order to create a new string that matches the given string t. Return true if this is possible, otherwise, return false. An anagram is a word or phrase formed by rearranging the letters of a different word or phrase, using all the original letters exactly once. A substring is a contiguous non-empty sequence of characters within a string. Example 1:

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/rearrange-k-substrings-to-form-target-string/ |
| Rating | 1514 |
| AC | Y |
| Time | 14min |
| Pattern | frequency-count / chunk matching |
| Revision due | 2026-05-15 |
| Remark | Map with freq tracking, not Set — Set fails when t has duplicate chunks (says "exists" but you've only consumed one). Decrement freq per match. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
