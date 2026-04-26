# Zerotrac Playbook

How to use zerotrac as the daily LC grind tool. The log lives in `zerotrac-log.md`. Schedule lives in `TT.md`.

## What zerotrac is

https://zerotrac.github.io/leetcode_problem_rating/

A community-maintained rating database for every LC problem from contests. Filters by rating range, sorts by problem ID (recency) or rating. The standard tool for serious LC grinders past the Striver / NeetCode phase.

## Why zerotrac over Striver / NeetCode

- **Striver / NeetCode = pattern library.** Curated, taught, walkthroughs everywhere. Builds recognition.
- **Zerotrac = unlabeled, unsorted by topic, contest-rated.** No "this is sliding window" hint. Builds *derivation* — the muscle that actually moves contest rating.

Past 1500, the bottleneck is no longer "do I know this pattern?" — it's "can I derive the approach in 30 min on a problem I've never seen, with no topic label hinting the family?" Zerotrac is the only mainstream tool that simulates that.

## Daily protocol (90-min morning slot)

| Time | Block |
|------|-------|
| 8:00-8:05 | **Day-7 re-solve** — write algorithm structure cold from memory (no run, no submit) |
| 8:05-8:35 | **New problem** — 30 min hard cap, paper-first |
| 8:35-8:50 | If failed: 3-line stuck-note, then editorial |
| 8:50-9:20 | **Cold re-solve of today's problem** from blank file |
| 9:20-9:30 | Log everything in `zerotrac-log.md` |

### The day-7 re-solve (recall test)

Not a re-grind. Just a recall check.

- Open the problem (or just title — should remember prompt)
- Write core algorithm in blank file: function signature, data structures, main loop, key state
- 5 min cap
- **Pass = wrote the structure cleanly. Fail = struggled / structural errors / blanked.**
- No need to run or submit (do that later if you want, in evening Study #1)

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

## Graduation rule (when to bump range)

Look at **rolling last 10** in current range:

| Metric | Pass |
|--------|------|
| AC <30min, no editorial | ≥ 7/10 |
| Day+7 re-solve cold | ≥ 7/10 |

**Both must clear independently.** Sum is irrelevant.

| 30-min AC | Day+7 | Action |
|-----------|-------|--------|
| ≥7/10 | ≥7/10 | **Bump +50** |
| ≥7/10 | <7/10 | Stay. Session memory ≠ skill. |
| <7/10 | ≥7/10 | Stay. Outlier picks. |
| <7/10 | <7/10 | Stay. Protocol issue, not range issue. |

Realistic: 4-8 weeks per range. Don't rush bumps.

## What zerotrac is NOT

- **Not contest practice.** That's Wed virtual + Sun real.
- **Not pattern learning.** If you've never seen sliding window, learn it from a course/book first, then zerotrac it.
- **Not for hards.** Stay in medium territory until 1700+. Hards have ROI past Knight.
- **Not a count grind.** 1 deep > 3 shallow. The log is for honest signal, not vanity.

## The cheat reflexes to watch for

These will undo months of grind. Catch yourself:

1. **Opening editorial before 30 min hits** — even a glance counts
2. **Skipping the day-7 re-solve** "because I clearly remember it"
3. **Marking AC <30min as Y** when it took 35 min and you fudged the timer
4. **Skipping problems that look unfamiliar** — that's exactly the one you need
5. **Re-solving while peeking at yesterday's code** — it's not a cold re-solve then

The log is only useful if it's honest. Inflated logs lie to future-you about whether to bump range, and the rating ceiling stays.
