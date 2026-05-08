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
| `virtual-contest-log.md` | Log for 90-min virtual contests (12+ months old, separate pool from zerotrac) |
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

## Current grind state (as of 2026-05-07)

- **Active zerotrac range:** 1600-1650 (graduated from 1550-1600 on 2026-05-07, 10/10 first-try AC)
- **Revision due:** Week 1 of 1450-1500 batch — to be done before next new-problem week
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
1. Active zerotrac band reaches **1800-1850** (per zerotrac data this is the first band that is ~100% Q3 — meaning derivation is being trained at the level needed for contest Q3 solves; 1600-1700 is still mostly Q2, 1750-1800 is 50/50)
2. Virtual contests consistently 3-solved (Q1+Q2+Q3) within 90-min window

Once both are true, strict 30-min cap returns — because at that point speed is the binding constraint, not derivation.

**Q4 note:** Q4-rated problems (~1900+) are out of scope for the 1700 target; that's an SDE-3/FAANG concern for 2028.

When deciding graduation, do NOT silently relax the rule — call out which ACs were over-cap, then explicitly apply this clause.
