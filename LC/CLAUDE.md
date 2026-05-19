# LC Folder — Context for Claude Sessions

This folder is the DSA grind log for a 1-year plan to push LC contest rating from ~1530 to 1700+ by Apr 2027.

## Who the user is

- 28yo backend engineer, 2.6 years experience (Java + Spring Boot + LangGraph agents)
- LC contest rating: ~1530. 567 solved but mostly watched — derivation muscle is the real gap, not pattern recognition
- Target: 1700 by Q1 2027 (opens Atlassian / Razorpay / PhonePe / Swiggy tier). 1800-1900 by 2028 opens FAANG
- Also building **LeetDezine** (leetdezine.com) — system design interview prep platform

## What this folder contains

| File / Folder | Purpose |
|---------------|---------|
| `01-game_plan.md` | Full career strategy, rating → company mapping, daily schedule, 1-year eval rule |
| `TT.md` | Locked daily/weekly timetable, zerotrac progression, adherence tracker |
| `zerotrac.md` | Full protocol for using zerotrac — picking problems, 30-min cap, cold re-solve, graduation rule |
| `zerotrac-log.md` | Per-problem log for zerotrac sessions (compact table format) |
| `1450-1500.md` | Deep logs for the 1450-1500 rating band (insight, bug, reps tracking) |
| `1500-1550.md` | Deep logs for the 1500-1550 rating band |
| `weekly-contest-log.md` | Log for real weekly contests (recent, 90 min timed) |
| `biweekly-contest-log.md` | Log for real biweekly contests (recent, 90 min timed) |
| `virtual-contest-log.md` | Log for 90-min virtual contests (12+ months old, separate pool from zerotrac) |
| `contest/` | Individual problem deep dives (saved when insight is worth revising) |
| `patterns/` | Pattern-specific notes |
| `02-syntax/` | Java syntax reference (data structures, conversions, gotchas) |

## Logging rules — read before adding any entry

### zerotrac-log.md (compact table per problem)
```
| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Link | url |
| Rating | 1xxx |
| AC | Y / N |
| Time | <30min / xmin / hinted |
| Pattern | short label |
| Revision due | YYYY-MM-DD (Day+14, batched by week) |
| Remark | one line — key insight or bug hit |
```

### 1450-1500.md / 1500-1550.md (deep log per problem)
Only insight, key gotcha, complexity. **No full solution code.** Format:
```
### #N — Problem Name
**Link:** url
**Date attempted:** YYYY-MM-DD
**Rating:** 1xxx
**Time:** xmin — AC Y/N
**Pattern:** pattern label

**Insight:**
One paragraph — the key idea that unlocks the problem.

**Key gotcha:** (only if there's a real one)
What breaks naively and why.

**Complexity:**
O(?) time, O(?) space.
```

### virtual-contest-log.md
Log by contest. Include Q1/Q2/Q3/Q4 result (Y/N/S), what you were stuck on for each N, and upsolve due date.

## Current grind state (as of 2026-05-16)

- **Active zerotrac range:** 1700-1750 (graduated from 1650-1700 on 2026-05-16 — 7/10 first-try AC, 9/10 pass+soft-fail)
- **Revision due:** 1650-1700 batch — due 2026-05-30 (before any 1700-1750 Week 3 problems)
- **Contest rating:** ~1530 (frozen, returning after gap)
- **Projection:** ~1680 by Dec 2026 if protocol holds

## Core protocol rules (don't break these)

1. **30-min hard cap** on new problems — stop at 30, write 3-line stuck note, then editorial
2. **Cold re-solve same day** — after editorial (or AC), close everything, blank file, solve again
3. **No editorial before 30 min** — even a glance counts as a fail
4. **Pool separation** — zerotrac = last 6 months of contests. Virtual contest = 12+ months old. Never mix
5. **Two-week revision lock** — revision is batched, not daily. Week N's problems get revised in Week N+2, *before* any Week N+2 new problem is started. Revision = approach recall only (5-10 min per problem), not full re-solve. Hard fails get a full cold re-solve + Day+14-from-now retry.
6. **Graduation** — bump range +50 only when rolling last 10 hits ≥7/10 first-try AC AND ≥8/10 revision (Pass + Soft fail combined), independently. See `zerotrac.md` for Pass / Soft fail / Hard fail definitions.

## Derivation-over-speed clause (current phase)

The user's diagnosed gap is **derivation muscle**, not pattern recognition (567 solved but mostly watched). For the current phase, self-derived ACs that overshoot the 30-min cap **count as passes for graduation**, provided no editorial/hint was used. The time overshoot is the price of training the exact muscle that was missing.

**How to apply:**
- Self-derived AC at any time → counts as pass
- AC reached only after editorial/hint → counts as fail (cap rule still applies for hint-gating)
- Speed pressure is trained separately via virtual contests (90-min, 4 problems) — not via the 30-min cap on practice

