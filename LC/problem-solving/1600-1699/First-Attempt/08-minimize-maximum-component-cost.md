# 08 — Minimize Maximum Component Cost

- **Link:** https://leetcode.com/problems/minimize-maximum-component-cost/
- **Band:** 1600–1699 · sealed queue · blind deal #8 · Q2 (AR 43.6%) · *insight-gated* tier
- **Bucket:** answer key files it **Union-Find ★ + Binary-Search** (BS on cost threshold + DSU connectivity under it). **OUR code = Kruskal MST via Union-Find** (+ a redundant heap). → credit **Union-Find**; **Binary-Search NOT used → stays 0/2**; **Heap NOT credited** (over-tool, see below).
- **Dealt:** 2026-06-12
- **AC:** 2026-06-12 (40m **OVER-CAP** → derivation clause → counts; self-derived) · logged 06:53
- **Result:** ✅ **clean first-submission AC, self-derived.** **Union-Find 3rd rep** — already OWNED (2/2 after #01), so **no ownership change**, but a valuable **blind-spot reinforcement**. Clean-rate now **7/8 (88%)**; clean streak = 6 (#03–#08).
- **Net new debt closed: ZERO** — UF already owned, Heap over-tooled (not credited), Binary-Search not used. Still a clean rep + good UF reinforcement + two real lessons (over-tool, DSU bug).

---

## The problem
Undirected **connected** weighted graph, `n` nodes. Remove any edges so the result has **≤ k components**. A component's cost = its **max edge weight** (0 if edgeless). Minimize the maximum component cost.

## Approach (self-derived) — Kruskal min-spanning-forest, answer = the forced top edge
- Keeping extra edges can only *raise* a component's max, never help → the optimal kept set is a **forest**.
- To reach ≤ k components from `n` singletons you need **≥ n−k merges**; exactly `n−k` (more merges = fewer components = possibly larger max). Choose the **n−k smallest** non-cycle edges (Kruskal ascending).
- The **largest** of those n−k kept edges is the answer (it's the cost of whichever component holds it; every other kept edge is ≤ it).
- Equivalently: build the MST, **remove the k−1 heaviest** tree edges (each tree edge is a bridge → +1 component per removal), answer = max remaining.

## Self-derivation arc (original AC → canonical)
**As-submitted (AC, but over-tooled):** Kruskal into a list, push kept edges to a **max-heap**, poll `k−1` of them, answer = heap top.
- The heap is **redundant**: Kruskal hands the kept edges out **already sorted ascending**, so a max-heap over sorted data does zero ordering work — same family as #03's stack-of-tuples ([[lc-index-bookkeeping-overmodel]]).
- First refinement (mine, Socratic): the removed edges are exactly the **suffix** (largest k−1) → no heap, no set, just `kept[size − k]`.
- Final canonical (the revision target): you don't need the list either — process ascending, the **(n−k)-th real merge** *is* the answer. One pass after the sort.

## Canonical solution (bank this — revision must reproduce THIS, not the heap version)
```java
class Solution {

    class DSU {
        int[] parent, size;

        DSU(int n) {
            parent = new int[n];
            size = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                size[i] = 1;
            }
        }

        int find(int x) {
            if (parent[x] == x) return x;
            parent[x] = find(parent[x]);
            return parent[x];
        }

        boolean union(int x, int y) {
            int px = find(x), py = find(y);
            if (px == py) return false;

            if (size[px] < size[py]) {
                parent[px] = py;
                size[py] += size[px];
            } else {
                parent[py] = px;
                size[px] += size[py];
            }
            return true;
        }
    }

    public int minCost(int n, int[][] edges, int k) {
        Arrays.sort(edges, (a, b) -> Integer.compare(a[2], b[2]));

        DSU dsu = new DSU(n);
        int needed = n - k;
        int merges = 0;

        for (int[] e : edges) {
            if (dsu.union(e[0], e[1])) {
                if (++merges == needed) return e[2];
            }
        }
        return 0;
    }
}
```
- `needed = n − k`; the `needed`-th successful `union` returns the largest kept edge.
- `union` returns `boolean` (was it a real merge?) — folds the cycle check + merge into one call.
- `needed ≤ 0` (k ≥ n) → loop never hits it → `return 0` (keep no edge). Connected graph guarantees ≥ n−1 merges available, so for k ≥ 1 we always reach `needed` when positive.

## WA-cause [latent] — DSU union-by-size was dead code (AC'd anyway)
Original `union`: `int sx = getSize(px); ... sx += sy;` — updated a **local**, never `size[px]`. So union-by-size compared stale sizes and degenerated toward arbitrary union.
- **No correctness impact, no TLE** — path compression alone kept `find` fast enough at these constraints (E ≤ 1e5).
- Real defect: the balancing optimization did nothing. Fixed in canonical (`size[px] += size[py]`, both array writes live in each branch so parent/size can't drift). **Greppable lesson: when a "by-size/by-rank" union AC's, confirm the size array is actually being written — a silently-broken heuristic hides until a deeper adversarial test.**

## Bucket accounting (the honest call)
| Bucket | Used? | Load-bearing? | Credit |
|---|---|---|---|
| Union-Find ★ | yes | yes (cycle detection = the core) | **3rd rep — already owned; reinforcement** |
| Heap | yes | **no** (data already sorted) | **NOT credited — over-tool, stays 1/2** |
| Binary-Search | no | — | not used — **stays 0/2** (intended amortizer missed) |

**Heap discriminator vs #06:** #06's heap ran on an *unsorted* stream (bounded top-k = real selection work → credited). Here the heap eats *already-sorted* Kruskal output → zero ordering work → over-tool → not credited. The rule to bank: *credit a heap only when it does real ordering work on unordered data.*

## Lesson
- **Minimize-the-max under a "≤ k components / partition" constraint → Kruskal min-spanning-forest; the answer is the largest forced edge** (the (n−k)-th ascending merge). Don't reach for binary-search-on-answer when the greedy forest gives it directly in one pass.
- **Over-tool check:** if your data is already ordered by the time it reaches a heap/set, the heap/set is dead weight — index the order instead.
- **DSU hygiene:** an AC doesn't prove your union heuristic works; verify the size/rank array is actually mutated.

## Why `n−k` works (Socratic derivation — reproduce cold on revision)
1. **Start state:** no edges added → every node is its own root → **n components.**
2. **One real merge** (`union` returns `true`: endpoints in *different* groups) fuses two groups into one → component count **−1**. A cycle edge (`false`) fuses nothing → **±0**.
3. So `components = n − (#true-merges)`. Set `components = k` → `#merges = n − k` → that's `int needed = n - k;`.
4. **Why stop at the (n−k)-th merge (not go further):** "≤ k components" *allows* fewer components too — we don't stop because it's illegal. We stop because each extra merge pulls in a **heavier** edge (ascending order) → can only **raise** the max → fewer components is never better. Minimum-max ⇒ fewest legal merges ⇒ exactly `n−k`.
5. **Why the (n−k)-th merge edge is the answer:** ascending sort ⇒ merges fire in non-decreasing weight ⇒ the (n−k)-th is the **largest** kept edge ⇒ it is the reported component cost.

One-breath: *n−k merges to reach k components; ascending order makes the last of those the heaviest kept edge; return it.*

## Perturbation debrief (worked Socratically 2026-06-12 — [[lc-perturbation-debrief]])
Poke each "suspicious specific" to see which ones are **load-bearing** (break the approach) vs **decorative** (swap → same answer).

| # | Specific perturbed | Change | Verdict | Why |
|---|---|---|---|---|
| 1 | cost = **MAX** edge weight | → cost = **SUM** of edges | **LOAD-BEARING** | MAX is a *bottleneck* objective — the answer is one single edge, so greedy-ascending / BS-on-threshold both work. SUM is *additive* → "partition into ≤k groups minimizing max group sum" = **makespan/partition = NP-hard**. "Cut the heaviest" stops being provable. (Counter: star with arms `10` and `4,4,4` — for max cut the `10`; for sum the `4+4+4=12` group is the real bottleneck, cutting `10` does nothing.) |
| 2 | "**at most** k" components | → "**exactly** k" | **DECORATIVE** | With weights ≥ 1, fewer-than-k components only pulls in heavier edges → strictly worse. Optimum always sits at exactly k, so both phrasings give the identical answer; `needed = n−k` unchanged. |
| 3 | graph is "**connected**" | → graph disconnected (c₀ pieces) | **LOAD-BEARING (for correctness of `return 0`)** | You only *remove* edges, so components can only grow from the start count. Connected ⇒ up to **n−1** real merges available ⇒ `needed = n−k ≤ n−1` is **always reachable** ⇒ the `return 0` fall-through only fires in the harmless `k ≥ n` (all-singletons, cost 0) case. Disconnected with c₀ pieces caps merges at **n−c₀**; then a `k < c₀` request is *infeasible* but the code would silently `return 0` — a wrong answer masquerading as valid. |

**Bank:** the hinge is the word **"maximum"** (bottleneck ⇒ poly-time greedy). "at most k" is noise. "connected" is a feasibility guarantee that makes the `return 0` safe rather than a silent failure.

## PENDING
- **Revision Day+14: must reproduce the CANONICAL counter-form** (process ascending, return the (n−k)-th merge) — NOT the heap version. Re-derive *why* n−k merges and *why* the (n−k)-th ascending merge is the max forced edge, cold. [[lc-revise-to-cleanest-form]]
- Revision check: re-state probe 1 (max→sum breaks to NP-hard) from scratch — it's the load-bearing assumption.
