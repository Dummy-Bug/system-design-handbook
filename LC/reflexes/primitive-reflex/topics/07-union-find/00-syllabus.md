# Union-Find (DSU) — Family Syllabus

Discriminator: **what each set *carries* (augmentation) + how elements are *keyed*.**
Goal: with all 7 installed, a DSU problem can only fail on **mapping**, never a missing tool. (★ = blind-spot, rule 6B.)
Shared kernel of every primitive = `find` + `union` (by rank/size) + path-compression — the 7 are **riders on that one template**. The kernel is exactly what rusted on 1600-1699 #01 (38 of 46 min), so it gets drilled cold first.

---

## The 7 primitives (learning order: foundation → hard)

| # | Primitive | Set carries / keying | What union / the answer means | Canonical problems (AM/LY) |
|---|---|---|---|---|
| 1 | Vanilla + component count | rank/size; int keys `0..n-1` | answer = #sets (`n − successful unions`) | Number of Provinces · Number of Connected Components in an Undirected Graph |
| 2 | Constraint-check (two-pass) | parent only | union ALL "equal" first, then every "≠"/constraint must straddle two roots | Satisfiability of Equality Equations |
| 3 | Cycle / redundant edge | parent only | `union` returns false (already same root) ⇒ this edge closes a cycle | Redundant Connection |
| 4 | Per-set size / aggregate | `size[root]` (or sum/min) | union combines aggregates; answer reads a component's size | Find Latest Group of Size M |
| 5 | Grid-flatten (+ size) | `id = r*C + c` | union 4-neighbours; answer from component sizes | Making a Large Island |
| 6 | Non-int keys + member-collection | `HashMap key→id`; gather members by root | map keys → union → bucket members per root (sort/merge) | Accounts Merge · Smallest String With Swaps |
| 7 | Union-by-shared-attribute | `attribute→representative` map | union any two elements sharing a key (row/col, prime factor) | Most Stones Removed with Same Row or Column · GCD Sort of an Array |

> #6 vs #7 are the **"indirect key" pair**, learned by contrast: #6 keys *the elements themselves* (emails, indices) into a map; #7 keys a *shared attribute* (row/col/factor) so any two elements with that attribute merge. Same map trick, two different meanings → two atoms.

## Deferred (Hard / higher band — install when they stall, not now)

- **Sorted / offline union (Kruskal-flavored)** — process edges/queries by weight: Checking Existence of Edge-Length-Limited-Paths · Remove Max Number of Edges to Keep Graph Fully Traversable.
- **Reverse-time / offline-with-undo** — Bricks Falling When Hit.
- **Directed DSU + case analysis** — Redundant Connection II.
- **Weighted / parity DSU (relation-to-parent)** — Evaluate Division / bipartite-via-DSU (not in these lists; surfaces ≥1700).
- **Composite** — Rank Transform of a Matrix (grid + per-component ordering, Hard).

## Completeness

Cross-checked vs `learnyard-data` DSU (13) + `algomaster-data` DSU (4 + intro): **every problem maps to these 7 + the deferred set.** Same closure standard as Stack. The kernel (`find`/`union` by rank + path-compression) is common to all 7; a DSU problem differs only by *augmentation* (none/count/size/members/attribute) and *keying* (int/grid/hashmap) — both closed axes.

---

## Atoms

| # | Atom | Folder | Status |
|---|---|---|---|
| 1 | Vanilla + component count | `01-vanilla-count/` | ⏳ install (reflex); ownership rep banked (1550-1600 #37 properties-graph, clean) |
| 2 | Constraint-check (two-pass) | `02-constraint-check/` | ⏳ install (reflex); ownership rep banked (1600-1699 #01 satisfiability, clean) |
| 3 | Cycle / redundant edge | `03-cycle-redundant/` | ⏳ not started |
| 4 | Per-set size / aggregate | `04-set-size/` | ⏳ not started |
| 5 | Grid-flatten (+ size) | `05-grid-flatten/` | ⏳ not started |
| 6 | Non-int keys + member-collection | `06-hashmap-keys/` | ⏳ not started |
| 7 | Union-by-shared-attribute | `07-shared-attribute/` | ⏳ not started |

Per atom: derive Socratically → produce code cold (announced) → install recognition (disguised) → perturbation debrief → write files → tick.
Each atom folder: `01-skeleton.md` · `02-notes.md` · `03-log.md`. **Drill by retrieval, never re-reading** ([[lc-retrieval-not-reread]]).
**Reflex ≠ ownership:** the install anchors below are AM/LY curriculum problems; zerotrac/band problems stay as ownership reps, not install material.

---

## Practice plan — minimal non-redundant reps (announced + disguised)

| Atom | Announced (install) | Disguised / applied |
| --- | --- | --- |
| 1 vanilla + count | [ ] Number of Provinces | [ ] Number of Connected Components (≈same — note, not a 2nd rep) |
| 2 constraint two-pass | [✅] Satisfiability of Equality Equations (clean, #01 — reflex drill still owed cold) | — |
| 3 cycle / redundant | [ ] Redundant Connection | — |
| 4 per-set size | [ ] Find Latest Group of Size M | — |
| 5 grid-flatten | [ ] Making a Large Island | (gentler warm-up: grid-flatten a count problem first) |
| 6 hashmap keys | [ ] Accounts Merge | [ ] Smallest String With Swaps |
| 7 shared-attribute | [ ] Most Stones Removed with Same Row or Column | [ ] GCD Sort of an Array |

> The **kernel drill** (blank-page `find`/`union` by rank + path-compression to <5 s) runs first and underlies every row above — it's the thing that cost the 38 min, so it's the highest-value rep.

## Graduation bar (per the track)
Kernel + each atom named in **< 5 s** cold, mixed-order with other families, held **3 consecutive days**. `★` blind-spot — Union-Find ownership already 2/2 (CLAUDE.md), this track adds the *speed/recognition* layer on top.
