# LC Extended Reference — read only when explicitly asked

This file holds the detailed procedures that don't need to be in context every session. The lean always-loaded context lives in `CLAUDE.md`. Read this file when: setting up a new band, reviewing a solution against the code-quality standard, logging a contest, or when the user explicitly says to.

---

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

Run this **before clicking submit**. These are the bugs that bit across 1500-1850, derived from the actual log audit on 2026-05-22. **Items 14-16 + the minimal-tool prompt added 2026-06-26** after the 1600-1699 re-solve audit found these four families recurring across multiple problems while never getting promoted (the protocol's own promote-on-recurrence step had never fired):

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
14. **Modular-arithmetic discipline** — if the recurrence is ≥ exponential (doubling/Fibonacci) or sums outgrow `long` before the input cap, take `% MOD` at *every* step, not just at the end (1600-1699 #27: `2^n`/`φ^n` crosses `long` by length ~63-90 « the `10^5` cap; #02: no mod inside the loop → overflow WA). Recipe: exponential base `b` ⇒ overflow length `≈ 63 / log₂(b)`; if below max input, mod intermediately. **And modular *subtraction* can go negative** — `%` keeps the dividend's sign and mod is not order-preserving, so a reduced `a` can drop below a reduced `b` even when the true `a ≥ b` → always `((a - b) % MOD + MOD) % MOD` (#27).
15. **Both endpoints must exhaust (1-to-1 correspondence)** — when two sequences must match/transform/walk in lockstep, the accept test is "*both* ran out together" (`i == n1 && j == n2`), never just one side. Checking one direction silently lets the other carry unmatched extras (#24 move-pieces: dangling `L` after target matched; #28 expressive-words: trailing `"world"` while `s` was fully built). This family recurred twice in one band — make "which side am I *not* checking?" reflexive.
16. **Never read a slot the code may not have filled** — don't index a memo/DP/array position assuming it's populated. In memoized recursion, *invoke* `helper(x)` — don't read `dp[x]` directly (#27: recursion stepping −2/−4 from 5 never visits `dp[4]` → stale `-1`). For default-initialized accumulators/sentinels, guard before use — don't let a default (`0`/`-1`) silently act as a real value (#29 di-string: `int j = 0` flush fired on an empty stack → spurious full reverse; #12: stored cumulative desynced from its count). Sibling of item 8.

Before submitting, scan this list. If your solution touches the bug family, verify the fix is applied.

### Pre-*derivation* prompt — fires while modeling, before any code

- **Minimal-tool check (over-model)** — before reaching for `Map<key, Deque/List<index>>` or a stack of `(value, index)` tuples, ask: ***"count or positions? what is this structure actually doing — can a running variable / counter / two-pointer replace it?"*** This is the **#1 recurring quality leak**: a comfort-Map where one scalar suffices — #03 push-dominoes, #17 advantage-shuffle, #19 max-width-ramp, #26 car-fleet, #29 di-string (**5× and counting**). Over-modeling still ACs, so the clean-rate doesn't catch it — but it dodges the target mechanic *and* burns contest time. This prompt fires at derivation time precisely because a pre-submit check is too late. See [[lc-index-bookkeeping-overmodel]].

---

## Band setup protocol — how to generate problem sets for any new band

When starting a new band (or when the user asks to set up a band), follow this **exact** procedure. Do NOT ask the user to re-explain any of this.

### Step 1 — Read every statement in the band
- Source: `zerotrac-data/content-tsv/all_<band>_with_content.tsv` (cached HTML → clean to text).
- Read ALL problems in the rating range, not a sample. Title-only classification produced 4 mislabels — always read the actual statement.

### Step 2 — Fetch acceptance rate AND official tags for every problem
- Source: LeetCode GraphQL API. `POST https://leetcode.com/graphql` with `User-Agent` header (required — bare requests get 403).
- Query: `{"query":"query q($t:String!){question(titleSlug:$t){difficulty stats topicTags{name}}}","variables":{"t":"<slug>"}}`
- Parse `acRate` from the `stats` JSON string, `difficulty`, and the `topicTags` list.
- **`topicTags` is LC's canonical classification — fetch it here so Step 3 can verify against it, not guess.**
- Join with Q-position from `zerotrac-data/ratings.tsv` (columns: Rating, ID, Title, Title ZH, **Title Slug**, **Contest Slug**, **Problem Index** Q1-Q4).
- Save to `zerotrac-data/band_<lo>_<hi>_with_ar.tsv` with columns: `Rating | ID | Title | Slug | Contest | QPos | Difficulty | AR | LCtags`.
- Rate-limit: 0.5s sleep between requests, browser User-Agent header.

### Step 3 — Classify every problem by topic (verify against LC tags)
- Assign each problem to one (or more) of the band's ~15 core topic buckets.
- Core = everything EXCEPT trivial direct-simulation. **Math/number-theory and Bit/XOR are both CORE** (math-reflex trains recall only, not problem-solving).
- Use the statement + AR + Q-position, never just the title.
- **MANDATORY tag verification (added 2026-05-28 after the 1550-1600 mislabel audit).** Before locking any problem's bucket, cross-check it against the LC `topicTags` fetched in Step 2. A statement-based guess that contradicts the official algorithmic tag is a mislabel — trust the LC tag. *Root cause this prevents:* Closest Nodes Queries in a BST was hand-classified "Tree DP" and dealt blind under that label, but its LC tags are `Binary Search, BST` — there is no DP tag at all. The reader hit a binary-search problem with no prior binary-search acquisition rep. Ignore pure data-structure scaffolding tags (Array, Hash Table, String) — bucket by the *algorithmic* tag (Binary Search, Stack/Monotonic Stack, Union-Find, DP, Sliding Window, Greedy, etc.).
- **Plain binary search ≠ binary-search-on-answer.** Keep them as separate buckets — conflating them is what hid the plain-BS gap at 1550-1600.
- **Design is EXCLUDED at every band (added 2026-05-28).** Never make Design (data-structure-design problems) a target bucket — not in Group A acquisition, not in Group B, not in the ownership tracker. It is not a derivation-muscle target. Skip design-tagged problems entirely when building any band's Phase 1/Phase 2.

### Step 3b — Exclude already-solved problems (MANDATORY, added 2026-05-28)
- Before any selection, list every problem already solved in this band by reading `<band>/First-Attempt/` and `<band>/Second-Attempt/` (the `NN-<slug>.md` filenames are the slugs).
- **Never queue a duplicate.** An already-solved problem in a blind queue is a wasted rep — the reader recognizes it instantly. *Root cause this prevents:* the 1550-1600 Phase 2 queue contained 4 already-solved problems (band #1/#3/#8/#10) dealt as "blind."
- This exclusion applies to BOTH Phase 1 and Phase 2 selection.
- **Filename↔slug mismatch trap (added 2026-05-28).** `First-Attempt/` filenames are sometimes shortened and do NOT match the real LC slug (e.g. file `happy-strings` → real slug `the-k-th-lexicographical-string-of-all-happy-strings-of-length-n`; `construct-bst-from-preorder` → `construct-binary-search-tree-from-preorder-traversal`; `restore-array-from-adjacent-pairs` → `restore-the-array-from-adjacent-pairs`). Exact-slug exclusion silently leaks these solved problems back into the "unsolved" pool. When excluding, fuzzy-match shortened filenames to band slugs (or maintain a per-band alias set) and verify the exclusion count matches the number of logged files.

### Step 4 — Build Phase 1 (acquisition, dealt BLIND)

**Phase 1 installs a pattern's MECHANIC, and a mechanic is installed once — at the lowest band where the topic appears.** A topic already acquired in a lower band does NOT get a fresh acquisition problem here; the harder band re-creates the need for *derivation + pattern-recognition* (that's Phase 2), not re-installation. So split the band's buckets into two groups (added 2026-05-28 — the "one problem per *every* topic" rule was wrong; it re-taught known mechanics):

- **Group A — acquire in this band.** Topics that are NEW this band, or were never *acquired* in any lower band (deferred / dropped / absent). Each gets a real acquisition problem = the **easiest** available (highest AR, lowest Q-position). These are the only Phase 1 problems to solve.
  - **Bucket a problem by its UNINSTALLED topic, not its installed one (added 2026-05-28).** A problem usually carries several tags. If ALL its topics are already installed → it's Group B / Phase-2 material (skippable for acquisition). But if it contains *any* uninstalled topic — even alongside installed ones — it is an **acquisition target for that uninstalled topic.** *Substitutability is NOT grounds to skip:* a "k-th smallest" problem whose best solution is quickselect (uninstalled) but which *also* admits a heap solution (installed) still counts as the **quickselect** acquisition — because the intended solution uses the uninstalled tool and this is the only window to install it. Always defaulting to the owned substitute would leave the new pattern permanently uninstalled — that is exactly the blind-spot mechanism to avoid.
  - **Foundational vs Advanced classification (added 2026-05-28).** Every candidate Group A topic is one of two classes:
    - **Foundational** — core CS patterns the user MUST own for 1700-rating contests: monotonic stack, tree DP, backtracking, trie, plain BS, greedy, linear/grid DP, graph BFS/DFS, two-pointer, sliding window, hashing, heap/top-k, math/NT/bit, BS-on-answer, prefix/sort-scan, game theory, interval DP, union-find, difference array. **Install at the FIRST band where the pattern appears, regardless of supply.** The ≥3 rule below does NOT apply. Rationale: deferring foundational patterns on thin supply leaves permanent blind spots — exactly the failure mode 1500-1700 already suffered with monotonic stack / tree DP / union-find.
    - **Advanced** — patterns that are real CS topics but appear sparsely and where install-band choice matters: Topological Sort, Dijkstra / Shortest Path (weighted), Bitmask DP, Segment Tree, BIT, MST, monotonic deque/queue, Quickselect, Rolling Hash, Digit DP, KMP, etc. **Apply the ≥3-in-band-reps rule.** Install ONLY at the first band with ≥3 viable (non-Design) in-band reps (1 acquisition + 2 disguised derivation reps). Below 3, **defer** to the next band — log it in `LC/topic-install-ledger.md`. If no band 1500-1899 ever has ≥3, classify as **outlier / skip-class** (excluded as a target bucket, like Design). Examples confirmed outlier 2026-05-28: Segment Tree / BIT (0 viable in 8 bands), Monotonic deque (1-2/band always), Quickselect (2 in 1650-99 only), Rolling Hash (1-2/band always), MST (1-2/band, adjacent to Union-Find anyway), Geometry (niche LC topic, thin across 1700-2049).
  - **Update the central ledger.** Every Phase 1 generation reads and updates `LC/topic-install-ledger.md` — single source of truth for which pattern is installed at which band, what's deferred, and what's outlier-class. Group B citations in each band's Phase-1-Acquisition.md should reference this ledger.
  - **Subtopic granularity via LearnYard (added 2026-05-28).** Classify at LearnYard *subgroup* level (119 subgroups, `learnyard-data/subgroups.tsv`), NOT broad LC-tag level. A subtopic new to a band is a Phase-1 acquisition even if its parent main-topic was already installed (e.g. DP-on-Trees is a fresh acquisition even though Linear DP installed earlier). Use `scripts/classify_band_to_learnyard.py` (3 signals: doocs editorial tags + approach names + LC tags).
  - **Contest-pool-absent foundational patterns source from LearnYard (added 2026-05-28).** Some foundational patterns never appear as the *intended* solution in the rated zerotrac pool because contests favor greedy/DP optimizations over brute force. **Backtracking is the proven case** — a phantom across 1500/1550/1600 (every "Backtracking"-tagged contest problem solves via greedy/DP). When a foundational pattern is a phantom for 2+ consecutive bands, install it from LearnYard's curated list instead (`learnyard-data/<topic>.tsv` — these are classic, often *unrated* problems: Subsets, Permutations, Combination Sum, N-Queens, Sudoku for backtracking). Mark the acquisition "LearnYard-sourced" in the band's Phase 1. Don't keep deferring a foundational pattern band after band waiting for a contest problem that will never come.
  - **MANDATORY editorial-correctness check before locking any Group A pick (added 2026-05-28).** A topic is installable at a band ONLY if the **doocs editorial's actual solution** uses that pattern — not merely if the LC/doocs *tag* lists it. Tags are necessary, not sufficient. Fetch editorials via `scripts/fetch_doocs_editorials.py` → `editorials-data/band_<lo>_<hi>/`. Two phantom installs were caught this way at 1500-1549: "Tree DP" (pick was tree *traversal*, editorial = Recursion not DP) and "Backtracking" (both tagged problems had Greedy editorials). A phantom = passes the tag check, fails the editorial check. Always verify the editorial approach names before locking Group A.
- **Group B — already acquired in a lower band → Phase 2 only.** Listed in the Phase 1 file for completeness, tagged with the lower-band acquisition problem (and its outcome as provenance), but **no acquisition problem to solve.** Their disguised/derivation reps and this band's 2-clean (self-derived) ownership come entirely from Phase 2.
  - A soft-fail/hinted acquisition in the lower band is still Group B — do NOT re-acquire. Rule 8 guarantees the lower band has *graduated* (2 clean self-derived ACs per bucket) before this band opens, so Group B topics are **owned, not shaky** on arrival. The lower-band Phase-1 outcome is historical provenance only.

> **⚠ MODEL CHANGE 2026-06-03 — acquisition is FLOOR-BAND-ONLY.** The Phase-1 acquisition concept below applies
> only to the floor band (1500-1550). In every non-floor band there is **no acquisition phase**: every clean
> self-derived first-AC counts toward ownership (Set-A or Set-B alike), owned = **2** such ACs (CLAUDE.md rule 6A,
> [[lc-no-vanilla-reps]]). The Step 4-5 two-phase build below still describes the OLD per-band model and should be
> reworked at the next non-floor band setup (single disguised pool, no separate easiest-per-topic Phase-1 set).

- Save to `<band>/Phase-1-Acquisition.md` with both groups and a tracker table for Group A only (topic column is SPOILER — for logging only).
- **Deal Phase 1 (Group A) blind** — same protocol as Phase 2. The user says "next" or "give me a problem", Claude hands ONE bare LC link with NO topic label, NO AR, NO hint. Topic is revealed ONLY after the user finishes (AC or stuck), for the debrief. Phase 1 problems are shuffled before serving so order doesn't leak topic.
- The user works through Phase 1 (Group A) before entering Phase 2. The only difference from Phase 2 is that Phase 1 picks the *easiest* problem per topic.

### Step 5 — Build Phase 2 (derivation, blind shuffled)
- **Two problems per topic** = derivation-hard, disguised/combined instances.
- Selection basis (all four layers): (1) correct bucket, (2) Q3/Q4 contest slot, (3) low AR relative to band median, (4) statement disguises the pattern.
- **Shuffle ALL Phase 2 problems together** (across all topics) using `random.seed(<band_low>)` for reproducibility.
- Save to `<band>/_Sealed-Queue-Phase2.md` with topic in a SPOILER column (revealed after solve, not before).
- Deal one bare link at a time on "next" — no topic, no AR, no Q-position visible.

### Step 6 — Handle shortfalls
- Some topics have <3 problems in the band. Note these in the sealed queue file under "Shortfalls."
- Do NOT pull problems from adjacent bands to fill shortfalls. The band is self-sufficient; shortfalls stay uncapped and complete later when working the adjacent band naturally.

### Step 7 — Handle non-clean solves (dynamic queue growth)
- When a problem is solved but not clean (WA / hinted / editorial), it does NOT count toward the topic's 2 clean self-derived ACs.
- Generate a **replacement problem** from the same topic in the same band (if supply exists), append it to the sealed queue.
- If no more problems exist in-band for that topic, the topic stays at its current clean count — cross-band later.

### Step 8 — Ownership tracker
- Each band's `00-Band-Topic-Map.md` has an ownership tracker table: `Topic | Cold cleans | Status (◯/◐/●) | Need`.
- After each solve, update the tracker: bump the bucket(s) the problem hit.
- A problem that's disguised/combined bumps **every** bucket it touches (amortization).
- Band graduates when all core buckets hit `●` (2 clean self-derived ACs each).

### File layout per band (the standard)
```
<band>/
  00-Band-Topic-Map.md              ← SPOILER: full classification + ownership tracker + Set A/B
  Phase-1-Acquisition.md            ← 15 intro problems, topic-visible, with tracker
  _Sealed-Queue-Phase2.md           ← shuffled blind queue + answer key + shortfalls
  First-Attempt/
    00-band-overview.md             ← band header + meta-lessons
    01-<slug>.md ... NN-<slug>.md   ← one file per solved problem (description + thinking + code)
  Second-Attempt/                   ← (if re-solves happen)
    00-band-overview.md
    01-<slug>.md ... NN-<slug>.md
```

### AR data location
Saved at `zerotrac-data/band_<lo>_<hi>_with_ar.tsv` — reuse for analysis, do not re-fetch.

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

## Pattern-Reflex Deck — capture one move per solve

Lives in `patterns/deck.md`. It is the framing-level companion to `math-reflex/`: math-reflex installs *recall* (atomic facts → <5s), the deck installs *recognition* (a problem situation → the move that cracks it → <5s). The point is to permanently retire the "this should've taken seconds but cost me 5 minutes" class of fumble.

**The core rule — a card is born only from a real solve.** After a problem AC's, during debrief, ask the user one question:

> "What single move would have made this instant instead of slow?"

If a specific framing/micro-move cost real time, that move becomes one card. If nothing did, no card. **Never invent cards from intuition or mine them from a corpus** — the move lives in the solution, not the statement, and a card with no real-time-cost behind it is noise. One move per problem, max.

**Card shape (see `patterns/deck.md` for the format):** Trigger (the *felt signal* — what the user should recognize, usually a hesitation like "should this go here or there?") → Move (the mechanical response) → Anchor (the problem that birthed it) → Quiz prompt (1-line scenario; reflex answer names the move in <5s).

**Drilling & graduation:** identical bar to `math-reflex/00-protocol.md` — <5s cold, mixed order, 3 consecutive days, `◐` installing → `●` graduated. Drill the deck inside the **3-minute maintenance slot** of the daily math-reflex session, mixed in with the math facts. Quiz is application-level (a mini-scenario), never "define X".

**Why this and not a syllabus:** building a tagged framing-syllabus upfront is meta-work that solves zero problems and feeds the same over-scaffolding tendency behind the skip-3 history. The deck builds itself as a byproduct of reps. Keep the user grinding; harvest one card per solve.

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
