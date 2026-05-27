### #15 — Construct Binary Search Tree from Preorder Traversal
**Link:** https://leetcode.com/problems/construct-binary-search-tree-from-preorder-traversal/
**Date attempted:** 2026-05-27 ~07:00
**Rating:** 1550–1600 band (Phase 1 acquisition — Tree DP blind spot)
**Time:** 85 min (35 min derivation + 50 min coding/debug) — hinted
**Pattern:** Tree DP / tree construction (blind spot)

---

**Verbatim thinking:**

- this is a recursion problem — we need preorder + inorder to construct a unique BST
- preorder is given, but inorder is NOT given
- recalled the classic "construct tree from preorder + inorder" approach from before
- key insight: for a BST, inorder = sorted preorder. just sort the array → inorder acquired
- briefly doubted: can [1,2,3] inorder produce multiple trees? yes, but preorder+inorder combo is unique — only one BST produces that exact pair
- recurrence: root = pre[start], find root's position `pos` in inorder, left subtree has `length = pos - inStart` elements
  - node.left = f(start+1, start+length, inStart, pre, in)
  - node.right = f(start+length+1, end, pos+1, pre, in)
- base case: start > end || start >= pre.length → return null

**Bug hit:**

**WA-cause [impl-bug]:** right subtree's `inStart` parameter was `start + length + 1` — but `start` is a preorder index and `inStart` should be an inorder index. Mixed coordinate systems. Works at root (both 0) but diverges in deeper recursion. Fix: use `pos + 1` instead.

**Insight:**
For BST, inorder = sorted(preorder). Then use the classic "construct tree from preorder + inorder" divide-and-conquer: root from preorder, split left/right using inorder position, recurse with correct index ranges in both arrays.

**Key gotcha:**
Preorder indices and inorder indices are separate coordinate systems. Don't mix them — `start` (preorder) ≠ `inStart` (inorder). Right subtree's inorder start is `pos + 1`, not `start + length + 1`.

**Complexity:**
O(n log n) time (sort dominates), O(n) space (map + recursion stack).

**Solution code:**

```java
class Solution {
    
    Map<Integer,Integer> map;

    private TreeNode helper(int start, int end, int inStart, int[] pre, int[] in){
        
        if (start > end || start >= pre.length){
            return null;
        }
        
        int pos = map.get(pre[start]);
        int length = pos - inStart;
        
        TreeNode node = new TreeNode(pre[start]);
        
        node.left = helper(start + 1, start + length, inStart, pre, in);
        node.right = helper(start + length + 1, end, pos + 1, pre, in);

        return node;
    }

    public TreeNode bstFromPreorder(int[] preOrder) {
        
        int n = preOrder.length;
        int[] inOrder = new int[n];
        
        for (int i = 0; i < n; i++){
            inOrder[i] = preOrder[i];
        }
        Arrays.sort(inOrder);

        map = new HashMap<>();

        for (int i = 0; i < n; i++){
            map.put(inOrder[i], i);
        }

        return helper(0, n - 1, 0, preOrder, inOrder);
    }
}
```
