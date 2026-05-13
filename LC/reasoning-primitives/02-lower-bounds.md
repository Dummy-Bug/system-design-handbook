# Lower Bounds — Reasoning About the Floor Before the Algorithm

Most people approach optimization problems by asking "what algorithm should I use?" Lower bound reasoning flips that question entirely: **what does any correct solution have to do, regardless of strategy?**

The answer to that question is the lower bound — the floor below which no solution can go.

---

## The door game

Five doors. At least one prize behind them. You open doors one by one. In the worst case, how many do you open?

The instinct is to say 5. But if you've opened 4 and found nothing, the 5th must have the prize — you don't need to open it. So the worst case is 4.

Can any strategy guarantee finding the prize in fewer than 4 opens? No. The adversary can always arrange the prize behind whichever door you haven't opened yet. 4 is the lower bound — no strategy escapes it.

---

## Finding the minimum in an unsorted array

You have n elements, unsorted. You want the minimum. How many comparisons does any correct solution need?

You need n-1. Not because of any algorithm — because skipping any element means the adversary could hide the minimum there. Every element must be examined at least once. That's the floor, and every linear scan achieves it.

Notice: you didn't think about the algorithm at all. You asked what any correct solution must do, and the floor appeared.

---

## The important lesson from "abc" → "cba"

Don't guess the lower bound — derive it.

For reversing `"abc"` to `"cba"` using single character swaps, the intuition might be `ceil(n/2)` or some formula involving n. But tracing it: swap index 0 with index n-1, done in 1 swap. The lower bound depends on the specific input, not just n.

**Lesson: always derive from the constraints of the specific problem. Never guess a formula and work backwards.**

---

## Tasks and machines

n tasks, each takes 1 unit of time, 1 machine. Lower bound: n units. The machine can't parallelize — every task must be processed sequentially.

Add a second machine. Now both run in parallel. Lower bound: `ceil(n/2)`. For odd n=5: machine 1 gets 3 tasks, machine 2 gets 2 tasks, done in 3 units.

General form: `ceil(n/m)` for n tasks, m machines, 1 unit each.

The critical observation: you derived this without deciding which task goes to which machine. No assignment strategy was needed. The floor came purely from counting — tasks that must be done divided by capacity to do them in parallel.

---

## Increment-only array equalization

Array of n numbers. Operation: pick any element, increment by 1. Make all elements equal.

Since you can only increment, the target must be the maximum element — you can't bring anything down. Every element below the maximum has a gap, and each gap costs exactly that many operations to close.

```
Array:  [0, 0, 0, ..., 0, 10^9]   (n elements)
Target: 10^9
Cost:   (n-1) * 10^9 operations
```

No algorithm needed. Just: what must any correct solution pay? Each element below max must close its gap. That sum is the floor. And since you can close each gap independently, the floor is also achievable — making it the exact answer.

---

## The three-step pattern

Every lower bound derivation follows the same structure:

```
1. Ask: what must any correct solution do, regardless of strategy?
2. Derive the floor from that constraint alone — no algorithm, no assignment
3. Check if the floor is achievable
   → If yes: floor = answer, algorithm design becomes trivial
   → If no: floor is a bound, not the answer — tighten it
```

The most valuable outcome is step 3 confirming the floor is achievable. At that point, you know the answer before writing a single line of code. Any algorithm that hits the floor is optimal by definition.

---

## Connection to invariants

Lower bounds and invariants work together.

- **Invariant** tells you what an operation cannot change — what's locked in by the input.
- **Lower bound** tells you the minimum cost any solution must pay given those locks.

Find the invariant first. The invariant constrains what operations can actually accomplish. From that constraint, the lower bound on cost falls out directly.

On the non-decreasing array problem: the invariant (differences inside a range are preserved) told us each drop must be paid independently. That independence is what made the lower bound = sum of all drops. The invariant unlocked the lower bound.
