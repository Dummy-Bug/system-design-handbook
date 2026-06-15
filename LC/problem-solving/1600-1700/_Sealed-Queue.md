# 1600–1699 — Sealed Queue (Derivation / Ownership)

> Built 2026-06-10 from the full assembled band data (editorials both halves + AR + LC tags + cached statements).
> Targets the **open buckets** in `00-Band-Topic-Map.md`: blind-spot trio (Union-Find, Tree-DP, Mono-Stack)
> + carried 0/2 & 1/2 debts. Owned buckets (Greedy/Prefix-Sum/Sliding-Window/Graph/Math) appear only as
> amortized ride-alongs, never as the target.
>
> **BLIND-DEAL RULE** ([[lc-blind-deal-protocol]]): on "next", take the next un-ticked link from the DEAL LIST only.
> Do NOT open the ANSWER KEY before solving — it is a SPOILER (buckets, tiers, traps). Reveal only in the debrief.
> Protocol: 30-min cap (derivation clause: self-derived over-cap AC still counts; **first submission must be AC**), then cold re-solve.
> **Headline metric this band:** Step-2 (worked example) + Step-3 (named edges) on EVERY solve; track first-submission-clean rate (≥70%, ≤1 hinted/10).

---

## DEAL LIST (blind — links only)

> Genuine random shuffle (2026-06-10). **RE-SHUFFLED 2026-06-11** — undealt #6–23 re-randomized after a chat-side bucket leak. **RE-SHUFFLED AGAIN 2026-06-15** — undealt #16–23 re-randomized after Claude again leaked the next deal's bucket (`maximum-number-of-moves-in-a-grid` named as DP-Grid). That problem is now **⚠ bucket-contaminated** — when dealt, its log notes reduced derivation credit (implementation rep only). **#17–23 RE-RANDOMIZED AGAIN 2026-06-15 on user request** (#16 minimum-remove kept as the active deal; contaminated problem now at #23). **Position is NOT a tell.** Deal top-down; tick after the cold re-solve.

