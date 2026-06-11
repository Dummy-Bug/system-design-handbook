# 03 — Push Dominoes

- **Link:** https://leetcode.com/problems/push-dominoes/
- **Band:** 1600–1699 · sealed queue · blind deal #3 · Q2 (AR 63.0%)
- **Bucket:** intended **Two-Pointers** (disguised; editorial frames it as BFS). **OUR code's mechanic = prefix-scan (`lastRIndex`, owned) + an over-modeled stack** → see adjudication.
- **Dealt:** 2026-06-10
- **AC:** 2026-06-10 _(self-derived, no hint; 45m over-cap → derivation clause)_
- **Result:** ✅ **clean first-submission AC.** Counts for the band **clean-rate metric (now 2/3, 67%)**.
- **Bucket credit:** ❌ **Two-Pointers NOT credited → stays 0/2.** The intended two-pointer tool was *not* used; the solve is the **[[lc-index-bookkeeping-overmodel]]** over-model again (stack of `(char,index)` tuples for what a running variable / gap-sweep gives free). Crediting an over-model would reward the reflex we're killing. _(User-adjudicable — overrule if you disagree.)_

---

## The problem
Dominoes string of `L`/`R`/`.`. Each `.` is pushed by the nearest `R` on its left and nearest `L` on its right; **closer force wins, equal forces → stays `.`**. Return the final state. `n ≤ 1e5` (so no O(n²)).

## The derivation (correct core insight)
Self-derived, fast: a `.` resolves by **distance to nearest `R` on the left (`ld`) vs distance to nearest `L` on the right (`rd`)** — smaller wins, tie → `.`. Correct. The slowness was all in *implementation choice*, not insight.

## What was submitted (Tier 1 — over-model)
Stack of `(char, index)` tuples preloaded right→left for "nearest special to the right," plus `lastRIndex` (a single var) for the left:
```java
class Tuple { char ch; int index; ... }
Deque<Tuple> stack = new ArrayDeque<>();
// preload R/L from the right; pop while peek().index <= i; compare ld vs rd
```
Works, AC. But: the **left side was already clean** (`lastRIndex` = one variable, no stack) and the **right side is its mirror** — yet it reached for a whole stack of tuples. That asymmetry is the tell.

## Over-model debrief — the 3 tiers (worked in chat)
| Tier | Approach | Extra space | Verdict |
|---|---|---|---|
| 1 | Stack of `(char,index)` tuples (submitted) | O(n) stack + objects | works; the over-model to **un-learn** |
| 2 | **Two-pass + array** — `pushRight` via `lastR`, `pushLeft` via `lastL`, closer wins | O(n) array | **canonical / reproduce cold** |
| 3 | Two-pointer **gap-fill** between consecutive walls (sentinels `L@-1`,`R@n`) | O(1) extra | elegant; **recognize-only** |

User correctly noted Tier 2 still needs an O(n) array to bridge the two passes — only Tier 3 is O(1) extra. (My initial "no structure" claim was wrong; corrected.)

### Tier 2 — canonical re-solve (interview weapon)
```java
public String pushDominoes(String dominoes) {
    int n = dominoes.length();
    char[] s = dominoes.toCharArray();
    final int INF = Integer.MAX_VALUE;

    int[] pushRight = new int[n]; int lastR = -1;
    for (int i = 0; i < n; i++) {
        if (s[i] == 'R') lastR = i; else if (s[i] == 'L') lastR = -1;
        pushRight[i] = (s[i] == '.' && lastR != -1) ? i - lastR : INF;
    }
    int[] pushLeft = new int[n]; int lastL = -1;
    for (int i = n - 1; i >= 0; i--) {
        if (s[i] == 'L') lastL = i; else if (s[i] == 'R') lastL = -1;
        pushLeft[i] = (s[i] == '.' && lastL != -1) ? lastL - i : INF;
    }
    char[] res = new char[n];
    for (int i = 0; i < n; i++) {
        if (s[i] != '.')                     res[i] = s[i];
        else if (pushRight[i] < pushLeft[i]) res[i] = 'R';
        else if (pushLeft[i] < pushRight[i]) res[i] = 'L';
        else                                 res[i] = '.';
    }
    return new String(res);
}
```
Subtlety: **reset the running index on the opposite letter** (an `L` blocks rightward force; an `R` blocks leftward). `INF` = "no force," keeps the compare uniform.

## Lesson / reflex to bank
**[[lc-index-bookkeeping-overmodel]]:** counter-heuristic *"do I need the positions, or just what happens between consecutive specials?"* Here the answer depends only on **distance to the nearest special on each side** → a running variable per direction, never a stack of stored positions. Your own `lastRIndex` was the proof; the right side was the same move mirrored.

**Google/interview note:** clean + correct + explainable **O(n) beats clever O(1)**. Tier 2 is the reproducible weapon (intuitive, hard to botch, one-line to explain); Tier 3 is recognize-only — fumbling its sentinels live is a worse signal than Tier 2 clean.

## PENDING
- Perturbation debrief — to be worked Socratically in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written here.
- Revision Day+14: reproduce **Tier 2** cold (the reset-on-opposite-letter is the only trap); re-state the positions-vs-gaps reflex.
