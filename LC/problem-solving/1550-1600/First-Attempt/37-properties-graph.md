# 37 — Properties Graph

- **Link:** https://leetcode.com/problems/properties-graph/
- **Band:** 1550–1600 · Phase 2 sealed queue · re-shuffled-order deal #1 (post-leak shuffle 2026-06-08) · Q2
- **Bucket (revealed post-solve):** **Union-Find / DSU ★** (blind-spot — the connected-components mechanic in our code) · Graph (framing) · Hashing (set-intersection). Credit by [[lc-classify-by-own-solution]]: our code counts components via DSU, so it credits the **Union-Find blind-spot**, not Graph.
- **Dealt:** 2026-06-08
- **AC:** 2026-06-09 06:33 IST _(self-derived, no hint on the algorithm; debugged locally, **no WA on the judge**)_
- **Result:** ✅ **CLEAN first-submission AC (no WA), ~60 min over-cap → derivation clause.** Counts toward ownership. **Union-Find blind-spot rep 1 of 2.**

## The problem
`n` properties (rows of ints), threshold `k`. Edge between `i`,`j` iff `intersect(i,j) = |distinct values in common| ≥ k`. Return the number of connected components. `n ≤ 100`, row length ≤ 100, values ≤ 100.

## Approach (our code)
1. For each row build a `Set<Integer>` of its distinct values.
2. For every pair `(i, j)`, count common values; if `≥ k`, `union(i, j)`.
3. Components = number of DSU roots (`parent[i] == i`).

DSU with **path compression** (`parent[node] = getParent(parent[node])`) + **union by size**. Component count = self-parent count at the end.

## Complexity (the unlock)
The block was a false TLE fear: thought worst case ≈ 10⁸. Real math — `n ≤ 100` so pairs ≈ n² = 10⁴; each intersection with a `Set` is O(m) ≈ 100 → **n²·m ≈ 10⁶**, instant. The 10⁸ only appears if intersection is done as an O(m²) nested array loop instead of a set lookup. **`n ≤ 100` is the constraint *telling* you brute-force pairwise is intended** — no sorting/optimization needed (the rabbit hole that ate most of the stuck time).

## Code cleanup (not a bug)
`s2` is rebuilt inside the inner loop, so each row's set is constructed `n` times → O(n²·m) set-building. **Precompute all `n` sets once** into a `List<Set<Integer>>` before the pair loop; then the pair loop is pure intersection. Same judge verdict (both ≪ limits), cleaner canonical form.

## Lesson
"Edge iff similarity ≥ threshold, count groups" ⇒ it's **connected components** ⇒ DSU (or DFS/BFS). The mechanic you pick decides the bucket: **DSU → Union-Find blind-spot**; DFS/BFS → Graph (already owned). Recognizing "components under a pairwise predicate" is the reusable trigger. The only trap is hunting an optimization the small `n` never asked for.

## Assistance & adjudication (transparency — [[lc-credit-mechanic-not-label]], rule 7)
On the stuck-debrief I (Claude) corrected the **complexity misconception** (it's 10⁶, brute-force is intended) and named "connected components / use DSU for the blind-spot credit." **User adjudicated this CLEAN** on the basis that the components+DSU framing was held *before* the reveal (user had already listed "set → edges → BFS/DFS/DSU" himself) and the sole real blocker was the false 10⁸ TLE fear — a scale/confidence issue, not an algorithm hint. Recorded openly so the call is auditable rather than hidden. DSU implementation (path compression + union-by-size) was entirely self-written and debugged to a no-WA AC.

## REVISION TARGET (Day+14)
Re-derive cold: "threshold-edge ⇒ connected components ⇒ DSU"; re-implement DSU (path compression + union-by-size + root-count) from a blank page; re-state why `n ≤ 100` licenses brute-force pairwise.
