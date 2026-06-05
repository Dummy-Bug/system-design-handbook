# Stack Atom 01 — notes

## Why a stack — the ladder (single counter → per-type multiset → stack)

The problem (Valid Parentheses, LC 20) is to decide whether a string of brackets is properly nested: every closing bracket has to match the most-recent still-open bracket of the same type, and nothing is left open at the end. Before reaching for a stack it's worth seeing why the two simpler tools fail, because that failure is the entire justification for the stack and is exactly what a revision needs to reconstruct.

Start with the easiest version: a single bracket type, only `(` and `)`. Here you don't need any data structure at all — a single integer counter is enough. Add one when you see `(`, subtract one when you see `)`. If the counter ever goes negative you closed something that was never opened, and if it isn't zero at the very end you left something open. That's the whole check. The counter works because with one type there is nothing to remember *except how many are currently open* — there's no question of "which kind."

Now make it harder: multiple types, `()[]{}`. The instinct is to scale the trick up — keep one counter per type. A counter for parentheses, a counter for brackets, a counter for braces, each going up on its open and down on its close, none allowed to go negative, all required to end at zero. This feels like it should work, and on many strings it does. But it is wrong, and the string that exposes it is `"([)]"`. Run the per-type counters on it: the parenthesis counter goes `+1` then later `−1`, ending at zero and never negative; the bracket counter does the same. Every counter is perfectly balanced, so the counters declare the string valid. It is not — `([)]` is interleaved, not nested. The `)` closes while the innermost unclosed bracket is `[`, which is illegal.

The reason the counters fail is the heart of the atom. A set of counters is a multiset: it records *how many* of each type are open, but it throws away the *order* in which they were opened. And validity is precisely a question of order — when a closing bracket arrives, the only correct partner is the single most-recently-opened bracket, and the counters have no idea which type that was. They remember counts; the problem needs sequence.

So the structure you actually need is the minimal one that remembers the order of the still-open brackets, with fast access to the most recent one. That is a stack. Push every opening bracket; when a closing bracket arrives, the top of the stack must be its matching open (otherwise the string is invalid), and you pop it. The top of the stack is always "the innermost thing currently waiting to be closed," which is exactly the partner a closing bracket is allowed to match. The stack is doing the one job the multiset couldn't: preserving last-opened-first-closed order across types.

That gives the move and its three failure points: an opening bracket pushes; a closing bracket fails if the stack is empty (closing something never opened) or if the top is the wrong type (interleaving, the `([)]` case), otherwise it pops; and after the whole scan, a non-empty stack means something was left open. Counter → multiset → stack is a ladder of *what gets remembered*: a single number, then per-type numbers, then the full ordered sequence — and only the last one carries enough to answer the question.

## Min Remove to Make Valid (LC 1249) — the count facet

Single type `(` `)` + letters. Ignore letters. Stack stores **indices** of unmatched `(`:
- `(` → push index.
- `)` → stack non-empty → pop (matched); empty → this `)` is unmatched, mark its index for removal.
- end → every index left in the stack is an unmatched `(` → mark for removal.
- build the result from indices NOT marked.

Use a `boolean[] remove` (indexed by position), not a `Set<Integer>` — O(1), no boxing, the index *is* the key.

```java
boolean[] rm = new boolean[n];
Deque<Integer> st = new ArrayDeque<>();
for (int i=0;i<n;i++){
    char c=s.charAt(i);
    if (c=='(') st.push(i);
    else if (c==')'){ if (st.isEmpty()) rm[i]=true; else st.pop(); }
}
while(!st.isEmpty()) rm[st.pop()]=true;
// append chars where !rm[i]
```

## Perturbation findings (the transferable part)

**1. Single-type is load-bearing → multi-type crosses into DP.**
Min *deletions* for **multi-type** is NOT this greedy. On a type-mismatch (`[` on top, `)` incoming) you can't locally decide whether to delete the open or the close — it depends on the rest of the string. Greedy collapses → DP. So adding *types* to a min-deletion problem changes the **difficulty class**. A perturbation that changes the difficulty class is itself diagnostic: it marks where the atom's tool stops working.

**2. Why the single-type greedy is *minimal*, not just valid (greedy theory, seeded here).**
Every bracket marked for removal is **forced**: an unmatched `)` can never be paired; a leftover `(` is never closed. No alternative is cheaper → the greedy choice is the *only* choice → minimal by necessity. ("Locally forced = globally forced" — the safest kind of greedy.)

**3. The deeper axis — easy vs DP = consequential choices.**
In single-type min-remove there are **no consequential choices**: which `(` a `)` matches is irrelevant (identical opens), and which bracket to remove is forced. A problem is **greedy/easy when it has no consequential choice**, and **needs DP when the choices matter and can't be decided locally** (exactly the multi-type case, and the `{1,3,4}`-coins case). Diagnosing *where the consequential choice lives* tells you greedy-vs-DP.

> Note: greedy is a paradigm (its own family, to be built much later). Parked here inline rather than cross-referenced — no Greedy family exists yet.

## Plain `Deque` peek vs char gotcha
`st.peek() == c` is safe only because `c` is a primitive `char` (auto-unboxes). Comparing two `Character` objects with `==` hits the cached-range bug (works ≤127, breaks above).
