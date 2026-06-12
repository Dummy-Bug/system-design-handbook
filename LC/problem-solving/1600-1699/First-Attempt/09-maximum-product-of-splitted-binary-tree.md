# 09 — Maximum Product of Splitted Binary Tree

- **Link:** https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/
- **Band:** 1600–1699 · sealed queue · blind deal #9 · Q3 (AR 55.7%) · *trap-carrier* tier (mod-at-end)
- **Bucket:** answer key filed it **Tree-DP ★**. **RE-CLASSIFIED 2026-06-12 → Subtree-Aggregation (NOT Tree-DP).** OUR code is a pure post-order **sum fold** (`left+right+val`) + a max taken *outside* the recursion over precomputed sums — no state, no recurrence-with-choice. → **Tree-DP NOT credited; blind-spot stays 0/2 and is now DEFERRED** (band has no problem forcing a true optimization recurrence — see `topic-install-ledger.md` §2). [[lc-tree-dp-deferred-supply]] · [[lc-credit-mechanic-not-label]]
- **Dealt:** 2026-06-12
- **AC:** 2026-06-12 (**15m SUB-CAP**, self-derived, first attempt)
- **Result:** ✅ **clean first-submission AC, self-derived.** Trap-carrier (mod-at-end) **handled correctly first try**. Clean-rate now **8/9 (89%)**; clean streak = 7 (#03–#09).
- **Net new debt closed: ZERO** — Subtree-Aggregation is not a gated bucket; Tree-DP not credited. Value of the rep = a clean post-order-subtree-statistic rep + the mod-timing trap dodged + the label-inflation catch (this is *why* tree-DP got deferred).

---

## The problem
Binary tree, sum of all values `total`. Remove **one edge** to split into two subtrees with sums `a` and `total−a`. Maximize `a·(total−a)` over all edges. Return it **mod 1e9+7**.

## Approach (self-derived) — one subtree sum per edge, product = `sub·(total−sub)`
- Cutting the edge above any node `v` isolates `v`'s subtree (sum `s_v`) from the rest (`total − s_v`). So every edge ↔ exactly one node's subtree sum.
- Need `total` first (one full sum). Then a second post-order pass produces every `s_v`; for each, score `s_v·(total − s_v)` and track the max.
- **The trap:** keep the product as `long` and **mod only at the very end.** Modding each product *before* the max comparison reorders magnitudes → wrong max. Max over true integers, mod the winner once.

## Step 2 — worked example reproduced (headline metric, every solve)
`root = [1,2,3,4,5,6]` → tree: 1·(2·(4,5), 3·(6)). `total = 1+2+3+4+5+6 = 21`.

| Node | subtree sum `s` | `s·(21−s)` |
|---|---|---|
| 4 | 4 | 4·17 = 68 |
| 5 | 5 | 5·16 = 80 |
| 2 | 2+4+5 = 11 | 11·10 = **110** |
| 6 | 6 | 6·15 = 90 |
| 3 | 3+6 = 9 | 9·12 = 108 |
| 1 (root) | 21 | 21·0 = 0 |

Max = **110** → matches expected output. Every number reproduced through the approach → no missing rule. (Note the root's own split = `21·0 = 0`, naturally never the max — the "edge above root" doesn't exist, and the code's `total·0` term harmlessly self-excludes.)

## Step 3 — named edge cases
1. **Overflow** — `n ≤ 5·10⁴`, `val ≤ 10⁴` → `total` up to 5·10⁸; product up to ~2.5·10¹⁷ ≫ `int`. **Must** hold product (and `maxProduct`) as `long`, cast before multiply.
2. **Mod-before-max trap** — modding each product before comparing breaks the ordering → wrong answer that still "looks modded." Mod only the final winner.
3. **Two-node tree** `[1,1]` — `total=2`, only split is `s=1` → `1·1=1`. Confirms a leaf-sized subtree is a valid split.
4. **Skewed / linear tree** (all-left chain) — recursion just deepens; sums still correct (constraints allow it; stack depth fine at 5·10⁴ for iterative-safe inputs, recursion OK here).
5. **Root term `total·0`** — included but always 0, never wins; no special-casing needed.

## As-submitted solution (clean AC)
```java
class Solution {
    final int MOD = 1_000_000_007;
    private long maxProduct = 1L;

    public int maxProduct(TreeNode root) {
        int totalSum = traverse(root);
        findMaxProduct(root, totalSum);
        return (int)(maxProduct % MOD);
    }

    private int findMaxProduct(TreeNode root, int totalSum) {
        if (root == null) return 0;
        int leftSum = findMaxProduct(root.left, totalSum);
        long currentProduct = (long)leftSum * (totalSum - leftSum);
        this.maxProduct = Math.max(currentProduct, maxProduct);
        int rightSum = findMaxProduct(root.right, totalSum);
        currentProduct = (long)rightSum * (totalSum - rightSum);
        this.maxProduct = Math.max(currentProduct, maxProduct);
        return leftSum + rightSum + root.val;
    }

    private int traverse(TreeNode root) {
        if (root == null) return 0;
        return traverse(root.left) + traverse(root.right) + root.val;
    }
}
```
- `MOD` written `1_00_000_000_7` in the original — same value (1e9+7), regrouped here for readability.
- Mod applied **once**, at the return → trap dodged. ✅
- `maxProduct` is a `long` field, compared un-modded → correct ordering. ✅

## Self-derivation arc (original → canonical)
**The redundant pass.** `traverse` computes the exact same thing `findMaxProduct` already returns (`left+right+val`). It exists only because you need `total` *before* the first product comparison. That's the **same primitive run twice** — the post-order subtree sum.

**Canonical (the revision target):** collapse to a clean two-phase shape — one sum pass to get `total`, one product pass that scores each subtree sum as it bubbles up. The second pass is unavoidable (you can't compare against `total` until you know it), so two passes IS canonical here — but only **one** of them should be a hand-written sum; the other reuses the returned subtree sum. Don't write the fold twice.

```java
class Solution {
    private long total = 0, best = 0;

    public int maxProduct(TreeNode root) {
        total = sum(root);          // pass 1: total only
        subtree(root);              // pass 2: score each subtree sum
        return (int)(best % 1_000_000_007L);
    }
    private long sum(TreeNode n) {
        return n == null ? 0 : n.val + sum(n.left) + sum(n.right);
    }
    private long subtree(TreeNode n) {
        if (n == null) return 0;
        long s = n.val + subtree(n.left) + subtree(n.right);
        best = Math.max(best, s * (total - s));   // un-modded compare
        return s;
    }
}
```
- One product check per node (covers every edge: the edge *above* `n` ↔ subtree `s`). The original checks per-child (left then right) — equivalent coverage, just phrased from the parent; the per-node form is one comparison instead of two and skips the harmless root·0 only by construction. Either is fine; bank the per-node form for revision.

## Bucket accounting (the honest call — this solve is *why* tree-DP got deferred)
| Bucket | Used? | Load-bearing? | Credit |
|---|---|---|---|
| Subtree-Aggregation (post-order sum fold) | yes | yes (the whole mechanic) | clean rep — **not a gated bucket**, no ownership counter |
| ~~Tree-DP ★~~ | **no** | — | **NOT credited.** No state, no recurrence-with-choice; `max` is taken outside the recursion. Blind-spot **stays 0/2 → DEFERRED**. |

**Discriminator to bank:** *post-order that returns a **statistic** (sum/count/depth/xor) and takes the answer-max **outside** the recursion = aggregation, NOT tree-DP. Tree-DP = the node returns an **optimized** quantity (`max/min over child states`) that the parent **decides** on (House-Robber-III shape).* Calling this tree-DP is exactly the label-inflation [[lc-credit-mechanic-not-label]] guards against — and the audit it triggered found the band has **0** true-optimization tree-DP problems → deferral.

## Lesson
- **"Split tree by one edge / sum on each side" → one post-order subtree-sum pass; per edge the score is `s·(total−s)`.** The "splitted tree" framing is a disguise over a plain subtree statistic.
- **Bottleneck of these trap-carriers is arithmetic discipline, not the algorithm:** `long` before multiply, **mod only the final answer** (mod-before-compare silently corrupts a max/min). Step-2/Step-3 are what caught both here first try.
- **Don't write the same fold twice** — if a "total" pass and a "per-node" pass compute the identical subtree quantity, reuse the returned value.
- **Label honesty:** an easy tree problem tagged "Tree-DP" usually isn't — check for the optimization recurrence before crediting a blind-spot.

## Perturbation debrief — **PENDING** (work Socratically in chat first, [[lc-perturbation-before-write]])
Candidate "suspicious specifics" to poke (do NOT pre-fill verdicts — derive in chat):
- node values are **non-negative** → what if values can be **negative**? (does `max product` still sit at a single subtree sum? does the mod / max interact?)
- exactly **one** edge removed → **two** edges (three pieces)?
- objective is a **product** `a·(total−a)` → does the "maximize near total/2" intuition the product encodes survive sign changes?
> To be filled after the Socratic pass, then this section + the PENDING note below get updated.

## PENDING
- **Perturbation debrief** — run the 3 probes above Socratically, identify the load-bearing assumption (prime suspect: **values ≥ 0**, which is what lets "closest subtree sum to total/2 wins" hold), then write it up. Doubles as the Day+14 check.
- **Revision Day+14:** reproduce the **canonical two-phase form** cold (one sum pass + one scoring pass, un-modded compare, mod once at end) — NOT the double-fold original. [[lc-revise-to-cleanest-form]]
