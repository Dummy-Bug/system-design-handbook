# Zerotrac Data — Empirical LC Problem Corpus

This folder is a self-contained dataset of LeetCode problems with contest ratings, plus all the tooling to classify them across any technical lens (math, DP, graph, strings, etc.).

The data here was used to build `math-band-*.md` files in the parent folder (`LC/`). The same dataset can be re-tagged for any other dimension without re-fetching anything from LC.

---

## What's here

```
zerotrac-data/
├── ratings.tsv                          ← 2,644 problems w/ empirical contest ratings (1084–3125), synced 2026-11-23 (weekly 528, biweekly 195)
├── ratings.json                         ← same data as JSON
├── classify.py                          ← old regex-based classifier (deprecated, kept for reference)
│
├── problem-content-cache/               ← cached LC GraphQL responses, one JSON per problem
│   ├── band_1400_1499/                  (214 files)
│   ├── band_1500_1599/                  (195 files)
│   ├── band_1600_1699/                  (187 files)
│   ├── band_1700_1799/                  (186 files)
│   ├── band_1800_1899/                  (165 files)
│   ├── band_1900_1999/                  (134 files)
│   ├── band_2000_2099/                  (160 files)
│   ├── band_2100_2199/                  (102 files)
│   ├── band_2200_2299/                  (107 files)
│   ├── band_2300_2399/                  ( 93 files)
│   ├── band_2400_2499/                  ( 78 files)
│   └── band_2500_plus/                  (143 files, covers 2500–3774)
│
├── slugs/                               ← title slugs per band (one per line)
│   └── all_<RATING>_slugs.txt           (12 files: 1400 → 2500)
│
├── content-tsv/                         ← extracted text content per band, pipe-separated
│   └── all_<RATING>_with_content.tsv    (12 files: 1400 → 2500)
│       Format: Rating|ID|Title|FirstNCharsOfContent
│
├── classifiers/                         ← manual classification dicts, one Python file per band
│   └── final_tags_<RATING>.py           (12 files: 1400 → 2500)
│       Each file: tags = {problem_id: [topic_list]} dict, plus printing logic
│
├── band_<RANGE>_final.tsv               ← classified output per band, format:
│                                          Rating | ID | Title | CommaSeparatedTags
│
└── scripts/
    ├── fetch_band.sh                    ← fetch & cache JSONs for any rating band
    └── extract_all.py                   ← generate content TSV from cache + ratings
```

**Note:** Band `1100-1399` was the first band done, before the strict 100%-verification protocol. It has a `band_1100_1399_tagged.tsv` and `band_1100_1399_by_topic.txt` at the top level but no full cache directory. Re-fetching it would use `fetch_band.sh 1100 1400`.

---

## How to use this dataset

### 1. Query an existing classification

```bash
# All MOD_ARITH problems in the 2000-2099 band:
grep MOD_ARITH band_2000_2099_final.tsv

# All problems tagged with BITMASK across every band:
grep -l BITMASK band_*_final.tsv | xargs grep BITMASK

# How many CONTRIBUTION problems exist in each band:
for f in band_*_final.tsv; do
  echo "$(basename $f): $(grep -c CONTRIBUTION $f)"
done
```

### 2. Re-classify the corpus under a NEW lens (e.g., DP subtypes, graph patterns)

The corpus is already fetched. To classify by a new dimension:

```bash
# Step 1 (optional): regenerate content TSV for the band you want to work on
python3 scripts/extract_all.py problem-content-cache/band_1800_1899 ratings.tsv 1800 1900 \
  > /tmp/all_1800_with_content.tsv

# Step 2: read every problem description in the TSV and write classifications
# Create classifiers/dp_tags_1800.py with:
#   tags = {1234: ["INTERVAL_DP", "PREFIX_SUM"], ...}
# Then run it to print stats and a band_1800_1899_dp_final.tsv

# Step 3: write a corresponding math-band-style markdown file
```

No curl, no LC API calls — the JSONs are already cached locally.

### 3. Fetch a NEW rating band (e.g., if you want 2500-2700 split out)

```bash
./scripts/fetch_band.sh 2600 2700 2600_2699
```

This:
1. Filters `ratings.tsv` to the band, writes slugs to `slugs/all_2600_slugs.txt`
2. Fetches each problem's JSON via LC GraphQL with 150ms throttle (skips already-cached)
3. Caches into `problem-content-cache/band_2600_2699/`
4. Auto-runs `extract_all.py` to produce `content-tsv/all_2600_with_content.tsv`

---

## Schema reference

### `ratings.tsv` (source of truth for ratings)

Tab-separated. Columns:
```
Rating | ID | Title | TitleZH | TitleSlug | ContestSlug | ProblemIndex
```

### `problem-content-cache/band_*/<slug>.json`

LC GraphQL response. Path of interest:
```python
import json
data = json.load(open("...some-slug.json"))
q = data["data"]["question"]
q["questionId"], q["title"], q["content"], q["difficulty"]
# content is HTML, strip tags via re.sub(r'<[^>]+>', ' ', content)
```

### `content-tsv/all_*_with_content.tsv`

Pipe-separated (because problem content has tabs/quotes). Columns:
```
Rating|ID|Title|FirstNCharsOfContent
```
First N is 500 by default — see `extract_all.py` to change.

### `classifiers/final_tags_<RATING>.py`

Each is a standalone Python script:
```python
tags = {
    1234: ["MOD_ARITH", "CONTRIBUTION"],   # problem has both tags
    5678: [],                              # not a math problem
    9012: ["BITMASK"],
    ...
}
# Followed by Counter logic to print per-topic counts
```

