# algomaster-data — AlgoMaster.io DSA roadmap (scraped)

**694 problems across 32 sections**, one TSV per section + `all_problems.tsv`. Mirrors `learnyard-data/` format.
Scraped 2026-06-03 from `https://algomaster.io/learn/dsa/course-roadmap`.

Columns: `Difficulty ⇥ Title ⇥ Slug ⇥ Source ⇥ Link`. Link = `https://algomaster.io/learn/dsa/<slug>`.
(AlgoMaster slugs ≈ LeetCode slugs for actual problems, so a LeetCode link is usually `https://leetcode.com/problems/<slug>/`.)
Rows with empty Difficulty = intro/lesson chapters (96 of them), not problems.

---

## How it was scraped (reproduce / reuse for other sites)

The page is a Next.js app, but it's **server-rendered** — the full roadmap is in the raw HTML (no JS execution needed). WebFetch is the wrong tool here: it truncates long pages (~stopped at section 29) and lossily summarizes slugs. **Use `curl` + parse the rendered HTML directly** — the sandbox has network.

### 1. Fetch raw HTML
```bash
curl -sL --max-time 30 "https://algomaster.io/learn/dsa/course-roadmap" -o /tmp/algomaster.html
# ~1.66 MB, 803 /learn/dsa/<slug> links
```

### 2. HTML patterns (the selectors that matter)
- **Section header** (32 of them): `<span class="font-semibold text-gray-900 dark:text-gray-100">SECTION</span>`
- **Problem anchor**: `href="/learn/dsa/SLUG" ...>...</a>`
- **Title** (inside the anchor): `<span class="text-sm">TITLE</span>`
- **Difficulty** (inside the anchor): `<span class="md:hidden ... text-COLOR-700 ...">Easy|Medium|Hard</span>`
  - **Gotcha 1 — colors:** Easy = `text-green-700`, **Medium = `text-amber-700`** (NOT yellow), Hard = `text-red-700`. Easiest to match the literal word `(Easy|Medium|Hard)` inside the `md:hidden` span.
  - **Gotcha 2 — stray span:** some titles have an empty `<span></span>` between title and difficulty. Don't require adjacency; search within the whole anchor block.
  - **Gotcha 3:** lessons/intros have no difficulty span → leave blank.
- **Grouping:** assign each problem to the section header with the greatest start-position ≤ the problem's position.

### 3. Parser + regenerate
```python
import re, html
from collections import OrderedDict
raw = open('/tmp/algomaster.html', encoding='utf-8', errors='replace').read()
sec_re   = re.compile(r'<span class="font-semibold text-gray-900 dark:text-gray-100">([^<]+)</span>')
anchor_re= re.compile(r'href="/learn/dsa/([a-z0-9][a-z0-9-]*)"[^>]*>(.*?)</a>', re.S)
title_re = re.compile(r'<span class="text-sm">([^<]*)</span>')
diff_re  = re.compile(r'md:hidden[^>]*>(Easy|Medium|Hard)<')
sections = [(m.start(), html.unescape(m.group(1))) for m in sec_re.finditer(raw)]
def sec_for(p):
    n=sections[0][1]
    for sp,sn in sections:
        if sp<=p: n=sn
        else: break
    return n
def slugify(s): return re.sub(r'[^a-z0-9]+','-', s.lower().replace('&',' and ')).strip('-')
rows=[]
for m in anchor_re.finditer(raw):
    tm=title_re.search(m.group(2))
    if not tm or not tm.group(1).strip(): continue
    dm=diff_re.search(m.group(2))
    rows.append((sec_for(m.start()), dm.group(1) if dm else '', html.unescape(tm.group(1)).strip(), m.group(1)))
# de-dup on (section, slug), then write one TSV per section.
```

### Reuse for the next site
The recipe generalizes: (1) `curl` the page, (2) confirm it's server-rendered (`grep` for a known problem title/slug in the raw HTML — if present, parse directly; if it's a JS shell like Striver A2Z, you need its backend API instead), (3) find the section-header + anchor + difficulty selectors by inspecting one known problem's surrounding markup, (4) group by position, de-dup, write TSVs.

**Known JS-shell sites (need API, not curl-parse):** Striver A2Z (takeuforward.org) — page has only section counts, problems load from a backend endpoint.
