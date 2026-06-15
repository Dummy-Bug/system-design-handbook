# Stack — Family Syllabus

Discriminator: **what the stack holds + what a pop means**.
Goal: with all 9 installed, a stack problem can only fail on **mapping**, never a missing tool. (★ = blind-spot, rule 6B.)

---

## The 9 primitives (learning order: foundation → hard)

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
| 9 | Monotonic **candidate** stack — farthest/widest ★ | non-dominated candidates (strictly monotonic by value) | retire a candidate with its **farthest** partner (reverse sweep) | Maximum Width Ramp (962); max distance/span of a pair under an order condition |

> #3 vs #4 are the **expression pair**, learned back-to-back by contrast: #3 holds **operands** (pop-and-apply); #4 holds **operators** (pop-by-precedence). Same surface topic, two different stack-meanings → two atoms. Prefix variants = postfix mirrored (reverse the scan), a note, not a separate rep.
>
> #6 vs #9 are the **monotonic pair**: #6 = **nearest** greater/smaller, per-element, one pass (pop = resolve/discard). #9 = **farthest/widest** pair, one global optimum, two passes (build candidate stack, then reverse-sweep; pop = retire with farthest partner). The discriminator is *nearest vs farthest* — both run the "drop dominated elements" engine. (Gap found 2026-06-15: #9 was missing, so Max Width Ramp didn't trigger any installed reflex.)

---

## Atoms

| # | Atom | Folder | Status |
|---|---|---|---|
| 1 | Matching / balancing | `01-matching/` | ✓ covered (validity + count facets) |
| 2 | Adjacent-collapse / resolve-against-top | `02-adjacent-collapse/` | ✓ covered (announced + disguised, both perturbed) |
| 3 | Expression — operand stack | `03-expression-operand/` | ✓ covered (announced + disguised, both perturbed) |
| 4 | Expression — operator-precedence (shunting-yard) | `04-expression-operator/` | approach self-derived; both reps guided (associativity + single-pass taught) — cold rep owed |
| 5 | Nested-structure fold-up | `05-fold-up-nested/` | ✓ both reps done (394 + 224), guided — cold rep owed |
| 6 | Monotonic stack ★ | `06-monotonic/` | announced (739) = CLEAN self-derived AC = ownership 1 of 2 (blind-spot); 84 recalled (reframe confirmed, doesn't count); rep 2 deferred to zerotrac |
| 7 | Min/max auxiliary stack | `07-minmax-stack/` | ✓ core installed via Min Stack (155, recalled); 895 deferred (design). Boundary harvest: lockstep cache breaks on non-top pop |
| 8 | Two-stack amortized | `08-two-stack/` | ⏸ **DEFERRED** — design/implementation problem (Queue-from-Stacks), interview-only, ~zero contest-rating value. Pick up live if needed |
| 9 | Monotonic candidate — farthest/widest ★ | `09-monotonic-farthest/` | installed 2026-06-15 via Max Width Ramp (962), **Socratically led = acquisition** (not a self-derived rep). Mono-Stack blind-spot stays 1/2; rep 2 owed cold (carried #9 max-chunks) |

Per atom: derive Socratically → solve announced (produce code cold) → solve disguised (install recognition) → perturbation debrief → write files → tick.

Each atom folder: `01-skeleton.md` · `02-notes.md` · `03-log.md` · `04-blind-deal.md` (DEALER-ONLY reserved-problem bank for the Phase-2 cold exam).

---

## Completeness

Cross-checked vs `learnyard-data/stack.tsv` (57) + `algomaster-data/stacks.tsv` (37) — every problem maps to these 8. (Validate Stack Sequences / Baseball Game = literal stack simulation = substrate, not a primitive.) Shunting-yard (#4) is contest-rare on LeetCode but a required sub-primitive — a composite problem can hide an infix→postfix step, so it's chunked here rather than deferred.

---

## Practice plan — minimal non-redundant reps (announced + disguised)

| Atom                  | Announced                                              | Disguised / applied                                             |
| --------------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| 1 matching            | [x] Valid Parentheses (20)                             | [x] Minimum Remove to Make Valid (1249)                         |
| 2 collapse            | [x] Remove All Adjacent Duplicates (1047)              | [x] Asteroid Collision (735)                                    |
| 3 operand stack       | [x] Evaluate RPN (150) — number payload                | [x] Postfix→Infix (GfG) — string payload (same move)            |
| 4 operator-precedence | [☑] Infix→Postfix (GfG) — code-assisted, cold rep owed | [☑] Basic Calculator II (227) — guided synthesis, cold rep owed |
| 5 fold-up             | [☑] Decode String (394) — hint-assisted, code self-written, cold rep owed | [☑] Basic Calculator I (224) — term-stack self-derived → reduced to canonical fold, guided, cold rep owed |
| 6 monotonic ★         | [✅] Daily Temperatures (739) — CLEAN self-derived AC (ownership 1/2) | [◐] Largest Rectangle (84) — recalled, reframe confirmed, doesn't count; rep 2 → zerotrac |
| 7 min/max             | [◐] Min Stack (155) — recalled, both forms reproduced  | [⏸] Maximum Frequency Stack (895) — deferred (design)           |
| 8 two-stack           | [⏸] Queue using Stacks (232) — DEFERRED (interview-only) | [⏸] Stack using Queues (225) — DEFERRED                        |
| 9 monotonic-farthest ★ | [◐] Maximum Width Ramp (962) — led install, not a rep   | [ ] carried #9 max-chunks — cold rep owed (Mono-Stack 2/2)      |

> Skipped as redundant (mirror/duplicate moves, no retention gain): all Prefix-source conversions, Eval Prefix, Postfix→Prefix, Prefix→Postfix. One "prefix = reverse-scan postfix" note covers them.
