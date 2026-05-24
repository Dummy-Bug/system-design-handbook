tags = {
    3409: [],                                  # longest subseq decreasing adj diff: DP
    3490: ["DIGIT_OPS","MOD_ARITH"],           # count beautiful numbers: digit DP
    1938: ["XOR"],                             # max genetic diff query: offline trie XOR
    3534: [],                                  # path existence queries: graph reachability
    2846: ["GCD_LCM"],                         # min edge weight equilibrium queries: LCA + GCD tracking on path
    3266: ["MATRIX_EXP","MOD_ARITH"],          # final array state K multiplications: matrix exp mod
    3303: [],                                  # first almost equal substring: Z-function + DP
    3161: [],                                  # block placement queries: segment tree / binary search
    2272: ["TRICK"],                           # substring largest variance: max (count_a - count_b) subarray — Kadane variant
    2040: [],                                  # kth smallest product two sorted arrays: binary search
    3757: ["MOD_ARITH"],                       # number effective subsequences: DP mod
    3241: [],                                  # time to mark all nodes: tree DP
    3661: [],                                  # max walls destroyed: geometry / sorting
    1632: [],                                  # rank transform matrix: union-find + sorting
    3459: [],                                  # longest V-shaped diagonal segment: DP
    1776: [],                                  # car fleet II: monotonic stack
    1896: [],                                  # min cost change expression: DP
    3378: ["GCD_LCM","PRIME"],                 # connected components LCM graph: union-find via prime factorization
    3312: ["GCD_LCM","DIVISORS"],              # sorted GCD pair queries: count pairs with GCD=g via Euler/Mobius
    2736: [],                                  # max sum queries: monotonic stack + segment tree
    1675: [],                                  # minimize deviation: heapify + greedy
    1948: [],                                  # delete duplicate folders: trie + hashing
    1595: ["BITMASK","MOD_ARITH"],             # min cost connect two groups: bitmask DP
    3505: [],                                  # min ops make elements within K subarrays equal: sliding window
    1819: ["GCD_LCM","PRIME"],                 # number different subsequences GCDs: for each g, check if any subsequence has GCD g
    3013: [],                                  # divide array min cost II: sliding window
    3197: ["GEOM"],                            # min area cover all ones II: try all rectangle orientations
    3901: [],                                  # no content
    3544: [],                                  # subtree inversion sum: tree DP
    3267: [],                                  # count almost equal pairs II: digit manipulation
    3287: ["BITMASK"],                         # find max sequence value: bitmask DP of OR values left/right
    3098: [],                                  # sum subsequence powers: DP
    3257: [],                                  # max value sum three rooks II: 3-row enumeration
    3077: [],                                  # max strength K disjoint subarrays: DP + prefix
    3234: [],                                  # count substrings dominant ones: sliding window / enumeration
    2014: ["PERM_COMB"],                       # longest subseq repeated k times: enumerate subsequences by frequency
    1815: ["BITMASK","MOD_ARITH"],             # max groups fresh donuts: bitmask DP on remainder classes
    2234: [],                                  # max total beauty gardens: binary search + greedy
    2030: [],                                  # smallest K-length subseq with occurrences: monotonic stack
    913:  ["GAME_THEORY"],                     # cat and mouse: BFS game DP
    3500: [],                                  # min cost divide array into subarrays: DP
    1489: [],                                  # critical edges MST: bridge finding
    1531: [],                                  # string compression II: DP
    2617: [],                                  # min visited cells grid: BFS + segment tree
    2813: ["TRICK","CONTRIBUTION"],            # max elegance K-length subseq: greedy swap — distinct categories contribute bonus
    936:  ["TRICK"],                           # stamping the sequence: reverse simulate stamps
    2019: ["MOD_ARITH","BITMASK"],             # score students solving math expression: DP with expression parsing, mod
    3563: [],                                  # lex smallest after adjacent removals: stack + DP
    1883: [],                                  # min skips arrive on time: DP
    2532: [],                                  # time cross bridge: simulation heap
    964:  ["TRICK","MOD_ARITH"],               # least operators to express number: base-k representation — greedy cost via digit analysis
    3321: [],                                  # X-sum K-long subarrays II: sliding window + ordered set
    3367: [],                                  # maximize sum weights edge removals: tree DP
    3594: ["BITMASK"],                         # min time transport individuals: bitmask DP states
    3474: [],                                  # lex smallest generated string: Z-function + greedy
    2911: ["PALINDROME","MOD_ARITH"],          # min changes K semi-palindromes: DP with palindrome costs
    3510: [],                                  # min pair removal to sort II: linked list simulation
    1687: [],                                  # deliver boxes storage to ports: DP + deque
    2056: ["BITMASK"],                         # valid move combinations chessboard: bitmask over piece positions
    3343: ["PERM_COMB","PRIME","MOD_ARITH"],   # count balanced permutations: digit sum split, C(n,k) over prime factorization
    2338: ["PERM_COMB","DIVISORS","MOD_ARITH"],# count ideal arrays: each value's divisor chain × C(n+k-1,k-1)
    2790: [],                                  # max groups increasing length: greedy binary search
    1830: ["PERM_COMB","MOD_ARITH"],           # min ops string sorted: count inversions × C(n,k) contribution mod
    2281: ["CONTRIBUTION","MOD_ARITH"],        # sum total strength wizards: monotonic stack contribution mod
    3333: [],                                  # find original typed string II: sliding window DP
    2213: [],                                  # longest substring one repeating char: segment tree
    2499: [],                                  # min total cost make arrays unequal: greedy frequency
    1787: ["XOR","BITMASK"],                   # make XOR all segments zero: DP with XOR bitmask over prefix
    3149: ["BITMASK"],                         # min cost array permutation: bitmask DP + greedy
    3625: ["GEOM","TRIPLE_COUNT"],             # count trapezoids II: collinear point count × pair choosing
    3525: ["MOD_ARITH"],                       # find X value array II: DP tracking prefix product mod
    2954: ["PERM_COMB","PRIME","MOD_ARITH"],   # count infection sequences: multinomial over prime-gapped segments
    3430: ["CONTRIBUTION"],                    # max and min sums K subarrays: monotonic stack contribution
    3590: ["XOR"],                             # kth smallest path XOR sum: linear basis on path XORs
    3671: ["MOD_ARITH"],                       # sum beautiful subsequences: DP mod
    2386: ["TRICK"],                           # find K-sum array: max sum + sorted differences — binary heap on complement
    2071: [],                                  # max tasks assign: binary search + greedy
    2097: [],                                  # valid arrangement pairs: Eulerian path
    1659: ["BITMASK"],                         # maximize grid happiness: bitmask DP over row states
    3261: [],                                  # count substrings K-constraint II: sliding window
    1923: [],                                  # longest common subpath: binary search + hashing
    3292: [],                                  # min valid strings form target II: DP + automaton
    3311: [],                                  # construct 2D grid matching graph: graph layout
    3139: ["TRICK","AP_SUM"],                  # min cost equalize array: max must become target; cost formula depends on parity
    1397: ["BITMASK","MOD_ARITH"],             # find all good strings: digit DP with KMP automaton bitmask
    3454: ["GEOM"],                            # separate squares II: line sweep on areas
    3086: ["CONTRIBUTION","AP_SUM"],           # min moves pick K ones: median + prefix sum, contribution per window
    2791: ["PALINDROME","BITMASK"],            # count paths palindrome in tree: bitmask XOR on tree path
    2573: [],                                  # find string with LCP: trie/union-find
    3181: ["BITMASK","MOD_ARITH"],             # max total reward operations II: bitmask DP size up to 2×max_value
    1960: ["PALINDROME"],                      # max product two palindromic substrings: Manacher + segment tree
    3277: ["XOR"],                             # max XOR score subarray queries: offline DP with XOR basis
    3445: [],                                  # max diff even/odd freq II: sliding window char constraint
    3539: ["MOD_ARITH","PERM_COMB"],           # sum array product magical sequences: DP mod counting
    2977: [],                                  # min cost convert string II: Dijkstra groups
    3569: ["PRIME"],                           # maximize distinct primes after split: sieve + greedy
    3165: [],                                  # max sum subseq non-adjacent: segment tree DP
    3509: [],                                  # max product alternating sum: DP
    3017: ["CONTRIBUTION","GCD_LCM"],          # count houses distance II: contribution on circular distances
    2603: [],                                  # collect coins tree: tree DP
    3382: ["GEOM"],                            # max area rectangle point constraints II: sweep line + BIT
    3414: [],                                  # max score non-overlapping intervals: DP
    3721: [],                                  # longest balanced subarray II: DP
    3117: [],                                  # min sum values dividing array: DP + AND monotone
    3630: ["XOR","BIT_OPS"],                   # partition array max XOR and AND: XOR properties
    3449: [],                                  # maximize min game score: binary search
    2902: ["STARS_BARS","GCD_LCM","MOD_ARITH"],# count sub-multisets bounded sum: generating function / GCD of frequencies
    3480: [],                                  # maximize subarrays after removing conflicting pair: segment tree
    3441: [],                                  # min cost good caption: DP
    803:  [],                                  # bricks falling: union-find reverse
    2836: ["MATRIX_EXP","MOD_ARITH"],          # max value function ball passing: matrix exp (cycle detection + power)
    2983: ["PALINDROME","BITMASK"],            # palindrome rearrangement queries: bitmask char counts + LCP
    3395: ["PERM_COMB","MOD_ARITH"],           # subsequences unique middle mode: counting with Σ C(n,k) formula
    2060: [],                                  # original string given two encoded: DP
    3464: ["GEOM"],                            # maximize distance points on square: geometry greedy
    2916: ["CONTRIBUTION","MOD_ARITH"],        # subarrays distinct element sum squares II: contribution of each element
    1977: ["PERM_COMB","MOD_ARITH"],           # ways to separate numbers: DP with string comparison, Catalan-adjacent
    2612: [],                                  # minimum reverse operations: BFS + ordered set
    3130: ["MOD_ARITH"],                       # find all stable binary arrays II: DP mod (harder variant)
    3410: [],                                  # maximize subarray sum after removing: segment tree
    1728: ["GAME_THEORY"],                     # cat and mouse II: game DP
    3420: [],                                  # count non-decreasing subarrays: deque + segment tree
    2851: ["MATRIX_EXP","MOD_ARITH"],          # string transformation: matrix exp on letter transition counts
    3145: ["BIT_OPS","DIGIT_OPS","MOD_ARITH"], # find products big array: bit manipulation + prefix products mod
    770:  [],                                  # basic calculator IV: polynomial expression parsing
    1982: [],                                  # find array given subset sums: divide and conquer
    2699: [],                                  # modify graph edge weights: Dijkstra
    3022: ["BIT_OPS"],                         # minimize OR remaining: greedy bit manipulation
    3486: [],                                  # longest special path II: tree DFS
    3389: [],                                  # min ops character frequencies equal: DP
    3501: [],                                  # maximize active section with trade II: segment tree
    2945: [],                                  # find max non-decreasing array length: DP + deque
    2809: [],                                  # min time make array sum ≤ x: DP
    1719: [],                                  # ways to reconstruct tree: LCA graph
    3225: [],                                  # max score grid operations: DP
    3435: ["PERM_COMB","BITMASK"],             # frequencies of shortest superstrings: bitmask over string overlaps
    3003: ["BITMASK","MOD_ARITH"],             # max partitions after operations: bitmask DP over distinct char mask
    3357: [],                                  # minimize max adjacent diff: binary search + greedy
    3348: ["PRIME","DIVISORS"],                # smallest divisible digit product II: find number whose digit product divisible by n
    3049: [],                                  # earliest second mark indices II: binary search + greedy
    3245: [],                                  # alternating groups III: segment tree
    3743: [],                                  # maximize cyclic partition score: DP
    3235: ["GEOM"],                            # rectangle corner reachable: geometry / graph coloring
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
