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
Insight, key gotcha, complexity — and the full solution code is kept too (inline in the per-problem file, or in a per-problem/per-attempt file for newer bands; see the 1600-1650 per-attempt folder layout). Format:
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

## Current grind state (as of 2026-05-22)

- **Active zerotrac range:** 1700-1750 (resumed). Originally graduated from 1650-1700 on 2026-05-16 but then jumped to 1800-1850 prematurely after only 7/10 problems and entirely skipped 1750-1800. Pause acknowledged 2026-05-22 — returning to finish 1700-1750 (need 3 more), then full 10-problem pass at 1750-1800, before resuming 1800-1850.
- **1700-1750 pattern gap (target for remaining 3):** monotonic stack, binary search on answer, interval/tree DP. Current 7 ACs concentrated in greedy + reframing.
- **1800-1850 paused:** 5 problems logged, marked paused in `1800-1850.md`.
- **Revision due:** 1650-1700 batch — due 2026-05-30.
- **Contest rating:** ~1530 (frozen, returning after gap)
- **Projection:** ~1680 by Dec 2026 if protocol holds (slightly later now due to backfill)

## Core protocol rules (don't break these)

1. **30-min hard cap** on new problems — stop at 30, write 3-line stuck note, then editorial
2. **Cold re-solve same day** — after editorial (or AC), close everything, blank file, solve again
3. **No editorial before 30 min** — even a glance counts as a fail
4. **Pool separation** — zerotrac = last 6 months of contests. Virtual contest = 12+ months old. Never mix
5. **Two-week revision lock** — revision is batched, not daily. Week N's problems get revised in Week N+2, *before* any Week N+2 new problem is started. Revision = approach recall only (5-10 min per problem), not full re-solve. Hard fails get a full cold re-solve + Day+14-from-now retry.
6. **Graduation (tightened 2026-05-22)** — bump range +50 only when ALL of the following hold for the prior band:
   - **10 problems logged.** No skip-3 escapes. If the band has fewer than 10, you have not finished it.
   - **≥7/10 first-submission AC.** "First-submission AC" means AC on the very first submit — not AC after a WA. WA-then-AC = soft fail.
   - **≤1/10 hinted.** Hinted = took editorial, took a hint from Claude, or had any external nudge before reaching the approach. Hinted counts as fail, not pass.
   - **≥8/10 pass + soft-fail combined on revision** (unchanged from prior rule).
   See `zerotrac.md` for Pass / Soft fail / Hard fail definitions.

   **Historical audit (2026-05-22):** prior graduations were called with looser counting. By the tightened rule above, 1550-1600 was 9/10 (1 hint), 1650-1700 was 6/10 first-submission (3 WAs + 1 hint), 1600-1650 and 1700-1750 were 7/10 (skip-3, ineligible). The 1750-1800 band was skipped entirely. These are now acknowledged inflations — the new rule prevents this from compounding further.

7. **Header integrity** — every band's `.md` file header MUST state the actual stats: `X/10 first-submission AC`, `Y/10 hinted`, `Z WA-then-AC`. Do not write summary stats like "10/10 first-try AC" if any of those 10 were WA-then-AC or hinted. Optimistic counting is the root cause of skip-3 — premature graduation feels earned because the headers lie, and the next band lands underprepared.

8. **No new band before prior band passes rule 6.** Opening a new band while the prior band's tightened-grad-check is unmet = protocol break. Caught retroactively, this triggers a backfill (return to the prior band and finish), not a header rewrite.

## Derivation-over-speed clause (current phase)

The user's diagnosed gap is **derivation muscle**, not pattern recognition (567 solved but mostly watched). For the current phase, self-derived ACs that overshoot the 30-min cap **count as passes for graduation**, provided no editorial/hint was used. The time overshoot is the price of training the exact muscle that was missing.

