# Reflex Install Roadmap (pre-band primitive build)

> The ordered plan for Socratically installing primitive/trigger reflexes **before** opening the 1700-1800 band — so band problems aren't "hitting in the dark." Point Claude here to resume: *"continue the reflex roadmap."*
>
> Spans both reflex tracks: **`primitive-reflex/`** (bits, graph, BS-on-answer, trie, DP) and **`math-reflex/`** (maths). Created 2026-06-17.

## Why this exists (the diagnosis)

Rating stuck ~1500–1530. Real bottleneck = **Q2 derivation SPEED + carelessness**, not topic coverage. Thesis ([[lc-derivation-budget-chunking]]): pre-install primitives as cold reflexes so in-contest the derivation budget goes to *mapping the novel problem*, not re-deriving a primitive (e.g. `x&-x`). We had **no trigger/primitive reflexes** for bits, maths, graph, DP, BS-on-answer, trie — so we build them, in order, then solve.

⚠ Reflex-building is a *means to faster solving*, not an end. Pair it with **timed practice** or it becomes perfectionism. Bits is one topic — don't let any single family sprawl.

## The order (and the rationale)

Bits + maths first **because they're used inside other problems**; DP last because it's heaviest and composes everything above.

| # | Topic | Track | Status |
|---|---|---|---|
| 1 | **Bits** | `primitive-reflex/topics/10-bit-manipulation/` | ◑ IN PROGRESS — Module 0 (Foundations) ✅ done 2026-06-17; Modules 1–4 left (5–6 deferred) |
| 2 | **Maths** (number theory) | `math-reflex/` | ▢ not started |
| 3 | **Graph** (BFS/DFS/topo/Dijkstra/0-1 BFS/Bellman-Ford) | `primitive-reflex/topics/07-graph` (+ `07-union-find` ✅) | ▢ not started |
| 4 | **Binary Search on answer** (guess + feasibility check) | `primitive-reflex/topics/05-binary-search` | ▢ not started |
| 5 | **Trie** (also the band blind-spot) | `primitive-reflex/topics/12-advanced` (Trie) | ▢ not started |
| 6 | **DP** (last — leans on all above) | `primitive-reflex/DP/01-syllabus.md` | ▢ not started |

## Bits sub-progress (topic 1)

Family syllabus: `primitive-reflex/topics/10-bit-manipulation/00-syllabus.md`. Active scope = Modules 0–4.

- **Module 0 — Foundations** ✅ (Number System + Operators + Single-Bit-Ops + Idioms; all 18 atoms derived)
- **Module 1 — Counting & bit arithmetic** ✅ (2026-06-18) — popcount/Kernighan, Counting-Bits DP, count-bits-in-1..N (column-flip), reverse (in Foundations), add-via-XOR+carry, divide (batch-doubling)
- **Module 2 — XOR mastery** ✅ (2026-06-18) — parity invariant, Single Number ×3 (136/260/137), reconstruction/decode (268/1720), prefix-XOR (1310/1442), Gray code `i^(i>>1)`. *(1 carry: LC 1442 O(n) hashmap opt owed)*
- Module 3 — Per-bit thinking & properties ▢ NEXT
- Module 3 — Per-bit thinking & properties ▢
- Module 4 — OR/AND over subarrays ▢
- Module 5 — Bitmask as a set ⏸ deferred · Module 6 — Advanced ⏸ deferred

## How we install each (the loop)

Per the family syllabuses: **Socratic derivation first** (user derives, one concept at a time, no dumping) → notes written *only after* deriving → blind problems to test mapping. Retention = retrieval (blank-page recall), never re-reading. See `primitive-reflex/00-master-syllabus.md`.

## Downstream gate

These feed the **1700-1800 band** (already built: `problem-solving/1700-1800/`), which is rule-8 gated behind 1600-1700 graduating. Install primitives here → graduate 1600-1700 → open 1700-1800 with the reflexes ready.
