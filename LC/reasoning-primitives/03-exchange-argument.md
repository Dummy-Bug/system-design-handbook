# Exchange Argument — Proving a Greedy is Correct

Greedy algorithms are easy to come up with and easy to get wrong. The exchange argument is how you prove a greedy is actually optimal — or find the counterexample that kills it.

The core idea: take any two adjacent elements in your solution and swap them. If swapping always makes things worse or equal, your ordering is optimal. If swapping ever makes things better, your greedy is wrong — and the swap just showed you the counterexample.

---

## The task scheduling problem

You have n tasks. Each task has a deadline (must finish by this time) and a reward (points collected if completed). You have one machine, each task takes 1 unit. You want to maximize total reward.

Three tasks, two slots:
- Task A: deadline 1, reward 6
- Task B: deadline 2, reward 8
- Task C: deadline 2, reward 10

Two greedy strategies come to mind immediately.

**Strategy 1 — earliest deadline first:** schedule A (deadline 1) first, then pick highest reward among remaining → C. Total: 6 + 10 = 16.

**Strategy 2 — highest reward first:** schedule C (reward 10) first, then B (reward 8). A gets dropped — it had deadline 1 but slot 1 is taken. Total: 10 + 8 = 18.

Strategy 2 wins here. But does highest reward first always win?

---

## Finding counterexamples via swap

Take:
- Task A: deadline 1, reward 10
- Task B: deadline 2, reward 8
- Task C: deadline 2, reward 6

Highest reward first: A (slot 1), B (slot 2). C dropped. Total: 18.

What if someone schedules C first (ignoring reward order)?
- Slot 1: C (reward 6)
- Slot 2: A — deadline was 1, missed. B fits instead → reward 8.
- Total: 6 + 8 = 14.

14 < 18. Highest reward first wins here.

But swap back to the earlier example (A reward 6, C reward 10): highest reward first gave 18 while earliest deadline first gave 16. Neither strategy is universally correct.

---

## What the exchange argument actually derives

Instead of guessing a strategy, ask: given two adjacent tasks X and Y, when is X before Y better than Y before X?

The rest of the sequence is identical in both orderings — it cancels out. You only need to compare what happens at those two slots.

**Case 1 — both orders are safe (neither task misses its deadline either way):**
Reward is the same either way. Order doesn't matter for these two.

**Case 2 — one order causes a task to miss its deadline:**
Say X before Y is safe, but Y before X causes X to miss its deadline.
- X before Y: collect reward(X) + reward(Y)
- Y before X: collect only reward(Y) (X is missed)

X before Y is strictly better. The rule: if scheduling Y first risks X missing its deadline, put X first.

**Case 3 — both orders cause one task to miss (slots are that tight):**
Pick whichever order saves the higher reward task.

The combined rule — deadline safety first, then reward — is not guessed. It falls out directly from asking "which swap is always worse?"

---

## The structure of every exchange argument

```
1. Assume you have an optimal solution
2. Take any two adjacent elements that seem "out of order" by your greedy rule
3. Show what happens when you swap them
4. If swap is always worse or equal → original order is optimal → greedy is proved
5. If swap is sometimes better → greedy is wrong → the swap IS the counterexample
```

The power is in step 5. You don't need to search for counterexamples — the swap reveals them mechanically.

---

## Connection to invariants and lower bounds

- **Invariant** tells you what an operation cannot change.
- **Lower bound** tells you the minimum any solution must pay.
- **Exchange argument** tells you the optimal ordering among choices.

Together: invariant constrains the space, lower bound sets the floor, exchange argument finds the best path through that constrained space.

---

## When to reach for the exchange argument

Trigger: the problem asks you to order or schedule a set of items to minimize/maximize something, and a greedy ordering feels natural but you're not sure it's correct.

Don't trust the greedy until you've run the exchange argument. One swap that improves the solution is enough to kill it.
