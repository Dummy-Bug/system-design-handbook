# Manual classification: id -> [tags]
# Tags: MOD_ARITH, GEOM, BIT_OPS, BITMASK, PERM_COMB, PARITY, PAIR_COUNT,
#        TRIPLE_COUNT, DIGIT_OPS, PALINDROME, XOR, CONTRIBUTION, SUBARRAY_COUNT,
#        STREAK, GCD_LCM, PRIME, FIB, GAME_THEORY, AP_SUM, STARS_BARS,
#        TRICK, PIGEONHOLE, MATRIX_EXP, PROB, CATALAN, POWER, DIVISORS
# Empty list = not a math problem

tags = {
    1665: [],                          # greedy + sorting
    2602: ["AP_SUM"],                  # prefix-sum cost formula = arithmetic sums
    2608: [],                          # shortest cycle, BFS
    3122: [],                          # DP on grid conditions
    3081: [],                          # frequency + greedy
    1124: ["TRICK"],                   # +1/-1 encoding, cumulative trick
    3728: ["AP_SUM"],                  # equal boundary & interior sum
    3067: ["MOD_ARITH"],               # divisibility by signalSpeed along paths
    991:  ["TRICK"],                   # broken calc: work backwards multiply first
    3298: [],                          # sliding window frequency
    2585: [],                          # knapsack DP
    873:  ["FIB"],                     # longest Fibonacci subsequence
    2049: [],                          # tree traversal + product calculation
    2296: [],                          # data structure design
    1147: ["PALINDROME"],              # chunked palindrome decomposition
    2680: ["BIT_OPS"],                 # max OR with prefix OR
    1898: [],                          # binary search
    1671: [],                          # LIS
    3356: [],                          # binary search + difference array
    1373: [],                          # max sum BST in tree
    2875: ["MOD_ARITH"],               # subarray in infinite array = mod position
    2147: ["PERM_COMB"],               # multiply gaps between consecutive S pairs
    2594: [],                          # binary search on time
    1043: [],                          # partition DP
    3394: ["GEOM"],                    # grid cut = interval merge on axes
    3669: ["DIVISORS"],                # split n into k factors, minimize max-min
    2673: [],                          # tree DP cost equalization
    3144: [],                          # frequency substring partition
    2398: [],                          # sliding window with budget
    3002: [],                          # greedy set union/intersection
    2069: [],                          # simulation
    1130: [],                          # monotonic stack DP
    1416: ["DIGIT_OPS"],               # restore array by parsing digit strings
    1552: [],                          # binary search (magnetic force)
    2731: ["TRICK"],                   # robots: collision = pass-through, positions sort-stable
    1745: ["PALINDROME"],              # palindrome partitioning IV (check 3-part)
    1727: [],                          # greedy matrix rearrangement
    3372: [],                          # tree BFS target count
    1449: ["DIGIT_OPS"],               # largest int from digits summing to target
    1562: [],                          # union-find / binary search
    2654: ["GCD_LCM"],                 # make all elements 1 via GCD operations
    1802: ["AP_SUM"],                  # binary search check uses sum formula n*(n+1)/2
    2018: [],                          # crossword string placement
    1705: [],                          # greedy heap (apples)
    1798: ["TRICK"],                   # consecutive values reachability: sort + greedy reach
    1574: [],                          # two pointer remove subarray
    996:  ["PERM_COMB", "POWER"],      # permutations where adj sum is perfect square
    1964: [],                          # LIS variant
    827:  [],                          # union find + BFS
    1818: [],                          # sorted + binary search abs diff
    3133: ["BIT_OPS"],                 # min array end: fill bits using AND constraint
    813:  [],                          # partition DP with averages
    2411: ["BIT_OPS"],                 # smallest subarray with max OR = track per-bit last position
    866:  ["PRIME", "PALINDROME"],     # prime palindrome (only even-digit pals are non-prime)
    777:  [],                          # string swap greedy
    2925: [],                          # tree DP score
    1760: [],                          # binary search on max ball size
    2762: ["SUBARRAY_COUNT"],          # count continuous subarrays (sliding window)
    2111: [],                          # LIS (make array k-increasing)
    3381: ["MOD_ARITH"],               # max subarray sum with length divisible by K
    2227: [],                          # encrypt/decrypt string data structure
    1482: [],                          # binary search (bouquets)
    1793: [],                          # two pointer good subarray
    3858: ["BIT_OPS"],                 # min bitwise OR from grid
    1631: [],                          # binary search + BFS min effort
    2516: [],                          # sliding window take K chars
    2509: ["POWER"],                   # cycle in complete binary tree: LCA via 2^level
    1153: [],                          # string transform graph
    1690: ["GAME_THEORY"],             # Stone Game VII
    1259: ["CATALAN"],                 # handshakes non-crossing = Catalan numbers
    2435: ["MOD_ARITH"],               # paths sum divisible by K = DP mod K
    1737: [],                          # min char changes, prefix frequency
    3891: [],                          # unknown / no content
    2434: [],                          # greedy robot print (stack)
    1696: [],                          # jump game DP + sliding window max
    3599: ["XOR"],                     # partition to minimize XOR
    1463: [],                          # cherry pickup 2D DP
    3720: ["PERM_COMB"],               # lex smallest permutation greater than target
    3593: [],                          # tree DP leaf path equalization
    2564: ["XOR", "BITMASK"],          # substring XOR queries = find value via bit positions
    2392: [],                          # topological sort matrix build
    2350: [],                          # shortest impossible roll sequence greedy
    1537: [],                          # get max score DP
    1642: [],                          # furthest building greedy heap
    802:  [],                          # find eventual safe states (topological)
    815:  [],                          # bus routes BFS
    3850: ["PRIME", "DIVISORS"],       # count sequences: prime factorization exponents
    2439: ["AP_SUM"],                  # minimize max = ceiling of prefix average
    1969: ["POWER", "MOD_ARITH"],      # min non-zero product: (2^n-1) * (2^n-2)^(2^(n-1)-1)
    1293: [],                          # BFS grid obstacles
    2872: ["MOD_ARITH"],               # K-divisible components: subtree sum mod K
    3756: ["DIGIT_OPS"],               # concatenate non-zero digits, multiply by digit sum
    1943: ["CONTRIBUTION"],            # describe painting via contribution / difference array
    3686: ["MOD_ARITH"],               # stable subsequences count mod
    835:  ["PAIR_COUNT"],              # image overlap: count pairs sharing same shift offset
    1032: [],                          # stream of chars (trie)
    3733: [],                          # tree DP deliveries
    1488: [],                          # greedy heap avoid flood
    3202: ["MOD_ARITH"],               # max valid subsequence length divisible by K
    907:  ["CONTRIBUTION", "MOD_ARITH"],# sum of subarray minimums (contribution technique)
    2831: [],                          # sliding window equal subarray
    1092: [],                          # LCS shortest common supersequence
    1882: [],                          # process tasks servers (priority queue)
    1278: ["PALINDROME"],              # palindrome partitioning III
    3138: ["GCD_LCM"],                 # min anagram concat length: period divides n via GCD
    2151: ["BITMASK"],                 # max good people: enumerate 2^n truth assignments
    3771: [],                          # no content
    3725: ["GCD_LCM", "DIVISORS"],     # coprime selection: inclusion-exclusion via GCD/Mobius
    3690: [],                          # no content
    805:  ["AP_SUM"],                  # split same average: avg = sum/n, check sum*n divisible
    1250: ["GCD_LCM"],                 # good array iff GCD = 1 (Bezout's identity)
    1733: [],                          # min people to teach
    3695: [],                          # no content
    2963: ["PERM_COMB", "MOD_ARITH"], # good partitions: 2^(free_cuts) via last occurrence
    940:  ["MOD_ARITH"],               # distinct subsequences II (DP count mod)
    928:  [],                          # minimize malware spread (graph)
    3836: [],                          # no content
    902:  ["DIGIT_OPS", "PERM_COMB"], # numbers at most N with digit set (digit DP)
    3844: ["PALINDROME"],              # longest almost-palindromic substring
    756:  ["BITMASK"],                 # pyramid transition matrix (bitmask DP)
    963:  ["GEOM"],                    # min area rectangle II (dot product perpendicularity)
    1625: [],                          # lex smallest string BFS
    927:  ["BIT_OPS", "PARITY"],       # three equal parts: trailing zeros must match, bit splits
    1986: ["BITMASK"],                 # min work sessions (bitmask DP over tasks)
    3224: ["PARITY"],                  # min changes to make diffs equal (parity of positions)
    1274: [],                          # ships in rectangle (divide and conquer)
    3440: [],                          # reschedule meetings (interval scheduling)
    2250: ["GEOM"],                    # count rectangles containing point (height binary search)
    3620: [],                          # no content
    3897: ["BIT_OPS"],                 # max value concatenated binary segments
    2488: ["SUBARRAY_COUNT", "TRICK"], # count subarrays with median K (+1/-1 trick)
    765:  [],                          # couples holding hands (graph/greedy)
    3886: ["DIGIT_OPS"],               # sum of sortable integers (digit-based sorting)
}

import sys

# Count math problems
math_probs = {k: v for k, v in tags.items() if v}
print(f"Total problems tagged: {len(tags)}")
print(f"Math problems: {len(math_probs)} ({100*len(math_probs)/len(tags):.1f}%)")

# Count by topic
from collections import Counter
topic_count = Counter()
for v in tags.values():
    for t in v:
        topic_count[t] += 1

print("\nBy topic (sorted by count):")
for t, c in topic_count.most_common():
    print(f"  {t}: {c}")

# Output TSV
print("\n\nFinal tags:")
for k, v in tags.items():
    print(f"{k}\t{','.join(v) if v else 'NONE'}")
