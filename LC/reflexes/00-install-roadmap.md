# Reflex Install Roadmap (pre-band primitive build)

> The ordered plan for Socratically installing primitive/trigger reflexes **before** opening the 1700-1800 band — so band problems aren't "hitting in the dark." Point Claude here to resume: *"continue the reflex roadmap."*
>
> All in the **`primitive-reflex/`** track (bits, **maths**, graph, BS-on-answer, trie, DP). Created 2026-06-17. (Maths moved into primitive-reflex as a self-contained family 2026-06-19; the older `math-reflex/` *recall* track is left untouched and is NOT part of this roadmap.)

## Why this exists (the diagnosis)

Rating stuck ~1500–1530. Real bottleneck = **Q2 derivation SPEED + carelessness**, not topic coverage. Thesis ([[lc-derivation-budget-chunking]]): pre-install primitives as cold reflexes so in-contest the derivation budget goes to *mapping the novel problem*, not re-deriving a primitive (e.g. `x&-x`). We had **no trigger/primitive reflexes** for bits, maths, graph, DP, BS-on-answer, trie — so we build them, in order, then solve.

⚠ Reflex-building is a *means to faster solving*, not an end. Pair it with **timed practice** or it becomes perfectionism. Bits is one topic — don't let any single family sprawl.

## The order (and the rationale)

Bits + maths first **because they're used inside other problems**; DP last because it's heaviest and composes everything above.

| # | Topic | Track | Status |
|---|---|---|---|
| 1 | **Bits** | `primitive-reflex/topics/10-bit-manipulation/` | ◑ NEAR DONE — Modules 0–3 ✅; **Module 4 derivations done** (4.1 owned, 4.2/4.3/4.4 holdout-pending); 5–6 deferred. Only the deferred problem block remains before Bits is complete |
| 2 | **Maths** (NT · Combinatorics · Contribution · Game/Parity) | `primitive-reflex/topics/11-maths/` | ◑ family syllabus built (2026-06-19); modules M0–M4 pending derivation |
| 3 | **Graph** (BFS/DFS/topo/Dijkstra/0-1 BFS/Bellman-Ford) | `primitive-reflex/topics/07-graph` (+ `07-union-find` ✅) | ▢ not started |
| 4 | **DP** (last — leans on all above) | `primitive-reflex/DP/01-syllabus.md` | ▢ not started |

### Removed from this track (2026-06-19)
- **Binary Search on answer** — **dropped** (not a gap). Already OWNED in-band (1600-1699 #13/#14, both BS-on-answer; plain-BS carry closed [[lc-binary-search-one-bucket]]) and its feasibility-math (isqrt §3.12, triangular-inverse §3.11) is installed in `math-reflex`. Revisit ONLY if a specific BS problem surfaces a concrete gap.
- **Trie ★** — **relocated to the 1800-1900 consolidation** (below). It's an advanced DS that skews higher-rated, so it batches with the other advanced installs there; carries the bit-trie / LC 421 max-XOR carry from bits Module 3.

### Next band — 1800-1900 consolidation (Q3 tier)
After bits/maths/graph/DP feed the **1700-1800** band, the **1800-1900** band is the Q3-tier consolidation. Two facts drive it:
- **Band-owned ≠ reflex-installed** ([[lc-reflex-install-vs-band-owned]]): several families are band-owned but never got the bits-style install (discriminator + audited variant catalog).
- At Q3 the failure mode is **recognition + composition under disguise**, not missing primitives — so owned buckets are *exercised on harder problems*, not re-derived ([[lc-no-vanilla-reps]]).

**Committed installs at 1800-1900:**
- **Owned-but-uninstalled** (give them the one-time bits-style install): sliding-window · prefix/suffix · heap · backtracking · trees.
- **Advanced / new at 1800+:** Trie ★ (+ bit-trie/LC 421) · segment-tree/BIT · advanced string-matching · line-sweep variants beyond the audited Interval family.
- Already reflex-installed (done): two-pointers ✅ · stack ✅ · interval ✅ · union-find ✅.

## Bits sub-progress (topic 1)

Family syllabus: `primitive-reflex/topics/10-bit-manipulation/00-syllabus.md`. Active scope = Modules 0–4.

- **Module 0 — Foundations** ✅ (Number System + Operators + Single-Bit-Ops + Idioms; all 18 atoms derived)
- **Module 1 — Counting & bit arithmetic** ✅ (2026-06-18) — popcount/Kernighan, Counting-Bits DP, count-bits-in-1..N (column-flip), reverse (in Foundations), add-via-XOR+carry, divide (batch-doubling)
- **Module 2 — XOR mastery** ✅ (2026-06-18) — parity invariant, Single Number ×3 (136/260/137), reconstruction/decode (268/1720), prefix-XOR (1310/1442), Gray code `i^(i>>1)`. *(1 carry: LC 1442 O(n) hashmap opt owed)*
- **Module 3 — Per-bit thinking & properties** ✅ (2026-06-19) — per-bit contribution (Hamming/AND/OR/XOR pair-sums, carry-conservation order-swap), greedy bit construction (Max AND pair), bit-algebra identities (`a+b=(a^b)+2(a&b)`, trigger `a+b==a^b ⟺ a&b==0`). *(carries: Smallest-XOR 2nd rep; LC 421/1835/1442 deferred to revision)*
- Module 4 — OR/AND over subarrays ◑ DERIVATIONS DONE (2026-06-19) — 4.1 ✅ owned (LC 201); 4.2 bit-count-in-window, 4.3 no-shared-bits window, 4.4 LogTrick all derived (holdout-pending; problem block deferred)
- Module 5 — Bitmask as a set ⏸ deferred · Module 6 — Advanced ⏸ deferred

## How we install each (the loop)

Per the family syllabuses: **Socratic derivation first** (user derives, one concept at a time, no dumping) → notes written *only after* deriving → blind problems to test mapping. Retention = retrieval (blank-page recall), never re-reading. See `primitive-reflex/00-master-syllabus.md`.

## Downstream gate

These feed the **1700-1800 band** (already built: `problem-solving/1700-1800/`), which is rule-8 gated behind 1600-1700 graduating. Install primitives here → graduate 1600-1700 → open 1700-1800 with the reflexes ready.
