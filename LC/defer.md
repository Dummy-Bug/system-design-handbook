# Deferred Problems

Problems queued for later — to be mixed into normal zerotrac flow (1 every 5-6 problems), not grinded back-to-back.

---

## Game Theory

Most GT problems at 1500-1700 reduce to one of: one-move reduction, parity / Nim-style, interval DP minimax, or position parity. The real skill is recognising **"is this actually a game, or a disguised observation?"**

| # | Problem | Pattern | Notes |
|---|---------|---------|-------|
| 1 | [Nim Game](https://leetcode.com/problems/nim-game/) | Parity | Easy. Lose iff `n % 4 == 0`. |
| 2 | [Stone Game](https://leetcode.com/problems/stone-game/) | DP minimax | Foundational. `dp[l][r]` = best score for current player on `nums[l..r]`. |
| 3 | [Stone Game II](https://leetcode.com/problems/stone-game-ii/) | DP minimax variant | Adds `M` parameter — state = `(i, M)`. |
| 4 | [Stone Game VII](https://leetcode.com/problems/stone-game-vii/) | DP minimax | Score = sum of remaining after removal. |
| 5 | [Predict the Winner](https://leetcode.com/problems/predict-the-winner/) | DP minimax | Same as Stone Game with looser constraints. |
| 6 | [Divisor Game](https://leetcode.com/problems/divisor-game/) | Parity trick | Answer is just `n % 2 == 0`. Strategy stealing. |
| 7 | [Cat and Mouse](https://leetcode.com/problems/cat-and-mouse/) | Graph + GT | Optional, harder (1900+). Skip until later. |

**After each problem, log:** "I overcomplicated it because X" OR "I saw the trick because Y."

---

## Pigeonhole + Determinism = Bounded Search Space

Core idea: **finite state space + deterministic transition ⇒ either reach goal in ≤ |states| steps, or cycle forever.**

After each, force yourself to answer out loud:
1. What was the **state**?
2. What was the **transition**?
3. What was the **bound on state space**?

| # | Problem | Rating | Why it matches |
|---|---------|--------|----------------|
| 1 | [Happy Number](https://leetcode.com/problems/happy-number/) | ~1300 | State = current number. Sequence either hits 1 or cycles. |
| 2 | [Smallest Integer Divisible by K](https://leetcode.com/problems/smallest-integer-divisible-by-k/) | ~1400 | Same family as repunit divisibility — small variant. |
| 3 | [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) | ~1500 | Functional graph. Floyd's tortoise-and-hare exploits determinism to find cycle start. |
| 4 | [Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) | ~1700 | Pigeonhole *guarantees* duplicate exists (n+1 in [1,n]). Treat array as functional graph → cycle entry = duplicate. Cleanest LC demonstration of the principle. |
| 5 | [Prison Cells After N Days](https://leetcode.com/problems/prison-cells-after-n-days/) | ~1700 | State space = 2^8 = 256, must cycle within 256 days. Naive simulation impossible (N up to 10^9). |

**Suggested order:** 202 → 1015 → 142 → 287 → 957.

After 287 and 957, you should start spotting this structure in problems where it isn't obvious. That's the real win.

---

## Pointers to standalone deferred plans

These are full deferred curricula with their own files — not problem queues like the sections above. They have detailed resume triggers, gap analysis, and ladders.

| File | Topic | Resume trigger |
|------|-------|----------------|
| [math-plan.md](math-plan.md) | Algebra / inequality derivation / abs-value mechanics | Zerotrac ≥ 1700 OR 3+ contests blocked by math derivation |
| [bitmask-plan.md](bitmask-plan.md) | Bitmask DP, TSP-shape, submask enumeration | Zerotrac ≥ 1900-2000 OR 3+ band problems blocked by unrecognised bitmask DP |

