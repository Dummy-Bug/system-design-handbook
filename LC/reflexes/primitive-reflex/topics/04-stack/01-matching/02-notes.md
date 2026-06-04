# Stack Atom 01 — Matching · notes

## Why not multiple counters? (the deeper "why a stack")

A natural pushback after the single-counter case: *for multi-type brackets, why not just keep one counter per type — `paren`, `brack`, `brace`?*

**Test it on `"([)]"`:**

```
(   → paren = 1
[   → brack = 1
)   → paren = 0   ✓ (non-negative)
]   → brack = 0   ✓
end → all zero    → multi-counters say VALID
```

But `"([)]"` is **invalid**. Multi-counters give the wrong answer.

**Why it fails:** counters tell you *how many* of each type are open — a **multiset**. They throw away the **order** the opens arrived in. Validity depends on exactly that order: when you hit `)`, the most recent still-open bracket must be `(` — but here it's `[`, opened *after* `(`. A per-type counter can't see "what is the most recent open **across all types**," because it never recorded the interleaving.

## The upgrade ladder (three rungs, not two)

1. **Single counter** — enough with one type (just balance: `"((("` ).
2. **Multiple counters** — enough only if types **never interleave**; still a multiset, blind to cross-type order. Dies on `"([)]"`.
3. **Stack** — records the **ordered sequence** of opens, so the top is "most recent open of *any* type." That order is the exact thing validity needs.

## Sharpened atom

A stack is the **minimal structure that remembers LIFO order across types**; counters only remember counts. The moment correctness depends on *which* opened thing is innermost — not just *how many* are open — counters die and you need the stack.
