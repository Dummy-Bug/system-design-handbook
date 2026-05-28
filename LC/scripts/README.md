# LC Data-Fetch Scripts — Runbook

All scripts that pull external data for the LC prep system live here. Each script is idempotent (safe to re-run) and writes to a documented output location. Built 2026-05-28.

---

## 1. `fetch_lctags_generic.py` — Live LC tag/AR/difficulty per band

Fetches official LC `topicTags`, `acRate`, and `difficulty` from the LeetCode GraphQL API for every problem in a rating-band slug file. This is the canonical data source per CLAUDE.md Step 2.

**Usage:**
```bash
# 1. Build the slug list for a band (filter ratings.tsv to the range)
awk -F'\t' 'NR>1 && $1>=1500 && $1<1550 {printf "%.0f\t%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $5, $6, $7}' \
  zerotrac-data/ratings.tsv | sort -k1 -n > /tmp/band_1500_1549_slugs.tsv

# 2. Run fetch
python3 scripts/fetch_lctags_generic.py /tmp/band_1500_1549_slugs.tsv \
  zerotrac-data/band_1500_1549_lctags.tsv
```

**Output schema** (`band_<lo>_<hi>_lctags.tsv`):
`Rating | ID | Title | Slug | Contest | QPos | Difficulty | AR | LCtags`

**Rate limit:** 0.5s between requests. Browser User-Agent required (bare requests get 403). Re-runs are cheap — overwrite is safe.

**Already fetched:** 1500-1549, 1550-1599, 1600-1649, 1650-1699, 1700-1749, 1750-1799, 1800-1849, 1850-1899, 1900-1949, 1950-1999. Do NOT fetch above 1999 — out of scope for 2026 target.

---

## 2. `extract_learnyard_bundle.py` — LearnYard DSA Sheet → structured TSVs

LearnYard's DSA sheet is a Next.js SPA that bundles the entire topic tree + problem metadata into a single client-side JS chunk. This script parses that chunk and dumps every problem to `learnyard-data/`.

**Usage:**
```bash
# 1. Find current bundle filename (changes per deploy)
BUNDLE_URL=$(curl -sL "https://learnyard.com/practice/dsa" -A "Mozilla/5.0" \
  | grep -oE 'src="[^"]*app/practice/dsa/page-[^"]+\.js[^"]*"' | head -1 \
  | sed -E 's/^src="//; s/"$//')
BUNDLE_PATH=$(echo "$BUNDLE_URL" | sed 's/?.*//')

# 2. Download bundle
curl -sL "https://learnyard.com${BUNDLE_PATH}" -A "Mozilla/5.0" -o /tmp/learnyard-dsa.js

# 3. Extract everything
python3 scripts/extract_learnyard_bundle.py
```

**Output** (`learnyard-data/`):
- `all_problems.tsv` — master (MainTopic, Subgroup, Difficulty, Title, Slug, Source, Link), ~1431 rows
- 27 per-topic TSVs (`graphs.tsv`, `heap-priority-queue.tsv`, etc.)
- `subgroups.tsv` — 119-row index of MainTopic × Subgroup × ProblemCount
- `sources.tsv` — source breakdown (LC 1097, GFG 79, etc.)

**Two gotchas in the regex** (don't simplify):
1. Group keys can contain digits (`DYNAMIC_PROGRAMMING_1`, `MATH_2`) — regex must be `[A-Z_0-9]+` not `[A-Z_]+`.
2. Subgroups block uses nested arrays — must use bracket-balanced walker, not lazy regex.

**When to re-run:** when LearnYard updates their sheet. The current bundle hash changes per deploy.

---

## 3. `fetch_doocs_editorials.py` — Per-problem editorial fetch from doocs/leetcode

Fetches the `README_EN.md` editorial for every problem in a band. Each editorial has:
- YAML frontmatter with algorithmic `tags:` (more specific than LC's broad tags)
- Multiple `### Solution N:` sections naming each approach (e.g. "DP + Monotonic Stack")
- Full solution code in multiple languages (Python, Java, C++, Go, TypeScript, Rust)

**Usage:**
```bash
# Set BAND_TSV, OUT_DIR, SUMMARY at the top of the script (edit), then:
python3 scripts/fetch_doocs_editorials.py
```

**Output** (per band):
- `editorials-data/band_<lo>_<hi>/<padded_id>_<slug>.md` — full editorial markdown per problem
- `editorials-data/band_<lo>_<hi>_summary.tsv` — Slug | ID | Title | Status | DoocsTags | Approaches | File | SourceURL

**URL pattern**: `https://raw.githubusercontent.com/doocs/leetcode/main/solution/<bucket>/<padded_id>.<title>/README_EN.md` where bucket is `(id//100)*100 ~ (id//100)*100+99`, padded as `0XXX-0YYY`. Title spaces URL-encoded as `%20`.

**API fallback:** if direct URL 404s (title mismatch), the script lists the bucket folder via GitHub API to find the right folder.

**Rate limit:** 0.4s. GitHub raw doesn't rate-limit aggressively for moderate volume; the API fallback does (60/hour unauth).

**Already fetched:** 1500-1549 (112/112 hits). Other bands not yet fetched.

**Why doocs and not leetcode.cn:** leetcode.cn editorials are behind Cloudflare bot protection (403s). qinhanmin2014 has only 92 problems total. doocs/leetcode covers ~all of LC + has both Chinese and English READMEs.

---

## 4. `audit_subtopic_supply.py` — Map a band's supply to LearnYard subgroups

Given a band's lctags TSV, applies LC-tag → LearnYard-subgroup classification rules to estimate per-subtopic supply. Used to decide Group A acquisitions at LearnYard granularity rather than broad LC tag granularity.

**Usage:**
```bash
# Edit the BAND_TSV path at the top of the script, then:
python3 scripts/audit_subtopic_supply.py
```

**Output:** stdout-only — prints supply per LearnYard subgroup, sorted desc, plus a ≥3 filter section.

**Caveat:** this is heuristic (LC tags → LY subgroup mapping by tag combinations). For higher-confidence classification, use the doocs editorial data (`fetch_doocs_editorials.py` output) which names the actual algorithm per problem.

**Future improvement:** rewrite to consume doocs `band_<lo>_<hi>_summary.tsv` and use the `Approaches` column directly — gives ground-truth algorithmic classification per problem, not tag inference.

---

## Data-source dependency graph

```
LeetCode GraphQL ─→ zerotrac-data/band_*_lctags.tsv  (tags, AR, difficulty)
LearnYard SPA   ─→ learnyard-data/                   (canonical subtopic taxonomy)
doocs/leetcode  ─→ editorials-data/band_*/           (editorial markdowns + algo names)
                   editorials-data/band_*_summary.tsv

audit_subtopic_supply.py reads: lctags + (optionally) editorials → subtopic counts
```

---

## What's NOT scripted yet (manual or one-off)

- The actual Phase 1 / Phase 2 / topic-install-ledger writes — these are judgment calls per band, made in-session
- Cross-band ownership tracking — lives in per-band `00-Band-Topic-Map.md` files, hand-updated after each solve
- Higher-band (2000+) lctags — explicitly out of scope per the 2026 target

---

## Session-resumption checklist

Next session can fully re-derive the install state by:
1. Read `CLAUDE.md` Step 4 → rules
2. Read `topic-install-ledger.md` → current install state
3. Read `learnyard-data/subgroups.tsv` → canonical taxonomy
4. For any band needing analysis, the lctags TSV + editorials are already on disk — no re-fetch needed
