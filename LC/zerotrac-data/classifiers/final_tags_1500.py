# Final manual classification of all 195 Band 1500-1599 problems
# Based on reading each description above
tags = {
3096: ["PREFIX_SUM"], 915: [],
1090: [], 1750: [],
2730: [],
2358: ["AP_SUM", "TRICK"], 2661: [], 2708: ["BIT_OPS"], 3424: [],
1461: ["BIT_OPS"], 2104: ["CONTRIBUTION", "MONOTONIC"], 2761: ["PRIME"],
3795: [], 869: ["DIGIT_OPS", "PERM_COMB", "BIT_OPS"],
1253: [],
1780: ["BIT_OPS"], 2981: [],
1387: ["DIGIT_OPS"], 3551: ["DIGIT_OPS"],
2105: [], 892: ["GEOM"],
1151: [], 1496: ["GEOM"],
1647: [], 2216: ["PARITY"], 2671: [], 3233: ["PRIME"], 3583: ["TRIPLE_COUNT"],
1110: [], 1557: [],
3365: [],
1855: [],
2849: ["PARITY"], 3106: ["MOD_ARITH"],
775: ["PAIR_COUNT"], 904: [],
2683: ["XOR"], 3160: [],
3334: ["GCD_LCM"], 3531: ["GEOM"],
1641: ["PERM_COMB", "STARS_BARS"], 2865: [],
1041: ["GEOM"], 1615: [], 1763: [], 2971: ["GEOM"], 3091: [],
1829: ["XOR"], 3152: ["PARITY"], 3484: [],
1272: [], 1442: ["XOR"], 1640: [], 2997: ["BIT_OPS"], 3913: [],
2201: ["GEOM"],
2918: [],
1921: [],
1695: [],
3732: [], 881: [],
1400: ["PARITY"], 1657: [], 1726: ["PAIR_COUNT", "PERM_COMB"], 2591: [],
3824: [],
2429: ["BIT_OPS"], 900: [],
1362: ["GEOM"], 1930: ["PALINDROME"], 2770: [], 3016: ["PERM_COMB"],
1797: [], 3890: ["POWER"], 865: [],
2958: [],
1861: [], 2933: [], 3723: ["DIGIT_OPS"],
1023: [],
2178: ["AP_SUM"],
1992: ["GEOM"],
1382: [], 2349: [], 3128: ["GEOM", "TRIPLE_COUNT"],
1007: [], 1209: [], 1229: [], 1283: [], 1749: [], 2575: ["DIGIT_OPS", "MOD_ARITH"], 3537: [], 986: [],
812: ["GEOM"],
2811: [],
1104: ["BIT_OPS"], 1233: [], 3468: [], 794: ["TRICK"],
2841: [],
3770: ["PRIME"],
758: [], 954: ["PAIR_COUNT"],
1329: [], 1599: [], 2456: [], 3503: ["PALINDROME"], 3587: ["PARITY"], 3885: [], 3932: ["POWER"],
2527: ["XOR", "TRIPLE_COUNT", "TRICK"], 2780: [],
2207: [], 2208: [],
2461: [],
3361: ["MOD_ARITH"],
2131: ["PALINDROME"], 3652: [], 3653: ["XOR", "MOD_ARITH"], 3849: ["BIT_OPS"],
2007: ["PAIR_COUNT"],
1101: [], 1144: [], 1181: [], 1243: [], 2310: ["DIGIT_OPS", "MOD_ARITH"],
2470: ["GCD_LCM"],
3693: [],
1256: [], 1376: [],
1008: [], 1452: [], 2409: [], 856: [],
2970: [], 3305: [], 800: [],
3249: [], 3493: [], 846: [],
769: [],
2044: ["BIT_OPS"], 3243: [],
3567: [],
1109: [], 2592: [],
1019: [],
779: ["BIT_OPS"],
1268: [], 1423: [], 3393: ["XOR"], 931: [],
1578: [], 981: [],
1415: ["PERM_COMB"],
2288: [],
1034: [], 3412: [], 3868: [],
1743: [], 3528: ["MOD_ARITH"], 3623: ["GEOM", "PAIR_COUNT"], 3789: [],
1839: [], 2765: [],
2211: [], 3021: ["GAME_THEORY", "PAIR_COUNT", "PARITY"],
2536: [], 2874: ["TRIPLE_COUNT"],
3780: ["TRIPLE_COUNT", "MOD_ARITH"],
1030: ["GEOM"],
1764: [], 1813: [], 2844: ["MOD_ARITH", "DIGIT_OPS"],
1573: ["PERM_COMB"], 1664: [], 877: ["GAME_THEORY"], 893: ["PARITY"], 969: [],
1286: ["PERM_COMB"], 3207: [], 3355: [], 3828: ["GAME_THEORY", "TRICK"], 930: ["PREFIX_SUM"],
1577: ["TRIPLE_COUNT", "POWER"], 3228: [], 3790: ["PIGEONHOLE", "MOD_ARITH"], 3829: [],
822: [],
3255: ["STREAK"],
2476: [],
1218: [], 1247: ["PARITY"], 2750: [],
1048: [],
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
            tag_str = "?UNKNOWN"
            unknown.append(pid)
        elif t == []:
            tag_str = "-"
        else:
            tag_str = ",".join(sorted(t))
        print(f"{rating}\t{pid}\t{tag_str}\t{title}")
if unknown:
    print(f"\n--- UNKNOWN: {len(unknown)} ---", file=sys.stderr)
    for p in unknown: print(p, file=sys.stderr)
