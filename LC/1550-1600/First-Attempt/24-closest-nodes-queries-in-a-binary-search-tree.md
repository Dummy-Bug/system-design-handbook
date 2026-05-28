### #24 — Closest Nodes Queries in a Binary Search Tree
**Link:** https://leetcode.com/problems/closest-nodes-queries-in-a-binary-search-tree/
**Date attempted:** 2026-05-28, solved ~12:40 IST
**Rating:** 1550–1600 band (Phase 2 derivation, Q01)
**Time:** 40 min total — **TLE on first submission, fixed to AC** → soft fail (over 30-min cap; time exempt under derivation clause, but TLE-then-AC is soft fail regardless)
**Pattern:** BST in-order → sorted array → binary search (floor/ceil)
**Sealed-queue label:** "Tree DP" — **mislabel.** The actual solve is binary-search-on-sorted-array, not tree DP. Does NOT credit the Tree DP bucket.

---

**Approach (derived correctly, first try):**

- In-order traversal of a BST yields a **sorted** array (BST property: left < node < right).
- For each query: `findFloor` = largest value ≤ q, `findCeil` = smallest value ≥ q.
- Both are binary searches on the sorted in-order array.
- If no floor (q < min) or no ceil (q > max), return -1 for that side.

**Complexity:** O(n + q log n) time, O(n) space. Optimal for n, q ≤ 10⁵.

---

**The bug — TLE, not WA (correct answer, wrong complexity):**

First submission produced **correct answers** but TLE'd. The binary searches degraded to **linear scans** because the bounds moved by ±1 instead of jumping to mid±1:

```java
// WRONG — moves bound by one index, eliminates 1 element/iteration → O(n) per query
else if (inorder.get(mid) > num){ candidate = inorder.get(mid); high = high - 1; }
else { low = low + 1; }
```

Trace `findFloor(9)` on `[1,3,5,7,9]` → 5 iterations for a 5-element array (should be ~2). Each query becomes O(n).

**Numbers that prove TLE:** n ≤ 10⁵ nodes, q ≤ 10⁵ queries → cost = q × n = 10⁵ × 10⁵ = **10¹⁰ ops**. Java limit ~10⁸–10⁹/s → blows the limit ~100×. Hence TLE, not WA.

**Fix — discard half each step:**

```java
else if (inorder.get(mid) > num){ candidate = inorder.get(mid); high = mid - 1; }
else { low = mid + 1; }
```

Restores O(log n) per query → total O(n + q log n). AC.

**WA-cause [impl-bug]:** binary search degraded to linear scan — moved bounds `high-1`/`low+1` instead of `mid-1`/`mid+1`, making each query O(n) → 10¹⁰ ops → TLE.

---

**Meta:** First binary-search problem in ~1 year — the half-discard reflex (`mid±1`) had rusted. Approach derivation was instant and correct; the slip was purely in the BS mechanic. Candidate for a Pattern-Reflex Deck card (see below).

**Solution code (AC):**

```java
class Solution {

    List<Integer> inorder = new ArrayList<>();

    private void traversal(TreeNode root){
        if (root == null){ return; }
        traversal(root.left);
        inorder.add(root.val);
        traversal(root.right);
    }

    private int findCeil(int num){
        int low = 0, high = inorder.size() - 1, candidate = -1;
        while (low <= high){
            int mid = (low + high)/2;
            if (inorder.get(mid) == num){ return inorder.get(mid); }
            else if (inorder.get(mid) > num){ candidate = inorder.get(mid); high = mid - 1; }
            else { low = mid + 1; }
        }
        return candidate;
    }

    private int findFloor(int num){
        int low = 0, high = inorder.size() - 1, candidate = -1;
        while (low <= high){
            int mid = (low + high)/2;
            if (inorder.get(mid) == num){ return inorder.get(mid); }
            else if (inorder.get(mid) < num){ candidate = inorder.get(mid); low = mid + 1; }
            else { high = mid - 1; }
        }
        return candidate;
    }

    public List<List<Integer>> closestNodes(TreeNode root, List<Integer> queries) {
        traversal(root);
        int n = queries.size();
        List<List<Integer>> ans = new ArrayList<>();
        for (int i = 0; i < n; i++){
            int q = queries.get(i);
            int floor = findFloor(q);
            int ceil = findCeil(q);
            List<Integer> range = new ArrayList<>();
            range.add(floor);
            range.add(ceil);
            ans.add(range);
        }
        return ans;
    }
}
```
