# Category checklists — quick reference

> [!info] Each problem type has known edge case traps. Before coding, identify the category and run its checklist.

---

## How to use

When you start a problem:

1. Identify the category (Array? Tree? Graph? DP?)
2. Open the corresponding row below
3. Mentally run through each edge case
4. Decide which apply to this specific problem
5. Write them into your scratch as test cases to verify

---

## Array

| Edge case | Smallest failing test | Why it fails |
|-----------|----------------------|--------------|
| Empty | `[]` | Loop never executes, accumulator returns init value |
| Single element | `[x]` | Pair operations have no pair |
| All same | `[5, 5, 5, 5]` | Difference logic returns 0, duplicate handling matters |
| All negative | `[-1, -2, -3]` | Max-tracking with 0 init breaks |
| All zero | `[0, 0, 0]` | Division, sign tracking edge |
| Max size | `n = 10^5` | Overflow risk in sums, TLE risk in O(n²) |
| Sorted ascending | `[1, 2, 3, 4]` | Binary search boundary, worst case for some algos |
| Sorted descending | `[4, 3, 2, 1]` | Same |
| Duplicates present | `[1, 1, 2, 2]` | Set-vs-Map confusion |
| Min and max value coexist | `[INT_MIN, INT_MAX]` | Subtraction overflow |

## String

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Empty | `""` | charAt(0) throws |
| Single char | `"x"` | Pair-of-chars logic breaks |
| All same char | `"aaaa"` | Group-counting edges |
| Length 2 | `"ab"`, `"aa"` | Smallest non-trivial size |
| Separator at start/end | `",abc"`, `"abc,"`, `",abc,"` | Empty-token edges |
| Consecutive separators | `"a,,b"` | Empty token between |
| Only separators | `",,,"` | No real content |
| Unicode | `"café"` | byte vs char vs code-point confusion |
| Whitespace boundary | `"  abc  "` | Trim behavior |
| Mixed case | `"AbC"` | Case-insensitive comparison hazard |

## Tree

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Null root | `null` | NPE on any access |
| Single node | one-node tree | Children-based logic breaks |
| Skewed left | linked-list-like leftward | Recursion stack depth, base cases |
| Skewed right | leftward | Same |
| Two-node (left only) | root + left child | Right-child null handling |
| Two-node (right only) | root + right child | Same |
| Balanced tree | full binary | Standard case |
| Single path tree | root → leaf | Single-child-only handling |
| Negative values | nodes with negative weights | Max-path-sum sign handling |

## Graph

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Empty graph | 0 nodes, 0 edges | Iteration vacuous |
| Single node | 1 node, no edges | Connected components edge |
| Disconnected | 2+ components | BFS/DFS must restart per component |
| Self-loops | node connected to itself | Visited handling |
| Parallel edges | multiple edges between same pair | Adjacency list / set / counter choice |
| Cycle | smallest cycle (triangle) | Cycle detection logic |
| DAG | no cycles | Topological sort applicability |
| Bidirectional vs unidirectional | check problem | Common confusion |
| Dense graph | n nodes, ~n² edges | O(n²) memory, TLE risk |
| Sparse graph | n nodes, ~n edges | Different algorithms preferred |

## DP

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Base case n=0 | empty input | dp[0] init matters |
| Base case n=1 | single element | dp[1] often differs from recurrence |
| Negative subproblem indices | dp[i-2] when i=0 | Need guard or padding |
| Overflow in transitions | very large n | sum/product accumulator type |
| Memo of MIN_VALUE / sentinel | not-yet-computed state | Distinguish "unvisited" from "valid 0" |
| Space-optimized rolling array | k-step transitions | Reusing arrays correctly |
| Restoration of decisions | back-tracking from final dp | Auxiliary array needed |

## Math / Number

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Zero | `0` | Division by zero, log(0), 0^0 |
| One | `1` | Trivial loop never executes |
| Negative | `-5` | Sign-dependent logic |
| Very large | `10^18` | Overflow even with long |
| Negative MOD result | `(a - b) % MOD` | Add MOD before final % |
| Math.abs(MIN_VALUE) | special case | Returns MIN_VALUE itself |
| Integer division truncation | `5 / 2 = 2` | Lost precision |
| Float comparison | `0.1 + 0.2 != 0.3` | Use epsilon or BigDecimal |
| Prime / composite | 1, 2 | Edge values for primality |
| Factorial / Fibonacci | n = 0, 1 | Off-by-one in base cases |

## Map / Set lookup

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Self-reference | nums[i] looks up itself | See [[02-self-reference-in-lookup]] |
| Duplicates in input | `[1, 1, 2]` | Frequency map vs set |
| Collision in hash | depends on values | Java HashMap usually safe |
| Custom object key | needs equals + hashCode | Always override both |
| Key absence vs null value | `map.get(k)` returns null | Use containsKey or getOrDefault |
| Mutating key after insertion | mutable key (List, array) | Map breaks silently |

## Sliding window

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Window size k > n | `nums = [1]`, `k = 5` | Loop never executes |
| Window size k = 0 | `k = 0` | Degenerate case, problem-specific |
| Window size k = n | `k = n` | Single iteration |
| Window of all same | `[5, 5, 5]`, `k = 2` | Duplicate handling in window |
| Shrink-to-empty | window where left = right + 1 | State after shrinking |
| First/last window | window at start, window at end | Index boundaries |

## Binary search

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Empty space | `nums = []` | Loop never enters |
| Target not present | search miss | Return -1, not last visited |
| Target at left boundary | `nums[0]` is target | Off-by-one on left |
| Target at right boundary | `nums[n-1]` is target | Off-by-one on right |
| Duplicates of target | find first vs last vs any | Logic differs |
| Monotonic predicate boundary | binary search on answer | "Just past true" vs "just before false" |
| Integer overflow in midpoint | `(left + right) / 2` | Use `left + (right - left) / 2` |

## Linked List

| Edge case | Smallest failing test | Why |
|-----------|----------------------|-----|
| Null head | `null` | NPE on any operation |
| Single node | one node | head == tail |
| Two nodes | smallest non-trivial | next-pointer manipulation |
| Cycle | tail.next = head | Floyd's algorithm domain |
| Modifying head | delete first | Dummy node simplifies |
| Modifying tail | delete last | Predecessor tracking |

---

## Template for using this

When you start a problem:

```
1. Read constraints (file 05)
2. Identify category — array? graph? string? DP?
3. Open this file, run through the category's row
4. Pick the 3-5 edge cases most relevant to your specific problem
5. Write them as comments above your code, e.g.:
   // EDGE CASES:
   //   1. n=1 → return nums[0]
   //   2. all duplicates → frequency map needed
   //   3. negative values → ensure long for sum
6. Code with those in mind from the start, not patched in after WA
```

---

## Related patterns

- [[05-constraint-reading-first]] — feeds into category identification
- [[06-adversarial-test-construction]] — for problem-specific edge cases not in this list