1. [x] ~~https://leetcode.com/problems/satisfiability-of-equality-equations/~~ ✅ dealt+AC 2026-06-10 (**clean first-AC, 46m over-cap → derivation clause; Union-Find ★ 2/2 → OWNED ●**) → `First-Attempt/01`
2. [x] ~~https://leetcode.com/problems/count-number-of-ways-to-place-houses/~~ ❌→✓ dealt 2026-06-10 (**HINTED + WA-then-AC** — axis-switch hinted; overflow WA, mod-timing; DP-Linear does NOT count, still owes 2) → `First-Attempt/02`
3. [x] ~~https://leetcode.com/problems/push-dominoes/~~ ✅ dealt+AC 2026-06-10 (**clean first-AC, 45m over-cap**; but **over-model [[lc-index-bookkeeping-overmodel]]** → Two-Pointers NOT credited, stays 0/2; clean-rate 2/3) → `First-Attempt/03`
4. [x] ~~https://leetcode.com/problems/partition-string-into-substrings-with-values-at-most-k/~~ ✅ dealt+AC 2026-06-10 (**clean first-AC, 25m SUB-CAP**; Greedy ride-along — DP-String still 0/2; comprehension-assisted; clean-rate 3/4) → `First-Attempt/04`
5. [x] ~~https://leetcode.com/problems/find-the-punishment-number-of-an-integer/~~ ✅ dealt+AC 2026-06-11 (**clean first-AC, self-derived, 30m**; **Backtracking 2/2 → OWNED ●**; clean-rate 4/5) → `First-Attempt/05`
6. [x] ~~https://leetcode.com/problems/reward-top-k-students/~~ ✅ dealt+AC 2026-06-11 08:26 (**clean first-AC, self-derived, 20m SUB-CAP**; bounded size-`k` min-heap → **Heap 1/2**; soft/vanilla rep — heap not load-bearing; clean-rate 5/6) → `First-Attempt/06`
7. [x] ~~https://leetcode.com/problems/construct-the-longest-new-string/~~ ✅ dealt+AC 2026-06-12 05:57 (**clean first-AC, self-derived, 36m OVER-CAP** → derivation clause; **closed-form Math/Greedy, NOT DP** → DP-Linear stays 0/2, no new ownership; clean-rate 6/7) → `First-Attempt/07`
8. [x] ~~https://leetcode.com/problems/minimize-maximum-component-cost/~~ ✅ dealt+AC 2026-06-12 (**clean first-AC, self-derived, 40m OVER-CAP** → derivation clause; **Kruskal MST via Union-Find** → UF 3rd rep (already owned, reinforcement); **Heap over-tooled, NOT credited**; **Binary-Search NOT used, stays 0/2**; DSU size-bug fixed in canonical; clean-rate 7/8) → `First-Attempt/08`
9. [x] ~~https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/~~ ✅ dealt+AC 2026-06-12 (**clean first-AC, self-derived, 15m SUB-CAP**; **re-classified Subtree-Aggregation, NOT Tree-DP** — pure post-order sum fold, no recurrence-with-choice → Tree-DP NOT credited; mod-at-end trap handled; clean-rate 8/9) → `First-Attempt/09`
10. [—] ~~k-th-largest-perfect-subtree-size-in-binary-tree~~ — **REMOVED 2026-06-12: Tree-DP DEFERRED (band tree supply is traversal/aggregation, not optimization recurrence — see ledger §2)**
11. [x] ~~https://leetcode.com/problems/minimum-number-of-swaps-to-make-the-string-balanced/~~ ❌ dealt 2026-06-12 (**HARD FAIL — EDITORIAL-level help (not a mere hint); 33m OVER-CAP, impl only 3m. Stuck 30m, then was walked through the FULL approach across turns: the reduction, the `]]]…[[[` canonical shape, AND the `⌈k/2⌉` formula confirmed.** bucket **Stack/Reframe** ✦; code correct but NOT credited per rule 6C — editorial; clean-rate 8/10) → `First-Attempt/11`
12. [x] ~~https://leetcode.com/problems/minimum-number-of-seconds-to-make-mountain-height-zero/~~ ⚠️❌ dealt 2026-06-13 (**Heap route: SOFT FAIL — 2× WA then AC, self-derived**; WA-causes: wrong heap key `t·k` + stored-cumulative desynced from count → Heap stays 1/2. **BS route (2026-06-15): HARD FAIL — could not self-derive `helper`, full code given (editorial) → Binary-Search debt stays 0/2.** Banked recurring bug: shift `>>` binds looser than `+` → `low+(hi-lo)>>1` = `hi/2`. clean-rate 8/11) → `First-Attempt/12`
13. [x] ~~https://leetcode.com/problems/minimum-time-to-complete-trips/~~ ✅ dealt 2026-06-13 (**CLEAN — first-sub self-derived AC, 18m**; Binary-Search on answer, feasibility `Σ⌊T/t⌋ ≥ totalTrips`. **Binary-Search debt 0/2 → 1/2** — first clean rep on the plain-BS debt carried since 1500-1550. Precedence reflex held: wrote `low+((hi-lo)>>1)` correctly. clean-rate 9/12) → `First-Attempt/13`
14. [x] ~~https://leetcode.com/problems/count-number-of-bad-pairs/~~ ⚠️ dealt 2026-06-15 (**HINTED — not clean**; stuck 20m, self-pivoted to good-pairs complement but took LC hint "count the not-bad pairs" before the 30 cap; load-bearing `nums[i]-i` key reframe was the real block. **Hashing already OWNED 2/2 → no rep at stake.** clean-rate 10/14 ~71%) → `First-Attempt/15`
15. [x] ~~https://leetcode.com/problems/count-the-number-of-beautiful-subarrays/~~ ✅ dealt 2026-06-15 (**CLEAN — first-sub self-derived AC, 43m OVER-CAP** → derivation clause; XOR-cancellation reframe ⇒ subarray-XOR-0 ⇒ prefix-XOR count. **Bit 1/2 → 2/2 → OWNED ●**; Hashing ride-along. clean-rate 11/15 ~73%) → `First-Attempt/16`
16. [x] ~~https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/~~ ♻️ dealt 2026-06-15 (**RE-SOLVE — clean but NO NEW REP**; LC 1249 already solved **2026-06-03** in stack-reflex atom `04-stack/01-matching`, same index-stack+`boolean[]` approach reproduced → rule 6A: re-solve gives no rep. **Stack stays 0/2.** Good 12-day retention. **Queue-build oversight: pre-solved problem included.** NOT counted in clean-rate; no First-Attempt file.)
17. [x] ~~https://leetcode.com/problems/advantage-shuffle/~~ ✅ dealt 2026-06-15 (**CLEAN first-sub self-derived AC**; advantage-greedy via **TreeMap** (`higherKey`/`firstKey`-dump). **Greedy ride-along (OWNED) → no new rep; Two-Pointers NOT credited (our code wasn't two-pointer), stays 0/2** — same as #03 push-dominoes. Banked exchange lemma: smallest is never a unique beater. clean-rate 12/16 ~75%) → `First-Attempt/17`
18. [x] ~~https://leetcode.com/problems/apply-bitwise-operations-to-make-strings-equal/~~ ⚠️ dealt 2026-06-15 (**HINTED ("soft" — 2 counterexample-disproofs + "positions don't matter" nudge) → not clean**; positional flip-sim was the trap, answer is the positionless invariant `s.contains("1")==target.contains("1")`. **Bit owned 2/2 + Invariant/Reframe non-gating → no rep at stake.** clean-rate 12/17 ~71%) → `First-Attempt/18`
19. [ ] https://leetcode.com/problems/maximum-width-ramp/
20. [—] ~~minimum-time-to-collect-all-apples-in-a-tree~~ — **REMOVED 2026-06-12: Tree-DP DEFERRED (see ledger §2)**
21. [ ] https://leetcode.com/problems/maximum-product-after-k-increments/
22. [ ] https://leetcode.com/problems/flip-string-to-monotone-increasing/
23. [ ] ⚠ https://leetcode.com/problems/maximum-number-of-moves-in-a-grid/ — **bucket-contaminated 2026-06-15 (Claude leaked DP-Grid); implementation rep only when dealt**

