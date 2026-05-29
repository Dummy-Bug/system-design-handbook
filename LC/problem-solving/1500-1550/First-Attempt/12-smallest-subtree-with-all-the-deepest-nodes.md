# #12 — Smallest Subtree with all the Deepest Nodes

**Link:** https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (Group A #2 — Binary Tree / Implementary acquisition)
**Time:** 56 min — **AC clean, first attempt**
**Pattern:** Binary Tree traversal (depth + LCA of deepest leaves)

---

## Problem

Given the root of a binary tree, the *depth* of a node is its distance from the root. A node is *deepest* if it has the largest depth in the whole tree. Return the smallest subtree (the node) that contains **all** the deepest nodes.

Equivalent framing: find the **lowest common ancestor (LCA) of all deepest leaves**.

## Approach (verbatim)

First get the highest-depth path and store it. Then for each node from the top of that path, check if its left depth == right depth — if yes, that's the root of the answer subtree, return it. After storing the path you can cache the depth result at each level so it isn't recomputed again and again.

## Solution (as submitted)

```java
class Solution {

    private int maxDepth = 0;
    private Deque<TreeNode> maxDepthPath = new ArrayDeque<>();

    public TreeNode subtreeWithAllDeepest(TreeNode root) {

        findDeepestPath(root, 0, new ArrayDeque<>());

        Deque<TreeNode> orderedPath = new ArrayDeque<>();
        while (!maxDepthPath.isEmpty()) {
            orderedPath.push(maxDepthPath.pop());
        }

        maxDepth--;
        while (!orderedPath.isEmpty()) {
            TreeNode node = orderedPath.pop();
            int leftDepth  = getMaxDepth(node.left);
            int rightDepth = getMaxDepth(node.right);

            if (leftDepth == rightDepth && leftDepth == maxDepth) {
                return node;
            }
            maxDepth--;
        }
        return null;
    }

    private int getMaxDepth(TreeNode node) {
        if (node == null) return 0;
        int left  = getMaxDepth(node.left);
        int right = getMaxDepth(node.right);
        return 1 + Math.max(left, right);
    }

    private void findDeepestPath(TreeNode node, int depth, Deque<TreeNode> path) {
        if (node == null) {
            if (depth > maxDepth) {
                maxDepthPath = new ArrayDeque<>(path);
                maxDepth = depth;
            }
            return;
        }
        path.push(node);
        findDeepestPath(node.left,  depth + 1, path);
        findDeepestPath(node.right, depth + 1, path);
        path.pop();
    }
}
```

**Complexity:** the path walk is O(n), but each `getMaxDepth(node.*)` re-traverses the subtree, so worst case is O(n) nodes on the path × O(n) per depth call = **O(n²)**. Space O(h) for recursion + the stored path.

## Debrief notes

- **Correct, AC first try.** The core insight is sound: the answer is the deepest node on the root→deepest-leaf path where the left and right subtrees are *equally* deep — that's the LCA of all deepest leaves. Walking the path top-down and returning the first node whose `leftDepth == rightDepth == remaining maxDepth` is a valid way to find it.
- **It cost 56 min and felt like a fight — that's the signal.** The approach was over-built: store a full path, reverse it through a second deque, decrement a shared `maxDepth` counter while walking. Three moving parts that have to stay in sync (the `maxDepth--` in two places is exactly the kind of off-by-one that eats time). AC, but fragile.
- **The clean idiom — single post-order pass, O(n).** Return *both* the depth and the answer-node from one recursion. No path storage, no second traversal, no shared counter:

  ```java
  public TreeNode subtreeWithAllDeepest(TreeNode root) {
      return dfs(root).node;
  }

  private Result dfs(TreeNode node) {
      if (node == null) return new Result(null, 0);
      Result L = dfs(node.left);
      Result R = dfs(node.right);
      if (L.depth == R.depth) return new Result(node, L.depth + 1); // balanced → this node is the LCA so far
      return L.depth > R.depth
          ? new Result(L.node, L.depth + 1)   // deeper side carries the answer up
          : new Result(R.node, R.depth + 1);
  }

  record Result(TreeNode node, int depth) {}
  ```

  The trick that removes all the bookkeeping: **when left and right depths tie, the current node is the LCA of everything deepest below it** — bubble it up. When they differ, the deeper child's answer is still the answer; carry it. One pass, O(n) time, O(h) space, no global state.
- **Pattern installed:** "return a tuple (value + node) from one DFS" is the universal fix for tree problems where you're tempted to do a second traversal to recompute something. Whenever you catch yourself calling a `getDepth()` helper *inside* a walk you already did — that's the cue to fold it into one post-order return.
