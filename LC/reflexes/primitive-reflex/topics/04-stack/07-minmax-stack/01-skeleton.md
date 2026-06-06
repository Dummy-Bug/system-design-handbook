# Stack Atom 07 — Min/max auxiliary stack

*2026-06-06 19:05*

## The problem (Min Stack, LC 155)

Design a stack supporting `push`, `pop`, `top`, **and `getMin`** — all in O(1). After `push(-2) push(0) push(-3)`, `getMin()=-3`; after `pop()`, `getMin()=-2`. The crux is the last one: popping must instantly restore the *previous* minimum.

## ① Trigger

You need a stack that also answers a **running aggregate** (min / max) of its current contents in O(1). A plain stack does push/pop/top in O(1) but `getMin` would be an O(n) scan. The signal: "stack operations **plus** an O(1) extreme/aggregate query."

## ② Motivation — why an auxiliary (break the simpler tool)

A single plain stack forces `getMin` to scan all elements → O(n). To get O(1), you carry the answer **in lockstep** with the data: every time the stack changes, the min is already known. Two equivalent ways to carry it — a parallel min-stack, or the min stored inside each node. Either way the invariant is: *the min of everything currently in the stack is available without looking past the top.*

## ③ The move

**Single stack of pairs (cleanest):** each node stores `(val, minSoFar)` where `minSoFar = min(val, previousTop.minSoFar)`.

```java
push(v): int m = stack.isEmpty() ? v : Math.min(v, stack.peek().min);
         stack.push(new Node(v, m));
getMin(): return stack.peek().min;
pop():    stack.pop();          // min leaves with the node — no extra logic
```

**Two stacks (alternative):** main stack + min-stack; push to min-stack when `v <= currentMin`; on pop, also pop min-stack iff the popped value equals its top. The `<=` (not `<`) is load-bearing: duplicate minimums must *all* go on the min-stack, else popping one drops the min prematurely.

Both are O(1) for every op. The pair version needs **zero pop-time logic** (the min rides inside each node); the two-stack version uses less memory when the min rarely changes.

## ④ Costumes & boundary

- Max Stack / getMax — same, flip `min`→`max` (deferred rep here: **Max Frequency Stack 895** is a harder cousin, see ⑤).
- The lockstep cache trick works **only when** (a) removal is always at the **top** and (b) the query is **read-only**. Min Stack satisfies both. When a problem's `pop` removes a *non-top* element or *mutates* the aggregate, the cache goes stale — that's a different structure (see confusion matrix).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| monotonic stack (#6) | #6 **discards** dominated elements (the stack's contents are a *subset*; popping changes which elements exist); min/max-aux **keeps every element** and just carries the running extreme alongside — nothing is thrown away |
| Max Frequency Stack (895) | looks like "max-stack" but its `pop` removes the **max-frequency** element (usually *buried*, not the top) and *mutates* freqs → the lockstep cache breaks; needs **bucket-by-frequency** (group: freq→stack) so the wanted element is a top again, or a PQ keyed `(freq, seq)` |
| matching (#1) | #1's pop checks delimiter *pairing*; here pop is a normal top-removal and the stack additionally answers an aggregate query |

## ⑥ Reflex check

Prompt: *stack ops + O(1) min/max query — move?*
Answer: *carry the aggregate in lockstep. Single stack of `(val, minSoFar=min(val, prevTop.min))` → getMin = top.min, pop is automatic. Or two stacks with `<=` push to the min-stack. Works because pop is top-only and the query is read-only; if pop removed a buried element or mutated the aggregate, the cache would go stale (→ bucket-by-key instead).*
