# P — Single Number (LC 136)

**Task:** every element appears twice except one. Find the one. Required: O(n) time, O(1) space.

## Solution

```java
class Solution {
    public int singleNumber(int[] nums) {
        int xor = 0;
        for (int num : nums) {
            xor = xor ^ num;
        }
        return xor;
    }
}
```

## The insight: XOR self-inverse cancels the pairs

XOR everything together. By the §3 property `x ^ x = 0` and `x ^ 0 = x`:
- every value that appears **twice** XORs with itself → `0` (cancels out)
- the one value appearing **once** has nothing to cancel it → it survives

XOR is also commutative + associative, so order doesn't matter — the pairs find each other regardless of position. Start the accumulator at `0` (the XOR identity).

This is the canonical payoff of "even occurrences cancel, the odd one remains," and it's why XOR gives O(1) space where a hash-set would need O(n).

*Status: clean self-derived AC. Direct application of the XOR self-inverse property installed in §3.*
