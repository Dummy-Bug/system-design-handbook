# 01 — Satisfiability of Equality Equations

- **Link:** https://leetcode.com/problems/satisfiability-of-equality-equations/
- **Band:** 1600–1699 · sealed queue · blind deal #1 · Q2 (AR 51.9%)
- **Bucket (revealed post-solve):** **Union-Find / DSU ★** (blind-spot). Disguise: reads like string parsing, not graph. Credit by OUR code ([[lc-classify-by-own-solution]]) = DSU with path-compression + union-by-size.
- **Dealt:** 2026-06-10
- **AC:** 2026-06-10 _(self-derived, no hint)_
- **Result:** ✅ **clean first-submission AC** (no WA). 46m — **over the 30-min cap → derivation clause applied** (clause exempts time, not implementation discipline; first submission was clean → counts toward ownership).
- **Ownership:** **Union-Find ★ rep 2/2 → bucket now OWNED ●.** First of the three blind-spots closed.
- **Cold re-solve:** ⏳ pending (optional — clean sub-derivation; cold re-solve only mandatory for hinted/WA/editorial per [[lc-cold-resolve-scope]]). Worth a timed re-run to drill the DSU template.

---

## The problem
`equations[i]` is `"a==b"` or `"a!=b"` (single lowercase letters). Return whether all can hold simultaneously. ≤500 equations, 26 variables.

## The derivation (self-led)
- First reached for a **HashMap** (constraints tiny), then **rejected it cold** by constructing the edge case `["a!=b", "b==c", "c==a"]` — equality is transitive across a chain, so a pairwise map misses transitive closure. (This is the Step-3 edge reflex firing *before* coding — the win of this band.)
- Reframe: `==` = an edge joining two equal variables ⇒ build **connected components** of equal variables, then every `!=` must straddle **two different components**. → DSU.
- **Two-pass** structure: union ALL `==` first, then check every `!=`.

## Solution (clean first-AC)
```java
class DSU {
    int[] parent, size;
    DSU(int n){ parent=new int[n]; size=new int[n];
        for(int i=0;i<n;i++){ parent[i]=i; size[i]=1; } }
    int find(int x){ return parent[x]==x ? x : (parent[x]=find(parent[x])); }
    void union(int x,int y){
        int px=find(x), py=find(y);
        if(px==py) return;
        if(size[px]>=size[py]){ size[px]+=size[py]; parent[py]=px; }
        else { size[py]+=size[px]; parent[px]=py; }
    }
}
public boolean equationsPossible(String[] equations) {
    DSU dsu = new DSU(26);
    for (String e : equations)                       // PASS 1: union all "=="
        if (e.charAt(1) == '=') dsu.union(e.charAt(0)-'a', e.charAt(3)-'a');
    for (String e : equations)                       // PASS 2: check all "!="
        if (e.charAt(1) == '!' && dsu.find(e.charAt(0)-'a') == dsu.find(e.charAt(3)-'a'))
            return false;
    return true;
}
```
> Submitted version carried leftover `System.out.println` debug lines — stripped here. **Add "remove debug prints" to the pre-submit glance.**

## Process notes (what to keep / fix)
- ✅ Edge case `[a≠b, b==c, c==a]` generated *before* coding → killed the wrong (HashMap) approach. Keep.
- ✅ DSU implementation bugs were caught **locally**, not via WA → first submission stayed clean. Keep.
- ⚠️ **Time split: ~8 min insight, ~38 min DSU template rust** (union-by-size / path-compression / size bookkeeping). Signature of an **un-chunked primitive eating derivation budget** ([[lc-derivation-budget-chunking]]). **Action: bank a canonical DSU template as a reflex atom** → next time ~15 min, not 46.

---

## Perturbation debrief — the load-bearing assumption

**THE assumption:** `==` is an **equivalence relation** — reflexive, symmetric, **transitive** (`a==b, b==c ⟹ a==c`). Transitivity is what makes "connected component = all equal" valid, and DSU is exactly the structure for equivalence classes under merging. `!=` is symmetric but **NOT transitive** (`a≠b, b≠c` says nothing about a vs c) → it can't form components; it's only a pairwise constraint **checked against** the classes that `==` built. Everything else falls out of this.

**P1 — why must all `==` be unioned before any `!=` is checked?**
Breaking input for a single in-order pass: `["a!=b", "b==c", "a==c"]`. In order: `a!=b` checked first → a,b in different sets → **passes**; then `b==c`, `a==c` merge a,b,c into one set. The `!=` you already cleared is now violated but never re-checked. → **a later union can invalidate an earlier `!=` check** ⇒ separate the passes.

**P2 — why DSU, not a graph of `!=` edges?**
Because the structure to build is the **equivalence closure of `==`** (needs transitivity). `!=` edges have no closure to build (non-transitive) — they're pure constraints. DSU builds the closure incrementally; a `!=` graph would build nothing useful.

**P3 — perturb the relation to `<` (`a<b`):**
DSU **fails**. `<` is transitive but **anti-symmetric** → an *ordering*, not an equivalence. Model as a **directed** graph (`a→b` for `a<b`); satisfiable **iff acyclic** (a cycle `a<b<c<a` = contradiction). → cycle detection / topological sort, not union-find.

**One-line bank:** *DSU models transitive + symmetric relations (equivalence). Non-transitive (`≠`) ⇒ check-only against the classes; ordered (`<`) ⇒ directed graph + acyclicity, not DSU.*

## REVISION TARGET (Day+14)
Re-derive cold: the HashMap-fails edge case, the two-pass order (reproduce P1's breaking input), and *why* `==`→DSU but `!=`→check-only (transitivity). Reproduce the cleanest DSU template from the reflex atom (target ≤15 min). Re-state the `<`-perturbation (directed graph + acyclicity).
