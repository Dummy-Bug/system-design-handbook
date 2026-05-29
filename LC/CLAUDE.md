# LC Folder — Context for Claude Sessions

This folder is the DSA grind log for a 1-year plan to push LC contest rating from ~1530 to 1700+ by Apr 2027.

> **Detailed procedures live in `extendedClaude.md`** — band setup (Steps 1-8), the full code-quality standard (5-step ritual, enforcement contract, pre-submit checklist), logging templates, WA-cause tagging, pattern-reflex deck, and contest logging. **Read `extendedClaude.md` only when the user explicitly asks, or when setting up a new band / reviewing a solution against the standard.** This file holds the always-needed operating context.

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
| `1450-1500.md` / `1500-1550.md` | Deep logs for those rating bands (insight, bug, reps tracking) |
| `weekly-contest-log.md` | Log for real weekly contests (recent, 90 min timed) |
| `biweekly-contest-log.md` | Log for real biweekly contests (recent, 90 min timed) |
| `virtual-contest-log.md` | Log for 90-min virtual contests (12+ months old, separate pool from zerotrac) |
| `contest/` | Individual problem deep dives (saved when insight is worth revising) |
| `patterns/` | Pattern-specific notes (incl. `deck.md` — pattern-reflex deck) |
| `02-syntax/` | Java syntax reference (data structures, conversions, gotchas) |
| `topic-install-ledger.md` | Single source of truth: which pattern is installed at which band, deferred, outlier-class |

Logging formats for each file are in `extendedClaude.md` (Logging rules section).

## Current grind state (as of 2026-05-29)

