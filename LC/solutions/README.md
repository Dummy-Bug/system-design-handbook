# Solutions Archive

Full accepted solution code, one file per problem, organized by band: `solutions/<band>/<leetcode-slug>.<ext>`.

## Purpose
A code corpus for **analysis only** — cross-problem comparison, grepping recurring bug families (`(int)Math.pow`, `Set<int[]>`, overflow casts), and first-vs-second-attempt implementation diffs.

## Hard rule — do NOT open during revision
This archive is **off-limits during the two-week revision pass.** Revision is approach *recall*, not code *re-reading* (see `LC/CLAUDE.md`). Reading your old solution during revision destroys the cold-re-solve muscle. The band logs stay code-free for exactly this reason; the code lives here instead so the log can point to it without inviting a peek.

Open this archive only when:
- doing deliberate cross-problem code analysis, or
- a problem is fully graduated (`●`) and no longer in any revision cycle.

## File header convention
Each solution starts with a comment block: problem title + URL, band, log reference, verdict + time, one-line approach, and any review flags (habit-level, not bugs).

## Note on problem statements
Full problem descriptions (prose, sample test cases, constraints) are already cached as HTML at
`zerotrac-data/problem-content-cache/band_<lo>_<hi>/<slug>.json` (`data.question.content`).
No need to duplicate them here.
