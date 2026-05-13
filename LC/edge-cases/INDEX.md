# Edge Cases — Pattern Library

A living dictionary of edge case patterns. Built one problem at a time.

**Diagnosed gap:** edge cases are the #1 reason for WA on 1600+ problems. The gap isn't *handling* edge cases — it's *flagging* them while reading the problem. This folder builds the trigger → pattern dictionary.

**How to use:**
1. Before coding any problem, scan the trigger keywords in each file.
2. After every WA or hinted pass, log the new pattern as a new file here.
3. Target: 50+ patterns by Dec 2026, 150+ by interview time.

---

## Universal patterns (apply to any problem)

| # | Pattern | Trigger | Source |
|---|---------|---------|--------|
| 01 | [Distinct indices → frequency map](01-distinct-indices-frequency-map.md) | "distinct indices, may share value" | #7 outlier (2026-05-13) |
| 02 | [Self-reference in lookup](02-self-reference-in-lookup.md) | Iterating `i`, looking up `f(nums[i])` | #7 outlier |
| 03 | [Integer overflow — use long](03-integer-overflow-use-long.md) | sum/product up to 10^9, 10^10 | #3 House Robber V |
| 04 | [Modular arithmetic with negative offsets](04-modular-arithmetic-negative-offsets.md) | `(a - b) % MOD` where a<b possible | #4 Caesar Cipher |
| 05 | [Constraint reading first](05-constraint-reading-first.md) | Always | Meta-skill |
| 06 | [Adversarial test construction](06-adversarial-test-construction.md) | Always | Meta-skill |
| 07 | [Boundary — first/last element](07-boundary-first-last-element.md) | Index-based logic, prefix/suffix | Universal |
| 08 | [Empty and single element](08-empty-and-single-element.md) | n=0, n=1 inputs | Universal |
| 09 | [Tie-breaking rules](09-tie-breaking-rules.md) | "smallest", "largest", "lexicographically first" | Universal |
| 10 | [Category checklists](10-category-checklists.md) | Per-problem-type quick reference | Universal |

---

## Reading order (if starting from zero)

1. **05-constraint-reading-first** — read constraints BEFORE the problem
2. **10-category-checklists** — know what type of problem you're facing
3. **02-self-reference-in-lookup** — the most common bug class
4. **06-adversarial-test-construction** — the "solve, don't guess" mindset
5. Then walk through specific patterns as they come up

---

## How to add a new pattern

After every WA or hinted pass, create a new file:

```
NN-<short-kebab-case-name>.md
```

Template (copy this):

```markdown
# <Pattern Name>

> [!info] One-line plain-English summary

## When to suspect it
List of trigger keywords/conditions in problem statements.

## The bug — concrete failing example
Minimal test case + trace showing what goes wrong with the naive approach.

## The fix
Correct approach.

## Why it works
Brief explanation of why the fix is correct.

## Source problems
- LC #xxxx (link)

## Template for spotting in future problems
The mental check to run.

## Related patterns
[[other-pattern-name]]
```

Then add a row to the table above.
