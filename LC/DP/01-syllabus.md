# DP Syllabus — dependency-sorted learning order

Ordered by **what each pattern requires knowing first**, not by the reference-table order in `patterns/master-taxonomy.md`. Vocab is mapped onto the canonical DP sub-pattern names from that taxonomy.

Each pattern is taught the same way as `1D.md` / `2D.md`: **problem → prove naive is broken with numbers → diagnose → optimise step by step**, Socratically.

| #      | Pattern                                                            | Why it sits here                                                                                                                     | Status             |
| ------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| **0**  | **Linear DP / Fibonacci** — 1 state variable, recurrence on `i`    | The atom: state → recurrence → base → fill. Everything else is this with more dimensions or more choices.                            | ✅ `1D.md`          |
| **1**  | **Grid / 2D DP** — 2 state variables `(i,j)`, move right/down      | Adds a second dimension. Still "where am I", no item choice yet.                                                                     | ✅ `2D.md`          |
| **2**  | **0/1 Knapsack (bounded)** — each item used **0 or 1 times**       | **The keystone.** Introduces the *include-or-exclude* decision + a *capacity* dimension. State = `(item index, remaining capacity)`. | ⬜ ← **start here** |
| **3**  | **Unbounded Knapsack** — each item used **∞ times**                | A *one-line* mutation of 0/1 (where the index pointer moves). Pointless before feeling the 0/1 transition.                           | ⬜                  |
| **4**  | **Subset-Sum / Coin Change family**                                | Knapsack with value=weight, or counting variants. Re-skins of #2/#3.                                                                 | ⬜                  |
| **5**  | **LIS** — subsequence, `O(n²)` then `O(n log n)`                   | New recurrence shape: "best ending at `i` over all `j<i`".                                                                           | ⬜                  |
| **6**  | **LCS / Edit Distance / String DP** — 2 sequences, `(i,j)`         | 2D again, but indices into *two strings*. Builds on grid + include/skip idea.                                                        | ⬜                  |
| **7**  | **Palindrome DP**                                                  | Special case of string 2D DP.                                                                                                        | ⬜                  |
| **8**  | **Interval / MCM DP** — `dp[i][j]` over a *range*, split point `k` | New shape: answer of a range from its sub-ranges. Harder fill order.                                                                 | ⬜                  |
| **9**  | **DP on Trees** ★                                                  | Recurrence over children instead of indices. Blind-spot (rule 6B).                                                                   | ⬜                  |
| **10** | **Bitmask DP**                                                     | State = a *set*. Needs comfort with everything above.                                                                                | ⬜                  |
| **11** | **Digit DP / Probability DP / State-Machine DP / DP on Graphs**    | Specialized leaves; learn last, as-needed.                                                                                           | ⬜                  |
| **12** | **Kadane** — running best vs. restart                              | Deliberately last: a 1D "take it or restart" trick that's easy to slot in once the choice-DP muscle is built.                        | ⬜                  |

---

## Why 0/1 knapsack is the keystone (#2)

Unbounded knapsack is defined by its *one* difference from 0/1 knapsack: the "aha" is *"why does the index pointer stay put instead of advancing?"* — and that question is meaningless until you've felt the 0/1 version where it *does* advance.

So 0/1 knapsack is the load-bearing lesson. Once owned, unbounded is a ~2-minute delta, and subset-sum / coin-change fall out for free.

---

## Blind-spot tie-in (rule 6B)

- **#9 DP on Trees** is one of the three mandated blind-spot patterns (needs 3 cold cleans). Treat it as a priority once #0–#8 are solid.