---

## RETIRED (already dealt — do NOT re-deal)

| Dealt | Problem | Result | File |
|---|---|---|---|
| 2026-06-10 | satisfiability-of-equality-equations | ✅ **clean first-AC** (46m over-cap → derivation clause; **Union-Find ★ 2/2 → OWNED ●**) | `First-Attempt/01` |
| 2026-06-10 | count-number-of-ways-to-place-houses | ❌→✓ **HINTED + WA-then-AC** (wrong-axis combinatorics → DP hint; overflow/mod-timing WA; DP-Linear still 0/2) | `First-Attempt/02` |
| 2026-06-10 | push-dominoes | ✅ **clean first-AC** (45m over-cap; over-model → Two-Pointers NOT credited, 0/2; clean-rate 2/3) | `First-Attempt/03` |
| 2026-06-10 | partition-string-...-values-at-most-k | ✅ **clean first-AC, 25m SUB-CAP** (Greedy ride-along, DP-String still 0/2; comprehension-assisted; clean-rate 3/4) | `First-Attempt/04` |
| 2026-06-11 | find-the-punishment-number-of-an-integer | ✅ **clean first-AC, self-derived, 30m** (**Backtracking 2/2 → OWNED ●**; clean-rate 4/5) | `First-Attempt/05` |

---

<details>
<summary>⚠️ SPOILER — ANSWER KEY (do not open before solving)</summary>

### Per-problem buckets (sorted hardest → easiest by AR)

