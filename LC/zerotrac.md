# Zerotrac Playbook

How to use zerotrac as the daily LC grind tool. The log lives in `zerotrac-log.md`. Schedule lives in `TT.md`.

## What zerotrac is

https://zerotrac.github.io/leetcode_problem_rating/

A community-maintained rating database for every LC problem from contests. Filters by rating range, sorts by problem ID (recency) or rating. The standard tool for serious LC grinders past the Striver / NeetCode phase.

## Why zerotrac over Striver / NeetCode

- **Striver / NeetCode = pattern library.** Curated, taught, walkthroughs everywhere. Builds recognition.
- **Zerotrac = unlabeled, unsorted by topic, contest-rated.** No "this is sliding window" hint. Builds *derivation* — the muscle that actually moves contest rating.

Past 1500, the bottleneck is no longer "do I know this pattern?" — it's "can I derive the approach in 30 min on a problem I've never seen, with no topic label hinting the family?" Zerotrac is the only mainstream tool that simulates that.

## Daily protocol (60-min morning slot)

| Time      | Block                                                |
| --------- | ---------------------------------------------------- |
| 8:00-8:30 | **New problem** — 30 min hard cap, paper-first       |
| 8:30-8:45 | If failed: 3-line stuck-note, then editorial         |
| 8:45-8:55 | **Cold re-solve of today's problem** from blank file |
| 8:55-9:00 | Log everything inside files of respective range      |

### Revision is batched, not daily

Revision happens **2 weeks after a problem batch**, not Day+7 staggered. See "Revision protocol" section below. The morning slot is for new problems only — no Day+7 mini-rep.

### The new problem (30-min cap)

| Phase | Time | Action |
|-------|------|--------|
| Read | 0-5 | Identify pattern family on paper. What's the state? What's the invariant? |
| Derive | 5-15 | Approach on paper. Pseudocode. NO IDE yet. |
| Code | 15-25 | Translate to code |
| Debug | 25-30 | Run, fix |
| **30** | — | **Hard stop.** If AC, done. If not, 3-line note → editorial. |

### The 3-line stuck-note (when you fail)

Before opening editorial, write on paper:

1. Pattern I thought it was: _____
2. Where my approach broke: _____
3. What I think the missing insight is: _____

Then read editorial. The note forces honesty about *why* you failed — not just *that* you failed.

### Cold re-solve of today's problem

