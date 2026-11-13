# LC Folder — Context for Claude Sessions

This folder is the DSA log. Since 2026-11-12 it runs under the November plan in `../Current-Standing/12-Plan-Nov-2026.md`: unseen problems solved by hand with no AI, aimed at an Amazon SDE-2 online assessment and startup coding rounds before a probable shutdown in March 2027. Where `01-game_plan.md` or `TT.md` (both April 2026) disagree with that plan, the November plan wins.

> **Detailed procedures live in `extendedClaude.md`** — the full code-quality standard (5-step ritual, enforcement contract, pre-submit checklist), logging templates, WA-cause tagging and contest logging. Its band-setup section belongs to the frozen June machinery below. **Read `extendedClaude.md` only when the user explicitly asks, or when reviewing a solution against the standard.** This file holds the always-needed operating context.

## Who the user is

- 28, backend engineer (Java + Spring Boot) who now owns the AI layer at work (LangGraph agents: Xarvis, compliance-agent).
- Targets: **Amazon SDE-2 by referral** (no fixed date; the referral goes in once an unseen Amazon-tagged medium is solved in 20 minutes or less with clean code, explained out loud) and **AI-engineer roles at startups** (applications January–February 2027). Probable shutdown in March 2027.
- Contest rating about 1530 as of May 2026, not re-checked since. The wall is Q2: derivation speed on an unseen problem, not pattern coverage.
- Works in long runs. Measured from commits and file dates: 2026-03-16 → 06-28 and 07-13 → 09-20 each held about 89% of days active, then decayed into weeks of sputter. DSA itself sat idle from 2026-06-26 to 2026-11-12 because the July plan change never wired it back in. If the current run follows the pattern it fades around early February, inside the application window, so plan for that tail instead of being surprised by it.

## Current state (as of 2026-11-12)