| AR | Q | Problem | Bucket (credit by OUR code) | Trap / disguise |
|---|---|---|---|---|
| 39.8% | Q3 | minimum-time-to-complete-trips | **Binary-Search on answer** (carried plain-BS) | `T` trap: overflow in upper bound `min(trip)*trips` & in the feasibility sum → use long |
| 42.7% | Q3 | apply-bitwise-operations-to-make-strings-equal | **Bit** ✦ Invariant/Reframe (STRONG) | op preserves "has ≥1 one" ⇒ equalizable iff both nonzero or both all-zero. No simulation |
| 43.6% | Q2 | minimize-maximum-component-cost | **Union-Find ★** + Binary-Search (amortizes both) | BS on the cost threshold; DSU connectivity check under threshold |
| 44.0% | Q3 | maximum-product-after-k-increments | **Heap** | min-heap, +1 to smallest ×k; mod only the final product |
| 44.0% | Q2 | count-number-of-ways-to-place-houses | **DP » Linear** | Fib-like per side, answer = side² mod. `T` trap: cast to long before squaring + mod each step |
| 47.1% | Q2 | reward-top-k-students | **Heap** (+Hashing) | score via pos/neg word sets; tie-break id asc |
| 47.7% | Q3 | partition-string-into-substrings-with-values-at-most-k | **DP » String** (greedy partition) | value ≤ k per piece; handle leading multi-digit / impossible single char |
| 51.9% | Q2 | satisfiability-of-equality-equations | **Union-Find ★** | DSU: union all `==`, then check no `!=` joins one set. Trap: process ALL `==` before ANY `!=`. Disguise: looks like string parsing |
| 54.2% | Q3 | count-the-number-of-beautiful-subarrays | **Bit/XOR + Hashing** ✦ Reframe | reframe "remove equal-bit pairs" ⇒ subarray **XOR == 0** ⇒ prefix-XOR + count map |
| 54.2% | Q2 | count-number-of-bad-pairs | **Hashing** ✦ Reframe | bad = C(n,2) − good; `nums[j]−nums[i]==j−i ⟺ nums[i]−i == nums[j]−j` ⇒ key by `nums[i]−i` |
| 54.6% | Q3 | advantage-shuffle | **Two-Pointers** (greedy) | sort both; assign smallest that beats, else dump weakest on their strongest |
| 54.8% | Q2 | construct-the-longest-new-string | **DP » Linear** | small DP/greedy over AA/BB/AB counts + adjacency rule |
| 55.7% | Q3 | maximum-product-of-splitted-binary-tree | ~~Tree-DP ★~~ → **Subtree-Aggregation** (NOT tree-DP — pure post-order sum fold, no recurrence-with-choice) | DFS subtree sums; per edge product = sub·(total−sub). `T` trap: keep long, **mod only at the very end** (mod before max breaks comparison) |
| 55.9% | Q2 | maximum-width-ramp | **Monotonic-Stack ★** (+Two-Ptr) | decreasing-index stack from left, scan from right popping. Disguise: "ramp" ≠ stack |
| 58.3% | Q2 | minimum-number-of-seconds-to-make-mountain-height-zero | **Binary-Search on answer** | per worker in time t: k with `wt·k(k+1)/2 ≤ t`. `T` trap: overflow + triangular-inversion |
| 58.8% | Q3 | maximum-number-of-moves-in-a-grid | **DP » Grid** | dp over columns, move to strictly-greater right/diag |
| 61.9% | Q2 | flip-string-to-monotone-increasing | **DP » String** | dp keep-monotone flips, or prefix ones-vs-zeros |
| 62.3% | Q2 | ~~k-th-largest-perfect-subtree-size-in-binary-tree~~ REMOVED | ~~Tree-DP ★~~ → tree-DP-*lite* (composite-state predicate fold, plain post-order) — **DEFERRED, removed from deal list** | DFS returns (isPerfect, size); perfect ⟺ both children perfect AND equal height |
| 63.0% | Q2 | push-dominoes | **Two-Pointers** | scan forced L/R regions, fill gaps by rule. Disguise: editorial says BFS |
| 63.7% | Q3 | ~~minimum-time-to-collect-all-apples-in-a-tree~~ REMOVED | ~~Tree-DP ★~~ → tree-DP-*lite* (conditional cost recurrence, strongest of the 3 but still no optimization) — **DEFERRED, removed from deal list** | DFS returns subtree collect-cost, +2 per useful child edge. Trap: build undirected adj + visited |
| 71.5% | Q3 | minimum-remove-to-make-valid-parentheses | **Stack** | stack of `(` indices; drop unmatched. Trap: counters suffice (don't over-model with index store) |
| 78.1% | Q3 | minimum-number-of-swaps-to-make-the-string-balanced | **Stack** ✦ Reframe | don't simulate swaps; answer = ⌈unmatched-close / 2⌉ |
| 81.7% | Q3 | find-the-punishment-number-of-an-integer | **Backtracking** | for each i, can i·i's digits partition to sum i? backtracking partition |

### Bucket coverage this queue provides (vs the open debts)

| Bucket | Owed | In queue | Picks |
|---|---|---|---|
| **Union-Find ★** | 1 | 2 | satisfiability-of-equality-equations, minimize-maximum-component-cost |
| ~~**Tree-DP ★**~~ DEFERRED | 2 | **0 genuine** | band tree supply is traversal/aggregation; the 3 "tree-DP" tags are 1 sum-fold + 2 tree-DP-*lite* — **none force an optimization recurrence**. Removed from deal list; roll to a band with House-Robber-on-tree / tree-knapsack supply. See ledger §2. |
| **Monotonic-Stack ★** | 1 | 1 | maximum-width-ramp (2nd also reachable via carried #9 max-chunks) |
| Two-Pointers | 2 | 2 | advantage-shuffle, push-dominoes |
| Binary-Search | 2 | 2 | minimum-time-to-complete-trips, min-seconds-mountain |
| Heap | 2 | 2 | maximum-product-after-k-increments, reward-top-k-students |
| Bit | 2 | 2 | count-beautiful-subarrays, apply-bitwise-operations |
| Stack (plain) | 2 | 2 | min-remove-valid-parens, min-swaps-balanced |
| DP » Linear | 2 | 2 | count-ways-place-houses, construct-longest-new-string |
| DP » String | 2 | 2 | flip-string-monotone, partition-string-≤k |
| DP » Grid | 1 | 1 | maximum-number-of-moves-in-a-grid |
| Backtracking | 1 | 1 | find-the-punishment-number |
| Hashing | 1 | 1 (+amort) | count-number-of-bad-pairs |

**Rolls cross-band (no clean in-band candidate found):** **DP » LIS-variant** (0 in band) and **DP » Interval** (none genuine — "cutting cake I" is greedy, not interval DP). Both are 1/2 already — owe 1 each, roll forward. **Tree-DP ★ (DEFERRED 2026-06-12 — supply-justified):** the band's ~20 tree problems are traversal/BFS-level/construction; the only true-optimization tree-DP on hand is House Robber V (seed inventory, re-solve only → no new ownership rep). True tree-DP that "cannot be solved without the recurrence" = **0 fresh in band.** Trie / Topo-Sort / Dijkstra / SegTree deferred per topic map.

### Trickiness tiers (true difficulty by editorial, not AR — [[lc-difficulty-by-editorial]])

- **Insight-gated (train derivation):** satisfiability-of-equality-equations, minimize-maximum-component-cost, maximum-width-ramp, advantage-shuffle, push-dominoes, count-beautiful-subarrays, apply-bitwise-operations, min-swaps-balanced, count-bad-pairs.
- **Trap-carrier (train carelessness — Step-2/3 earns its keep):** maximum-product-of-splitted-binary-tree (mod-at-end), count-ways-place-houses (square+overflow), minimum-time-to-complete-trips (overflow bounds), min-seconds-mountain (overflow + inversion), min-remove-valid-parens (index over-model).
- **Standard application (clean reps):** min-time-collect-apples, kth-largest-perfect-subtree, max-product-after-k-increments, reward-top-k-students, flip-string-monotone, partition-string-≤k, max-moves-grid, find-punishment-number, construct-longest-new-string.

### ✦ Invariant / Reframe members (grow & review deck — never gates graduation)
apply-bitwise-operations-to-make-strings-equal (STRONG), count-the-number-of-beautiful-subarrays (XOR reframe), minimum-number-of-swaps-to-make-the-string-balanced (reframe), count-number-of-bad-pairs (key reframe), maximum-width-ramp (lighter).

</details>
