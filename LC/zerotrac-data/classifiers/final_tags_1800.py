# Manual classification: Band 1800-1899 (165 problems)
tags = {
1673: [], 2934: [], 3703: [],
1953: ["TRICK"],
1080: [], 2096: [], 3742: [],
1035: [],
1073: ["BIT_OPS"], 3335: ["MOD_ARITH", "MATRIX_EXP"], 3408: [],
1594: ["MOD_ARITH"],
1230: ["PROB"], 1519: [], 2302: [],
1345: [], 776: [],
1284: ["BITMASK", "BIT_OPS"], 2642: [],
3738: [],
773: ["BITMASK"],
3026: ["PAIR_COUNT"],
1658: [], 1792: ["GEOM"], 2787: ["PERM_COMB", "POWER"], 795: ["SUBARRAY_COUNT"],
3588: ["GEOM"], 861: ["BIT_OPS"],
2055: [], 3148: [],
1405: [],
1363: ["MOD_ARITH", "DIGIT_OPS"], 2217: ["PALINDROME", "DIGIT_OPS"], 2931: ["CONTRIBUTION"],
1377: ["PROB"], 1458: [], 3781: ["TRICK", "PAIR_COUNT"],
1298: [],
1702: ["TRICK"], 1835: ["BIT_OPS", "XOR"], 934: [],
1095: [], 3332: [], 3752: ["PERM_COMB"],
1754: [], 2135: ["BITMASK"],
790: ["FIB", "MOD_ARITH"], 980: ["BITMASK", "PERM_COMB"],
2034: [], 3012: ["GCD_LCM"], 3796: [], 755: [],
2370: [],
995: [],
1316: [], 2146: [],
1559: [],
2311: [],
2332: [], 3186: [], 3800: ["BIT_OPS"],
2013: ["GEOM"],
2576: ["PAIR_COUNT"],
1411: ["MOD_ARITH"], 3604: [],
1504: ["SUBARRAY_COUNT", "CONTRIBUTION"], 2598: ["MOD_ARITH"], 3558: ["MOD_ARITH", "PARITY"], 3825: ["BIT_OPS"],
1514: ["PROB"], 3196: [], 874: ["GEOM"],
1258: [], 3297: ["PERM_COMB"], 3676: ["TRIPLE_COUNT"],
1177: ["PALINDROME", "PARITY"], 3180: [], 3747: ["DIGIT_OPS"],
2059: ["BIT_OPS"], 3176: [],
1152: [], 1477: [], 1775: ["MOD_ARITH"],
2162: ["DIGIT_OPS"], 2830: [], 3508: [],
1301: [], 3639: [], 3650: [], 3815: [],
1269: ["MOD_ARITH", "PERM_COMB"], 1334: [],
1202: [], 1546: [], 2800: [], 3443: ["GEOM", "PARITY"], 799: ["AP_SUM"],
2266: ["FIB", "MOD_ARITH"], 3035: ["PALINDROME", "PARITY"],
1584: ["GEOM"],
1744: ["MOD_ARITH"],
3863: [], 3910: ["BITMASK", "PARITY"],
1996: [], 2301: [],
1993: [], 3342: [],
1163: [], 2767: ["BIT_OPS", "POWER"], 3326: ["PRIME", "DIVISORS"], 3346: [],
2039: [],
1340: [],
1605: [], 1717: ["TRICK"],
1616: ["PALINDROME"], 2212: ["BITMASK"], 924: [],
2002: ["PALINDROME", "BITMASK"], 3635: [],
1589: ["CONTRIBUTION", "MOD_ARITH"], 2008: [],
1526: ["TRICK"],
1001: ["GEOM"], 2975: ["GEOM"],
1015: ["PIGEONHOLE", "MOD_ARITH"],
2808: [],
1392: [], 1838: [], 955: [],
1234: [], 752: [],
1106: [], 1536: [], 2101: ["GEOM"], 754: ["AP_SUM", "PARITY"], 858: ["GCD_LCM", "GEOM"],
1255: ["BITMASK"],
2976: [],
2054: [], 3472: [], 3514: ["XOR", "TRIPLE_COUNT"], 3665: [], 3923: ["GEOM", "BITMASK"],
1066: ["BITMASK"], 1326: [], 2064: [],
2305: ["BITMASK"],
2817: [], 3542: [],
2537: ["PAIR_COUNT", "SUBARRAY_COUNT"], 3097: ["BIT_OPS"],
1722: [], 3608: [],
2327: ["FIB", "MOD_ARITH"],
3036: [],
1871: [], 3030: ["GEOM"], 878: ["GCD_LCM", "MOD_ARITH"],
1878: ["GEOM"], 2360: [], 3250: ["MOD_ARITH", "PERM_COMB"], 780: ["GCD_LCM"],
2901: [],
823: ["PERM_COMB", "MOD_ARITH"],
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
