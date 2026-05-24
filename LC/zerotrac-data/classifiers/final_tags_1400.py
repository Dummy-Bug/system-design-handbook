# Final manual classification of all 214 Band 1400-1499 problems
# Format: id -> list of tags (or [] if NOT_MATH)
# Tags: PAIR_COUNT, TRIPLE_COUNT, SUBARRAY_COUNT, DIGIT_OPS, MOD_ARITH, BIT_OPS, XOR,
#       PRIME, GCD_LCM, PERM_COMB, STARS_BARS, AP_SUM, CONTRIBUTION, GEOM, GAME_THEORY,
#       PROB, PALINDROME, POWER, POPCOUNT_GROUP, PIGEONHOLE, FIB, JOSEPHUS, PARITY,
#       TRICK, MOD_EXP, STREAK, CEIL_DIV

tags = {
1198: [], 3111: ["GEOM"], 3839: [],
1508: ["SUBARRAY_COUNT", "MOD_ARITH"],
1237: ["PAIR_COUNT"], 1700: [], 3101: ["SUBARRAY_COUNT", "STREAK"], 3751: ["DIGIT_OPS"],
1410: [], 1457: ["BIT_OPS", "PALINDROME"], 1561: [], 2734: [], 2744: ["PAIR_COUNT"],
2946: ["MOD_ARITH"], 2996: [],
2451: [], 3867: ["GCD_LCM", "PAIR_COUNT"],
1006: [], 1217: ["PARITY"], 1325: [], 1886: [], 3899: ["GEOM"],
1588: ["CONTRIBUTION", "SUBARRAY_COUNT"], 2110: ["SUBARRAY_COUNT", "STREAK"], 3909: [],
2834: ["PAIR_COUNT", "MOD_ARITH"],
1138: [],
3121: [], 3546: ["SUBARRAY_COUNT"],
1823: ["JOSEPHUS"], 841: [],
2383: [], 2521: ["PRIME"],
1985: [], 2825: ["MOD_ARITH"], 3675: ["MOD_ARITH"], 3722: [], 890: [],
1652: ["SUBARRAY_COUNT", "MOD_ARITH"], 2294: [], 3462: [],
2139: ["BIT_OPS"],
1052: [], 1656: [], 1962: [], 2374: [],
3275: ["GEOM"],
2760: ["PARITY"], 3848: ["DIGIT_OPS", "PERM_COMB"],
1033: [], 1360: [], 1630: ["AP_SUM"], 2326: [],
2606: [], 2938: [], 3737: ["SUBARRAY_COUNT"],
1333: [], 1493: [], 3039: [], 791: [],
840: [], 883: ["GEOM"],
1003: [], 1315: [], 1432: ["DIGIT_OPS"], 2437: ["DIGIT_OPS"],
1887: [],
1669: [], 1845: [], 2711: [], 3834: [], 817: [],
1357: [], 2957: [], 988: [],
1636: [], 2924: [],
1170: [], 2415: [],
1785: [], 3192: ["BIT_OPS"], 967: ["DIGIT_OPS"], 994: [],
1535: [],
2600: [],
1025: ["GAME_THEORY", "PARITY"], 2001: ["PAIR_COUNT", "GCD_LCM"], 2559: [], 3523: [], 3896: ["PRIME"],
1433: [], 1701: [], 845: [],
1375: [], 1609: ["PARITY"],
1261: [], 3556: ["PRIME", "DIGIT_OPS"], 3659: ["PERM_COMB"],
1094: [],
836: ["GEOM"],
1560: ["MOD_ARITH"], 3411: ["GCD_LCM"], 3876: ["PARITY"], 763: [],
1465: ["GEOM", "MOD_ARITH"], 2028: ["SUM_ARITH"], 2526: [], 3779: [], 942: [],
1946: ["DIGIT_OPS"], 2295: [], 3223: [],
1026: [],
2099: [],
2596: [], 3301: [], 945: [],
3741: ["TRIPLE_COUNT"],
2511: [], 2947: ["MOD_ARITH", "SUBARRAY_COUNT"], 2961: ["MOD_EXP"], 831: [],
3200: ["AP_SUM"], 3227: ["GAME_THEORY", "PARITY"],
1472: [], 3634: [], 781: ["CEIL_DIV"],
1846: [], 2094: ["DIGIT_OPS", "PERM_COMB"], 2487: [], 3325: [], 3727: ["POWER"],
2391: [],
3318: [],
2062: [],
1310: ["XOR"], 2452: [], 3566: ["PERM_COMB"],
1663: [], 1910: [], 3147: [], 833: [],
1909: [], 3619: ["MOD_ARITH"], 946: [],
1022: ["BIT_OPS"],
3638: [],
1361: [], 1396: [],
1414: ["FIB"],
2012: [], 2038: ["GAME_THEORY", "STREAK"], 3719: ["PARITY"],
2900: [],
1093: ["SUM_ARITH"], 2047: [], 3853: [],
2265: [], 3407: [],
1328: ["PALINDROME"], 1352: [], 897: [],
984: [],
2300: ["PAIR_COUNT"], 2368: [],
2645: [], 951: [],
1390: ["GCD_LCM"], 2909: ["TRIPLE_COUNT"],
1166: [], 1545: ["BIT_OPS"], 2501: ["POWER"], 2914: [],
1087: [], 3006: [],
1167: [], 1807: [], 2380: [],
1314: [], 2904: [], 3169: [], 3259: [],
2789: [],
1190: [], 1418: [],
1566: [], 1637: ["GEOM"], 2840: ["PARITY"],
1753: ["TRICK"],
3175: [],
1175: ["PRIME", "PERM_COMB"], 2658: [], 3576: ["PARITY"], 3702: ["XOR"],
1296: [], 1759: ["SUBARRAY_COUNT", "STREAK", "MOD_ARITH"], 3713: [],
1806: ["MOD_ARITH"], 3137: [],
3810: [],
2483: [],
1685: ["CONTRIBUTION"], 2419: ["BIT_OPS"], 949: ["DIGIT_OPS", "PERM_COMB"],
1208: [], 2191: ["DIGIT_OPS"], 2285: [], 3011: ["POPCOUNT_GROUP"],
998: [],
1904: ["MOD_ARITH"], 3070: [],
1525: [], 1968: [], 2507: ["PRIME"],
}

# Output as TSV
import sys
with open(sys.argv[1]) as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 3: continue
        rating, pid = parts[0], parts[1]
        title = parts[2] if len(parts) > 2 else ""
        pid_int = int(pid)
        t = tags.get(pid_int, None)
        if t is None:
            tag_str = "?UNKNOWN"
        elif t == []:
            tag_str = "-"
        else:
            tag_str = ",".join(sorted(t))
        print(f"{rating}\t{pid}\t{tag_str}\t{title}")
