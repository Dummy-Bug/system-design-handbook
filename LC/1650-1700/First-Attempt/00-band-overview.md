# LC Training Log — 1650-1700 band

Protocol: see `zerotrac.md`. Graduated from 1600-1650 on 2026-05-13 (7/10 AC in band, moved forward with stricter edge-case vetting — all future problems will have thought process logged with gap analysis).

**Format:** For each problem, capture:
1. User's actual thought process
2. What was discussed / what they realized
3. What should have been thought (gaps in approach, missed edge cases)
4. Final solution and lessons

---

---

## Meta-lesson from #1 (2026-05-13) — Algorithm-first vs Answer-first thinking

> **Status: HYPOTHESIS (single data point — #1).** This framework was derived from one problem. Validate or revise after 5-10 more problems in this band. Do not treat as a locked rule yet.

The 1h31min on this problem wasn't from being stuck on a single thing. It was from spending ~60-70 min searching through algorithms (lift to min, extend till recovery, extend till next >= nums[i]) without ever asking what the answer must be.

Hypothesis: this is the most important meta-pattern for 1650+ problems. To be validated on subsequent problems.

---

### The distinction

**Algorithm-first thinking** (what happened on #1):
"Which subarray do I pick? What x value? Where do I stop the operation?"

You're searching through possible strategies. You produce a number, but you have no way to verify it's optimal — your only point of comparison is your own algorithm's output. You can spend hours iterating on variations of a strategy without realising the strategy itself is structurally suboptimal.

**Answer-first thinking** (what should have happened):
"Regardless of what operations I choose, what is the minimum total cost I must pay?"

You're reasoning about the cost structure itself — a lower bound argument. Focus on what operations can and cannot do at the structural level, not on which specific operations to perform.

---

### Important clarification: "answer-first" does NOT mean knowing the answer beforehand

The name is misleading. You're not pulling the answer out of thin air. You're **deriving** what the answer must be by reasoning about your operations — *before* trying to design an algorithm.

The derivation uses a fixed 4-question framework.

---

### The Q1-Q4 framework (run before any algorithm idea)

**Q1: What does ONE operation do, mechanically?**

Not "what could a clever sequence achieve" — literally one move. Strip it down to its mechanical effect on the state.

**Q2: What invariant does that imply?**

An invariant is anything one operation CANNOT change. Whatever the operation preserves is locked in by the input. This is the most important question — invariants tell you what you cannot escape, which tells you what you must pay for.

**Q3: What's the minimum cost to make one unit of required progress?**

A "unit of progress" depends on the problem — one drop fixed, one element placed, one constraint satisfied. Given Q2's invariant, what's the cheapest way to achieve one unit?

**Q4: Can units share cost, or are they independent?**

If two units can be progressed by the same single operation, total cost < sum of unit costs. If they cannot, total cost = sum of unit costs. Prove this by contradiction using Q2's invariant.

Once Q1-Q4 are answered, the answer formula falls out. Then designing the algorithm is just "find any sequence of operations that achieves the bound."

---

### Walkthrough of Q1-Q4 on this problem

**Q1: What does ONE operation do, mechanically?**

Pick a range [l..r], add the same x to every element in that range. That's it.

**Q2: What invariant does that imply?**

If two adjacent elements i and i+1 are BOTH inside [l..r], they both get +x. Their **difference is unchanged**.

→ Invariant: an operation cannot change the relative difference between any two elements that are both inside its range.

**Q3: What's the minimum cost to fix one drop?**

A drop is a pair (i, i+1) with nums[i] > nums[i+1]. The final values must satisfy new[i] <= new[i+1].

Three cases for how an op interacts with this pair:
- Op covers both i and i+1: difference unchanged (Q2 invariant). Useless for this drop.
- Op covers i+1 but not i: index i+1 lifts by x, index i stays. Drop decreases by x.
- Op covers i but not i+1: drop gets worse.

→ Only operations that include i+1 but exclude i can reduce this drop. To fully close a drop of size d, the total x across such operations must be at least d.

**Q4: Can one operation fix two drops at once?**

Suppose drops at positions i and j (j > i). To reduce drop at i, op range [l..r] must satisfy l <= i+1 and l > i, so l = i+1 (or more precisely, l <= i+1 and r >= i+1, but to exclude index i we need l >= i+1, so l = i+1... actually any l in (i, ...] works, meaning l >= i+1). To reduce drop at j similarly, op must exclude j and include j+1, so l >= j+1.

Combining: l >= j+1 AND l <= i+1. Since j > i, j+1 > i+1. Contradiction.

→ No single operation can reduce two different drops. Drops are independent.

**Conclusion**

Sum of independent lower bounds = sum over all drops of drop amount = `sum of max(0, nums[i] - nums[i+1])`.

Achievable by extend-to-end (any operation that covers [i+1..n-1] fixes exactly drop at i without disturbing others). So lower bound = upper bound = answer.

Total derivation time: ~5 minutes once you sit down and write Q1-Q4. No segment exploration. No "where do I stop." Just structural reasoning.

---

### When to run the Q1-Q4 framework

Trigger keywords in the problem statement:
- "minimum" / "maximum" of a sum over choices
- "minimum number of operations to..."
- "minimum cost to..."
- "fewest moves to..."

Whenever you see one of these, pause. Do NOT start sketching algorithms. Spend the first 5-10 minutes on Q1-Q4. The vast majority of 1650+ optimisation problems collapse once Q1-Q4 are answered.

---

### Why this matters at 1650+

At 1450-1600 most problems are pattern-recognition: "this is a sliding window," "this is a hashmap lookup," "this is DP on intervals." Match the pattern, code the template, AC.

At 1650+ many problems require deriving the answer formula from first principles before any pattern applies. Algorithm-first thinking dead-ends on these because the operations look like they need clever orchestration — but once you derive the lower bound via Q1-Q4, the algorithm is often trivial (sometimes a single line, as on #1).

---

### The skill to train

Every time you see "minimum / maximum of a sum of operations," pause and run Q1-Q4 before touching any algorithm idea. Write the four answers down on paper. Only after Q1-Q4 are done should you consider strategies.

If after 10 minutes Q1-Q4 are blank, that's a signal you don't understand what the operation actually does — re-read the problem until you can answer Q1.

---
