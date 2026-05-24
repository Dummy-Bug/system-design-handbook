tags = {
    911:  [],                               # binary search on timestamps
    1686: ["GAME_THEORY"],                  # Stone Game VI: sort by a+b, take greedily
    2328: [],                               # increasing paths in grid DP
    2850: [],                               # BFS on 3x3 grid states
    2092: [],                               # union-find (secret spread)
    1927: ["GAME_THEORY", "AP_SUM"],        # Sum Game: digit sum constraint with average argument
    1761: [],                               # minimum degree trio (graph counting)
    2448: ["AP_SUM"],                       # min cost make array equal: cost formula = weighted prefix sums
    1888: [],                               # flips for alternating string (deque rotation trick, more algorithmic)
    3811: ["XOR", "MOD_ARITH"],             # alternating XOR partitions
    3524: ["MOD_ARITH"],                    # Find X value of array: product mod constraints
    1223: [],                               # dice roll simulation DP
    1981: [],                               # minimize target-chosen diff: knapsack DP
    880:  ["TRICK"],                        # decoded string at index: work backwards with mod (string length)
    3614: [],                               # string simulation
    2333: [],                               # min sum squared diff: sort + greedy (no dominant math reflex)
    1102: [],                               # path max-min BFS/binary search
    2477: ["TRICK"],                        # min fuel: ceil(subtree_size / seats) — tree grouping insight
    3273: [],                               # min damage: greedy sort by ratio
    2472: ["PALINDROME"],                   # max non-overlapping palindrome substrings
    1105: [],                               # filling bookcase DP
    1354: ["TRICK", "MOD_ARITH"],           # construct target: work backwards from max, subtract mod
    1353: [],                               # max events greedy heap
    3008: [],                               # beautiful indices: string pattern matching
    3645: [],                               # optimal activation order greedy
    909:  [],                               # snakes and ladders BFS
    2547: [],                               # min cost split array DP
    3027: ["GEOM", "PAIR_COUNT"],           # place people: sort, count pairs where one "contains" the other
    2517: [],                               # binary search (tastiness)
    2741: ["BITMASK", "PERM_COMB"],         # special permutations: bitmask DP over adjacent pairs
    2271: ["AP_SUM"],                       # max white tiles: binary search + prefix sum of tile lengths
    2251: ["CONTRIBUTION"],                 # flowers in bloom: difference array contribution
    1210: [],                               # min moves rotations BFS
    1235: [],                               # job scheduling DP
    2597: ["PERM_COMB"],                    # beautiful subsets: backtrack count, avoid pairs with diff k
    1734: ["XOR"],                          # decode XORed permutation: XOR of prefix gives back permutation
    751:  ["BIT_OPS"],                      # IP to CIDR: lowest set bit gives block size
    1067: ["DIGIT_OPS", "PERM_COMB"],       # digit count in range: digit DP
    3681: ["XOR"],                          # maximum XOR of subsequences
    1406: ["GAME_THEORY"],                  # Stone Game III: minimax DP
    1626: [],                               # best team LIS/DP
    1320: ["GEOM"],                         # min distance typing two fingers: keyboard coordinate DP
    895:  [],                               # max freq stack (data structure)
    3428: ["CONTRIBUTION"],                 # max/min sums size-K subsequences: contribution of each element
    1231: [],                               # divide chocolate binary search
    2772: ["TRICK"],                        # make array zero: difference array insight (when to flip)
    2426: ["PAIR_COUNT"],                   # pairs satisfying inequality: rearrange to count inversions
    2919: [],                               # min increment for beautiful array DP
    3864: [],                               # min cost partition binary string DP
    1425: [],                               # constrained subsequence sum DP
    3578: [],                               # count partitions max-min ≤ k: sliding window
    2262: ["CONTRIBUTION"],                 # total appeal: each char contributes based on prev occurrence
    2136: [],                               # earliest full bloom greedy
    828:  ["CONTRIBUTION"],                 # count unique chars all substrings: contribution via nearest same char
    947:  [],                               # most stones removed: union-find
    1335: [],                               # min difficulty job schedule DP
    1140: ["GAME_THEORY"],                  # Stone Game II: minimax DP
    3552: [],                               # grid teleportation BFS
    1348: [],                               # tweet counts simulation
    2245: ["PRIME"],                        # max trailing zeros: count factors of 2 and 5 (min = trailing zeros)
    2116: [],                               # valid parentheses string: greedy balance range
    3654: ["MOD_ARITH"],                    # min sum after divisible sum deletions
    1590: ["MOD_ARITH"],                    # make sum divisible by P: prefix sum mod P
    1201: ["GCD_LCM"],                      # ugly number III: binary search + LCM + inclusion-exclusion
    3366: [],                               # min array sum DP
    1371: ["BITMASK"],                      # longest substring vowels even counts: bitmask for vowel parity
    1751: [],                               # max events II: DP + binary search
    3872: ["AP_SUM", "STREAK"],             # longest arithmetic sequence after 1 change
    3494: [],                               # brew potions: simulation
    2551: ["CONTRIBUTION"],                 # put marbles: sort adjacent pair sums, take extremes
    2735: ["CONTRIBUTION"],                 # collecting chocolates: contribution of each type per rotation
    3331: [],                               # subtree sizes after changes: DFS
    3113: ["SUBARRAY_COUNT"],              # subarrays where boundary = max: monotonic stack count
    2948: [],                               # lex smallest array by swapping: greedy grouping
    1553: ["TRICK", "MOD_ARITH"],           # min days eat N oranges: eat n%2 or n%3 to get to multiple first
    1648: ["AP_SUM"],                       # sell diminishing balls: binary search + triangle sum formula
    3209: ["BIT_OPS"],                      # subarrays with AND value K: AND monotone, count via bit tracking
    1224: ["TRICK"],                        # max equal frequency: greedy frequency pattern analysis
    1856: ["CONTRIBUTION", "MOD_ARITH"],    # max subarray min-product: monotonic stack contribution
    3785: [],                               # no content
    3933: [],                               # largest local matrix II (grid simulation)
    3072: [],                               # distribute elements: segment tree counting
    2467: [],                               # most profitable path: tree DFS + time sync
    839:  [],                               # similar string groups: union-find
    1575: ["MOD_ARITH"],                    # count all possible routes: DP mod 1e9+7
    2542: [],                               # max subsequence score: greedy + heap
    1473: [],                               # paint house III: DP
    2197: ["GCD_LCM"],                      # replace non-coprime: merge if LCM fits (GCD check)
    1131: ["GEOM", "TRICK"],                # max absolute value expression: Manhattan distance via 4 sign expansions
    2508: ["PARITY"],                       # add edges for even degrees: parity constraint on degree sums
    2681: ["CONTRIBUTION", "POWER", "MOD_ARITH"], # power of heroes: each element^2 * prefix sum contribution
    2366: ["TRICK"],                        # min replacements to sort: ceil arithmetic for split count
    3316: [],                               # max removals source string: DP subsequence
    2106: ["AP_SUM"],                       # max fruits: sliding window, turning cost = 2*min + remaining (sum formula)
    2156: ["MOD_ARITH"],                    # find substring with hash: rolling hash + modular inverse (backwards)
    801:  [],                               # min swaps sequences increasing: DP
    3229: ["CONTRIBUTION"],                 # min ops make array equal to target: diff array, sum positive gaps
    855:  [],                               # exam room data structure
    1770: [],                               # max score multiplication DP
    3489: [],                               # zero array transformation IV: bitset DP
    1368: [],                               # min cost valid path grid: 0-1 BFS
    3821: ["DIGIT_OPS", "PERM_COMB"],       # Nth smallest with K one-bits: count via digit-level C(n,k)
    1168: [],                               # optimize water: MST
    2514: ["PERM_COMB", "MOD_ARITH"],       # count anagrams: product of permutations mod 1e9+7
    1808: ["POWER", "MOD_ARITH", "DIVISORS"],# max nice divisors: split n (like integer break → use 3s) + fast exp
    2607: ["GCD_LCM"],                      # make K-subarray sums equal: period = GCD(n,k), group by cycle
    3154: ["PERM_COMB", "POWER"],           # ways to reach K-th stair: count jump sequences via C(n,k) + powers of 2
    2866: [],                               # beautiful towers: monotonic stack
    1799: ["BITMASK", "GCD_LCM"],           # maximize score N ops: bitmask DP, score = i * GCD(pair)
    1850: ["PERM_COMB"],                    # min swaps to Kth smallest: next-permutation k times + bubble sort count
    2845: ["MOD_ARITH"],                    # count interesting subarrays: prefix count mod modulo
    3685: [],                               # no content
    3782: [],                               # no content
    871:  [],                               # min refueling stops: greedy heap
    2906: ["MOD_ARITH"],                    # construct product matrix: prefix/suffix product with specific modulus
    2354: ["PAIR_COUNT", "BIT_OPS"],        # excellent pairs: popcount(a|b) = popcount(a)+popcount(b)-popcount(a&b) ≥ k
    2449: ["PARITY", "CONTRIBUTION"],       # make arrays similar: pair odd/even by sorted order
    1088: ["DIGIT_OPS"],                    # confusing number II: digit DP for confusing numbers in range
    2959: ["BITMASK"],                      # possible sets closing branches: enumerate 2^n subsets
    843:  [],                               # guess the word: randomized game
    1786: [],                               # restricted paths: DP + Dijkstra
    1712: ["SUBARRAY_COUNT"],               # ways to split into 3: binary search for valid left/right boundaries
    975:  [],                               # odd even jump: monotonic stack + reachability
    3924: [],                               # min threshold path: binary search + graph
    1643: ["PERM_COMB"],                    # Kth smallest instructions: count paths via C(H+V-1, H)
    1718: [],                               # lex largest valid sequence: backtracking
    3240: ["PALINDROME"],                   # min flips binary grid palindromic II
    2555: [],                               # max win two segments: binary search + DP
    2560: [],                               # house robber IV: binary search
    1639: ["PERM_COMB", "MOD_ARITH"],       # ways to form target: DP, count char usage per position
    2857: ["PAIR_COUNT", "BIT_OPS"],        # count pairs distance k: enumerate XOR splits per k
    3291: [],                               # min valid strings: greedy/DP
    1847: [],                               # closest room: offline + sorted set
    1494: ["BITMASK"],                      # parallel courses II: bitmask DP
    2050: [],                               # parallel courses III: DAG DP
    774:  [],                               # minimize max distance gas station: binary search
    2009: ["SUBARRAY_COUNT"],               # make array continuous: sort + dedup + sliding window
    2267: [],                               # valid parentheses path: DP
    1192: [],                               # critical connections: Tarjan
    982:  ["TRIPLE_COUNT", "BITMASK"],      # triples AND = 0: enumerate all pairs, use precomputed AND counts
    3855: ["DIGIT_OPS", "MOD_ARITH"],       # sum of K-digit numbers in range: digit DP
    3351: ["CONTRIBUTION", "MOD_ARITH"],    # sum of good subsequences: each element contributes to prev+1 length chains
    3624: ["BIT_OPS", "DIGIT_OPS"],         # integers with popcount-depth = K: count via popcount levels
    1563: ["GAME_THEORY"],                  # Stone Game V: minimax DP
    3739: ["SUBARRAY_COUNT"],               # subarrays with majority element II: contribution ±1 trick
    2318: ["GCD_LCM"],                      # distinct roll sequences: DP, consecutive dice share no common factor
    2193: ["PALINDROME"],                   # min moves make palindrome: greedy + BIT/Fenwick for swap counting
    1383: [],                               # max performance of team: greedy heap
    2751: [],                               # robot collisions: stack simulation
    2842: ["PERM_COMB", "MOD_ARITH"],       # count K-subsequences max beauty: freq sort + choose per freq class
    2412: ["TRICK"],                        # min money before transactions: find worst-case ordering (loss = cost-cashback)
    1049: [],                               # last stone weight II: subset sum DP
    2444: ["SUBARRAY_COUNT"],               # count subarrays fixed bounds: count subarrays where min=minK, max=maxK
    2402: [],                               # meeting rooms III: greedy heap
    3123: [],                               # edges in shortest paths: Dijkstra + DAG check
    3434: ["TRICK"],                        # max freq after subarray op: convert to +1/-1 for target, Kadane
    1976: ["MOD_ARITH"],                    # ways to arrive at destination: DP mod 1e9+7
    3854: ["PARITY"],                       # min ops parity alternating: count parity mismatches
    899:  ["TRICK"],                        # orderly queue: k≥2 → can sort; k=1 → min rotation
    778:  [],                               # swim in rising water: binary search + BFS
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
