# Final manual classification of all 187 Band 1600-1699 problems
tags = {
1864: ["PARITY"], 3350: [],
3047: ["GEOM"], 926: [],
2249: ["GEOM"], 2447: ["GCD_LCM"],
3319: [],
2316: ["PAIR_COUNT"], 2424: [], 2522: [], 2546: ["BIT_OPS", "TRICK"], 3107: [], 809: [],
1300: [], 1604: [], 3799: ["GEOM"],
1123: [], 2320: ["FIB", "MOD_ARITH"], 2745: ["TRICK", "AP_SUM"], 3080: [], 3286: [], 962: [],
2567: [], 3926: [],
2438: ["BIT_OPS", "MOD_ARITH"],
1524: ["PARITY", "MOD_ARITH"], 1670: [],
2232: [],
789: ["GEOM"],
1277: [], 2766: [],
2145: [],
1020: [],
2241: [],
1503: ["TRICK"], 3840: [],
2541: [],
3132: [],
2086: [], 2364: ["PAIR_COUNT"], 2365: [], 2425: ["XOR", "PARITY"],
1248: [],
3805: ["PAIR_COUNT", "MOD_ARITH"], 785: [], 916: [],
2684: [], 2860: [],
1182: [], 1366: [],
1332: ["PALINDROME", "PARITY"],
1680: ["BIT_OPS", "MOD_ARITH"],
1540: ["MOD_ARITH"], 2580: ["COUNTING"],
820: [],
1053: ["PERM_COMB"], 1319: [], 1466: [],
1899: [], 2471: [], 3076: [],
1386: [], 2384: ["PALINDROME"], 2512: [],
1558: ["BIT_OPS"],
1926: [], 2779: [], 3679: [], 838: [], 990: [],
3603: [],
2187: [], 2344: ["GCD_LCM"],
2375: [],
3613: [],
2275: ["BIT_OPS"],
2024: [], 2196: [], 3371: ["TRICK"],
3153: ["DIGIT_OPS", "PAIR_COUNT"],
1358: [], 2226: [],
3709: [],
1975: ["PARITY"], 2423: [], 3698: [], 870: [],
1367: [], 2523: ["PRIME"], 2571: ["BIT_OPS"],
2343: [], 3927: ["GCD_LCM"], 750: ["GEOM"],
1311: [],
1155: ["PERM_COMB", "PROB"], 1509: [],
1257: [], 3218: [],
1004: [], 3598: [],
2222: ["TRIPLE_COUNT"], 3766: ["BIT_OPS", "PALINDROME"],
1249: [], 3015: [],
1091: [], 1169: [], 1254: [], 1583: [], 1958: [], 2195: ["AP_SUM"], 2304: [], 2915: [], 3532: [],
3029: [],
3265: ["DIGIT_OPS", "PAIR_COUNT"],
2170: [], 2550: ["GEOM", "PERM_COMB", "MOD_ARITH"], 3914: [],
1219: [], 2063: ["CONTRIBUTION", "SUBARRAY_COUNT"], 2611: [], 3201: ["PARITY"], 3513: ["XOR", "TRIPLE_COUNT", "BIT_OPS"], 3755: ["XOR", "PARITY"], 863: [],
1121: [],
1620: ["GEOM"], 2593: [],
1162: [],
3761: ["DIGIT_OPS", "PAIR_COUNT"],
1738: ["XOR"], 2033: [], 3905: [],
1438: [], 3212: ["SUBARRAY_COUNT"],
1215: ["DIGIT_OPS"], 1339: [], 1922: ["PERM_COMB", "MOD_ARITH"],
1870: [], 974: ["SUBARRAY_COUNT", "MOD_ARITH"], 987: [],
2641: [],
2943: ["GEOM"],
1905: [], 2115: [], 2317: ["BIT_OPS"], 2698: ["DIGIT_OPS"], 853: [], 885: ["GEOM"],
1402: [], 2492: [],
1031: [], 1865: ["PAIR_COUNT"], 2182: [], 2280: ["GEOM", "GCD_LCM"], 2457: ["DIGIT_OPS"],
767: [],
1443: [], 2497: [],
2074: [], 2233: [],
950: [],
3397: [],
1963: [], 3043: ["DIGIT_OPS"],
1419: [], 3071: ["GEOM"],
919: [], 935: ["PERM_COMB"],
1462: [], 3290: [],
2337: [],
2466: ["PERM_COMB"], 3296: [], 829: ["AP_SUM", "DIVISORS"],
1942: [], 2420: [], 792: [],
1487: [], 2588: ["XOR", "PREFIX_XOR"], 3143: ["GEOM"],
1017: ["BIT_OPS"], 1289: [], 3862: [],
825: ["PAIR_COUNT"],
3488: [],
3607: [],
}

import sys
unknown = []
with open(sys.argv[1]) as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 3: continue
        rating, pid, title = parts[0], parts[1], parts[2]
        pid_int = int(pid)
        t = tags.get(pid_int, None)
        if t is None:
            tag_str = "?UNKNOWN"; unknown.append(pid)
        elif t == []:
            tag_str = "-"
        else:
            tag_str = ",".join(sorted(t))
        print(f"{rating}\t{pid}\t{tag_str}\t{title}")
if unknown:
    print(f"\n--- UNKNOWN: {len(unknown)} ---", file=sys.stderr)
    for p in unknown: print(p, file=sys.stderr)
