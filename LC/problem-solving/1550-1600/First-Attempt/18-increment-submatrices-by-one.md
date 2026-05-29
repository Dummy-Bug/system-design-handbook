### #18 — Increment Submatrices by One
**Link:** https://leetcode.com/problems/increment-submatrices-by-one/
**Date attempted:** 2026-05-27 ~18:15
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 40 min (21 min approach + 19 min coding) — first-submission AC ✓
**Pattern:** Difference array (2D)

---

**Verbatim thinking:**

- previously solved Jan 2025, must re-derive from scratch
- this is 2D difference array — extension of 1D difference array to matrices
- brute force q.length * n would pass constraints but not challenging enough
- for 1D: +1 at start, -1 at end+1, then prefix sum
- for 2D: place four corners — +1 at (topRow, topCol), -1 at (topRow, bottomCol+1), -1 at (bottomRow+1, topCol), +1 at (bottomRow+1, bottomCol+1)
- traced on n=5, upper (1,3) bottom (3,3) to verify
- then two sweeps: row-wise prefix sum, then column-wise prefix sum (order doesn't matter — both produce same result)
- boundary check: if bottomCol+1 or bottomRow+1 == n, skip that placement (out of bounds)

**Insight:**
2D difference array is the natural extension of 1D. In 1D you place +1 at start and -1 at end+1. In 2D you place four corners: +1 at top-left, -1 at top-right+1, -1 at bottom-left+1, +1 at bottom-right+1 (inclusion-exclusion). Then two prefix sum sweeps (row-wise + column-wise, order independent) reconstruct the full matrix.

**Key gotcha:**
Boundary checks — if bottomRow+1 or bottomCol+1 equals n, don't place the -1/+1 markers there (out of bounds). The `if != n` guards handle this.

**Complexity:**
O(n² + q) time, O(n²) space.

**Solution code:**

```java
class Solution {
    public int[][] rangeAddQueries(int n, int[][] queries) {

        int [][] matrix = new int[n][n];
        
        for (int[] query : queries){

            int topRow = query[0];
            int topCol = query[1];
            int bottomRow = query[2];
            int bottomCol = query[3];

            matrix[topRow][topCol] += 1;

            if (bottomCol + 1 != n){
                matrix[topRow][bottomCol + 1] -= 1;

            }
            if (bottomRow + 1 != n){
                matrix[bottomRow + 1][topCol] -= 1;
            }

            if (bottomRow + 1 != n && bottomCol + 1 != n){
                matrix[bottomRow + 1][bottomCol + 1] += 1;
            }
        }

        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){

                if (j == 0){
                    continue;
                }
                matrix[i][j] = matrix[i][j] + matrix[i][j-1] ;
            }
        }

        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){

                if (i == 0){
                    continue;
                }

                matrix[i][j] = matrix[i][j] + matrix[i-1][j];
            }
        }
        return matrix;
    }
}
```
