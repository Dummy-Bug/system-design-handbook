import re, sys

# Math topic patterns (case-insensitive). Order matters — more specific first.
patterns = [
    ("GAME",         r"\bgame\b|\bnim\b|\bstone game\b|optimal play|alice|bob"),
    ("PROB",         r"probability|expected|expectation|random|toss|dice|coin"),
    ("PRIME",        r"\bprime\b|\bcoprime\b|\bsieve\b"),
    ("GCD_LCM",      r"\bgcd\b|\blcm\b|greatest common|coprime|divisor"),
    ("MOD_DIV",      r"divis[ie]|modul[ao]|\bmod\b|harshad|multiple"),
    ("PERM_COMB",    r"permutation|combination|arrange|nCr|choose|factorial"),
    ("PAIR_TRIP",    r"\bpair\b|\bpairs\b|\btriplet\b|tuple"),
    ("COUNT",        r"^count |count of | count$"),
    ("DIGIT",        r"\bdigit\b|digits|harshad"),
    ("BIT_XOR",      r"\bxor\b|\bbit\b|bits|binary|gray code|hamming"),
    ("PALIN",        r"palindrome|palindromic"),
    ("POWER_ROOT",   r"\bpower\b|square|cube|root|n-th|^pow"),
    ("SUM_ARITH",    r"^sum |\bsum\b|^max sum|sum of"),
    ("FIB",          r"fibonacci|tribonacci"),
    ("GEOM",         r"area|rectangle|triangle|coordinate|distance|geometry|line|point"),
]

with open(sys.argv[1]) as f:
    lines = f.readlines()

tagged = []
math_count = 0
for line in lines:
    parts = line.strip().split('\t')
    if len(parts) < 3:
        continue
    rating, pid, title = parts[0], parts[1], parts[2]
    tags = []
    for tag, pat in patterns:
        if re.search(pat, title, re.IGNORECASE):
            tags.append(tag)
    is_math = len(tags) > 0
    if is_math:
        math_count += 1
    tagged.append((rating, pid, title, ",".join(tags) if tags else "-"))

# Print classified table
for r, p, t, tg in tagged:
    print(f"{r}\t{p}\t{tg}\t{t}")

print(f"\n--- Total: {len(tagged)} | Math-tagged by title: {math_count} ({100*math_count/len(tagged):.1f}%) ---", file=sys.stderr)
