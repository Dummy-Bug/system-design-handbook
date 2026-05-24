## Drill log — Topic 03 (Pair / Triple Count)

### 2026-05-24 — first install pass

| Card | Status | Notes |
|------|--------|-------|
| a.1 — `n(n-1)/2` pair count | ● graduated | Fired clean. User already had the formula from prior practice. |
| a.2 — concrete recall (n=10→45, n=20→190) | ● graduated | Both correct without hesitation. Said "stop" before n=100 drill — fair, growth pattern was clear. |
| a.3 — n² overflow at n ≈ 46340 | ● graduated | User said "anything after 10⁴ is risky" — sharpened to ~4.6×10⁴ = `√(2.1×10⁹)`. Locked as sibling reflex to triangular sum. |
| a.4 — inverse: recover n from P | ○ parked | User wrote `n² + n - 2P = 0` (wrong sign — should be `n² - n - 2P = 0`). After correction, user noted "this won't come in LC problems" — accurate. Parked. Formula `n = (1 + √(1 + 8P))/2` recorded but not drilled. |
| b.1 — `n(n-1)(n-2)/6` triple count | ● graduated | User asked for full intuition derivation. Walked the 3! = 6 orderings of `{a,b,c}`. User then asked for the same depth on the pair derivation — captured all three framings (pair-with-others, sequential-pick, `C(n,2)`) in notes per request. |
| b.2 — n³ overflow at n ≈ 1290 | ● graduated | User estimated 10³ initially — sharpened to ~1290 (cube root of `2.1×10⁹`). Locked the cast-first-operand trap. |
| b.3 — general `C(n, k)` derivation | ● graduated | User flagged this should be in notes since we derived it in chat. Written into notes as "the general C(n,k) — derivation" section. Deeper machinery still pointed to [[10-permutations-combinations]]. |
| c.1 — bucket pairs (sum of `k(k-1)/2`) | ● graduated | User got it after one example. Confirmed `C(k,2)` per unique occurrence. Code given in plain `put + getOrDefault` form (user objected to `Map.merge` syntax — noted for syntax-reference folder). |
| d.1 — running pair count | ● graduated | Took two passes. First explanation included Java `merge` which derailed. Second pass with plain Java + walkthrough table on `[1,2,2,3,2,1]` landed. User's own articulation: *"as we are storing the count in total for the older pairs"* — clean restatement. |
| d.2 — derived-key bucketing | ◐ shaky | Approach landed (bucket by remainder, pair with complement). Algebraic justification (`(a+b)%k = (a%k + b%k)%k`) the user already knew, but the derivation chain through `a = qk + r` was unfamiliar — said "will have to revisit it". Marked for re-drill when [[06-modular-arithmetic]] opens. |

### Insights captured beyond the cards

- "Pairs `(i, j)` with `i < j`" = LC's linguistic convention for **unordered**. The `i < j` is not algorithmic; it's how the problem signals "count each pair once." User asked for this to be locked permanently in notes.
- Three framings of pair count (pair-with-others, sequential-pick, `C(n, 2)`) all land on `n(n-1)/2`. User wanted all three captured explicitly — derivation muscle priority over single-formula memorisation. *"these little stuff matters because i might forget all about these formulas and all after 6 months but the derivation muscle should stay intact"*.
- The "÷ k! kills the ordering" rule generalises pairs → triples → quadruples → `C(n, k)`. Captured as the unifying principle.
- `Map.merge` syntax — user wants this in `02-syntax/` not in math notes. Will write a separate Java-syntax entry covering `merge`, `compute`, `computeIfAbsent`, `getOrDefault`.
- The d.1 → d.2 jump captured as one-line reflex: *"bucket by derived key, pair with complement key, read before write."*

### Next session

- Re-drill d.2 algebra after [[06-modular-arithmetic]] cards `a` (modular identities) are installed.
- Move to **Topic 04 — Digit Operations** next (per syllabus order).
