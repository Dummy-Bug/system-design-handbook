### #21 — Minimum Operations to Halve Array Sum
**Link:** https://leetcode.com/problems/minimum-operations-to-halve-array-sum/
**Date attempted:** 2026-05-27 ~22:00
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 15 min (12 min coding + 3 min debug) — soft fail (WA-then-AC)
**Pattern:** Heap-greedy

---

**Verbatim thinking:**

- immediately saw: max-heap, keep halving the largest element, track how much total reduction we've made
- knew the gotcha would be precision — int values get halved into decimals
- used Float first → WA on large values (float has ~7 sig digits, not enough for values near 10^7)
- switched to Double → AC

**WA-cause [impl-bug]:** Used `Float` (32-bit, ~7 significant digits) instead of `Double` (64-bit, ~15 significant digits). Large input values (5-9 million) lose precision under repeated halving with float. Called it out beforehand ("only issue could be int instead of float") but still picked the wrong floating type.

**Insight:**
Greedy: always halve the current largest element. Max-heap gives O(log n) access to the largest. Track cumulative reduction; stop when reduction ≥ originalSum / 2.

**Key gotcha:**
Use `double`, not `float`. Values up to 10^7 halved repeatedly need >7 significant digits of precision.

**Complexity:**
O(n log n) time, O(n) space.

**Solution code:**

```java
class Solution {
    public int halveArray(int[] nums) {
        
        PriorityQueue<Double> pq = new PriorityQueue<>((a,b) -> Double.compare(b,a));
        
        double sum = 0.0;

        for (int num : nums){
            pq.offer(num + 0.0);
            sum += num;
        }
        
        int count = 0;
        double currentSum = 0.0;

        while(currentSum < sum/2.0){

            double value = pq.poll();
            double halvedValue = value/2.0;
            currentSum += halvedValue;
            pq.offer(halvedValue);
            count++;
        }
        return count;
    }
}
```
