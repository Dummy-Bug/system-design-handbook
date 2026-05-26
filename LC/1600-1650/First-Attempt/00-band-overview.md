# LC Training Log — 1600-1650 band

Protocol: see `zerotrac.md`. Graduated from 1550-1600 on 2026-05-07 (10/10 first-try AC, derivation-over-speed clause applied — see `CLAUDE.md`).

---

## Lessons learned from #7 (2026-05-13)

**Diagnosed gap (corrected 2026-05-25, second attempt):** the failure is *recognition*, not handling. I know how to handle index-distinctness — I just don't *see* it as a live threat while reading. A value-based validity check under an index-based constraint is the trigger: the value I match can be the same physical element as my candidate. The prompt literally said "distinct indices, but may share the same value" and I read past it because I never converted it into the question "could my match alias my current index?". Until that question is reflexive, the freq map will keep looking unnecessary. Do NOT log this as a "used Set instead of Map" knowledge slip — that mislabels it and guarantees a third fumble.

**Habit to install: decide the approach BEFORE coding, including edge cases.** Don't start writing the orchestrator and discover edge cases via WA on submit. The 5-step ritual in `CLAUDE.md` exists for this — actually use it.

### Edge case detection checklist (apply during step 3 of the 5-step ritual)

Run this on every problem before touching the keyboard:

1. **"Distinct indices" trigger.** If the problem says "distinct indices, may share values" (or variant) → **frequency map, NOT set**. The author is screaming the bug exists.
2. **Self-reference check.** When iterating `i` and looking up `f(nums[i])`, ask: "Can the lookup return `nums[i]` itself?" → edge case branch.
3. **Cardinality check.** Before using a Set, ask: "Do I care *whether* X exists, or *how many times*?" Default to frequency map unless duplicates explicitly ruled out.
4. **Algebraic collision check.** For derived values (target, complement, sum-minus-X), ask: "Can computed `target` accidentally equal `nums[i]`?" → distinct-index check required.
5. **Constraint keyword scan.** Search problem statement for: "distinct", "unique", "may be equal", "may share", "at least one". Each is a loaded flag.
6. **Adversarial test construction.** Before submitting, spend 5 min constructing the test most likely to break your solution. Derive backwards from the bug condition algebraically — don't guess arrays, *solve* for them.

### Pre-submit ritual

Answer two questions out loud before clicking submit:
1. "Where could my lookup return the same element I'm iterating on?"
2. "What's the most adversarial valid input I can construct that satisfies my bug condition?"

### Post-problem ritual (after AC)

Write one line: *"What pattern did this problem test, and what was the trigger keyword in the problem statement?"*

For #7: *"Distinct indices, may share values → frequency map, not set. Trigger: 'distinct indices, but may share the same value.'"*

**Goal:** build a trigger → pattern dictionary across 30+ problems so edge cases become reflexive, not learned-by-WA.

### Algebraic-thinking principle (also from #7)

When constructing failing test cases or spotting edge cases, **don't guess inputs and check** — **solve for inputs that satisfy the constraint**. Strong solvers do this naturally:

> "I want X to happen. What constraint does X impose? Solve for inputs that satisfy it."

Example from this problem: "I want target == nums[i]. Constraint: nums[i] = tSum/3. Pick valid array with one element = tSum/3 appearing once → `[1, 4, 5, 2]` (tSum=12, value 4 = 12/3)."

---
