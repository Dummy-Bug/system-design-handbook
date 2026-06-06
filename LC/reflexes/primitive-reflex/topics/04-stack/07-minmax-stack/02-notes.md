# Stack Atom 07 — notes

## Min Stack (LC 155) — the announced rep

The job is an ordinary stack that *also* answers `getMin()` in O(1). The hard case is pop: after `push(-2) push(0) push(-3)`, the min is `-3`; pop the `-3` and the min must instantly become `-2` again. A single plain stack can't do that without scanning — so you carry the min **in lockstep** with the data, recomputed on every change so it's always one peek away.

### Two implementations, same invariant

**Two stacks (the recalled version).** Keep the normal stack plus a `minStack`. Push `val` onto the main stack always; push it onto `minStack` only when `val <= current min` (i.e. `minStack.isEmpty() || val <= minStack.peek()`). On pop, pop the main stack, and *also* pop `minStack` iff the popped value equals `minStack.peek()`. `getMin()` = `minStack.peek()`.

The load-bearing detail is **`<=`, not `<`.** Consider pushing `[2, 2]`. With strict `<`, only the first `2` lands on `minStack`. Pop the second `2` (it equals the min-stack top) and you'd pop the min entry too — now `getMin` reports the wrong value while a `2` is still in the main stack. Pushing on `<=` keeps one min-stack entry per duplicate minimum, so each pop peels exactly one. (Storing the index alongside the value also works, but it's unnecessary once `<=` guarantees every duplicate is represented.)

**Single stack of pairs (the cleanest).** Each node carries the min *as of when it was pushed*:

```java
class MinStack {
    private static class Node { int val, min; Node(int v, int m){ val=v; min=m; } }
    private Deque<Node> stack = new ArrayDeque<>();

    public void push(int value) {
        int min = stack.isEmpty() ? value : Math.min(value, stack.peek().min);
        stack.push(new Node(value, min));
    }
    public void pop()    { stack.pop(); }
    public int top()     { return stack.peek().val; }
    public int getMin()  { return stack.peek().min; }
}
```

The single line `min(value, prevTop.min)` is the whole trick: each node knows the min of *everything at or below it*. So `getMin` is `top().min`, and `pop` needs **zero** extra bookkeeping — when the top leaves, the new top already stores the correct min for what remains. Trade-off: this stores a min with *every* element (more memory when the min rarely changes), whereas the two-stack `<=` version only adds a min entry when the min actually drops. Both are O(1) on every operation.

### Why `pop` being top-only and the query being read-only is what makes lockstep work

This is the deep point of the atom, and it's easiest to see by where it *fails* — the Max Frequency Stack (895), which we deferred but is worth recording because the contrast is the lesson.

`FreqStack.pop()` does **not** remove the top; it removes the **most-frequent** element (ties broken by recency). Try to mirror Min Stack's trick — store the current max-frequency element inside each node — and it breaks on two counts:

1. **The element to remove is usually buried, not on top.** Push `5,7,5,7,4,5`; the first pop returns `5` (freq 3, conveniently the top), but the next pop must return `7` (freq 2) which sits *under* the `4`. A stack can't remove from the middle, so knowing the answer doesn't let you take it.
2. **The cache goes stale.** Removing that buried `7` drops its frequency, changing which element is now the max — but every node still in the stack was stamped with its max at *push* time and has no idea a `7` just left from the middle. The next read is wrong.

Min Stack never hits either problem because (a) its `pop` always removes the **top** — the same end you push — so the newly exposed top's cached min is still exactly correct, and (b) `getMin` is **read-only**, it never mutates the aggregate. FreqStack violates both: pop targets a buried element and mutates the frequencies.

| | Min Stack | FreqStack |
|---|---|---|
| pop removes | the **top** (push end) | the **max-frequency** element (usually buried) |
| query | read-only `getMin` | a **mutation** that changes frequencies |
| cache-in-node | stays valid (only the top ever leaves) | goes **stale** (a middle element leaves, shifting other freqs) |

The general repair, when the element you want isn't a top: **bucket by the key so it becomes a top again.** For 895, keep `group: freq → stack of vals at that freq`; on push at freq `f` do `group[f].push(val)`; on pop take `group[maxFreq].pop()` (top of that bucket = most recent at that freq = the recency tiebreak for free), decrement, and drop `maxFreq` when its bucket empties. That's O(1). A priority queue keyed `(freq desc, seq desc)` also works — the `seq` (a global push counter) supplies the recency tiebreak a freq-only heap would lose — but it's O(log n). (Code for both lives with 895 when we return to it.)

## Perturbation findings — what's load-bearing in Min Stack

- **The aggregate is a min/max** (order statistic that's *monotone under the lockstep recompute*): `min(val, prevMin)` only needs the previous answer, never the whole history. That's why a single cached value per node suffices. A non-monotone aggregate (e.g. "median") would *not* be reconstructible from `(val, prevAnswer)` alone — different structure.
- **`pop` is top-only.** This is the silent assumption that lets the cache stay valid; remove it (pop a non-top, as in 895) and the cache approach collapses → bucket-by-key.
- **`<=` vs `<`** in the two-stack form is the duplicate-minimum trap; the single-stack pair form sidesteps it entirely (every node carries its own min, duplicates included).

> **Logging honesty:** Min Stack (155) was **recalled** ("I have solved this one as well"), not cold-derived — recognition confirmed, both the two-stack `<=` and single-stack-pair forms reproduced. Min/max stack is **not** a blind-spot, so recall is fine for installing the chunk; no cold ownership rep is gated here. The disguised rep (Max Frequency Stack 895) is **deferred** (design problem, revisit later) — its real value (the lockstep-breaks-on-buried-pop lesson) is already captured above.
