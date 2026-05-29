# #13 — Remove Sub-Folders from the Filesystem

**Link:** https://leetcode.com/problems/remove-subfolders-from-the-filesystem/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (Group A #3 — Tries / Trie involving String acquisition pick)
**Time:** 31 min — solved ~10:37 AM — **AC clean, first attempt**
**Pattern as solved:** sort + prefix-set (the non-trie canonical)

---

## Problem

Given a list of folder paths, remove every folder that is a *sub-folder* of another folder in the list. `"/a/b"` is a sub-folder of `"/a"`. Return the remaining top-level folders in any order.

## Approach (verbatim)

Looked daunting, but the constraints (≤ 4·10⁴ folders, each ≤ 100 chars) say an n² is fine. Sort the folders lexicographically so a parent always lands before its children. Keep a set of folders we've decided to keep. For each folder, walk its characters; at every `/` check whether the prefix up to that point is already in the kept-set — if so, this is a sub-folder, skip it. If we reach the end without finding a kept ancestor, add it to the set.

Worst case ≈ checking each of 10⁴ strings against ~100-char prefixes ≈ 10⁸ — right on the n² edge, acceptable.

## Solution (as submitted)

```java
class Solution {
    public List<String> removeSubfolders(String[] folder) {
        Arrays.sort(folder);
        Set<String> set = new HashSet<>();

        for (String s : folder) {
            int n = s.length();
            int i = 1;
            while (i < n) {
                if (s.charAt(i) == '/') {
                    if (set.contains(s.substring(0, i))) break;   // an ancestor is already kept
                }
                i++;
            }
            if (i == n) set.add(s);   // no kept ancestor → this is top-level
        }
        return new ArrayList<>(set);
    }
}
```

**Complexity:** sort O(n·L·log n); main loop O(n·L) with each `substring` up to O(L) → O(n·L²) worst case. Space O(n·L) for the set.

## Why the sort makes it correct

After lexicographic sort, every ancestor of a path appears **before** it and they sit **contiguously**: `"/a"`, `"/a/b"`, `"/a/b/c"` all precede `"/ab"`, because at the divergence point `/` (code 47) sorts below any letter. So when you reach a child, any kept ancestor is guaranteed to already be in the set.

The `/`-separator check is what prevents the `"/a"` vs `"/ab"` false positive: for `"/ab"` the only prefix tested would need a `/` after `"/a"`, but `"/ab"` has `b` there — so `"/ab"` is correctly kept as its own top-level folder.

## Debrief notes

- **Correct, AC first try, well-reasoned.** The constraint-read up front (spotting that n² is allowed) is exactly the right move and saved time — no premature optimization.
- **One efficiency nit — repeated `substring`.** `s.substring(0, i)` allocates a fresh string every `/`. The standard tightening is to compare each path only against the **last kept folder** (since after sorting, a sub-folder's parent, if kept, is always the most recent addition):

  ```java
  List<String> ans = new ArrayList<>();
  for (String s : folder) {
      if (ans.isEmpty()) { ans.add(s); continue; }
      String last = ans.get(ans.size() - 1);
      if (!(s.startsWith(last) && s.charAt(last.length()) == '/'))
          ans.add(s);
  }
  ```

  This drops it to O(n·L) with no substring garbage — check against one predecessor instead of all prefixes.
- **Trie mechanic was NOT exercised.** This problem is the band's *Trie* acquisition pick, but it's cleanly solvable (and arguably easier) via sort + prefix-set, which is what was used. So the **trie itself is still un-installed** — same phantom risk as the backtracking pick noted in the Phase-1 file. The clean AC counts as a solve, but for genuine Trie ownership a problem that actually *needs* a trie (e.g. insert paths node-by-node, prune at a folder boundary) should be the rep that closes the bucket. Flagging so Trie doesn't get falsely marked owned.
