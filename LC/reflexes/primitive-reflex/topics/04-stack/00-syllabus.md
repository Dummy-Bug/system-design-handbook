# Stack — Family Syllabus

Discriminator: **what the stack holds + what a pop means**.
Goal: with all 8 installed, a stack problem can only fail on **mapping**, never a missing tool. (★ = blind-spot, rule 6B.)

---

## The 8 primitives (learning order: foundation → hard)

| # | Primitive | Stack holds | Pop means | Canonical problems |
|---|---|---|---|---|
| 1 | Matching / balancing | open delimiters (or indices) | close → must pair; validity | Valid Parentheses (20), Min Add to Make Valid (921), Longest Valid Parentheses (32) |
| 2 | Adjacent-collapse / resolve-against-top | processed elements so far | top interacts with incoming → annihilate/merge/cancel | Remove All Adjacent Duplicates (1047), Asteroid Collision (735), Simplify Path (71) |
| 3 | Expression — **operand stack** | operands (a value, or a sub-expression string) | operator → pop its k operands, apply (compute / concat), push result | Evaluate RPN (150), Eval Postfix/Prefix, Postfix→Infix, Prefix→Infix |
| 4 | Expression — **operator-precedence stack** (shunting-yard) | operators (+ open-parens) | incoming op of ≤ precedence → pop & emit before pushing | Infix→Postfix, Infix→Prefix, Basic Calculator II (227, synthesis: precedence applied to eval) |
| 5 | Nested-structure fold-up | per-level partial result | close-bracket → fold child into parent | Score of Parentheses (856), Decode String (394), Basic Calculator I (224, parens), Number of Atoms (726) |
| 6 | Monotonic stack ★ | values/indices in sorted order | incoming breaks monotonicity → next/prev greater-smaller | Daily Temperatures (739), Sum of Subarray Minimums (907), Largest Rectangle in Histogram (84), Next Greater Element (496/503), Remove K Digits (402) |
| 7 | Min/max auxiliary stack | (value, running min/max) | lockstep with main | Min Stack (155), Maximum Frequency Stack (895) |
| 8 | Two-stack amortized | two stacks, transfer between | move when one empties | Queue using Stacks (232), Stack using Queues (225) |

> #3 vs #4 are the **expression pair**, learned back-to-back by contrast: #3 holds **operands** (pop-and-apply); #4 holds **operators** (pop-by-precedence). Same surface topic, two different stack-meanings → two atoms. Prefix variants = postfix mirrored (reverse the scan), a note, not a separate rep.

---

## Atoms

| # | Atom | Folder | Status |
|---|---|---|---|
| 1 | Matching / balancing | `01-matching/` | ✓ covered (validity + count facets) |
| 2 | Adjacent-collapse / resolve-against-top | `02-adjacent-collapse/` | ✓ covered (announced + disguised, both perturbed) |
| 3 | Expression — operand stack | `03-expression-operand/` | ✓ covered (announced + disguised, both perturbed) |
| 4 | Expression — operator-precedence (shunting-yard) | `04-expression-operator/` | not started |
| 5 | Nested-structure fold-up | `05-fold-up-nested/` | not started |
| 6 | Monotonic stack ★ | `06-monotonic/` | not started |
| 7 | Min/max auxiliary stack | `07-minmax-stack/` | not started |
| 8 | Two-stack amortized | `08-two-stack/` | not started |

Per atom: derive Socratically → solve announced (produce code cold) → solve disguised (install recognition) → perturbation debrief → write files → tick.

Each atom folder: `01-skeleton.md` · `02-notes.md` · `03-log.md` · `04-blind-deal.md` (DEALER-ONLY reserved-problem bank for the Phase-2 cold exam).

---

## Completeness

Cross-checked vs `learnyard-data/stack.tsv` (57) + `algomaster-data/stacks.tsv` (37) — every problem maps to these 8. (Validate Stack Sequences / Baseball Game = literal stack simulation = substrate, not a primitive.) Shunting-yard (#4) is contest-rare on LeetCode but a required sub-primitive — a composite problem can hide an infix→postfix step, so it's chunked here rather than deferred.

---

## Practice plan — minimal non-redundant reps (announced + disguised)

| Atom | Announced | Disguised / applied |
|---|---|---|
| 1 matching | [x] Valid Parentheses (20) | [x] Minimum Remove to Make Valid (1249) |
| 2 collapse | [x] Remove All Adjacent Duplicates (1047) | [x] Asteroid Collision (735) |
| 3 operand stack | [x] Evaluate RPN (150) — number payload | [x] Postfix→Infix (GfG) — string payload (same move) |
| 4 operator-precedence | [ ] Infix→Postfix / shunting-yard (GfG) | [ ] Basic Calculator II (227) — synthesis |
| 5 fold-up | [ ] Decode String (394) | [ ] Basic Calculator I (224, parens) |
| 6 monotonic ★ | [ ] Daily Temperatures (739) | [ ] Largest Rectangle in Histogram (84) |
| 7 min/max | [ ] Min Stack (155) | [ ] Maximum Frequency Stack (895) |
| 8 two-stack | [ ] Queue using Stacks (232) | [ ] Stack using Queues (225) |

> Skipped as redundant (mirror/duplicate moves, no retention gain): all Prefix-source conversions, Eval Prefix, Postfix→Prefix, Prefix→Postfix. One "prefix = reverse-scan postfix" note covers them.
