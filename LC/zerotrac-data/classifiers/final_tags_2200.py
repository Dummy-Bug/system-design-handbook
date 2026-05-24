tags = {
    3129: ["MOD_ARITH"],                    # stable binary arrays: DP count mod
    3306: ["SUBARRAY_COUNT"],               # substrings every vowel+K consonants: sliding window
    847:  ["BITMASK"],                      # shortest path all nodes: BFS + bitmask state
    2045: [],                               # second min time: BFS
    3777: [],                               # min deletions alternating: string DP
    1453: ["GEOM"],                         # max darts in circle: O(n²) angular sweep geometry
    3714: ["PARITY"],                       # longest balanced substring II: parity of 0s and 1s
    1246: ["PALINDROME"],                   # palindrome removal: interval DP cost
    2781: [],                               # longest valid substring: sliding window
    879:  ["MOD_ARITH"],                    # profitable schemes: 2D knapsack count mod
    1157: [],                               # online majority element: Boyer-Moore + binary search
    3495: ["BIT_OPS"],                      # min ops make elements zero: bit-level zeroing strategy
    2835: ["BIT_OPS"],                      # min ops form subsequence target sum: greedy bit assignment
    1649: ["PAIR_COUNT"],                   # create sorted array: BIT/merge-sort for inversion count
    1568: ["TRICK"],                        # min days disconnect island: answer is always 0, 1, or 2
    3748: [],                               # no content
    2876: [],                               # count visited nodes directed graph: functional graph cycle
    2081: ["PALINDROME"],                   # sum k-mirror numbers: palindromes in both base 10 and base k
    992:  ["SUBARRAY_COUNT"],              # subarrays K different integers: sliding window trick
    1889: ["AP_SUM"],                       # min space wasted packaging: binary search + sum formula per batch
    3102: ["GEOM","TRICK"],                 # minimize Manhattan distances: rotate 45° → Chebyshev distance
    2025: ["CONTRIBUTION"],                 # max ways to partition array: prefix sum contribution per element
    2167: [],                               # min time remove cars: DP
    2223: [],                               # sum scores built strings: Z-function
    3458: [],                               # select K disjoint special substrings: string DP
    2543: ["GCD_LCM","POWER"],              # check if point reachable: reachable iff GCD(tx,ty) is power of 2
    1627: ["GCD_LCM"],                      # graph connectivity threshold: connect i,j if GCD(i,j) > threshold
    1542: ["BITMASK","PALINDROME"],         # longest awesome substring: bitmask of odd-count digits = palindrome
    2561: ["TRICK"],                        # rearranging fruits: always swap using global minimum cost element
    2276: [],                               # count integers in intervals: interval union data structure
    3677: ["PALINDROME","BIT_OPS"],         # count binary palindromic numbers: binary palindromes via construction
    2484: ["PALINDROME","MOD_ARITH"],       # count palindromic subsequences: DP for length-5 palindromes, mod
    2163: ["AP_SUM"],                       # min diff in sums after removal: prefix k-min + suffix k-max heaps
    2930: ["MOD_ARITH"],                    # strings rearranged to contain substring: inclusion-exclusion DP mod
    2581: ["CONTRIBUTION"],                 # possible root nodes: rerooting contribution
    3878: ["SUBARRAY_COUNT"],              # count good subarrays: sliding window count
    1012: ["DIGIT_OPS"],                    # numbers with repeated digits: digit DP complement
    3041: [],                               # maximize consecutive after modification: greedy
    1766: ["GCD_LCM"],                      # tree of coprimes: find ancestor with GCD=1 via precomputed sets
    3307: ["BIT_OPS"],                      # K-th char in string game II: trace back via bit decomposition of k
    3670: ["BIT_OPS"],                      # max product two ints no common bits: AND=0 constraint, enumerate
    1178: ["BITMASK"],                      # valid words for each puzzle: word → bitmask, check subset + first letter
    1915: ["BITMASK"],                      # wonderful substrings: bitmask for odd-count letters, XOR prefix
    3772: [],                               # no content
    3589: ["PRIME"],                        # prime-gap balanced subarrays: sieve + gap tracking
    3715: ["POWER"],                        # sum of perfect square ancestors: identify perfect squares via sqrt
    2528: [],                               # maximize min powered city: binary search + sliding window
    850:  ["GEOM"],                         # rectangle area II: coordinate compress + sweep line
    2646: [],                               # minimize price of trips: tree DP
    2732: ["BIT_OPS"],                      # find good subset of matrix: find two rows whose OR complement covers all
    1240: ["BITMASK"],                      # tiling rectangle fewest squares: bitmask DP on row states
    3082: ["MOD_ARITH"],                    # sum of power of all subsequences: contribution DP mod
    3419: [],                               # minimize max edge weight: binary search + graph
    3548: ["CONTRIBUTION"],                 # equal sum grid partition II: prefix sum equality via contribution
    2183: ["PAIR_COUNT","MOD_ARITH","GCD_LCM"], # pairs divisible by K: count GCD-based pairs, mod
    3519: ["DIGIT_OPS"],                    # count numbers non-decreasing digits: digit DP
    960:  [],                               # delete columns sorted III: DP
    3729: ["MOD_ARITH"],                    # distinct subarrays divisible by K sorted: divisibility count
    1307: ["BITMASK","PERM_COMB"],          # verbal arithmetic puzzle: assign digits via bitmask + backtrack
    1199: [],                               # min time build blocks: Huffman-like merge DP
    1125: ["BITMASK"],                      # smallest sufficient team: bitmask DP over skill coverage
    3869: ["DIGIT_OPS"],                    # count fancy numbers: digit DP
    3533: ["BITMASK","MOD_ARITH"],          # concatenated divisibility: bitmask DP, permutation mod check
    3574: ["GCD_LCM"],                      # maximize subarray GCD score: GCD of subarray × length
    3007: ["BIT_OPS","DIGIT_OPS"],          # max number sum of prices ≤ K: digit DP on set-bit positions
    864:  ["BITMASK"],                      # shortest path all keys: BFS + bitmask of collected keys
    3806: ["BIT_OPS"],                      # max bitwise AND after increment: bit manipulation
    857:  ["TRICK","AP_SUM"],               # min cost hire K workers: fix ratio worker, sort, sliding window sum
    1997: ["MOD_ARITH"],                    # first day in all rooms: DP with prefix sum mod
    3256: [],                               # max value sum placing three rooks: 3-row selection with column constraints
    3048: [],                               # earliest second to mark indices: binary search + greedy
    3920: [],                               # maximize fixed points after deletions: DP
    2141: ["AP_SUM","TRICK"],               # max running time N computers: binary search, total/N = threshold
    3203: [],                               # min diameter after merging trees: tree diameter
    3193: ["MOD_ARITH"],                    # count inversions: DP count mod
    3068: ["XOR"],                          # max sum node values: XOR pairs — parity of XOR operations used
    3244: [],                               # shortest distance road queries II: BFS
    952:  ["GCD_LCM","PRIME"],              # largest component size common factor: union-find via prime factorization
    2179: ["TRIPLE_COUNT"],                 # count good triplets: BIT/merge-sort count triplets in relative order
    1434: ["BITMASK"],                      # ways to wear different hats: bitmask DP, hats assigned to people
    753:  ["TRICK"],                        # cracking the safe: de Bruijn sequence — greedy Hierholzer
    3473: [],                               # sum K subarrays: DP
    1606: [],                               # servers handled most requests: sorted set simulation
    1498: ["PERM_COMB","POWER","MOD_ARITH"],# subsequences satisfying sum: sort + binary search + 2^count
    2973: ["DIVISORS"],                     # coins in tree nodes: sort children, product of top-3 subtree sizes
    749:  [],                               # contain virus: simulation
    2029: ["GAME_THEORY"],                  # Stone Game IX: count multiples of 3, optimal play
    3640: [],                               # no content
    2763: ["CONTRIBUTION"],                 # sum imbalance numbers: each (i,j) pair contributes to subarrays
    3031: [],                               # revert word to initial: string hashing/Z-function
    2407: [],                               # LIS II: segment tree
    3892: [],                               # no content
    2659: ["PAIR_COUNT"],                   # make array empty: count inversions-style, elements out of order
    1723: ["BITMASK"],                      # min time finish all jobs: bitmask DP partition work
    1851: [],                               # min interval include each query: binary search + heap
    3463: ["MOD_ARITH","PERM_COMB"],        # digits equal after operations II: C(n,k) mod prime via Lucas
    3915: [],                               # max sum alternating subsequence: DP
    1569: ["MOD_ARITH","PERM_COMB"],        # reorder array same BST: C(L+R,L) * dp[left] * dp[right]
    3485: [],                               # longest common prefix after removal: trie
    1591: [],                               # strange printer II: topological sort
    2862: ["POWER","DIVISORS"],             # max element-sum complete subset: i,j are "complete" if i/j is perfect square
    761:  ["TRICK"],                        # special binary string: recursive sort and join matching pairs
    932:  ["TRICK"],                        # beautiful array: divide and conquer on odd/even split
    2858: ["CONTRIBUTION"],                 # min edge reversals all nodes reachable: rerooting contribution
    3753: ["DIGIT_OPS"],                    # total waviness in range: digit DP on waviness = sum |d[i]-d[i+1]|
    1263: [],                               # min moves box to target: BFS
    2458: [],                               # height binary tree after removal: tree DP
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
