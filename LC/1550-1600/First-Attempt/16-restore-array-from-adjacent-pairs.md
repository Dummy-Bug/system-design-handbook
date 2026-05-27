### #16 — Restore the Array From Adjacent Pairs
**Link:** https://leetcode.com/problems/restore-the-array-from-adjacent-pairs/
**Date attempted:** 2026-05-27
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 38 min (12 min approach + 26 min coding) — first-submission AC ✓
**Pattern:** Graph / tree traversal

---

**Verbatim thinking:**

- generic graph approach: build neighbors for all elements, find element with only one edge (endpoint), BFS from there
- while thinking realized: exactly two elements appear only once in adjacent pairs — those are the start and end of the array
- all other elements appear exactly twice (they have a left neighbor and a right neighbor)
- so: build adjacency map, find any endpoint (size == 1), BFS/traverse from there
- considered int[] of size 2 per element but went with List<Integer> to avoid default-0 collision with valid values

**Insight:**
Adjacent pairs define a graph where each node has at most 2 neighbors (it's a path graph). The two endpoints have exactly 1 neighbor each. Find any endpoint, then traverse the path using BFS or simple iteration (skip the previous node to pick the next).

**Key gotcha:**
None — straightforward once you see it's a path graph. Using a visited set is slightly heavier than just tracking `prev`, but both work.

**Complexity:**
O(n) time, O(n) space.

**Solution code:**

```java
class Solution {
    
    Map<Integer,List<Integer>> map;

    private int[] helper(int source){

        Set<Integer> visited = new HashSet<>();
        List<Integer> ans = new ArrayList<>();

        Deque<Integer> q = new ArrayDeque<>();
        q.offer(source);
        visited.add(source);

        while(!q.isEmpty()){

            int u = q.poll();
            ans.add(u);

            for (Integer neighbor : map.get(u)){

                if (!visited.contains(neighbor)){
                    q.offer(neighbor);
                    visited.add(neighbor);
                }
            }

        }
        int [] array = new int [ans.size()];
        for (int i = 0; i < ans.size(); i++){
            array[i] = ans.get(i);
        } 
        return array;
    }

    public int[] restoreArray(int[][] adjacentPairs) {
        
        map = new HashMap<>();

        for (int[] pair : adjacentPairs){

            int u = pair[0];
            int v = pair[1];

            map.computeIfAbsent(u, k -> new ArrayList<>()).add(v);
            map.computeIfAbsent(v, k -> new ArrayList<>()).add(u);
        }

        int source = 0;
        for (Map.Entry<Integer,List<Integer>> entry : map.entrySet()){
            
            if (entry.getValue().size() == 1){
                source = entry.getKey();
                break;
            }

        }
        return helper(source);
    }
}
```
