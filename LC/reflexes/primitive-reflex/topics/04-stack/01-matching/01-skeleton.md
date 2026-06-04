# Stack Atom 01 — Matching / balancing

The "why a stack" foundation. *Derived Socratically 2026-06-03 (Valid Parentheses).*

## ① Trigger

Validity/structure depends on **proper nesting** (innermost closes first), not just a balanced count. The stack's top = the one thing that must be matched next.

## ② Motivation — the ladder (simpler tool first, then break it)

1. **Single type** `"(()"` → a **counter** suffices: `(`→+1, `)`→−1, never negative, end at 0. Stack is overkill.
2. **Multiple types** `"([)]"` → try **per-type counters**: paren `+1−1=0`, bracket `+1−1=0` → counters say *valid*, but it's **invalid**. Counters are a **multiset** (counts only) — they throw away order.
3. Validity needs **order** (which open is innermost) → only a **stack** records the sequence. Top = most-recent unclosed open of any type.

So: a stack is the minimal structure that remembers **LIFO order across types**; counters only remember counts.

## ③ The move

- opening → push it
- closing → stack empty? → false. Top wrong type? → false. Else pop.
- end → stack empty? valid : false

Three fail-checks: mismatch on pop · close on empty stack · non-empty at end.

```java
Deque<Character> st = new ArrayDeque<>();
for (char c : s.toCharArray()) {
    if (c=='('||c=='['||c=='{') st.push(c);
    else if (st.isEmpty() || !matches(st.pop(), c)) return false;
}
return st.isEmpty();
```

## ④ Costumes

- Validity — Valid Parentheses (20).
- Count / produce the fixes — Min Remove (1249), Min Add (921) [reskins of "count unmatched"].
- Longest valid run — Longest Valid Parentheses (32): push **indices**, measure spans between unmatched (different sub-technique, deferred).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| plain counter | counter works for one type / balance only; stack needed when *type + order* (nesting) matters |
| adjacent-collapse (#2) | matching only **pairs/validates**; collapse **resolves an interaction** and survivors are the answer |
| fold-up (#4) | matching pairs with no value; fold-up **combines a computed value** up the nesting |

## ⑥ Reflex check

Prompt: *brackets valid, multiple types — move?*
Answer: *push opens; on close, top must match (else false); end empty. Stack because last-opened must close first (LIFO).*
