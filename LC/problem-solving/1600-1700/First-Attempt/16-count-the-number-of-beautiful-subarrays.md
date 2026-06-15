# 16 — Count the Number of Beautiful Subarrays

- **Link:** https://leetcode.com/problems/count-the-number-of-beautiful-subarrays/ (LC 2588)
- **Band:** 1600–1699 · sealed queue · blind deal #15 · Q3 (AR 54.2%) · **answer-key bucket = Bit/XOR + Hashing ✦ Reframe**
- **Bucket (OUR code):** **Bit Manipulation** (XOR-cancellation reframe) + Hashing (prefix-XOR count map). Credited by mechanic-in-code [[lc-credit-mechanic-not-label]]; the load-bearing insight is the XOR reframe → Bit.
- **Dealt:** 2026-06-15 · **AC:** 2026-06-15 (**self-derived, no hint**), **first submission clean**, **43 min OVER-CAP** → derivation clause (over-cap self-derived counts; first sub was AC).
- **Result:** ✅ **CLEAN — first-submission self-derived AC.** **Bit Manipulation debt: 1/2 → 2/2 → ● OWNED.** 2nd Bit rep (after Unique-XOR-Triplets-I from the seed re-audit). Rides on Hashing (already owned). Clean-rate **10/14 → 11/15 (~73%)**.
- **Process note:** Step-1/Step-2 done on paper (notebook), not posted in chat. Followed, but not visible — post in chat next time so a slip can be caught pre-submit.

---

## The problem
`nums[i] ≥ 0`. One operation: pick two indices and a bit position `k`, subtract `2^k` from both (both must have that bit set). A subarray is **beautiful** if some sequence of ops makes all its elements 0. Count beautiful subarrays. `1 ≤ n ≤ 1e5`, `0 ≤ nums[i] ≤ 1e6`.

## Approach (self-derived) — XOR-cancellation reframe → prefix-XOR count
- **Reframe (the insight):** an op clears the *same* bit in two elements. To zero everything, each bit position must be cleared an even number of times across the subarray ⇒ **every bit position has even total count** ⇒ the subarray's total **XOR == 0**. (The pairwise cancellation between two elements is exactly their XOR.)
- **Subarray XOR 0 ⟺ `prefixXOR[r] == prefixXOR[l-1]`.** So beautiful subarrays ↔ **pairs of prefix positions with equal prefix-XOR**.
- Count via running map: `map[0]=1` (empty prefix), then per element `xor ^= num; ans += map[xor]; map[xor]++`. `ans += freq` accumulates `Σ C(count_k, 2)` — math-reflex §2.5/§2.6.

> **Same reflex as #15 (count-bad-pairs):** "count subarrays where `prefix[j]==prefix[i]`" *is* "count equal-key pairs" → `ans += freq`. Key was `nums[i]-i` there, prefix-XOR here. Generalization banked.

## Step 2 — worked example (`nums=[4,3,1,2,4]`, expected 2)
| num | xor | map[xor] before | ans += | map after |
|---|---|---|---|---|
| — | 0 | — | — | {0:1} |
| 4 | 4 | 0 | 0 | {0:1,4:1} |
| 3 | 7 | 0 | 0 | +{7:1} |
| 1 | 6 | 0 | 0 | +{6:1} |
| 2 | 4 | 1 | 1 | {4:2} |
| 4 | 0 | 1 | 2 | {0:2} |

ans = **2**. ✅ (The two beautiful subarrays: `[3,1,2,4]` and `[4,3,1,2,4]`, both XOR 0.)

## Step 3 — named edge cases
1. **Overflow in `ans`** — all-equal prefixes (e.g. `nums=[0,0,…]`) → `ans = 1+2+…+n = C(n+1,2) ≈ 5e9 ≫ int`. `ans` is `long`. ✅
2. **Seed `map.put(0,1)`** — without it, subarrays whose prefix-XOR is 0 from index 0 are missed (the empty prefix is a valid left boundary).
3. **XOR key fits int** — `nums[i] ≤ 1e6 < 2^20`, prefix-XOR bounded by `2^20` → `int` key fine.
4. **`freq`** — bounded by `n ≤ 1e5` → int.
5. **Single element** — `[0]` beautiful (xor 0, counts via seed); `[5]` not.

## As-submitted solution (AC)
```java
class Solution {
    public long beautifulSubarrays(int[] nums) {
        Map<Integer,Integer> map = new HashMap<>();
        map.put(0,1);
        long ans = 0L;
        int xor = 0;
        for (int num : nums){
            xor = num ^ xor;
            int freq = map.getOrDefault(xor, 0);
            ans += freq;
            map.put(xor , freq + 1);
        }
        return ans;
    }
}
```
- Time `O(n)`, space `O(n)`.

## Lesson
- **"Make subarray all-zero by clearing shared bits" → bit-parity → subarray XOR 0 → prefix-XOR equality → count equal-key pairs.** The XOR reframe is the load-bearing step (Bit); the counting is the §2.5 pair-count reflex (Hashing ride-along).
- **`ans += freq` is the general equal-key pair counter**, not an "ordered pairs only" trick — corrected a standing misconception. Works for any prefix-invariant (sum/XOR/parity) collapsed to `prefix[j]==prefix[i]`.

## PENDING
- **No cold re-solve owed** (clean self-derived first-AC). [[lc-cold-resolve-scope]]
- **Day+14 revision (due 2026-06-29):** re-derive the bit-parity → XOR-0 reframe cold (the insight, not the map boilerplate). [[lc-retrieval-not-reread]]
- **Bit Manipulation now ● OWNED 2/2** (#07 seed Unique-XOR-Triplets + #16).