The `tags` dict is the **source of truth** for the math classification. The `band_*_final.tsv` files are derived from these.

### `band_*_final.tsv`

Tab-separated. Columns:
```
Rating | ID | Title | CommaSeparatedTags
```
Tags = `NONE` means not a math problem.

---

## Math classification tags (used in `band_*_final.tsv`)

| Tag | Meaning |
|-----|---------|
| `MOD_ARITH` | Modular arithmetic, prefix sum mod, DP count mod |
| `BIT_OPS` | Bitwise operations (AND, OR, XOR as a tool) |
| `BITMASK` | Bitmask as state space (DP over subsets) |
| `XOR` | XOR-specific tricks (linear basis, prefix XOR) |
| `PERM_COMB` | Permutations and combinations (n choose k) |
| `MATRIX_EXP` | Matrix exponentiation for linear recurrences |
| `CONTRIBUTION` | "Each element contributes to..." technique (monotonic stack variant) |
| `AP_SUM` | Arithmetic progression sum formulas |
| `STARS_BARS` | Stars and bars combinatorial identity |
| `CATALAN` | Catalan numbers |
| `FIB` | Fibonacci-related |
| `GCD_LCM` | GCD/LCM as core technique |
| `PRIME` | Prime sieve, factorization, primality |
| `DIVISORS` | Divisor enumeration, divisor chains |
| `POWER` | Fast exponentiation, perfect squares/powers |
| `PARITY` | Parity arguments (even/odd) |
| `PIGEONHOLE` | Pigeonhole principle |
| `GAME_THEORY` | Minimax, Sprague-Grundy, optimal play |
| `PROB` | Probability DP |
| `GEOM` | Geometry (Manhattan, slopes, areas) |
| `PALINDROME` | Palindrome detection/construction |
| `DIGIT_OPS` | Digit DP, digit manipulation |
| `PAIR_COUNT` | Counting pairs by sorting/hashing |
| `TRIPLE_COUNT` | Counting triples (often via fix-middle) |
| `SUBARRAY_COUNT` | Counting subarrays with property (atMost-K trick, etc.) |
| `STREAK` | Longest streak / continuation patterns |
| `TRICK` | Hard-to-categorise reframe that unlocks the problem |

---

## Lenses that can be added (same corpus, new classification)

Each requires only writing a new set of `classifiers/<lens>_tags_<rating>.py` files. The corpus is already fetched.

- **DP subtypes** (interval, digit, bitmask, tree, knapsack, LIS/LCS, DP-on-graph)
- **Graph patterns** (BFS, Dijkstra, MST, Union-Find, SCC, topological sort, Eulerian)
- **Tree patterns** (rerooting, LCA, binary lifting, Euler tour, centroid, HLD)
- **String algorithms** (KMP, Z-function, rolling hash, suffix array, Manacher, trie)
- **Sliding window / two pointers**
- **Monotonic stack / monotonic deque**
- **Segment tree / BIT / sparse table**
- **Greedy patterns** (exchange argument, sort + heap, scheduling, regret)
- **Binary search on answer** (categorised by check-function type)

---

## Q2 and Q3 medians by year

Computed 2026-11-23 from `ratings.tsv` after the sync to weekly 528 and biweekly 195. Medians of the zerotrac rating of every Q2 and Q3 in the year's weekly and biweekly contests; 2026 runs from January to mid-November.

| Year | Contests (weekly, biweekly) | Weekly Q2 | Biweekly Q2 | All Q2 | Weekly Q3 | Biweekly Q3 | All Q3 | Q3 − Q2 |
| ---- | --------------------------- | --------: | ----------: | -----: | --------: | ----------: | -----: | ------: |
| 2020 | 52 (170-221), 26 (17-42)    |      1460 |        1491 |   1474 |      1812 |        1673 |   1752 |     278 |
| 2021 | 52 (222-273), 26 (43-68)    |      1491 |        1573 |   1510 |      1855 |        1840 |   1855 |     345 |
| 2022 | 52 (274-325), 26 (69-94)    |      1447 |        1468 |   1466 |      1716 |        1739 |   1718 |     252 |
| 2023 | 53 (326-378), 26 (95-120)   |      1483 |        1474 |   1480 |      1914 |        1752 |   1889 |     409 |
| 2024 | 52 (379-430), 26 (121-146)  |      1543 |        1533 |   1533 |      1901 |        1913 |   1907 |     374 |
| 2025 | 52 (431-482), 26 (147-172)  |      1561 |        1639 |   1579 |      2060 |        1941 |   2040 |     461 |
| 2026 | 46 (483-528), 23 (173-195)  |      1476 |        1505 |   1492 |      1861 |        1771 |   1841 |     349 |

Q2 stays between 1466 and 1579 in every year; Q3 swings by about 300 points and peaked in 2025.

**The 2026 drop may be rating deflation, not easier problems.** Zerotrac rates a problem from how contestants did on it, so a rise in AI-assisted solves would lower a rating without the problem getting easier. The user found 2026 problems no easier. Against it: LLMs were already strong in 2023-2025 while ratings rose every year. The data cannot separate the two, so for planning, 2024-2025 levels (Q2 about 1530-1580) are the safer reading.

**The years are inferred, not read.** `ratings.tsv` has no dates. Contest dates were computed back from weekly 502 on 2026-05-17 and biweekly 182 on 2026-05-09 (both from `../contest/Official/`), assuming one weekly every 7 days and one biweekly every 14 with none skipped. That holds for every logged contest in 2026; earlier year boundaries were not checked against LeetCode, whose contest API refused the request, so a contest at a boundary could sit in the neighbouring year.
