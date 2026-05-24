tags = {
    3336: ["GCD_LCM","MOD_ARITH"],          # count subsequences equal GCD: DP over gcd values
    3276: ["BITMASK"],                       # select cells max score: bitmask DP per row digit
    3363: [],                                # max fruits collected in tree: tree DP
    2747: [],                                # count zero request servers: sliding window
    1388: ["GAME_THEORY"],                   # pizza 3n slices: circular pick non-adjacent, DP
    3605: [],                                # no content
    3553: [],                                # min weighted subgraph: Dijkstra multi-source
    3651: [],                                # min cost path teleportations: Dijkstra
    3337: ["MATRIX_EXP","MOD_ARITH"],        # total chars after transformations II: matrix exponentiation mod
    1928: [],                                # min cost reach destination in time: DP
    3317: ["PERM_COMB","MOD_ARITH"],         # ways for event: C(n,x)*C(m,y)*y^z mod — multinomial
    2518: ["PERM_COMB","MOD_ARITH"],         # number of great partitions: C(n,k) complement count mod
    2003: [],                                # smallest missing genetic value: union-find
    2493: [],                                # divide nodes max groups: BFS bipartite + graph
    2663: [],                                # lex smallest beautiful string: greedy increment
    1203: [],                                # sort items by groups: topological sort
    3609: [],                                # min moves reach target grid: BFS
    3704: ["PAIR_COUNT","MOD_ARITH"],        # count no-zero pairs sum to N: Euler's totient / count coprime pairs
    2572: ["PRIME","MOD_ARITH"],             # count square-free subsets: inclusion-exclusion over primes mod
    1987: ["MOD_ARITH"],                     # number of unique good subsequences: DP mod (like distinct subsequences II)
    1000: ["MOD_ARITH"],                     # min cost merge stones: interval DP
    3362: [],                                # zero array transformation III: greedy + heap
    2742: [],                                # painting the walls: DP partition
    2867: ["PRIME","GCD_LCM"],               # count valid paths tree: paths with exactly 1 prime — sieve + DFS
    3585: [],                                # weighted median node tree: tree DP
    1044: [],                                # longest duplicate substring: binary search + rolling hash
    1998: ["GCD_LCM","PRIME"],               # GCD sort of array: union-find via shared prime factors
    782:  ["TRICK","PARITY"],                # transform to chessboard: count mismatches in rows/columns
    2565: [],                                # subsequence min score: sliding window two pointers
    2552: ["TRIPLE_COUNT"],                  # count increasing quadruplets: prefix count of smaller on left + BIT
    903:  ["MOD_ARITH","PERM_COMB"],         # valid permutations DI sequence: DP on relative rank count
    3425: [],                                # longest special path: tree DFS
    3700: [],                                # zigzag arrays II: DP
    1872: ["GAME_THEORY","AP_SUM"],          # stone game VIII: suffix sum + greedy DP
    3426: ["GEOM","AP_SUM"],                 # Manhattan distances all arrangements: sum = C(n,2)*k*total_positions
    2968: [],                                # apply ops maximize freq score: sliding window
    2421: [],                                # number of good paths: union-find + sorted values
    2949: ["PALINDROME","MOD_ARITH"],        # count beautiful substrings II: vowel-consonant balance + palindrome condition mod
    3646: ["PALINDROME"],                    # next special palindrome number: next palindrome generation
    3404: ["TRIPLE_COUNT","MOD_ARITH"],      # count special subsequences: count (x,y,z) triples x<y<z with x|y, y|z
    2926: [],                                # max balanced subsequence sum: monotonic stack DP
    2127: [],                                # max employees invited to meeting: functional graph cycle
    2953: ["PALINDROME"],                    # count complete substrings: sliding window + palindrome check
    3288: [],                                # length longest increasing path: DAG LIS
    3352: ["BIT_OPS","DIGIT_OPS"],           # count K-reducible numbers < N: digit DP + popcount chain
    3636: [],                                # no content
    3134: ["GCD_LCM"],                       # find median uniqueness array: binary search on median, count pairs via GCD
    3655: ["XOR","MATRIX_EXP"],              # XOR after range multiplication: matrix exp on XOR-based recurrence
    2463: ["BITMASK"],                       # min total distance: bitmask DP assign robots to factories
    3327: ["PALINDROME","BITMASK"],          # check DFS strings palindromes: bitmask XOR of char counts on DFS path
    1900: ["TRICK"],                         # earliest/latest rounds players compete: simulate with symmetry + memoization
    1040: ["GEOM","TRICK"],                  # moving stones until consecutive II: sliding window on sorted stones
    1499: [],                                # max value equation: sliding window max (y + x maximized)
    1782: ["PAIR_COUNT"],                    # count pairs of nodes: sort + binary search + prefix sums
    3562: [],                                # max profit trading stocks with discounts: DP tree
    2440: ["DIVISORS","AP_SUM"],             # create components same value: divisors of total sum — check each
    3538: [],                                # merge operations min travel time: DP
    3615: ["PALINDROME"],                    # longest palindromic path in graph: bitmask char counts on path
    1994: ["PRIME","MOD_ARITH","BITMASK"],   # number of good subsets: each subset picks at most one of each prime, mod
    1703: ["TRICK","AP_SUM"],                # min adjacent swaps K consecutive ones: median + prefix sum of positions
    3691: [],                                # no content
    2286: [],                                # booking concert tickets: segment tree
    3283: ["BITMASK","GAME_THEORY"],         # max moves kill all pawns: bitmask DP (TSP-style), minimax
    3302: [],                                # lex smallest valid sequence: greedy + Z-function
    3470: ["PERM_COMB","MOD_ARITH"],         # permutations IV: count permutations alternating parity, no consecutive equal
    1622: ["MOD_ARITH","POWER"],             # fancy sequence: lazy segment tree with modular inverse for division
    3666: [],                                # min ops equalize binary string: greedy
    2117: ["PRIME","DIGIT_OPS","MOD_ARITH"], # abbreviating product of range: track trailing zeros + first/last k digits
    1803: ["XOR","BIT_OPS"],                 # count pairs XOR in range: trie-based range XOR count
    1330: ["TRICK"],                         # reverse subarray maximize value: consider cases — endpoints or interior flip
    2289: [],                                # steps to make array non-decreasing: monotonic stack
    1932: [],                                # merge BSTs: tree validation
    1916: ["PERM_COMB","MOD_ARITH"],         # count ways build rooms ant colony: subtree size product of C(n,k)
    2035: ["TRICK"],                         # partition array min sum diff: meet in the middle (n=30)
    3579: [],                                # min steps convert string: string DP
    3762: [],                                # no content
    2157: ["BIT_OPS"],                       # groups of strings: bitmask of letters, union-find on 1-bit toggles
    1735: ["DIVISORS","MOD_ARITH"],          # count ways make array with product: prime factorization + stars-and-bars
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
