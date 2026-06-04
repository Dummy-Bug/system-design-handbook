# Stack Atom 01 — Matching / balancing

Stack family · the "why a stack" foundation
*Derived Socratically 2026-06-03 (Valid Parentheses).*

## ① Motivation (simpler tool first, then break it)

- Single bracket type `"((("`: a **counter** suffices (+1 open, −1 close, never negative, end at 0). Stack is overkill.
- Multi type `"([)]"`: the counter is blind — it tracks *how many* are open, not *which* or *in what order*. Count looks fine, yet it's invalid.

So the upgrade is forced by **nesting**: you must close the **most recently opened** bracket first. Last-opened-first-closed = LIFO = a stack.

## ② Trigger

Validity/structure depends on **proper nesting** (innermost closes first), not just a balanced count. The stack's **top = the one thing that must be matched next**.

## ③ The move

- Opening → push it.
- Closing → stack empty, or top doesn't match its type → invalid; else pop.
- End → stack must be empty (nothing left unclosed).

```java
Deque<Character> st = new ArrayDeque<>();
for (char c : s.toCharArray()) {
    if (c == '(' || c == '[' || c == '{') st.push(c);
    else {
        if (st.isEmpty()) return false;
        char open = st.pop();
        if (!matches(open, c)) return false;
    }
}
return st.isEmpty();
```

Three failure checks: mismatch on pop · close on empty stack · non-empty at end.

## ④ Costumes

- Validity (Valid Parentheses, 20).
- Count the fixes / unmatched (Min Add to Make Valid, 921) — count what can't be popped.
- Longest valid run (Longest Valid Parentheses, 32) — stack of **indices**, measure spans between unmatched.

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| plain counter | counter works for one type / balance only; stack needed when *type + order* (nesting) matters |
| fold-up (#4) | matching only **pairs** (no value) *vs* fold-up **combines a computed value** up the nesting |

## ⑥ Reflex check

Prompt: *brackets valid, multiple types — move?*
Answer: *push opens; on close, top must match (else false); end empty. Stack because last-opened must close first (LIFO).*
