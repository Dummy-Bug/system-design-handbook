# Stack — Family Syllabus

Status: ✅ AUDITED-COMPLETE (2026-06-03), 7 atoms. Learning from scratch — no prior install assumed.

Discriminator: **what the stack holds + what a pop means**.

Robustness goal: with these 7 installed, the only failure on a stack problem is **mapping the problem to the right primitive** — never a missing tool. (★ = blind-spot per CLAUDE.md rule 6B.)

---

## The 7 stack primitives — learning order (foundation → hard), with LC problems

| # | Primitive | Stack holds | Pop means | Canonical problems |
|---|---|---|---|---|
| 1 | Matching / balancing | open delimiters (or indices) | close → must pair; validity | Valid Parentheses (20), Min Add to Make Valid (921), Longest Valid Parentheses (32) |
| 2 | Adjacent-collapse / resolve-against-top | processed elements so far | top interacts with incoming → annihilate/merge/cancel | Remove All Adjacent Duplicates (1047/1209), Asteroid Collision (735), Simplify Path (71), Make String Great (1544) |
| 3 | Expression evaluation | operands (+ operators) | operator → pop operands, apply | Evaluate Reverse Polish Notation (150), Basic Calculator II (227) |
| 4 | Nested-structure fold-up | per-level partial result | close-bracket → fold child into parent | Score of Parentheses (856), Decode String (394), Basic Calculator (224, parens), Flatten Nested List Iterator (341) |
| 5 | Monotonic stack ★ | values/indices in sorted order | incoming breaks monotonicity → next/prev greater-smaller | Next Greater Element (496/503), Daily Temperatures (739), Largest Rectangle in Histogram (84), Sum of Subarray Minimums (907), Remove K Digits (402), 132 Pattern (456) |
| 6 | Min/max auxiliary stack | (value, running min/max) | lockstep with main | Min Stack (155), Max Stack (716) |
| 7 | Two-stack amortized | two stacks, transfer between | move when one empties | Implement Queue using Stacks (232), Implement Stack using Queues (225) |

**Cross-ref (not a core stack atom — lives in Trees/Graph):** explicit-stack recursion simulation (iterative inorder/preorder/postorder, iterative DFS).

---

## Atoms (all fresh — derive Socratically in order)

| # | Atom | Folder | Status |
|---|---|---|---|
| 1 | Matching / balancing | `01-matching/` | ✓ derived (Valid Parentheses) — why-a-stack/LIFO |
| 2 | Adjacent-collapse / resolve-against-top | `02-adjacent-collapse/` | ✓ derived (Remove Adjacent Duplicates) — cascade = the tell |
| 3 | Expression evaluation | `03-expression-eval/` | not derived |
| 4 | Nested-structure fold-up | `04-fold-up-nested/` | not derived |
| 5 | Monotonic stack ★ | `05-monotonic/` | not derived (blind-spot — priority) |
| 6 | Min/max auxiliary stack | `06-minmax-stack/` | not derived |
| 7 | Two-stack amortized | `07-two-stack/` | not derived |

Learning order = foundation → hard. #1 matching teaches *why a stack*; each later atom adds one idea (collapse → operands → value-fold → ordering invariant → design variants).