**Expiry triggers — clause holds until BOTH are true:**
1. Active zerotrac band reaches **1950-2000** (raised from 1800-1850 on 2026-05-18). Reasoning: contest data shows the actual gap is Q3 capability (1700-2100 rated problems, never solved in recent contests), not Q2 speed. Q3 derivation muscle is the binding constraint. Speed is trained separately via virtual contests; the cap doesn't need to bind on the practice track until Q3 derivation is deep — i.e., comfortable at 1950-2000.
2. Virtual contests consistently 3-solved (Q1+Q2+Q3) within 90-min window

Once both are true, strict 30-min cap returns — because at that point speed is the binding constraint, not derivation.

**Trade-off accepted by raising the threshold to 1950-2000:** extends the derivation-clause runway by 3 bands (1800-1850, 1850-1900, 1900-1950). Cost is that speed under cap doesn't get trained on the practice track during these bands — must be aggressively trained via virtual contests (target 1+/week minimum) and real contests (weekly, already in cadence). If virtual contest Q3 stays unsolved at the 90-min mark across 4+ consecutive contests while zerotrac progresses through 1800-1950, revisit this threshold — derivation alone isn't translating to contest output.

**Q4 note:** Q4-rated problems (~2100+) are out of scope for the 1700 target; that's an SDE-3/FAANG concern for 2028. The 1800-2100 zerotrac range maps to contest Q3, which is the current rating bottleneck.

When deciding graduation, do NOT silently relax the rule — call out which ACs were over-cap, then explicitly apply this clause.

---

## Code quality standard — always check solutions against this

Every solution the user writes (zerotrac, upsolve, or contest) must be reviewed against this standard before being logged as done.

### The 5-step ritual (before touching the keyboard)

```
1. Comprehend      — what is input, output, the rule? Write it in ONE sentence
2. Verify approach — trace 1-2 given examples mentally
3. Edge cases      — 3-5 boundary cases on paper
                     (empty input, single element, leading/trailing separator,
                      consecutive separators, max input size)
4. Decompose       — break into sub-problems, name each one
                     ask: which sub-problem is hardest / most bug-prone? code that first
5. Code bottom-up  — write helpers first, orchestrator last
```

### Extract the predicate rule

Whenever the loop has a "is this character/element valid/invalid?" decision, extract it into a named helper:

```java
private boolean isSeparator(String s, int i) { ... }   // hard logic isolated here
// main loop becomes:
if (isSeparator(s, j)) { flush; advance; }
else { extend; advance; }
```

If edge cases are appearing inside the main loop as nested conditionals, stop — they belong in the helper.

### Modularization guideline

- Extract when the logic is complex enough to need a name (e.g. `isSeparator`, `isValid`, `shouldPop`)
- Don't extract trivial iteration — inline it
- Don't use intermediate collections (ArrayList) if you can write directly to the final data structure (HashMap)
- Orchestrator should read like English: one line per logical step

### When reviewing a solution, check:

1. Was the 5-step ritual followed before coding? (edge cases listed, sub-problems named)
2. Is the hard predicate logic extracted into its own function?
3. Are there nested conditionals inside the main loop that belong in a helper?
4. Is there an unnecessary intermediate collection that could be eliminated?
5. Does the orchestrator read cleanly — one logical step per line?

If any of these fail, point it out and show the cleaner version.

---

## Problem solving session — Claude's role

**During active problem solving, Claude's ONLY job is to log what the user is thinking.**

- No hints. No nudges. No questions. No observations. No "interesting approach" commentary.
- Stay completely silent unless the user explicitly asks for help.
- When the user says "log it" or shares their thinking, record it faithfully.
- Help is given ONLY when the user says "help" or explicitly asks a question.

---

## Contest logging and upsolving protocol

### Three separate contest logs (do NOT mix):

1. **virtual-contest-log.md** — Contests 12+ months old (practice pool, separate from zerotrac)
2. **biweekly-contest-log.md** — Recent biweekly contests (real submissions)
3. **weekly-contest-log.md** — Recent weekly contests (real submissions)

Each log entry:
- Contest number + date clearly labeled
- Q1/Q2/Q3/Q4 result: Y (AC) / N (stuck/TLE) / S (skipped)
- For each N: what was the missing insight or why it TLE'd
- Upsolve due date: Day+14 from contest date

### Upsolving protocol (when to try vs read solution):

**For AC problems that "got lucky"** (solved but approach was flawed):
- Try the **correct approach once** without time pressure (10-15 min)
- Goal: understand why your approach was wrong and practice the right pattern
- Then compare to reference solution
- *Don't* look up the solution first — the pattern learning happens in trying

**For N (stuck/TLE) problems:**
- Cold attempt without time pressure (20-30 min)
- Goal: Can you derive the insight yourself?
- If stuck after 20 min → look at solution and understand the key idea
- One upsolve per problem, no re-solves unless it's a hard conceptual gap

**Timing:**
- Upsolve window: Mon-Tue after the contest (2 days max)
- Don't defer upsolves past Day+14 — memory decay makes them less useful

### Saving individual contest problems:

If a contest problem is especially valuable (tricky insight, pattern worth remembering):
- Create `contest/<contest-name>-q<num>-<slug>.md` (e.g., `biweekly-182-q2-coherent-string.md`)
- Include: problem statement, key insight, link to problem
- Use this for observation/enumeration problems or non-standard patterns
- *Don't* create for every problem — only ones worth revising
