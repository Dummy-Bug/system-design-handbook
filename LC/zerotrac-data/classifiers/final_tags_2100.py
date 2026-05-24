tags = {
    793:  ["PRIME","AP_SUM"],           # trailing zeros in n! = sum of n/5^k — binary search on this formula
    2430: [],                           # max deletions string: LCP DP
    2088: [],                           # fertile pyramids: triangle DP
    1944: [],                           # visible people: monotonic stack
    3529: [],                           # overlapping substrings: grid counting
    1937: [],                           # max points with cost: DP with slope optimization
    2209: [],                           # min white tiles: DP
    3108: ["BIT_OPS"],                  # min cost walk: AND of all edges in component (connected = AND of all)
    1172: [],                           # dinner plate stacks: data structure
    3543: [],                           # max weighted k-edge path: graph DP
    3469: [],                           # min cost remove elements: DP/greedy
    1483: ["POWER"],                    # kth ancestor: binary lifting (jump 2^k levels at a time)
    2967: ["PALINDROME","AP_SUM"],      # make array equalindromic: median + nearest palindrome distance
    1547: [],                           # min cost cut stick: interval DP
    3093: [],                           # longest common suffix: trie/hashing
    1601: ["BITMASK"],                  # max achievable requests: enumerate all 2^n subsets of requests
    2376: ["DIGIT_OPS","PERM_COMB"],    # count special integers: digit DP, no repeated digits
    972:  ["TRICK"],                    # equal rational numbers: convert repeating decimal to fraction
    3699: [],                           # zigzag arrays: DP
    1970: [],                           # last day cross: binary search + union-find
    1654: [],                           # min jumps reach home: BFS
    968:  [],                           # binary tree cameras: greedy DP
    1955: ["MOD_ARITH"],                # count special subsequences: DP count mod 1e9+7
    2746: [],                           # decremental concatenation: DP
    2246: [],                           # longest path diff adjacent chars: tree DP
    1444: ["MOD_ARITH","PERM_COMB"],    # ways to cut pizza: DP count mod, prefix sum for valid cuts
    2939: ["BIT_OPS","XOR"],            # max XOR product: greedily assign bits to maximise a^b * a^b
    3887: [],                           # no content
    798:  ["CONTRIBUTION"],             # smallest rotation highest score: count score changes via contribution
    1039: [],                           # min score triangulation: interval DP
    2076: [],                           # restricted friend requests: union-find
    1579: [],                           # remove max edges: union-find
    2749: ["BIT_OPS","TRICK"],          # min ops make integer zero: need popcount(n−i*k) for each possible subtract count
    2910: ["GCD_LCM"],                  # min groups valid assignment: group sizes must all be equal (within ±1), GCD of freq
    3791: ["DIGIT_OPS","PARITY"],       # balanced integers: digit DP, sum of odd positions = sum of even positions
    898:  ["BIT_OPS"],                  # bitwise ORs of subarrays: at most 32 distinct OR values ending at each pos
    1439: [],                           # kth smallest sum matrix: heap k-way merge
    910:  ["TRICK"],                    # smallest range II: sort, try each split point, formula for max−min
    3900: [],                           # longest balanced substring after swap: string parity analysis
    3710: ["PRIME","DIVISORS"],         # max partition factor: prime factorization to maximise product of factors
    959:  ["GEOM"],                     # regions cut by slashes: union-find on 4-cell subdivision grid
    2382: [],                           # max segment sum: union-find + reverse
    2290: [],                           # min obstacle removal: 0-1 BFS
    3629: ["PRIME"],                    # min jumps via prime teleportation: sieve + group by shared prime factor
    3786: [],                           # no content
    906:  ["PALINDROME"],               # super palindromes: palindromes whose square is also palindrome
    3568: ["BITMASK"],                  # min moves clean classroom: BFS + bitmask over trash locations
    1879: ["BITMASK","XOR"],            # min XOR sum two arrays: bitmask DP (assign elements to minimise XOR sum)
    3559: ["PERM_COMB","POWER","MOD_ARITH"], # ways to assign edge weights: count paths, 2^(edges on path) combos
    1906: [],                           # min abs diff queries: prefix frequency queries
    1610: ["GEOM"],                     # max visible points: angular sweep, circular sliding window
    2972: ["SUBARRAY_COUNT"],           # count incremovable subarrays II: binary search on valid prefix/suffix
    3320: ["MOD_ARITH","GAME_THEORY"],  # count winning sequences: game DP mod 1e9+7
    2812: [],                           # safest path: binary search + BFS
    2662: [],                           # min cost special roads: Dijkstra
    3187: [],                           # peaks in array: BIT range query
    2616: [],                           # minimize max diff pairs: binary search + greedy
    3911: [],                           # kth smallest even integer queries: binary search
    3347: [],                           # max frequency after operations: sliding window
    1515: ["GEOM"],                     # best position service centre: geometric median (ternary search / gradient)
    2218: [],                           # max value K coins: DP
    3768: ["PAIR_COUNT"],               # min inversion count in fixed-length subarrays: sliding window on inversion count
    3664: [],                           # no content
    2102: [],                           # rank tracker: sorted set
    2122: ["TRICK"],                    # recover original array: enumerate possible difference d, verify split
    2584: ["GCD_LCM"],                  # split array coprime products: find split where prefix & suffix GCD coprime
    3906: [],                           # no content
    3373: [],                           # maximize target nodes trees II: tree BFS
    3830: [],                           # longest alternating subarray after removal: DP
    3934: [],                           # no content
    3171: ["BIT_OPS"],                  # subarray AND closest to K: AND monotone decreasing, track distinct AND values
    1036: ["GEOM"],                     # escape large maze: BFS bounded by triangle area (blocked cells ≤ 200²/2)
    3429: [],                           # paint house IV: DP
    786:  ["PRIME"],                    # kth smallest prime fraction: binary search on value + count fractions
    1931: ["BITMASK"],                  # painting grid 3 colors: bitmask DP on column coloring states
    1862: ["DIVISORS","CONTRIBUTION"],  # sum of floored pairs: harmonic series trick — for each divisor d, count multiples
    3213: [],                           # construct string min cost: DP + automaton
    1691: [],                           # max height stacking cuboids: DP (sorted)
    2709: ["PRIME","GCD_LCM"],          # GCD traversal: union-find connecting numbers via shared prime factors
    2896: [],                           # apply ops two strings equal: DP
    3883: ["MOD_ARITH","STARS_BARS"],   # count non-decreasing arrays with digit sums: distribute sum among positions
    2454: [],                           # next greater element IV: monotonic stack twice
    1420: ["MOD_ARITH"],                # build array max exactly K comparisons: DP count mod
    2768: ["PAIR_COUNT"],               # number of black blocks: count 2×2 blocks containing each black cell
    3479: [],                           # fruits into baskets III: segment tree binary search
    2065: [],                           # max path quality: DFS backtracking
    3812: [],                           # min edge toggles tree: tree DP
    1912: [],                           # movie rental system: data structure
    1771: ["PALINDROME"],               # max palindrome from subsequences: LCS-based palindrome DP
    891:  ["CONTRIBUTION","POWER","MOD_ARITH"], # sum subsequence widths: sort, each element contributes ±2^k times
    1081: [],                           # smallest subsequence distinct chars: monotonic stack
    943:  ["BITMASK"],                  # shortest superstring: bitmask DP (TSP-style, overlap precomputed)
    3377: ["PRIME"],                    # digit ops make two integers equal: BFS + primality check at each step
    3928: [],                           # min cost buy apples II: graph + greedy
    3660: [],                           # jump game IX: greedy
    1074: ["SUBARRAY_COUNT"],           # submatrices sum to target: 2D prefix sum + hash (extend 1D subarray count)
    1478: ["AP_SUM"],                   # allocate mailboxes: DP, cost = median, sum of abs deviations = AP_SUM
    2503: [],                           # max points from grid queries: offline BFS + union-find
    834:  ["CONTRIBUTION"],             # sum of distances in tree: rerooting contribution technique
    3873: [],                           # no content
    1621: ["STARS_BARS","PERM_COMB"],   # sets of K non-overlapping segments: C(n+k-1, 2k) combinatorial formula
    1739: ["AP_SUM","GEOM"],            # building boxes: triangular number layers — T(k) = k(k+1)/2
}

from collections import Counter
math = {k: v for k, v in tags.items() if v}
print(f"Total: {len(tags)}, Math: {len(math)} ({100*len(math)/len(tags):.1f}%)")
topic_count = Counter(t for v in tags.values() for t in v)
print("\nBy topic:")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")