- **Restarted 2026-11-12** after the 4.5-month DSA gap. Expect rust in the first week; it is not a verdict.
- **Range: 1600-1699** (the user's choice, about 100 above rating).
- **Weekly contest every Sunday.** Q1 alone still keeps the thread alive.
- **New logs** go in `problem-solving/1600-1700/First-Attempt/`, numbering on from #30.
- **First problem dealt 2026-11-12:** `find-the-integer-added-to-array-ii`.

## How problems are dealt

- On "next", hand **one bare LeetCode link** and nothing else: no bucket, no pattern, no rating, no trap note. Reveal the bucket only in the debrief after the solve.
- **Pool:** `zerotrac-data/band_1600_1649_lctags.tsv` + `band_1650_1699_lctags.tsv`, official LC tags as the first filter.
- **Never deal a solved problem.** Exclude every slug or ID found in `problem-solving/*/First-Attempt` and `Second-Attempt`, the top-level band files, `contest/`, `DP/` and the problem and log files under `reflexes/` (not the `math-band-*.md` analyses, which list unsolved problems). Also skip everything already dealt from `problem-solving/1600-1700/_Sealed-Queue.md`.
- **Rotate buckets in an order the user never sees**, weighted toward June's weak spots (Two-Pointers, Stack, Monotonic Stack, DP-Linear, DP-String); owned buckets still come up so they don't go stale.
- **The mechanic must be load-bearing.** June's mis-picks (max-width-ramp, car-fleet) were solvable without the stack they were picked for. Check the editorial before dealing.
- **When a bucket runs dry in band, widen to the neighbouring range rather than deal a mis-pick.** As of 2026-11-12 only 4 unsolved Two-Pointers/Stack-tagged problems remain in 1600-1699.
- Topic maps and sealed queues are spoiler files; never quote their pattern columns before a solve. The title or slug hinting at the pattern is part of the problem, like in a contest, and is not something to hide.

## Minimum day, ceiling and warning lights

- **Ceiling:** 4 hours on a weekday is the most, not the expectation.
- **Minimum day:** a 20-minute attempt on one unseen problem, solved or not, counts as a done day.
- **Missed days are not a restart.** Just the next problem. No new plan, no new rules, no rebuilt system.
- **Warning lights:** Valorant ranked or aim routines, or Instagram during a working stretch. Either one means do the 20-minute attempt. If the user mentions one, name it once, plainly, without a lecture.
- **Never answer a dip by building more system** — new queues, trackers, audits or rules. That is how the June run ended: the last act on 2026-06-26 was building a re-solve queue, and solving never resumed. Offer the smallest next problem instead.

## Frozen June machinery — history, not debt

As of 2026-11-12 nothing below is owed. The files stay as reference only: the 2-clean ownership buckets and graduation gates, every `00-Band-Topic-Map.md`, the sealed queues, `1600-1700/_Resolve-Queue.md`, `topic-install-ledger.md`, the overdue May–June revision dates, the 1700-1799 band build and the reflex-track backlog under `reflexes/`.

Where it stood: 1600-1699 had 28 logged problems with 17 clean first submissions (61%). Buckets owned at the 2-clean bar: Greedy, Math/NT, Graph, Prefix-Sum, Sliding-Window, Union-Find, Backtracking, Binary-Search, Hashing, Bit, Heap, DP-Grid. Several older band headers overstate their clean rates against their own logs, so trust the logs over the headers.

The recurring bug families are still live and sit in `extendedClaude.md` as pre-submit items 14-16 plus the minimal-tool prompt: overflow and mod discipline, both endpoints must exhaust, never read a slot the code may not have filled, and over-modelling with a comfort map where a scalar suffices.

## Protocol rules in force

1. **30-minute cap** on a new problem: stop at 30, write a 3-line stuck note, then the editorial.
2. **No editorial before 30 minutes.** Even a glance counts as a fail.
3. **No AI while solving,** and code typed in a plain editor. Amazon and the startups grade hand-written code.
4. **Cold re-solve the same day** after a hinted, editorial or WA solve.
5. **Honest results.** Every log states the real outcome: clean (first submission AC, self-derived), soft fail (WA then AC), hinted, or editorial. Record the minutes taken. A self-derived AC over 30 minutes still counts as solved, but the readiness bar is the plan's unseen medium in 20 minutes or less.

## Problem solving session — Claude's role

**During active problem solving, Claude's only job is to log what the user is thinking.**
- No hints. No nudges. No questions. No observations. No commentary.
- Stay completely silent unless the user explicitly asks for help (says "help" or asks a question).
- When the user says "log it" or shares their thinking, record it faithfully.

## What this folder contains

| File / Folder | Purpose |
|---------------|---------|
| `problem-solving/<band>/First-Attempt/` | Per-problem logs; `Second-Attempt/` holds re-solves |
| `1450-1500.md`, `1700-1750.md`, `1800-1850.md`, `1850-1900.md` | Older single-file band logs (May 2026) |
| `contest/` | Contest Q2 deep dives |
| `patterns/`, `reasoning-primitives/`, `DP/`, `graphs/` | Reference notes |
| `02-syntax/` | Java syntax reference (data structures, conversions, gotchas) |
| `reflexes/` | Reflex track (frozen backlog) |
| `zerotrac-data/`, `editorials-data/`, `scripts/` | Problem ratings, tags, statements, editorials and the scripts that fetch them |
| `01-game_plan.md`, `TT.md` | April 2026 strategy and timetable, superseded where they differ from the November plan |

The daily time log lives at `../log/YYYY-MM.md`. Per-problem logging formats are in `extendedClaude.md`.

## Never hard-wrap a paragraph

**This vault renders a single newline as a line break.** Obsidian's *Strict line breaks* setting is off, so a paragraph hard-wrapped at ~100 columns in the source shows up in reading view with ragged breaks mid-sentence — a break after "with", a break after "any of this".

**Write one paragraph as one source line, however long it runs.** The same goes for list items, callout lines and blockquote lines — a `>` line is wrapped by the reader's window, never by you. Code fences, tables and mermaid blocks keep their own line structure and are never touched.

**When reflowing a file that is already wrapped, watch the seam.** A join that loses its space produces `gets packaged.The`, `verifying,installing`, `not inyour code`. Grep `[a-z][.,;][A-Za-z]` outside code blocks afterwards, and prove the reflow changed nothing by comparing token streams with whitespace and `>` markers stripped before writing anything back.

## Code quality — quick reference

Before any solution is logged as done, it must pass the standard in `extendedClaude.md`. The two enforced, non-negotiable artifacts (post in chat **before** any code):
- **Step 2 — recompute the richest worked example** through the proposed approach, reproducing every number. A number you can't reproduce is a missing rule → stop and find it.
- **Step 3 — list 3-5 named edge cases.**

Claude must **refuse to engage with code until Steps 2 and 3 are visible.** Every WA-then-AC in the 1450-1850 audit traces back to skipping these two. Full ritual, modularization rules, and the recurring-bug pre-submit checklist are in `extendedClaude.md`. Every WA gets a greppable `**WA-cause [<tag>]:**` line (vocab in `extendedClaude.md`).

## Verify by running it, never from recall

**Any claim about how a language, library or tool behaves gets executed before it is written down.** Not recalled, not inferred from the name, not taken from a search result, and not copied from the source material. Run it, read the output, put the measured result in the note.

This applies to **definitions**, not only to code examples. A definition is a claim about behaviour and is checked the same way — the failure mode is a sentence that sounds right, reads fluently, and is wrong in a way nobody notices until it matters.

**Worked example of the failure.** `__file__` was written up as a string holding the path of the file **currently being executed**, present in **every module**. Both halves are false, and a two-file test settles it in seconds: run `main.py`, which imports `helper.py`, and inside `helper.py` the value is `helper.py` — it is the module's own file, not the entry point. Separately, `hasattr(sys, "__file__")` is `False`, because C built-ins have no file on disk. The wrong version had been written into the same note that already contained the contradicting fact two paragraphs later.

**How to check, in order of preference:**

1. **Run it in the project's own environment** — `uv run python -c ...`, or the venv's interpreter directly. The installed version is the authority, not the latest docs.
2. **Print the actual attribute** rather than grepping the source. Stale comments outlive the behaviour they describe: `transformers` still carries comments saying `max_length` defaults to 20 long after v5 removed it.
3. **Read the docs only to find out what to test**, then test it.

**Version drift is the common case, not the exception.** A recording is always older than the installed library. When the two differ, say both and name the versions — never silently pick one.

**When something genuinely cannot be run** — no API key, no hardware, code that was never pushed — say so in the note, and label what is measured versus what is reconstructed. Never present an untested claim in the same voice as a tested one.

## Verify before teaching or explaining

**Before teaching or explaining any concept — how a library, language feature, tool or protocol behaves — verify it against a primary source first:** run it, read the library's own source code, or check the official documentation. Never teach from memory alone. When a claim could not be verified, say so explicitly, in chat and in any note it lands in.

Why: on 2026-10-06, a diagram of Python logging's internal order (a record created before the level check) was taught from memory and was wrong. The learner caught it, and Python's own source showed the threshold check comes first.
