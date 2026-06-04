# Stack Atom 01 — notes

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
