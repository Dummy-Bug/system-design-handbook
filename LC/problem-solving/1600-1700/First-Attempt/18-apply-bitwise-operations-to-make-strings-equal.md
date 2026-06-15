# 18 — Apply Bitwise Operations to Make Strings Equal

- **Link:** https://leetcode.com/problems/apply-bitwise-operations-to-make-strings-equal/ (LC 2546)
- **Band:** 1600–1700 · sealed queue · blind deal #18 · Q3 (AR 42.7%) · **answer-key bucket = Bit ✦ Invariant/Reframe (STRONG)**
- **Bucket (OUR code):** **Invariant/Reframe** (presence-of-a-`1` invariant). [[lc-invariant-reframe-bucket]] — non-gating. Bit-flavored but no bit-mechanic in the final code.
- **Dealt:** 2026-06-15 · **AC:** 2026-06-15.
- **Result:** ⚠️ **HINTED ("soft" — counterexample-disproofs + directional nudge, not editorial) → not clean, no rep.** Reached the invariant only after two failing test cases (`"10"→"11"`, `"10"→"01"`) disproved a positional left-to-right flip simulation, plus the nudge "the answer doesn't depend on positions — find the single global property." **Bit already OWNED 2/2 + Invariant/Reframe non-gating → no rep at stake.** Clean-rate **12/16 → 12/17 (~71%)**.

---

## The problem
Binary strings `s`, `target` (equal length). Op: pick `i,j`; simultaneously `s[i]=s[i]|s[j]`, `s[j]=s[i]^s[j]` (old values). Can `s` become `target`? `1 ≤ n ≤ 1e5`.

## The invariant (the whole problem)
Op outcomes on `(a,b)`: `(0,0)→(0,0)`, `(0,1)→(1,1)`, `(1,0)→(1,1)`, `(1,1)→(1,0)`. So the op can create or remove `1`s **but can never reach all-zero from a state with a `1`, nor create a `1` from all-zero.**
→ **"contains at least one `1`" is invariant.** Transformable ⟺ `(s has a 1) == (target has a 1)` — both have one, or both have none.

## The wrong path (why it took hints)
Modeled it positionally: per index, flip if a `1` exists to enable it. Two disproofs killed it:
1. **`"10"→"11"`** (true): right-only scan finds no `1` to the right of index 1 → falsely false. *(op picks ANY two indices — a `1` to the LEFT works too.)*
2. **`"10"→"01"`** (true): even scanning both sides, left-to-right order tries to zero index 0's `1` **before** manufacturing the `1` at index 1 → falsely false. *(ops can be reordered; you can create `1`s first.)*

**Lesson:** the suspicious specifics (which index, left vs right, order) were all red herrings — the answer is **positionless**. All the positional machinery sprang leaks because the problem was never positional. Recognizing "the answer depends on one global property, not positions" is the reframe — that was the hinted step.

## Step 2 — worked example
- `s="1010"`, `target="0110"`: both contain `1` → **true**. ✓ (LC ex1)
- `s="11"`, `target="00"`: s has `1`, target all-zero → **false**. ✓ (LC ex2)
- `s="00"`, `target="00"`: both all-zero → **true** (already equal; the edge case the first phrasing "both have a 1 else not" got wrong).

## Step 3 — named edge cases
1. **Both all-zero** → true (equal). The `==` form handles it; "both have a 1" alone does not.
2. **One all-zero, other not** → false (invariant broken).
3. **Single char** (`"0"`/`"1"`) → compares presence directly.
4. **No simulation / no positions** — O(n) presence check; positional logic is the trap.

## As-submitted solution (AC)
```java
class Solution {
    public boolean makeStringsEqual(String s, String target) {
        return s.contains("1") == target.contains("1");
    }
}
```
- Time `O(n)`, space `O(1)`.

## Lesson
- **Operation problems: enumerate one op's effect on the local state, find what it CAN'T change → that invariant is the answer.** Here `(a,b)` transitions show "has-a-1" is preserved → positionless yes/no.
- **When every positional attempt leaks, suspect the problem isn't positional.** That meta-signal should have come *before* the hint.

## PENDING
- **Day+14 revision (due 2026-06-29):** re-derive the op-transition table → "has-a-1" invariant cold (the meta-move, not the one-liner). [[lc-retrieval-not-reread]] [[lc-perturbation-debrief]]
- **Hinted-rate watch:** 3rd hinted in-band (with #02, #15) — see quality-gate note in topic map.
