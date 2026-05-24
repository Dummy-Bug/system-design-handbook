tags = {
    1697: [],                               # offline + union-find (edge limited paths)
    3600: [],                               # spanning tree stability: graph
    3398: [],                               # string manipulation
    2897: ["BIT_OPS"],                      # maximize sum squares: XOR adjacent allows redistributing bits freely
    3859: ["SUBARRAY_COUNT"],               # subarrays K distinct integers: sliding window
    2513: ["GCD_LCM","MOD_ARITH"],          # minimize max two arrays: binary search, count via LCM exclusion
    3455: [],                               # shortest matching substring: string matching
    2242: [],                               # max score node sequence: graph top-3 neighbor tracking
    2306: ["BIT_OPS"],                      # naming company: track suffix-letter bitmask intersections
    862:  [],                               # shortest subarray sum ≥ K: monotonic deque
    1655: ["BITMASK"],                      # distribute repeating integers: bitmask DP partition groups
    1617: ["BITMASK"],                      # count subtrees max distance: enumerate all 2^n subsets
    3405: ["PERM_COMB","MOD_ARITH"],        # arrays with K matching adjacent: C(n-1,k) * m * (m-1)^(n-k-1)
    1959: [],                               # min space wasted K resizing: DP
    3515: [],                               # shortest path weighted tree: tree DP/LCA
    1857: [],                               # largest color value directed graph: DAG DP
    2188: [],                               # min time finish race: tire DP
    1187: [],                               # make array strictly increasing: DP + binary search
    3251: ["PERM_COMB","MOD_ARITH"],        # count monotonic pairs II: DP counting, stars-and-bars style
    2827: ["DIGIT_OPS","MOD_ARITH"],        # beautiful integers in range: digit DP, divisible by k + digit constraint
    2940: [],                               # find building Alice Bob meet: monotonic stack + binary search
    3045: [],                               # count prefix suffix pairs II: string hashing
    882:  [],                               # reachable nodes subdivided: Dijkstra
    3734: ["PALINDROME"],                   # lex smallest palindromic permutation > target: next permutation on palindrome
    3621: ["BIT_OPS","DIGIT_OPS"],          # integers popcount-depth K I: trace popcount chain via bits
    1585: [],                               # string transformable: greedy
    1866: ["MOD_ARITH","PERM_COMB"],        # rearrange sticks K visible: Stirling numbers of first kind mod
    1674: ["CONTRIBUTION"],                 # min moves complementary: difference array contribution per pair
    3444: ["GCD_LCM"],                      # min increments for target multiples: LCM-based feasibility
    1505: ["DIGIT_OPS","PAIR_COUNT"],       # min integer after K adjacent swaps on digits: greedy + BIT for swap count
    810:  ["GAME_THEORY","XOR"],            # chalkboard XOR game: current XOR=0 → current player wins
    3547: [],                               # max sum edge values: graph matching
    2478: ["MOD_ARITH","PRIME"],            # beautiful partitions: partition starts with prime, DP count mod
    3826: [],                               # no content
    1611: ["BIT_OPS","TRICK"],              # min one-bit ops to zero: Gray code — f(n) = n XOR (n>>1) XOR ...
    2258: [],                               # escape spreading fire: binary search + BFS
    3845: ["XOR"],                          # max subarray XOR bounded range: linear basis (Gaussian elim for XOR)
    1096: [],                               # brace expansion II: set parsing
    2935: ["XOR"],                          # max strong pair XOR II: sliding window trie for XOR maximization
    837:  ["PROB"],                         # new 21 game: probability DP, converges for large N
    2920: ["BIT_OPS"],                      # max points collecting coins: bit-shift trick — values halved at most 14 times
    1713: [],                               # min ops make subsequence: LCS → LIS via unique values
    2999: ["DIGIT_OPS"],                    # count powerful integers: digit DP with fixed suffix constraint
    3530: ["BITMASK"],                      # max profit valid topological order in DAG: bitmask DP
    2719: ["DIGIT_OPS","MOD_ARITH"],        # count of integers: digit DP with digit sum in range
    1467: ["PROB","PERM_COMB"],             # probability two boxes same distinct balls: DP probability with C(n,k)
    1707: ["XOR"],                          # max XOR with element from array: offline queries + trie
    3575: ["BITMASK","MOD_ARITH"],          # max good subtree score: DP tracking which digits used (bitmask)
    1520: [],                               # max non-overlapping substrings: greedy
    2312: [],                               # selling pieces of wood: DP interval splitting
    1755: ["TRICK"],                        # closest subsequence sum: meet in the middle — enumerate half subsets
    2203: [],                               # min weighted subgraph: Dijkstra
    2132: ["CONTRIBUTION"],                 # stamping the grid: difference array 2D stamps
    3388: [],                               # count beautiful splits: Z-function / string DP
    3177: [],                               # max length good subsequence II: DP
    1183: ["AP_SUM"],                       # max number of ones: formula — floor(M/B)² * floor(M/B+1)² per block
    2801: ["DIGIT_OPS"],                    # count stepping numbers in range: digit DP
    2556: ["TRICK"],                        # disconnect path binary matrix: two independent DFS cannot both exist
    3260: ["PALINDROME","MOD_ARITH"],       # largest palindrome divisible by K: construct palindrome mod K
    3413: ["AP_SUM"],                       # max coins K consecutive bags: sliding window prefix sums
    1840: ["TRICK"],                        # max building height: constraint propagation on height limits
    3518: ["PALINDROME","PERM_COMB"],       # smallest palindromic rearrangement II: count valid palindromes lex
    3797: ["MOD_ARITH"],                    # count routes climb grid: DP path count mod
    3399: [],                               # smallest substring identical II: string
    3816: [],                               # lex smallest after delete duplicates: monotonic stack
    887:  ["AP_SUM","TRICK"],               # super egg drop: reframe — with t trials k eggs, max floors = Σ C(t,i)
    854:  [],                               # K-similar strings: BFS
    3680: [],                               # no content
    757:  [],                               # set intersection size ≥ 2: greedy interval cover
    2589: [],                               # min time complete tasks: greedy
    2334: [],                               # subarray elements > varying threshold: monotonic stack
    956:  [],                               # tallest billboard: DP equal-sum partition
    2468: ["DIGIT_OPS","AP_SUM"],           # split message based on limit: binary search on parts, digit length formula
    2577: ["PARITY"],                       # min time visit cell: Dijkstra + parity check on arrival time
    3272: ["DIGIT_OPS","PERM_COMB"],        # count good integers: enumerate palindromes, count unique permutations
    1521: ["BIT_OPS"],                      # mysterious function closest to target: AND monotone, ≤20 distinct values
    3841: ["PALINDROME","BITMASK"],         # palindromic path queries tree: bitmask parity of char counts on path
    1349: ["BITMASK"],                      # max students taking exam: bitmask DP row by row
    3448: ["MOD_ARITH"],                    # count substrings divisible by last digit: prefix mod grouping
    2713: [],                               # max strictly increasing cells: DP sorted values
    3116: ["GCD_LCM","PERM_COMB","MOD_ARITH"], # kth smallest amount: binary search + inclusion-exclusion via LCM
    1681: ["BITMASK"],                      # minimum incompatibility: bitmask DP partition into groups
    2322: ["BITMASK","XOR"],                # min score after removals tree: bitmask enumerate pairs + XOR tracking
    818:  [],                               # race car: BFS/DP with direction state
    2172: ["BITMASK"],                      # max AND sum of array: bitmask DP — assign values to slots
    1825: [],                               # finding MK average: ordered data structure
    808:  ["PROB"],                         # soup servings: probability DP, converges to 1 for large N
    2818: ["PRIME","CONTRIBUTION","MOD_ARITH"], # maximize score: prime score via sieve, monotonic stack contribution
    3504: ["PALINDROME"],                   # longest palindrome after concatenation: palindrome DP
    2569: [],                               # handling sum queries: segment tree
    2538: ["CONTRIBUTION"],                 # diff max min price sum: rerooting — each path contributes its max - min
    3801: [],                               # no content
    920:  ["MOD_ARITH"],                    # number of music playlists: DP count mod
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
