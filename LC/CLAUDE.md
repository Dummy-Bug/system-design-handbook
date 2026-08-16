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

## Current grind state (as of 2026-06-15)

- **1500-1550 WRAPPED 2026-05-29 (acquisition-only floor band).** This is the floor of the ladder — its job was to *install* each mechanic (one clean first-submission AC per bucket), NOT to own them; the 2-clean (self-derived, distinct problems) ownership grind starts at 1550-1600 cross-band. Session clean ACs (5): Greedy, Flood Fill, Binary Tree, Two-Pointer (Maximum Distance), Bitwise XOR. + Monotonic Stack acquired cross-band (1550-1600 #22). + Linear DP acquired syntax-assisted (☑*, not an ownership rep). **Carry-forwards:** (1) plain **Binary Search / upper-lower-bound — OPEN**, its pick was solved via two-pointer so the BS mechanic was never installed → genuine rep owed at 1550-1600; (2) **Trie — DEFERRED** (no trie-requiring problem in-band, all sort/prefix-solvable). Per-problem logs in `1500-1550/First-Attempt/` (#11-#16); tracker + wrap banner in `1500-1550/Phase-1-Acquisition.md`. Dominant failure mode in this band's earlier 9 zerotrac solves = **IMPLEMENTATION bugs** (overflow ×3, float-cast, Set-vs-Map, loop bound, lambda), not derivation.
- **1550-1600 CALLED 2026-06-10 — not fully graduated; open debts ROLLED FORWARD into the merged 1600-1699 band** (the real blocker is carelessness ~65% first-sub clean, NOT coverage; a 50-pt jump is difficulty-noise so debts close equally well next band). Was active 2026-05-29 → 2026-06-10. 40 First-Attempt problems logged (**no separate acquisition phase in this band** — acquisition is floor-band-only; every clean self-derived solve here counts as an ownership rep). Sealed queue at `1550-1600/_Sealed-Queue-Phase2.md` (blind deal-list + spoiler answer key + trickiness tiers) supplies further problems; deals #1-8 done. Topic map + ownership tracker at `1550-1600/00-Band-Topic-Map.md`: every solved problem classified by the mechanic in OUR code (**DP tracked by sub-pattern, not as one bucket**). **Ownership reality (re-audited 2026-06-03 under the 2-clean rule): OWNED ● = Greedy, Prefix-Sum, Sliding Window, Graph, Math/NT (5 buckets).** 1-of-2 = DP-LIS(34), DP-Grid(31), Hashing(33), Backtracking(19), Game-Theory(03), DP-Interval(13), Monotonic-Stack(22). 0-of-2 = DP-Linear, DP-String, Two-Pointers, Heap, Binary-Search, Tree, Union-Find. **tree-DP and Union-Find blind spots still 0.** **Policy: owned = 2 clean self-derived ACs per (sub-)bucket; Set-A or Set-B both count (no acquisition phase outside floor band).** Owe plain-BS rep carried from 1500-1550. **Debts at call-time (now owed in 1600-1699):** blind-spots Mono-Stack 1/2, Union-Find 1/2, Tree-DP 0/2; 0-of-2 = DP-Linear, DP-String, Two-Pointers, Heap, Binary-Search; 1-of-2 = DP-LIS, DP-Grid, Hashing, Backtracking, Game-Theory, DP-Interval. See `topic-install-ledger.md`.
- **>>> ACTIVE BAND: 1600-1699 <<<** (made active 2026-06-10; deliberate **100-pt-wide** band merging old 1600-1650 (7 logged) + 1650-1700 (10 logged) stubs — consolidates fragmented work AND doubles per-bucket supply so blind-spots Union-Find & Tree-DP become ownable in-band). Topic map + ownership tracker (carried debts pre-filled) at `1600-1700/00-Band-Topic-Map.md`; blind sealed queue (23 disguised problems, shuffled, spoiler answer key) at `1600-1700/_Sealed-Queue.md`. New problems → `1600-1700/First-Attempt/`. **Two jobs only:** close carried debts + own the blind-spots **in-band — now just Mono-Stack** (Union-Find ✅ OWNED 2/2 #01; **Tree-DP DEFERRED 2026-06-12, supply-justified** — re-audit of band tree tags found ~20 tree problems but **0 force a true optimization recurrence**; all traversal/aggregation/construction, so tree-DP can't be *owned* here and relocates cross-band per rule 6B; see `topic-install-ledger.md` §1+§2). Zero NEW ownership targets. **Headline metric: first-submission-clean rate** (Step-2/3 on EVERY solve; ≥70%, ≤1 hinted/10) — the carelessness fix is THE point of this band; current in-band rate **17/26 ≈ 65% — BELOW the 70% floor** (last 6 solves: 5 non-clean). **⚠ HINTED-RATE OVER BAR:** ~7 hinted/helped in 26 ≈ **2.7 per 10 ≫ the ≤1/10 limit (rule 6C)**. **⚠ OVER-MODEL RECURRING (5×):** push-dominoes/advantage/ramp/car-fleet/di-string all dodged their target mechanic via a comfort hashmap [[lc-index-bookkeeping-overmodel]]. **→ 2026-06-26: band PAUSED for a flow-fix + re-solve detour** (see 2026-06-26 snapshot below). Fix is behavioral, not coverage.
  - **PROGRESS SNAPSHOT (2026-06-15):** **OWNED 10/19 gating buckets (~53%)** = Greedy, Math/NT, Graph, Prefix-Sum, Sliding-Window, Union-Find (#01), Backtracking (#05), **Binary-Search (#13,#14 — both BS-on-answer; one bucket all flavors, closes plain-BS carry [[lc-binary-search-one-bucket]])**, **Hashing (seed re-audit)**, **Bit (#07 seed + #16 beautiful-subarrays, XOR reframe)**. **OWED: 11 reps / 7 gating buckets** = Two-Ptr(2), Heap(1), Stack(2), DP-Linear(2), DP-Grid(1), DP-String(2), Mono-Stack(1). **Deferred cross-band (supply <2, NON-gating): DP-LIS, DP-Interval, Tree-DP** (editorial-confirmed 2026-06-15). Blind-spots: UF ✅, Tree-DP ⊘, **Mono-Stack 1/2** (only blind-spot left in-band). **Long pole = DP** (5 reps / 3 sub-patterns: Linear 2, Grid 1, String 2) + scarce Mono-Stack. **Queue-coverage gap found 2026-06-15:** Stack (0/2) and Two-Pointers (0/2) have **exhausted their queue picks without credit** — Stack (#11 editorial, #16 pre-solved re-solve), Two-Ptr (#03 over-model, #17 TreeMap-greedy) — so **both need 2 FRESH non-queue picks each**. (Queue-build didn't dedup vs reflex-track solves nor enforce mechanic-match.) **Graduation estimate SUSPENDED 2026-06-26** (see next bullet): clean-rate fell below floor and the cold re-solve (rule 2) was found dropped band-wide → forward motion paused for a flow-fix + re-solve detour before fresh picks resume.
  - **AUDIT + RE-SOLVE DETOUR (2026-06-26):** Folder-wide audit (user-prompted) confirmed we keep *solving* non-clean and never *learning* from it — **cold re-solve (rule 2) was silently dropped** after `1600-1650-Old` (the only band with a `Second-Attempt/`: 8/8), and 4 bug-families recur across bands (overflow since floor band, over-model 5×, `incomplete-validation` #24→#28, stale-read #27/#29) while their counter-habits sit un-consolidated across 28 First-Attempt logs. **Decision (user): fix the FLOW before draining the stock** — the backlog refills every band because the generator is unfixed. **Phase A ✅:** promoted the 4 families to the pre-submit checklist (`extendedClaude.md` items 14-16 + a minimal-tool *pre-derivation* prompt — executing the protocol's own promote-on-recurrence step, which had never fired). **Phase B ✅:** scoped two-track re-solve queue at `1600-1700/_Resolve-Queue.md` (Track 1 = snippet drills for impl-bugs you had-but-botched; Track 2 = cold re-derive for never-owned; scope = current-band + 2 cross-band stale-read reps). Re-solve logs → **`1600-1700/Second-Attempt/`** (structure restored). **⚠ Guardrail: re-solves install the HABIT, not ownership** — rule 6 gives no rep for re-solving an AC'd problem, so Two-Ptr/Stack/DP-Linear/DP-String/Mono-Stack still need FRESH picks after. **Validation metric = Track-1 first-try-clean fraction.** Sealed queue (#1-30) fully dealt. **Order: Track 1 → Track 2 → overdue Jun 10-15 revision (rule 5) → resume fresh picks.**
  - **Seed inventory ✅ RE-AUDITED 2026-06-15** (was "PENDING"): 17 old First-Attempt logs classified by mechanic-in-insight (code predates archive). 4 clean self-derived first-ACs credited → **Hashing 1/2→OWNED 2/2** (Mirror-Pairs + Sum-Digit-Diff; Closest-Equal surplus) + **Bit 0/2→1/2** (Unique-XOR-Triplets-I). Multi-Source-Flood-Fill clean but Graph already owned. Corrected an optimistic mislabel (Split-Array was "clean" → actually soft-fail/WA). Old-band First-Attempt clean-rate ≈24% — corroborates the carelessness thesis. Verdict table in `1600-1700/00-Band-Topic-Map.md` seed section.
  - **Data assembled 2026-06-10:** editorials BOTH halves (`editorials-data/band_1600_1649/` + `band_1650_1699/`; 95 fetched via `scripts/fetch_doocs_editorials.py`), AR both halves (`zerotrac-data/band_1600_1649_lctags.tsv` + `band_1650_1699_lctags.tsv`), statements cached (`problem-content-cache/band_1600_1699/`). LearnYard subgroups classify only the 1600-1649 half. **Cross-band rolls (no in-band supply — confirmed 2026-06-15 by tag + EDITORIAL audit of both halves): DP-LIS (genuine LIS = 0; the 2 phrase-hits 1121/2943 are greedy-count + sort-scan, not LIS-DP), DP-Interval (0 in tags AND editorials; Cutting-Cake-I is greedy), Tree-DP (blind-spot, deferred 2026-06-12).** All three have <2 genuine in-band problems → cannot be *owned* here, relocate per rule 6B. The topic map's earlier "DP-Interval now in-band" note was an unverified optimistic tag-read, now corrected. Deferred to next band: Topo-Sort, Dijkstra. Outlier: SegTree/BIT. Trie acquire-only; Design deferred. All in `topic-install-ledger.md`.
- **1550-1600 selection system:** `00-Band-Topic-Map.md` (SPOILER — topic list, mechanic-in-own-code classification, per-bucket + DP-sub-pattern ownership tracker), `_Sealed-Queue-Phase2.md` (27 disguised problems, shuffled blind deal-list + spoiler answer key w/ trickiness tiers). Canonical pattern vocab: `patterns/master-taxonomy.md` (22 areas, 25 DP sub-patterns; LearnYard ∪ AlgoMaster). **Data pipeline:** editorials for all 83 at `editorials-data/band_1550_1599/`; LearnYard subgroups at `editorials-data/band_1550_1599_subgroups.tsv` (classifies only 59/83 — **misses all solved problems**, so classify solved ones from our code/editorial, not LearnYard); AR/tags at `zerotrac-data/band_1550_1599_lctags.tsv`. **Closable in-band:** Two Pointers, Sliding Window, Stack, Binary Search, Bit, Hashing, DP-Linear/Grid/LIS. **Cross-band (too few in-band):** Monotonic Stack, Heap, Game Theory, Tree, Union-Find (2 DSU problems are in the queue for acquisition), Trie, SegTree.
- **After 1600-1699 graduates:** resume backfill ladder — finish 1700-1750 (need 3 more), full pass at 1750-1800, then 1800-1850 (5 logged, paused in `1800-1850.md`).
- **Revision due:** 1650-1700 batch — due 2026-05-30.
- **Contest rating:** ~1530 — **LIVE, not frozen** (competing weekly+biweekly; 8 contests May 10–Jun 14 2026). **Real profile = avg 1.5/4, Q2-wall:** Q1 instant (~3 min), Q2 is the entire battle (3 of 8 were "Q1 then nothing for 85 min"; the 2/4s landed Q2 at 30–64 min — too slow), Q3/Q4 untouched. **Bottleneck = derivation SPEED on a novel Q2, not coverage** — the derivation clause's over-cap "clean" ACs (36–46 min this week) would all be contest misses; see [[lc-contest-bottleneck-q2-speed]]. **Projection:** ~1680 by Dec 2026 if Q2-time is compressed (reflex-chunking, not just timed simulation).

## Core protocol rules (don't break these)

1. **30-min hard cap** on new problems — stop at 30, write 3-line stuck note, then editorial.
2. **Cold re-solve same day** — after editorial (or AC), close everything, blank file, solve again.
3. **No editorial before 30 min** — even a glance counts as a fail.
4. **Pool separation** — zerotrac = last 6 months of contests. Virtual contest = 12+ months old. Never mix.
5. **Two-week revision lock** — revision is batched, not daily. Week N's problems get revised in Week N+2, *before* any Week N+2 new problem. Revision = approach recall only (5-10 min/problem). Hard fails get a full cold re-solve + Day+14 retry.
6. **Graduation (coverage-based).** Primary gate is **TOPIC COVERAGE, not raw count** — the count-only rule is what let the blind spots form (36 problems across 1500-1700, zero monotonic stack / tree DP / union-find). Bump range +50 only when ALL hold for the prior band:
   - **(A) Per-bucket OWNERSHIP — PRIMARY gate.** Every core bucket in the band's `00-Band-Topic-Map.md` must be **owned = 2 clean self-derived first-submission ACs on *distinct* problems.** Clean = first submission AC (no WA). Self-derived = no hint/editorial. **No acquisition phase exists outside the floor band** — every clean self-derived solve in a non-floor band counts toward ownership, whether the pattern was announced (Set-A) or disguised (Set-B). Set-A/Set-B is only a *selection/difficulty* aid, NOT a counting gate. A WA/hinted/editorial solve does NOT count and resets that rep; re-solving an already-solved problem gives no new rep. Amortization: one problem covers 2+ buckets at once and counts toward each. **No spacing requirement** — retention is handled separately by the two-week revision lock (rule 5). Realistic band total ≈ **18-24 problems.** Core = all band buckets EXCEPT trivial direct-simulation; **math/NT/bit IS core.** _(History: gate was 3 cold cleans w/ a vanilla rep-1 allowed; simplified 2026-06-03 to **2 clean self-derived ACs, no Set-B/spacing requirement** — acquisition is floor-band-only, and the revision lock already catches decay.)_
   - **(B) Blind-spot patterns mandatory and OWNED (cross-band).** Monotonic stack, tree DP, union-find must each reach 2 clean self-derived ACs (spread across whichever bands they appear in). BS-on-answer has reps (1500-1550 #8) but still needs 2 clean self-derived ACs to be owned.
   - **Growth principle:** reps are genuine cold derivations, not studied installs — acquisition lives ONLY in the floor band. Re-solving a problem you've already solved teaches nothing; depth comes from new problems. (This is why the count dropped 3→2: with acquisition off-loaded to the floor band, every non-floor solve is already a real rep, so a third was dead weight.)
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

## Never hard-wrap a paragraph

**This vault renders a single newline as a line break.** Obsidian's *Strict line breaks* setting is off, so a paragraph hard-wrapped at ~100 columns in the source shows up in reading view with ragged breaks mid-sentence — a break after "with", a break after "any of this".

**Write one paragraph as one source line, however long it runs.** The same goes for list items, callout lines and blockquote lines — a `>` line is wrapped by the reader's window, never by you. Code fences, tables and mermaid blocks keep their own line structure and are never touched.

**When reflowing a file that is already wrapped, watch the seam.** A join that loses its space produces `gets packaged.The`, `verifying,installing`, `not inyour code`. Grep `[a-z][.,;][A-Za-z]` outside code blocks afterwards, and prove the reflow changed nothing by comparing token streams with whitespace and `>` markers stripped before writing anything back.

## Code quality — quick reference

Before any solution is logged as done, it must pass the standard in `extendedClaude.md`. The two enforced, non-negotiable artifacts (post in chat **before** any code):
- **Step 2 — recompute the richest worked example** through the proposed approach, reproducing every number. A number you can't reproduce is a missing rule → stop and find it.
- **Step 3 — list 3-5 named edge cases.**

Claude must **refuse to engage with code until Steps 2 and 3 are visible.** Every WA-then-AC in the 1450-1850 audit traces back to skipping these two. Full ritual, modularization rules, and the recurring-bug pre-submit checklist are in `extendedClaude.md`. Every WA gets a greppable `**WA-cause [<tag>]:**` line (vocab in `extendedClaude.md`).
