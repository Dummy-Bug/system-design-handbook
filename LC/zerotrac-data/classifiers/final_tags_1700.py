# Manual classification: Band 1700-1799 (186 problems)
tags = {
2962: [], 3592: [],
1054: [], 1774: ["STARS_BARS"],
2929: ["STARS_BARS", "PERM_COMB"],
2080: [], 2100: [], 958: [],
3767: [],
1947: ["BITMASK"], 3457: ["PARITY"],
2672: [],
3025: ["GEOM"], 816: [],
1401: ["GEOM"], 2257: ["GEOM"], 2944: [], 3040: [], 826: [],
901: [],
2140: [], 979: [],
1136: [], 1567: ["PARITY"], 3310: [], 759: [], 923: ["TRIPLE_COUNT"],
1801: [], 2385: [],
1042: [],
1372: [], 2406: ["GEOM"],
1781: ["CONTRIBUTION", "SUBARRAY_COUNT"], 2359: [], 3315: ["BIT_OPS"],
3649: ["PAIR_COUNT", "GEOM"],
2202: [],
2017: [], 2397: ["BITMASK"],
1239: ["BITMASK"], 3557: [],
2563: ["PAIR_COUNT"],
2826: [], 3208: [], 3341: [],
1197: [], 1359: ["PERM_COMB", "MOD_ARITH"],
2070: [], 2261: ["MOD_ARITH"],
1011: [], 2416: [], 3820: ["GEOM", "TRIPLE_COUNT"],
3439: [],
1220: ["PERM_COMB", "MOD_ARITH"], 3499: [],
1014: ["CONTRIBUTION"], 3447: ["MOD_ARITH"],
889: [],
1273: [], 2786: ["PARITY"],
1292: ["GEOM"], 2048: ["DIGIT_OPS"],
2707: [], 3453: ["GEOM"],
1814: ["DIGIT_OPS", "PAIR_COUNT", "MOD_ARITH"], 3044: ["PRIME", "DIGIT_OPS"],
1593: [], 3694: ["GEOM", "CONTRIBUTION"], 3776: ["GEOM"],
1079: ["PERM_COMB"],
1145: [], 3020: ["POWER", "DIVISORS"],
2087: ["GEOM"], 3380: ["GEOM"],
1139: [], 1638: [],
1391: [], 1530: [], 2502: [], 3433: [], 3877: ["XOR"],
1024: [], 1849: [],
1191: [],
1297: [], 2134: [], 2171: [],
1111: [], 2401: ["BIT_OPS"], 2856: [], 2871: ["BIT_OPS"], 3577: ["PERM_COMB", "TRICK"],
2166: ["BIT_OPS"], 2400: ["PERM_COMB", "MOD_ARITH"],
1135: [], 939: ["GEOM"],
1216: [], 3478: [], 3628: [],
764: [],
2568: ["BIT_OPS"],
3112: [],
1027: ["AP_SUM"], 1954: ["GEOM", "AP_SUM"],
1541: [], 2075: ["GEOM"], 2498: ["PARITY"], 3835: [], 3922: [],
2121: ["CONTRIBUTION"], 3881: ["PERM_COMB", "MOD_ARITH"],
2453: ["MOD_ARITH"], 3403: [],
1262: ["MOD_ARITH"], 948: [],
2462: [], 2905: [], 3584: [],
1706: [], 3085: [],
875: [],
1914: ["GEOM"],
1600: [], 2718: [], 3281: ["GEOM"],
2685: [],
1146: [], 3882: ["XOR", "GEOM"],
3282: [],
2982: [], 3170: [],
1238: ["BIT_OPS"],
2531: [], 3644: ["BIT_OPS"],
3919: [],
3164: ["PAIR_COUNT", "MOD_ARITH"], 3573: [], 918: ["GEOM"],
1824: [],
1016: ["BIT_OPS"], 1129: [], 1424: ["GEOM"], 2369: [], 2601: ["PRIME"], 842: ["FIB"],
1895: ["GEOM"], 2353: [],
1171: [], 1765: [],
851: [],
2952: ["BITMASK"], 894: ["PERM_COMB", "CATALAN"],
1911: [],
2653: [],
1312: [], 1510: ["GAME_THEORY"], 787: [], 971: [], 983: [],
1156: [], 1497: ["MOD_ARITH", "PARITY"], 2192: [], 3387: [], 768: [],
3219: [], 3724: [],
2321: [],
2712: [], 2771: [],
1245: [],
1653: [], 2381: ["MOD_ARITH"], 2615: ["CONTRIBUTION"], 3092: [], 3376: [],
2998: ["BIT_OPS", "TRICK"], 886: [],
966: [],
3001: ["GEOM"], 3814: [],
1028: [], 1072: [], 1711: ["BIT_OPS", "PAIR_COUNT", "MOD_ARITH"], 1834: [],
3418: [],
1186: [],
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
    print(f"--- UNKNOWN {len(unknown)} ---", file=sys.stderr)
    for p in unknown: print(p, file=sys.stderr)
