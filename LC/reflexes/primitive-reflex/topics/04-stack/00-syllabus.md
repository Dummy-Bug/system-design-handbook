# Stack — Family Syllabus

Discriminator: **what the stack holds + what a pop means**.
Goal: with all 7 installed, a stack problem can only fail on **mapping**, never a missing tool. (★ = blind-spot, rule 6B.)

---

## The 7 primitives (learning order: foundation → hard)

| # | Primitive | Stack holds | Pop means | Canonical problems |
|---|---|---|---|---|
| 1 | Matching / balancing | open delimiters (or indices) | close → must pair; validity | Valid Parentheses (20), Min Add to Make Valid (921), Longest Valid Parentheses (32) |
| 2 | Adjacent-collapse / resolve-against-top | processed elements so far | top interacts with incoming → annihilate/merge/cancel | Remove All Adjacent Duplicates (1047), Asteroid Collision (735), Simplify Path (71) |
| 3 | Expression evaluation | operands (+ operators) | operator → pop operands, apply | Evaluate RPN (150), Basic Calculator I/II (224/227) |
| 4 | Nested-structure fold-up | per-level partial result | close-bracket → fold child into parent | Score of Parentheses (856), Decode String (394), Number of Atoms (726) |
| 5 | Monotonic stack ★ | values/indices in sorted order | incoming breaks monotonicity → next/prev greater-smaller | Daily Temperatures (739), Sum of Subarray Minimums (907), Largest Rectangle in Histogram (84), Next Greater Element (496/503), Remove K Digits (402) |
| 6 | Min/max auxiliary stack | (value, running min/max) | lockstep with main | Min Stack (155), Maximum Frequency Stack (895) |
| 7 | Two-stack amortized | two stacks, transfer between | move when one empties | Queue using Stacks (232), Stack using Queues (225) |

---

## Atoms

| # | Atom | Folder | Status |
|---|---|---|---|
| 1 | Matching / balancing | `01-matching/` | ✓ covered (validity + count facets) |
| 2 | Adjacent-collapse / resolve-against-top | `02-adjacent-collapse/` | not started |
| 3 | Expression evaluation | `03-expression-eval/` | not started |
| 4 | Nested-structure fold-up | `04-fold-up-nested/` | not started |
| 5 | Monotonic stack ★ | `05-monotonic/` | not started |
| 6 | Min/max auxiliary stack | `06-minmax-stack/` | not started |
| 7 | Two-stack amortized | `07-two-stack/` | not started |

Per atom: derive Socratically → solve announced (produce code cold) → solve disguised (install recognition) → perturbation debrief → tick.

---

## Completeness

Cross-checked vs `learnyard-data/stack.tsv` (57) + `algomaster-data/stacks.tsv` (37) — every problem maps to these 7. No 8th atom. (Validate Stack Sequences / Baseball Game = literal stack simulation = substrate, not a primitive.)

---

## Practice plan — 2 per atom (announced + disguised)

| Atom | Announced | Disguised / applied |
|---|---|---|
| 1 matching | [x] Valid Parentheses (20) | [x] Minimum Remove to Make Valid Parentheses (1249) |
| 2 collapse | [ ] Remove All Adjacent Duplicates (1047) | [ ] Asteroid Collision (735) |
| 3 expr-eval | [ ] Evaluate RPN (150) | [ ] Basic Calculator II (227) |
| 4 fold-up | [ ] Decode String (394) | [ ] Basic Calculator (224, parens) |
| 5 monotonic ★ | [ ] Daily Temperatures (739) | [ ] Sum of Subarray Minimums (907) · [ ] Largest Rectangle in Histogram (84) |
| 6 min/max | [ ] Min Stack (155) | [ ] Maximum Frequency Stack (895) |
| 7 two-stack | [ ] Queue using Stacks (232) | [ ] Stack using Queues (225) |
