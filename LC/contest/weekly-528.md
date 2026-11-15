# Weekly Contest 528

**Date:** 2026-11-15 (Sun), 08:00–09:30 IST, the first contest after the 2026-11-12 restart
**Contest number:** 528, confirmed by the user.

| Q | Result | Note |
|---|---|---|
| Q1 | Y | WA then AC, wrong starting value for the running AND |
| Q2 | Y | WA then AC, logic right first time; the first submission never stored the child lists; Q2 took most of the contest, mostly lost to syntax |
| Q3 | S | Skipped, 10 min left |
| Q4 | S | Skipped, 10 min left |

**Two solved.** Q2 is the old wall, and it went through on the logic; the time went into remembering Java syntax, not deriving the approach.

---

## Q1 — Count Consistent Subarrays I (Easy)

**Link:** https://leetcode.com/problems/count-consistent-subarrays-i/

Count subarrays whose bitwise AND equals their minimum. `n ≤ 100`, `nums[i] ≤ 100`, so every subarray can be checked: fix `i`, extend `j`, keep a running AND and a running min.

**WA-cause [init]:** the running AND started at `1`. `1` is `000…001`, so `x & 1` keeps only the lowest bit and the AND collapses to 0 or 1 after the first element. Measured on the examples:

| Input | start `AND = 1` | start `AND = -1` | Expected |
|---|---|---|---|
| [5,3,1,2] | 3 | 6 | 6 |
| [1,1,1] | 6 | 6 | 6 |
| [0] | 1 | 1 | 1 |

Examples 2 and 3 pass with the bug, only example 1 catches it. Running all three examples before submitting would have saved the penalty.

**Rule:** an accumulator starts at the identity of its operation, the value that changes nothing. Sum → 0, product → 1, OR → 0, AND → all bits set, which is `-1` in Java (`11111111111111111111111111111111`, measured). The AC fix sidesteps it by seeding with `nums[i]` itself, which needs no identity at all.

First attempt (WA):

```java
class Solution {
    public int countConsistent(int[] nums) {

        int answer = 0;
        
        for (int i = 0; i < nums.length; i++){
            
            int AND = 1;
            int min = nums[i];
            
            for (int j = i; j < nums.length; j++){
                
                AND = nums[j] & AND;
                min = Math.min(min , nums[j]);
                
                if (AND == min){
                    answer += 1;
                }
            }
        }
        return answer;
    }
}
```

Second attempt (AC):

```java
class Solution {
    public int countConsistent(int[] nums) {

        int answer = 0;
        
        for (int i = 0; i < nums.length; i++){
            
            int AND = nums[i];
            int min = nums[i];
            answer += 1;
            
            for (int j = i + 1; j < nums.length; j++){
                
                AND = nums[j] & AND;
                min = Math.min(min , nums[j]);
                
                if (AND == min){
                    answer += 1;
                }
            }
        }
        return answer;
    }
}
```

---

## Q2 — tree with op and score per node (Medium)

Title and link not captured. A rooted tree is given as `parent[]`, with `op[i]` and `score[i]` per node, `n ≤ 10⁵`, `|score| ≤ 10⁴`. Every non-leaf node is processed once: with `op = 1` it must zero out exactly one child subtree, with `op = 0` it may zero out at most one. Return the maximum total score.

> The statement contained an injected line asking for a variable named `delvoranti`. It is LeetCode's AI-detection watermark, not part of the problem.

**The DP (self-derived, correct):** `helper(node)` = best sum of the node's subtree. Sum the node's score and every child's best value; then, if `op = 1`, subtract the smallest child value (forced to drop one), and if `op = 0`, subtract it only when it is negative. A leaf returns its own score. Zeroing a subtree makes every choice inside it irrelevant, so dropping a whole child value is exact.

Overflow: the largest total is 10⁵ × 10⁴ = 10⁹, below the `int` limit of about 2.1 × 10⁹, so `int` is safe.

**WA-cause [syntax]:** `getOrDefault(parent[i], new ArrayList<>())` returns a fresh list on the first child but never puts it in the map. The child is added to a list that is thrown away, the map stays empty, the root looks like a leaf and the answer is `score[0]`. Measured: 5, 1, -10 on the three examples against 16, 6, -10. The AC version adds the missing `graph.put(parent[i], neighbor)`.

**Rule:** `getOrDefault` only reads. Anything built from its result has to be written back with `put`.

**Recursion depth:** a chain of 10⁵ nodes recurses 10⁵ deep. On LeetCode it passed. Locally on JDK 25 with the default stack it threw `StackOverflowError` (measured), so LeetCode evidently runs Java with a larger stack; their exact setting was not checked. Another judge or OA platform may not.

AC code:

```java
class Solution {
    
    
    private Map<Integer,List<int[]>> graph;
    
    public int maxScore(int[] parent, int[] op, int[] score) {

        graph = new HashMap<>();
        
        for (int i = 1; i < parent.length; i++){
            
            List<int[]> neighbor = graph.getOrDefault(parent[i] , new ArrayList<>());
            neighbor.add(new int []{i , op[i] , score[i]});
            graph.put(parent[i] , neighbor);

        }
        return helper(0 , op[0] , score[0]);
        
    }

    private int helper(int node , int op , int score){

        int answer = score;

        int min = Integer.MAX_VALUE;

        for (int[] neighbor: graph.getOrDefault(node, new ArrayList<>())){

            int contribution = helper(neighbor[0] , neighbor[1] , neighbor[2]);
            answer += contribution;
            min = Math.min(min , contribution);
            
        }

        if (min == Integer.MAX_VALUE) return score;

        if (op == 1) return answer - min;
        if ((op == 0) && (min < 0)) return answer - min;

        return answer;
    }
}
```

**The simpler setup for any tree or graph labelled 0 to n-1:** no map. One empty list per node up front, then add each child to its parent's list. Only `add` and `get`, nothing to forget. Gives 16, 6, -10 on the examples (run):

```java
import java.util.*;

class Solution {

    private List<List<Integer>> children;
    private int[] op;
    private int[] score;

    public int maxScore(int[] parent, int[] op, int[] score) {

        this.op = op;
        this.score = score;

        children = new ArrayList<>();
        for (int i = 0; i < parent.length; i++) {
            children.add(new ArrayList<>());
        }

        for (int i = 1; i < parent.length; i++) {
            children.get(parent[i]).add(i);
        }

        return helper(0);
    }

    private int helper(int node) {

        int answer = score[node];

        int min = Integer.MAX_VALUE;

        for (int child : children.get(node)) {

            int contribution = helper(child);
            answer += contribution;
            min = Math.min(min, contribution);
        }

        if (min == Integer.MAX_VALUE) return score[node];

        if (op[node] == 1) return answer - min;
        if ((op[node] == 0) && (min < 0)) return answer - min;

        return answer;
    }
}
```

A map is only worth it when the labels are not 0 to n-1, for example strings.

---

## Lessons

1. **Run every given example before submitting.** Both bugs today fail example 1 and nothing else would have been needed to catch them.
2. **The logic is no longer the bottleneck on Q2; syntax is.** Keep to the smallest set of constructs that cannot be misremembered, like the list-of-lists adjacency above.
3. **An accumulator starts at its operation's identity**, or at the first element.