After editorial (or if AC'd first try), close everything. Open blank file. Solve from scratch.

If you can't, you didn't internalize the editorial. Re-read, try again. Don't move on until cold-solve works.

## Picking problems

### Filter rules

- **Rating range:** see TT.md monthly progression. Always 50-100 below your contest rating.
- **Sort:** by ID descending (newest first). Recent contest problems = current style.
- **Pool separation:** zerotrac picks come from last ~6 months of contests. Virtual contest pool = 12+ months old. Don't mix.

### When to skip a problem

- Only if you've **already solved it** previously (mark in log, skip)
- Don't skip because it "looks hard" — that's the whole point
- Don't skip to find a "better" problem — first 1 in the filtered list is the one

### Bucket distribution (avoid cherry-picking easy)

Inside a 50-point range, split into 5 sub-buckets of 10 points each. Aim for **2 problems per sub-bucket** across the 10-problem graduation cycle.

Example for range 1450-1500:
- 1450-1459: 2 problems
- 1460-1469: 2 problems
- 1470-1479: 2 problems
- 1480-1489: 2 problems
- 1490-1499: 2 problems

Why: an even distribution prevents you from quietly weighting the bucket toward the easy end of the range. The graduation signal (7/10 AC) is only honest if the 10 problems span the full range.

If you don't hit 7/10, don't repeat the same 10 — pull 10 *new* problems with the same bucket distribution. Same range, fresh pool.

## Revision protocol (Day+14 batch, approach-only)

Revision is the second graduation gate. The bottleneck at 1500+ is **derivation recall**, not coding — so revision tests "can I retrieve the insight cold 2 weeks later?", not "can I retype the Java?".

### The two-week lag rule

> **Do not start Week N+2's new problems until Week N's revision batch is done.**

This is the lock. Revision is non-skippable — it gates new work. Calendar can't fragment because the grind itself stalls until the loop is closed.

Cycle:
- **Week 1:** solve fresh problems, log them
- **Week 2:** solve fresh problems, log them
- **Week 3:** revise *all* of Week 1's problems before any new Week 3 problem
- **Week 4:** revise Week 2's problems before any new Week 4 problem
- ... and so on

### Per-problem revision (5-10 min)

This is **approach recall, not full re-solve**. No coding unless you fail.

1. Open the problem link. Read the statement fresh.
2. Close everything. Speak or whiteboard the approach out loud:
   - What's the pattern family?
   - What's the key insight that unlocks it?
   - What was the gotcha (if any)?
3. Open your log entry. Compare against what you said.

### Pass / Soft fail / Hard fail

| Outcome | Definition | Action |
|---------|------------|--------|
| **Pass** | Approach recalled clean within ~30s of reading. Matches log. | Mark ✓. Done. |
| **Soft fail** | Approach correct, missed the gotcha or a detail. | Re-read your own gotcha note. Mark ◐. No re-solve. |
| **Hard fail** | Blanked on approach OR recalled wrong pattern. | **Full cold re-solve, 30-min cap, code + submit.** Mark ✗. Add to Day+14-from-now retry list. |

### Why approach-only

Coding gaps you've already mined out (StringBuilder, `(long)i*i`, `Math.ceil((double)`). The thing that costs rating is blanking on the insight in a contest. That's testable in 7 min, not 30. New weekly problems naturally exercise typing — revision doesn't need to.

### Graduation rule (when to bump range)

Two independent gates over the **rolling last 10** in current range:

| Metric | Pass |
|--------|------|
| AC <30min on first attempt, no editorial | ≥ 7/10 |
| Day+14 revision (Pass + Soft fail combined) | ≥ 8/10 |

**Both must clear independently.** Sum is irrelevant.

The revision bar is 8 not 7 because approach-only is faster — easier reps mean a higher bar to call retention "real".

| First-try AC | Revision | Action |
|-----------|----------|--------|
| ≥7/10 | ≥8/10 | **Bump +50** |
| ≥7/10 | <8/10 | Stay. Recall is fragile. |
| <7/10 | ≥8/10 | Stay. Sample was easy or lucky. |
| <7/10 | <8/10 | Stay. Range too high. |

### Hard-fail recovery

Every hard fail goes on a **Day+14-from-now retry list**. Don't roll it into the next batch silently — track the second attempt separately. A problem failed twice (original N + revision hard fail) is a known pattern gap; it gets a third dedicated cold rep before you call it owned.

Realistic: 4-8 weeks per range. Don't rush bumps.

## What zerotrac is NOT

- **Not contest practice.** That's Wed virtual + Sun real.
- **Not pattern learning.** If you've never seen sliding window, learn it from a course/book first, then zerotrac it.
- **Not for hards.** Stay in medium territory until 1700+. Hards have ROI past Knight.
- **Not a count grind.** 1 deep > 3 shallow. The log is for honest signal, not vanity.

## The cheat reflexes to watch for

These will undo months of grind. Catch yourself:

1. **Opening editorial before 30 min hits** — even a glance counts
2. **Skipping revision** "because I clearly remember it" — recall feels stronger than it is
3. **Marking AC <30min as Y** when it took 35 min and you fudged the timer
4. **Skipping problems that look unfamiliar** — that's exactly the one you need
5. **Calling a Soft fail a Pass** because you "would have got the gotcha eventually"
6. **Starting Week N+2 before Week N's revision is done** — breaks the lock
7. **Approach-recalling with the log open** — it's not cold recall then

The log is only useful if it's honest. Inflated logs lie to future-you about whether to bump range, and the rating ceiling stays.