**How to apply:**
- Self-derived AC at any time → counts as pass — **provided first submission is AC.** If you submitted, got WA, then fixed and AC'd, this is **soft fail**, not pass. The derivation clause exempts time, not implementation discipline.
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
2. Recompute the richest example — find the example with a number breakdown /
                     explanation; THAT is the spec, not the prose. Reproduce every
                     number in it from your model. A number you can't reproduce is a
                     missing rule — STOP and find it before coding. Other examples are
                     quick branch-checks only.                [MANDATORY WRITTEN]
3. Edge cases      — 3-5 boundary cases on paper            [MANDATORY WRITTEN]
                     (empty input, single element, leading/trailing separator,
                      consecutive separators, max input size)
4. Decompose       — break into sub-problems, name each one
                     ask: which sub-problem is hardest / most bug-prone? code that first
5. Code bottom-up  — write helpers first, orchestrator last
```

### Enforcement contract (added 2026-05-23)

Steps 2 and 3 are mandatory written artifacts. Across the 1450-1850 audit, every WA-then-AC traces back to skipping these two steps. Steps 1, 4, 5 are not the failure mode — they happen naturally. Steps 2 and 3 don't.

**How this is enforced during sessions:**
- After the user derives an approach and BEFORE any code is written or requested, the user must post in chat:
  - **Step 2:** Recompute the *richest* worked example (the one with a number breakdown/explanation) through the proposed approach, reproducing every number from the model. Tracing to *confirm* is not enough — tracing to *derive* is the bar. A number the model can't reproduce is a missing rule; stop and find it before coding. (Read-error on 1600-band #4 and #5 both came from skipping/rushing this — #5's whole cost model was spelled out in the example that got ignored.)
  - **Step 3:** List 3-5 edge cases by name (e.g., "n=1", "all same color", "all diff color", "two elements same color", "max input size").
- Claude must **refuse to engage with code** until both are present in the conversation. If the user says "show me the code" or pastes a solution without steps 2-3 visible, Claude prompts them back to do the ritual first.
- The ritual artifacts stay in chat. They do not need to be written into the log file — the log file follows the "insight + key gotcha + complexity + full solution code" format.
- Exception: if the user explicitly says "skip the ritual, I want to see how I fail" — allowed, but logged as a deliberate ritual break in that problem's entry.

**Cost-benefit:** ~5 min overhead per problem. Today's House Robber V cost 60+ min and 4 WAs because the ritual was skipped — would have been caught on the first submission with `n=2, same color` traced. 12× return at minimum.

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

### Pre-submit checklist — Java-impl bug families that have recurred across bands

Run this **before clicking submit**. These are the bugs that bit across 1500-1850, derived from the actual log audit on 2026-05-22:

1. **Overflow / cast-to-long** — any product of values near 10^9, any `mid*mid` in binary search, any sieve `i*i`. Write `(long)a * b`, never `(long)(a * b)`. Trap: `long j = i*i` overflows int *before* assignment.
2. **Float-cast trap** — `(int) Math.pow(1e9, 1.0/3) = 999`. Always `+1` after casting `Math.pow` or `Math.sqrt` to int.
3. **`char` → digit value** — never `(int) s.charAt(i)` (returns ASCII 48-57). Use `s.charAt(i) - '0'`. This bug appeared at 1650-1700 #3 AND came back at 1800-1850 — three bands later, still not reflexive. See `02-syntax/05-conversions.md`.
4. **Set vs frequency map** — if the problem says "distinct indices, may share values" (or similar), use frequency map, not Set. If you need to dedup `(int, int)` pairs, `Set<int[]>` does NOT dedup (reference equality) — encode to long or String.
5. **`Set<int[]>` reference-equality** — array hashing is identity-based in Java. Use `Set<Long>` with bit-packing or `Set<String>`.
6. **PriorityQueue<int[]> / Integer[] needs comparator** — `Integer[]` is not `Comparable`, throws CCE on first sift. Always supply comparator.
7. **`if` vs `else if` in heap-update / sliding-window** — two consecutive `if`s on a boundary condition can fire twice in one iteration. Default to `else if`.
8. **Sentinel / last-element init** — when a linear scan propagates state rightward, the last index may never get updated. Initialize all sentinels explicitly; never leave `-1` to "be obvious."
9. **Single-candidate trap on "nearest X"** — always generate a small candidate set (e.g. P-1, P, P+1 for mirror palindrome) and take min, never assume one candidate covers all cases.
10. **Diff-array off-by-one** — range increment is `diff[l] += v; diff[r+1] -= v`. No special case for `l == r`. Anything else double-counts.
11. **Operator precedence** — `(freq & 1) != 0` needs parens around `freq & 1` (Java precedence makes `freq & 1 != 0` parse as `freq & (1 != 0)` — compile error or wrong).
12. **Window not fully built before use** — when iterating with a sliding window, always add `s[j]` first, then check size, then use. Checking before adding leaves the current element out.
13. **Window-build order matches edge cases** — also test with empty window, single element, consecutive separators.

Before submitting, scan this list. If your solution touches the bug family, verify the fix is applied.

---

## Problem solving session — Claude's role

**During active problem solving, Claude's ONLY job is to log what the user is thinking.**

- No hints. No nudges. No questions. No observations. No "interesting approach" commentary.
- Stay completely silent unless the user explicitly asks for help.
- When the user says "log it" or shares their thinking, record it faithfully.
- Help is given ONLY when the user says "help" or explicitly asks a question.

---

## Pattern-Reflex Deck — capture one move per solve

Lives in `patterns/deck.md`. It is the framing-level companion to `math-reflex/`: math-reflex installs *recall* (atomic facts → <5s), the deck installs *recognition* (a problem situation → the move that cracks it → <5s). The point is to permanently retire the "this should've taken seconds but cost me 5 minutes" class of fumble.

**The core rule — a card is born only from a real solve.** After a problem AC's, during debrief, ask the user one question:

> "What single move would have made this instant instead of slow?"

If a specific framing/micro-move cost real time, that move becomes one card. If nothing did, no card. **Never invent cards from intuition or mine them from a corpus** — the move lives in the solution, not the statement, and a card with no real-time-cost behind it is noise. One move per problem, max.

**Card shape (see `patterns/deck.md` for the format):** Trigger (the *felt signal* — what the user should recognize, usually a hesitation like "should this go here or there?") → Move (the mechanical response) → Anchor (the problem that birthed it) → Quiz prompt (1-line scenario; reflex answer names the move in <5s).

**Drilling & graduation:** identical bar to `math-reflex/00-protocol.md` — <5s cold, mixed order, 3 consecutive days, `◐` installing → `●` graduated. Drill the deck inside the **3-minute maintenance slot** of the daily math-reflex session, mixed in with the math facts. Quiz is application-level (a mini-scenario), never "define X".

**Why this and not a syllabus:** building a tagged framing-syllabus upfront is meta-work that solves zero problems and feeds the same over-scaffolding tendency behind the skip-3 history. The deck builds itself as a byproduct of reps. Keep the user grinding; harvest one card per solve.

---

## WA-cause tagging — every WA gets a greppable cause line

Whenever a submission gets a WA (in any band log, cold re-solve, or contest upsolve), log a one-line tagged cause alongside the root-cause analysis:

```
**WA-cause [<tag>]:** one-line description — what was actually wrong.
```

The tag is a short category so all WAs across all files can be aggregated later (`grep "WA-cause"`) to see whether a failure mode is a real recurring pattern or just noise. **Do not turn a single WA into a new pre-submit checklist item** — one data point is an anecdote, not a pattern. Just tag it and move on; promote to a checklist item only when the grep shows the same tag recurring across several problems.

Current tag vocabulary (extend as needed, keep tags stable so grep works):
- `[read-error]` — misread the problem (wrong counted unit, wrong objective, missed a constraint clause)
- `[logic-recurrence]` — DP/recurrence incomplete or base case wrong/stale
- `[logic-accounting]` — mixed accounting models (delta vs cumulative, double-count)
- `[impl-bug]` — correct approach, Java/implementation slip (overflow, wrong API, off-by-one)
- `[untraced-submit]` — would have been caught by a full Step-2 trace before submitting

A WA can carry more than one tag. The point is a uniform, machine-greppable record so WA analysis is data-driven, not vibes.

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
