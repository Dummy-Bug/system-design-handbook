# 30 — Count Collisions on a Road (re-solve)

- **Link:** https://leetcode.com/problems/count-collisions-on-a-road/ (LC 2211, rating 1581, AR 58.1%)
- **Format:** single timed problem, old re-solve under the 2026-11-22 format (15-minute target, 30-minute cap). First attempt: `First-Attempt/30-count-collisions-on-a-road.md`, 2026-06-01.
- **Bucket:** simulation, reduced to two counting passes; LeetCode also tags it stack.
- **Timer:** 2026-11-22, 20:43.
- **AC:** about 21:04, 21 minutes.
- **Result:** clean first-submission AC, self-derived. The only exchange during the solve was a yes or no correctness check on the idea. Counts toward coverage, since no unseen simulation problem is left in 1550-1599: simulation 1 of 1.

| Attempt       | Time         | WAs | Help      | Approach                                                |
| ------------- | ------------ | --: | --------- | ------------------------------------------------------- |
| 1, 2026-06-01 | about 62 min |   3 | editorial | simulate the cars: next-L/S/R arrays, last-seen indexes |
| 2, 2026-11-22 | about 21 min |   0 | none      | two counting passes, one for L and one for R            |

## The problem

A string of `L`, `R` and `S` gives each car's direction on a line, all at the same speed. `R` meeting `L` adds 2 collisions; a moving car hitting a stationary one adds 1; after a collision the cars stay where they are. Return the total number of collisions.

## How it was solved, in order

1. Started down the June route: prefix and suffix arrays for S, L and R.
2. Could not make it concrete; the cases kept multiplying.
3. Took that as the sign that something simpler had to exist, and stepped back before writing any code.
4. Thought of two passes. Pass 1: only the `L` cars move, so `R` and `S` both behave like `S`, because the collision happens whether or not `R` and `L` move together; each car to the left counts 1, and once there is a first collision, every `L` to its right adds one. Pass 2: the same for `R`, from the other end. Checked it gave the same answers as the examples.

Step 3 is the difference from June. In June the simulation route was followed through three WAs; this time the explosion of cases was read as a signal and the route was dropped before it became code.

## AC code

```java
class Solution {
    public int countCollisions(String directions) {
        
        int n = directions.length();

        int count = 0;
        int ans = 0;

        for (int i = n - 1; i >= 0; i--){
            if (directions.charAt(i) == 'L'){
                count++;
                continue;
            }
            ans = ans + count;
            count = 0;
        }
        count = 0;

        for (int i = 0; i < n; i++){

            if (directions.charAt(i) == 'R'){
                count++;
                continue;
            }
            ans = ans + count;
            count = 0;
        }
        return ans;
    }
}
```

Run: 5 and 0 on the two examples, and the same output as a step-by-step simulation of the road on 200,000 random inputs.

## The June editorial, as an aside

The June log resolved it with one formula: every car that stops adds 1, so the answer is the number of `L` and `R` cars minus the leading run of `L` and the trailing run of `R`, which escape off the ends.

```java
int i = 0, j = n - 1;
while (i < n && s.charAt(i) == 'L') i++;
while (j >= 0 && s.charAt(j) == 'R') j--;
int count = 0;
for (int k = i; k <= j; k++) if (s.charAt(k) != 'S') count++;
```

It counts the same thing as the two passes: pass 1 adds every `L` except the leading run, pass 2 every `R` except the trailing run. On `LLRSLR` all three (the two passes, the formula, the simulation) give 2, and the two passes and the formula agree on 200,000 random inputs. The user chose not to learn this form; the two passes are the owned solution.
