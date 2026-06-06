# Stack Atom 05 — Nested-structure fold-up

*2026-06-05 18:30*

## The problem (Decode String, LC 394)

Decode a string encoded as `k[encoded_string]`, where `encoded_string` is repeated `k` times, and the encoding can nest to arbitrary depth. `"3[a]2[bc]"` → `"aaabcbc"`; `"3[a2[c]]"` → `"accaccacc"`; `"2[abc]3[cd]ef"` → `"abcabccdcdcdef"`. `k` is a positive integer (possibly multi-digit).

## ① Trigger

A structure that **nests to arbitrary depth** — a `[…]` inside a `[…]` inside a `[…]`. When you open an inner bracket, the outer one isn't finished: its half-built string and its repeat count have to be remembered and resumed *after* the inner one fully resolves. That "remember the parent's unfinished work, come back to it last-opened-first" is LIFO memory → a stack. Each closing bracket **folds** the completed child up into the parent.

## ② Motivation — why a stack (break the simpler tool)

With **no nesting** — `"3[a]2[bc]"` — two variables suffice: a current string and a current number. Read `3`, hit `[`, build `a`, hit `]` → append `a×3`, reset. One pass, no stack.

Now nest it — `"3[a2[c]]"`. At the inner `[` you're mid-way through the outer: you've built `"a"` and you're holding count `3`, but you must start the child fresh. Those two variables can hold only one level. Something has to **park the parent's (count, partial-string) while the child computes** and hand it back when the child closes. That park-and-restore-in-LIFO is the stack. Nesting is exactly what breaks the two-variable solution and forces the stack.

## ③ The move

Carry a current `StringBuilder sb` and a current `int num`. Scan left to right:

- **digit** → `num = num*10 + (ch-'0')` (multi-digit accumulate).
- **`[`** → push the pair `(num, sb)` — the count for the bracket about to open, and the prefix already built at this level — then **reset** `sb=""`, `num=0` and start the child fresh.
- **`]`** → pop `(count, prefix)`; the child is done in `sb`; fold up: `sb = prefix + (sb × count)`.
- **letter** → `sb.append(ch)`.

The fold is `prefix + inside×count`, **not** `(prefix + inside)×count` — the count repeats only the bracket's contents; the saved prefix glues on in front, un-repeated.

```java
else if (ch == ']') {
    Tuple top = stack.pop();              // (count, prefix)
    StringBuilder inside = new StringBuilder(sb);
    for (int i = 1; i < top.count; i++) sb.append(inside);   // sb now = inside×count
    sb.insert(0, top.s);                  // prefix + inside×count
}
```

## ④ Costumes

- Decode String (394) — payload is a string; fold = repeat-and-prepend.
- Basic Calculator I (224, parens) — payload is a running integer + sign; fold = add the child's value into the parent with the saved sign (planned disguised rep).
- Score of Parentheses (856) / Number of Atoms (726) — same skeleton, different fold operator (doubling / multiply-counts).

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| matching (#1) | #1 only checks the brackets pair up (validity / count); here brackets are valid by promise and the job is to **compute a value per level and fold child into parent** |
| operator-precedence (#4) | #4 defers operators by precedence within one flat expression; here the nesting itself is explicit (`[ ]`) and the stack saves **per-level partial results**, not operators waiting on precedence |
| recursion / call stack | not a confusion — they're the *same machine*. The explicit stack is the call stack made manual; `[` = recursive call, `]` = return. One-pass iterative is just the unrolled form (see notes) |

## ⑥ Reflex check

Prompt: *arbitrarily-nested `k[...]` (or parens) → decode/evaluate — move?*
Answer: *fold-up stack. Carry (sb, num). digit→accumulate; `[`→push (num, sb) and reset; `]`→pop (count, prefix), `sb = prefix + sb×count`; letter→append. Stack because each open level's partial work must survive while the inner level computes, resumed LIFO.*