- **1500-1550 WRAPPED 2026-05-29 (acquisition-only floor band).** This is the floor of the ladder — its job was to *install* each mechanic (one clean first-submission AC per bucket), NOT to own them; the 3-cold-clean ownership grind starts at 1550-1600 cross-band. Session clean ACs (5): Greedy, Flood Fill, Binary Tree, Two-Pointer (Maximum Distance), Bitwise XOR. + Monotonic Stack acquired cross-band (1550-1600 #22). + Linear DP acquired syntax-assisted (☑*, not an ownership rep). **Carry-forwards:** (1) plain **Binary Search / upper-lower-bound — OPEN**, its pick was solved via two-pointer so the BS mechanic was never installed → genuine rep owed at 1550-1600; (2) **Trie — DEFERRED** (no trie-requiring problem in-band, all sort/prefix-solvable). Per-problem logs in `1500-1550/First-Attempt/` (#11-#16); tracker + wrap banner in `1500-1550/Phase-1-Acquisition.md`. Dominant failure mode in this band's earlier 9 zerotrac solves = **IMPLEMENTATION bugs** (overflow ×3, float-cast, Set-vs-Map, loop bound, lambda), not derivation.
- **Active band: 1550-1600** (made active 2026-05-29 when 1500-1550 wrapped). Phase 1 acquisition COMPLETE (24 problems logged in `1550-1600/First-Attempt/`; monotonic stack first clean at #22). Phase 2 sealed queue rebuilt 2026-05-28 to 18 genuine unsolved problems, **0 solved under rebuilt queue**. Ownership tracker in `1550-1600/00-Band-Topic-Map.md` re-audited 2026-05-28 (all 24, LearnYard subgroups) and now current — owned: Greedy, Game Theory, Prefix Sum; ◐: Bit-XOR (2/3), Sliding Window (2/3), Graph traversal (2/3), Monotonic Stack (1/3), Interval DP (1/3 shortfall). Resume from the Phase-2 sealed queue to convert ◐ → ●; also owe plain-BS rep carried from 1500-1550.
- **1600-1650 paused:** Per-problem files in `1600-1650/First-Attempt/` and `Second-Attempt/`. **7/10 logged: 2 clean (#3 Split Array, #7 Sum of Digit Differences), 3 soft fail (#1 HRV, #2 Caesar, #4 Min Discards), 2 hinted (#5 Min Cost Path, #6 Outlier).** Word Squares II dropped. Graduation is ownership-based (rule 6). Dominant failure mode = **read-error / comprehension** (3 of 5 misses), not algorithm.
  - Selection system: `1600-1650/00-Band-Topic-Map.md` (SPOILER classification), `_Sealed-Queue.md` (sealed blind queue + answer key). Two sets — Set A = breadth/prereq ladder (study allowed); Set B = derivation×comprehension, cold. Interval DP confirmed absent at ≤1650.
- **1550-1600 selection system:** `00-Band-Topic-Map.md` (SPOILER, ownership tracker, Set A/B), `Phase-1-Acquisition.md` (15 intro, topic-visible), `_Sealed-Queue-Phase2.md` (24 derivation, shuffled blind). AR data at `zerotrac-data/band_1550_1599_with_ar.tsv`. Shortfalls (<3 reps): game theory, heap, mono stack, interval DP — stay uncapped, cross-band later. Union-Find dropped here (deferred to 1600-1650); Design dropped (not a derivation target).
- **After 1600-1650 graduates:** resume backfill ladder — finish 1700-1750 (need 3 more), full pass at 1750-1800, then 1800-1850 (5 logged, paused in `1800-1850.md`).
- **Revision due:** 1650-1700 batch — due 2026-05-30.
- **Contest rating:** ~1530 (frozen, returning after gap). **Projection:** ~1680 by Dec 2026 if protocol holds.

## Core protocol rules (don't break these)

1. **30-min hard cap** on new problems — stop at 30, write 3-line stuck note, then editorial.
2. **Cold re-solve same day** — after editorial (or AC), close everything, blank file, solve again.
3. **No editorial before 30 min** — even a glance counts as a fail.
4. **Pool separation** — zerotrac = last 6 months of contests. Virtual contest = 12+ months old. Never mix.
5. **Two-week revision lock** — revision is batched, not daily. Week N's problems get revised in Week N+2, *before* any Week N+2 new problem. Revision = approach recall only (5-10 min/problem). Hard fails get a full cold re-solve + Day+14 retry.
6. **Graduation (coverage-based).** Primary gate is **TOPIC COVERAGE, not raw count** — the count-only rule is what let the blind spots form (36 problems across 1500-1700, zero monotonic stack / tree DP / union-find). Bump range +50 only when ALL hold for the prior band:
   - **(A) Per-bucket OWNERSHIP — PRIMARY gate.** Every core bucket in the band's `00-Band-Topic-Map.md` must be **owned = 3 cold first-submission cleans on *distinct* problems.** Rep 1 may be vanilla; reps 2-3 must be disguised/combined (pattern not announced, Set B style); rep 3 is spaced (a session+ later, doubles as retention check). A WA/hinted/editorial solve does NOT count and resets that rep. Blind-spot/never-done buckets get an acquisition rep first (study-OK, doesn't count toward the 3). Amortization: a disguised problem covers 2+ buckets at once and counts toward each. Realistic band total ≈ **25-30 problems.** Core = all band buckets EXCEPT trivial direct-simulation; **math/NT/bit IS core.**
   - **(B) Blind-spot patterns mandatory and OWNED (cross-band).** Monotonic stack, tree DP, union-find must each reach 3 cold cleans (spread across whichever bands they appear in). BS-on-answer has reps (1500-1550 #8) but still needs 3 cold cleans to be owned.
   - **Growth principle:** depth lives in reps 2-3 (disguised forms), not rep 1. Re-solving vanilla teaches nothing.
   - **(C) Quality bar.** ≥70% first-submission clean AC; ≤1 hinted per 10 problems. WA-then-AC = soft fail.
   - **(D) Revision.** ≥80% pass + soft-fail combined on the two-week revision.
   - **Implication:** under (A)+(B), **none of 1500-1700 has truly graduated** — all four bands lack owned coverage of every core bucket, and the blind-spot trio has zero clean reps.
7. **Header integrity** — every band file header MUST state actual stats: `X/10 first-submission AC`, `Y/10 hinted`, `Z WA-then-AC`. Optimistic counting is the root cause of skip-3.
8. **No new band before prior band passes rule 6.** Opening a new band early = protocol break → triggers a backfill (return to prior band and finish), not a header rewrite.

(Pass / Soft fail / Hard fail definitions are in `zerotrac.md`.)

## Derivation-over-speed clause (current phase)

The diagnosed gap is **derivation muscle**, not pattern recognition. For the current phase, self-derived ACs that overshoot the 30-min cap **count as passes for graduation**, provided no editorial/hint was used.

- Self-derived AC at any time → pass — **provided first submission is AC.** WA-then-fix-then-AC = **soft fail** (the clause exempts time, not implementation discipline).
- AC only after editorial/hint → fail (cap rule still applies for hint-gating).
- Speed is trained separately via virtual contests (90-min, 4 problems), not via the 30-min cap.

**Expiry — clause holds until BOTH true:** (1) active band reaches **1950-2000**; (2) virtual contests consistently 3-solved (Q1+Q2+Q3) in 90 min. Then strict 30-min cap returns. Q4 (~2100+) is out of scope for the 1700 target.

When deciding graduation, do NOT silently relax the rule — call out which ACs were over-cap, then explicitly apply this clause.

## Problem solving session — Claude's role

**During active problem solving, Claude's ONLY job is to log what the user is thinking.**
- No hints. No nudges. No questions. No observations. No commentary.
- Stay completely silent unless the user explicitly asks for help (says "help" or asks a question).
- When the user says "log it" or shares their thinking, record it faithfully.

**Serving problems — deal BLIND:**
- On "next", hand **one bare LeetCode link** — NO pattern, NO set (A/B), NO score, NO trap note. Reveal set + pattern **only after** they finish, for the debrief.
- The pattern-labeled topic map and sealed queues are SPOILER files; never quote their pattern/set columns before a solve. Use a script that prints just the link column.
- The LC title/slug itself hinting the pattern is inherent to the problem (like a real contest) — not something to hide.

## Code quality — quick reference

Before any solution is logged as done, it must pass the standard in `extendedClaude.md`. The two enforced, non-negotiable artifacts (post in chat **before** any code):
- **Step 2 — recompute the richest worked example** through the proposed approach, reproducing every number. A number you can't reproduce is a missing rule → stop and find it.
- **Step 3 — list 3-5 named edge cases.**

Claude must **refuse to engage with code until Steps 2 and 3 are visible.** Every WA-then-AC in the 1450-1850 audit traces back to skipping these two. Full ritual, modularization rules, and the recurring-bug pre-submit checklist are in `extendedClaude.md`. Every WA gets a greppable `**WA-cause [<tag>]:**` line (vocab in `extendedClaude.md`).
