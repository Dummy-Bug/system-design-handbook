# 20 — Maximum Product After K Increments

- **Link:** https://leetcode.com/problems/maximum-product-after-k-increments/
- **Band:** 1600–1699 · sealed queue · blind deal #21 · Q2 (AR 44.0%)
- **Bucket:** answer key files it **Heap**; **OUR code = min-heap, +1 to smallest ×k** → credit **Heap**.
- **Dealt:** 2026-06-16
- **AC:** 2026-06-16 _(15m **SUB-CAP**; self-derived, clean)_
- **Result:** ✅ **clean first-submission AC, self-derived.** → **Heap 1/2 → 2/2 → OWNED ●**. Clean-rate now **14/19 ≈ 74%**.
- **Honest note on difficulty:** queue's *"Standard application (clean reps)"* tier — easy for the band (user's reaction: "what the fuck was this"). But unlike #06 (soft, heap not load-bearing), here the heap **is** load-bearing: the algorithm is literally "repeatedly fetch the current min, +1, reinsert" k times → min-heap is the right structure. Legit full Heap rep.

---

## The problem
Given `nums` and `k`, you may pick any element and +1 to it, total `k` times. Maximize the product of the array, return it mod 1e9+7.

## Approach — greedy: always increment the current minimum (self-derived)
1. Build a min-heap of all `nums`.
2. `k` times: poll the min, push `min+1`.
3. Multiply everything out, mod at each step.

## Solution (clean first-AC)
```java
class Solution {
    final int MOD = 1_000_000_007;
    public int maximumProduct(int[] nums, int k) {
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int num : nums) pq.offer(num);
        while (k-- > 0) {
            int num = pq.poll();
            pq.offer(num + 1);
        }
        long product = 1L;
        while (!pq.isEmpty()) {
            int num = pq.poll();
            product = (product * num) % MOD;
        }
        return (int) product;
    }
}
```
*(As submitted; original MOD literal was `1_00_00_00_00_7` = same value, regrouped here to `1_000_000_007` for typo-safety.)*

## Why greedy works — the exchange argument (derived in debrief)
Spend one +1 on `x` vs the smaller `y` (`x > y`), rest of product frozen as `P`:
- give to `x`: `(x+1)·y·P = (xy + y)·P`
- give to `y`: `x·(y+1)·P = (xy + x)·P`

`xy·P` cancels; since `x > y`, giving to `y` (the **minimum**) is strictly better. Induct over all k increments → always raise the current min. The min-heap mechanizes "fetch current min" in O(log n). This is the [[reasoning-primitives/03-exchange-argument]] template in its **allocation flavor** (which recipient gets the operation), not the usual ordering flavor — same 4 steps: assume two choices differ → freeze the rest → write both outcomes → compare under the known ordering.

## WINS
1. **Greedy instinct from brute-forcing a few cases** — found "increment the min" empirically, trusted it, shipped. Correct contest play.
2. **Heap as the grab-min engine** — load-bearing, used correctly.
3. **`long` product + mod each step** — no overflow; clean (answer-key "mod-at-end" trap doesn't bite here since there's no per-element comparison, only a running product).

## Gap surfaced (the real lesson of this solve)
User could *find* the greedy by example but **could not convert gut → proof**. The fix is not intelligence — it's installing the **exchange-argument template as a reflex**: the missing mechanical step is *"freeze everything else, compare just the two adjacent choices."* See [[reasoning-primitives/03-exchange-argument]] (allocation-flavor variant to be appended).

## Complexity
Heap build O(n). k increments O(k log n). Final product O(n log n) drain. **Total O((n+k) log n).**

## Lesson
- **Allocation greedy ("which element gets the operation k times") → min/max-heap.** The exchange argument proves *which* element: freeze the rest, the marginal gain favors the extreme element.
- The exchange argument has an **allocation flavor** (recipient of an op), not just the textbook **ordering flavor** (sequence position). Same template.

## PENDING
- Perturbation debrief — Socratic in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written.
- Revision Day+14: re-derive the exchange-argument proof for "increment the min" cold, from scratch (this is the rep that matters, not the heap mechanics).
