# Two-Pointers — Family Syllabus

Status: ✅ AUDITED-COMPLETE (2026-06-03). The family is closed — every two-pointer variant lands in exactly one of 6 atoms.

Discriminator: **pointer motion**. (Windowed two-pointers are excluded → Sliding Window, separate family.)

Robustness goal: with this catalog complete, the only failure on a two-pointer problem is **mapping the problem to the right motion** — never a missing primitive.

---

## Variant catalog (by motion) — with LC problems

### A. Converging — opposite ends `→ ←`  → Atom 1
| Variant | LC |
|---|---|
| Pair sum on sorted | Two Sum II (167) |
| k-sum by composition (fix + converge) | 3Sum (15), 4Sum (18), 3Sum Closest (16) |
| Area between two walls | Container With Most Water (11) |
| Trapping water (two-pointer form) | Trapping Rain Water (42) |
| Palindrome verification | Valid Palindrome (125), Valid Palindrome II (680) |
| Reverse in place | Reverse String (344), Reverse Vowels (345) |
| Merge-from-ends into sorted output | Squares of a Sorted Array (977) |

### B. Parallel, one array, read/write `→ →`  → Atom 2
| Variant | LC |
|---|---|
| Dedup sorted | Remove Duplicates (26) |
| Remove element by value | Remove Element (27) |
| Compact / move-to-end | Move Zeroes (283) |
| Dedup allowing ≤k copies | Remove Duplicates II (80) |

### C. Parallel, two sequences `→ →` ×2  → Atom 3
| Variant | LC |
|---|---|
| Asymmetric (needle/haystack) | Is Subsequence (392) |
| Symmetric advance-the-smaller + write | Merge Sorted Array (88) |
| Sorted intersection, dedup output | Intersection of Two Arrays II (350) |
| Two pointers from the end (recognition twist) | Backspace String Compare (844) |

### D. Different speeds `→ →→` (fast & slow)  → Atom 4
| Variant | LC |
|---|---|
| Cycle detection (Floyd) | Linked List Cycle (141) |
| Cycle entry point | Linked List Cycle II (142) |
| Find middle | Middle of the Linked List (876) |
| Nth-from-end via fixed gap | Remove Nth Node From End (19) |
| Functional-graph cycle | Happy Number (202), Find the Duplicate Number (287) |

### E. Diverging — expand around center `← →`  → Atom 5
| Variant | LC |
|---|---|
| Longest palindromic substring | Longest Palindromic Substring (5) |
| Count palindromic substrings | Palindromic Substrings (647) |
| Locate + expand outward | Find K Closest Elements (658) |

### F. Multi-region in-place (3 pointers)  → Atom 6
| Variant | LC |
|---|---|
| Dutch-flag / 3-way partition | Sort Colors (75) |
| Quickselect / quicksort partition | Kth Largest Element (215) |

---

## Atoms (collapsed — distinct skeleton = atom; rest are costumes)

| # | Atom | Motion | Folder | Status |
|---|---|---|---|---|
| 1 | Opposite-end (converging) | `→ ←` | `01-opposite-motion/` | mechanic ✓; recognition reps pending |
| 2 | Same-direction (single array) | `→ →` | `02-same-direction/` | covered ✓ (overwrite + swap) |
| 3 | Two sequences | `→ →` ×2 | `03-two-sequences/` | both facets ✓ |
| 4 | Fast & slow | `→ →→` | `04-fast-slow/` | cycle-detect ✓ + middle ✓; entry/nth/functional queued |
| 5 | Diverging / expand-around-center | `← →` | `05-diverging-expand/` | derive-on-contact (family owned) |
| 6 | Partition / Dutch-flag | 3-ptr | `06-partition/` | derive-on-contact (family owned) |

**Sweep closed 2026-06-03** — family derived fluently → owned. #5/#6 left derive-on-contact (no gap to fill). Recognition drill = name the motion → name the atom.
