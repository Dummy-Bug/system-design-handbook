### #23 — Alice and Bob Playing Flower Game
**Link:** https://leetcode.com/problems/alice-and-bob-playing-flower-game/
**Date attempted:** 2026-05-28 ~10:00
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 47 min (43 min derivation + 4 min coding) — first-submission AC ✓
**Pattern:** Game theory / combinatorial counting

---

**Verbatim thinking:**

- Alice wins iff x + y is odd (game theory: the parity of total flowers decides who takes the last)
- so the problem reduces to: count pairs (x, y) with x ∈ [1,n], y ∈ [1,m], x + y odd
- first approach: for each odd sum O in [3, n+m], count valid pairs (a, b) with a+b=O, a≤n, b≤m
- for an odd sum O, there are O−1 unconstrained pairs (1,O−1)…(O−1,1)
- cap by the smaller bound: min(O−1, min(n,m))
- if O−1 exceeds the larger bound, subtract the overflow: (O−1 − max(n,m))
- sum over all odd O
- traced n=3,m=2 → 3 ✓, then n=9,m=5 → 22 ✓ before coding

**Insight:**
Game theory reduces this to pure counting: Alice wins iff x+y is odd. Then count pairs summing to an odd value within the bounds [1,n] × [1,m]. For each odd sum O, the count of valid pairs is a clamped interval: start from O−1 unconstrained pairs, cap at min(n,m), and subtract the overflow past max(n,m).

**Cleaner alternative (parity counting — O(1)):**
Instead of iterating odd sums, count directly:
- odd x in [1,n] = (n+1)/2, even x = n/2
- answer = (odd in n)×(even in m) + (even in n)×(odd in m)
- for n=9,m=5: 5×2 + 4×3 = 22 ✓
This is O(1) vs the O(n+m) odd-sum loop. Both pass at n,m ≤ 10^5.

**Key gotcha:**
The odd-sum loop counts ordered pairs (a from [1,n], b from [1,m]) — they're NOT symmetric when n≠m. The clamping must respect which bound is which. Verified by trace before coding.

**Complexity:**
O(n + m) time (odd-sum loop), O(1) space. Parity-count alternative is O(1) time.

**Solution code:**

```java
class Solution {

    private long getPairs(int num , int x, int y){

        long totalPairs = num - 1;
        int min = Math.min(x,y);
        

        if (min >= totalPairs){
            return totalPairs;
        }
        long possiblePairs = min;

        int max = Math.max(x,y);
        if (totalPairs > max){
            return possiblePairs - (totalPairs - max);
        }
        return possiblePairs;
    }

    public long flowerGame(int n, int m) {

        int maxNumber = m + n;
        long pairs = 0;

        for (int num = 3; num <= maxNumber; num +=2){

            pairs += getPairs(num,n,m);
        }
        return pairs;
        
    }
}
```
