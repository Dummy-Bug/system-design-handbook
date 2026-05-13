# What is an Invariant?

An invariant is a property that an operation **cannot change** — no matter how many times you apply it, no matter which inputs you pick.

---

## Building the intuition

Start with sorting. You have `[3, 1, 4, 1, 5]`. Sort it → `[1, 1, 3, 4, 5]`. The array looks completely different, but the count and frequency of every element is identical. You can sort a million times — those properties never change. That's an invariant of the sort operation.

Same idea with adjacent swaps. Pick any two adjacent elements and swap them. The sum doesn't change. The product doesn't change. The frequency of each element doesn't change. These are all invariants of the swap operation.

---

## Why invariants matter for problem solving

If an operation preserves the sum, and the problem asks "what is the minimum sum after operations" — the answer is already sitting in the input. You don't need to search through strategies. The invariant collapses the search space to zero.

This is the core payoff: **an invariant tells you what you cannot escape, which tells you what you must pay for**.

---

## Worked example — Minimum Operations to Make Array Non-Decreasing

**The operation:** pick a range [l..r], add the same value x to every element in it.

**The invariant:** if two adjacent elements i and i+1 are *both* inside [l..r], they both get +x. Their difference `nums[i+1] - nums[i]` is unchanged.

→ An operation cannot change the relative difference between any two elements that are both inside its range.

---

## What the invariant immediately tells you

To fix a drop at position i (where nums[i] > nums[i+1]), the operation must treat i and i+1 differently — element i must be outside the range, element i+1 must be inside. If both are inside, the invariant locks the drop in place.

So the left boundary must be ≥ i+1. The operation must **exclude i and include i+1**.

---

## Why two drops cannot be fixed by one operation

Suppose you have drops at position i and position j, where j > i.

- To fix drop at i: left boundary ≥ i+1 (exclude i, include i+1)
- To fix drop at j: left boundary ≥ j+1 (exclude j, include j+1)

Since j > i, we have j+1 > i+1. The boundary that satisfies drop j excludes i+1 entirely — drop i gets no coverage. One operation cannot satisfy both constraints simultaneously.

The proof is clean because it comes directly from the invariant — inside a continuous range, either both elements are included or both are excluded. You cannot split a pair that is both inside the range.

**Drops are independent. You must pay for each one separately.**

---

## The full chain on this problem

```
Operation preserves differences inside range
→ to fix a drop at i, must exclude i and include i+1
→ extending to end of array prevents creating new drops at the right boundary
→ with extend-to-end, offset cancels on both sides of every remaining drop
→ differences in original array = differences you always pay
→ answer = sum of all positive drops in original array
→ no array modification needed, one pass O(n)
```

---

## The habit to build

Whenever you see a problem with "minimum/maximum cost of operations":

1. Ask: what does **one operation** do mechanically?
2. Ask: what property does it **preserve** (cannot change)?
3. That preserved property is your invariant — it tells you the floor of what you must pay.

If you find the invariant first, the algorithm usually becomes trivial.
