# Stack Atom 03 — Expression: operand stack · log

| Date | Event | Result |
|---|---|---|
| 2026-06-05 | Derived mechanic Socratically | ✓ self-derived: operand stack, operator pops fixed-arity operands, apply, push; second-popped = left operand |
| 2026-06-05 | Announced — Evaluate RPN (150) | ✓ clean AC; `Deque<Integer>`, isOperator/apply helpers, correct y/x order |
| 2026-06-05 | Perturbation (150) | ✓ load-bearing = input is postfix → precedence pre-resolved. Infix breaks apply-as-you-go (`3+4*2`→14 vs 11); postfix = post-order of expr tree → precedence frozen in token order → #3/#4 pipeline split. Tree schema seeded for #4 |
| 2026-06-05 | Disguised — Postfix→Infix (GfG) | ✓ clean AC; `Deque<String>`, same move with string payload, concat not compute |
| 2026-06-05 | Perturbation (Postfix→Infix) | ✓ every combination must be parenthesized — dropping parens makes output unfaithful (`ab+c*` → `a+b*c` reparses as `a+(b*c)` ≠ `(a+b)*c`, tree silently changed). Postfix encodes structure by position; infix by precedence+parens; payload must carry grouping, not just value |

**Atom #3 status:** ✓ covered — announced + disguised both clean, both perturbed.
**Owned (drill slot, later):** name in <5s cold, mixed-order, 3-day hold.
