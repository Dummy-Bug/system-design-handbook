# Stack Atom 04 — Expression: operator-precedence (shunting-yard) · log

| Date | Event | Result |
|---|---|---|
| 2026-06-05 | Derived approach Socratically | ✓ user self-derived the shape cold: operands→output, operators→stack, flush by precedence, parens self-contained; correctly judged it O(n), not brute force |
| 2026-06-05 | Announced — Infix→Postfix (GfG) | ☑ AC, **code-assisted** — Claude wrote the implementation from the user's approach; the associativity clause (`c != '^'`, right-assoc `^`) was taught, not self-derived. Acquisition-level, NOT a cold ownership rep |
| 2026-06-05 | Perturbation / concept (associativity) | ✓ precedence = different-level decision, associativity = equal-level tiebreaker; left-assoc pops on equal, right-assoc (`^`) doesn't; the whole difference is the `c != '^'` clause. Tree schema harvested (one tree → pre/in/post = prefix/infix/postfix) |
| 2026-06-05 | Disguised — Basic Calculator II (227) | ☑ AC, **guided**. User self-derived the two-pass convert→evaluate pipeline cold (valid #3⊕#4 answer); single-pass sum-of-terms solution + trailing-space bug were walked through. Acquisition, NOT a cold rep |
| 2026-06-05 | Perturbation (227) | ✓ load-bearing = NO parentheses → flat sum of terms → single pass (even O(1)). Add parens → nesting → save outer state on `(`, fold child on `)` = fold-up primitive (atom #5). Basic Calc I/III = 227 + fold-up. WA-cause [edge]: trailing-space dropped final number (`" 3/2 "`→3 not 1) |

**Atom #4 status:** approach self-derived; both reps (announced + disguised) **code/guidance-assisted** — associativity and single-pass both taught. **Cold rep still owed** — the chunking certificate is producing #4 from scratch (associativity included) on a Phase-2 blind deal.
**Owned (drill slot, later):** name in <5s cold, mixed-order, 3-day hold.
